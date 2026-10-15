# a small Pine -> Python translator for the chart structure engine part of the strategy (test only)
import re

TOK = re.compile(r'"(?:[^"\\]|\\.)*"|\d+\.\d*(?:[eE][-+]?\d+)?|\d+(?:[eE][-+]?\d+)?|[A-Za-z_][\w.]*|:=|==|!=|<=|>=|=>|\+=|-=|\*=|/=|\S')
SERIES = ('open', 'high', 'low', 'close')


def strip_comment(l):
    out = []; q = None; i = 0
    while i < len(l):
        c = l[i]
        if q:
            out.append(c)
            if c == '\\' and i + 1 < len(l): out.append(l[i + 1]); i += 2; continue
            if c == q: q = None
        else:
            if c == '"': q = c
            elif l.startswith('//', i): break
            out.append(c)
        i += 1
    return ''.join(out).rstrip()


def toks(e):
    e = re.sub(r'(array\.new)<[^>]*>', r'\1', e)    # array.new<line>() -> array.new()
    return TOK.findall(e)


def conv_toks(T):
    """token list -> python text; handles ?: , history refs, tuple literals, literals"""
    # split top-level ternary
    depth = 0
    for i, t in enumerate(T):
        if t in '([': depth += 1
        elif t in ')]': depth -= 1
        elif t == '?' and depth == 0:
            # find matching ':'
            d2 = 0; nest = 0
            for j in range(i + 1, len(T)):
                u = T[j]
                if u in '([': d2 += 1
                elif u in ')]': d2 -= 1
                elif d2 == 0 and u == '?': nest += 1
                elif d2 == 0 and u == ':':
                    if nest == 0:
                        return '(%s if %s else %s)' % (conv_toks(T[i + 1:j]), conv_toks(T[:i]), conv_toks(T[j + 1:]))
                    nest -= 1
            raise SyntaxError('no : for ? in ' + ' '.join(T))
    out = []
    i = 0
    while i < len(T):
        t = T[i]
        if t in '([':
            # find the matching bracket, convert the inside split by top-level commas
            d = 0
            for j in range(i, len(T)):
                if T[j] in '([': d += 1
                elif T[j] in ')]':
                    d -= 1
                    if d == 0: break
            inner = T[i + 1:j]
            parts = []; cur = []; d = 0
            for u in inner:
                if u in '([': d += 1
                elif u in ')]': d -= 1
                if u == ',' and d == 0: parts.append(cur); cur = []
                else: cur.append(u)
            if cur or parts: parts.append(cur)
            conv_parts = []
            for p in parts:
                # named argument  name = value
                if len(p) >= 3 and re.match(r'^[A-Za-z_]\w*$', p[0]) and p[1] == '=':
                    conv_parts.append('%s=%s' % (p[0], conv_toks(p[2:])))
                else:
                    conv_parts.append(conv_toks(p))
            prev = out[-1] if out else None
            if t == '[':
                if prev is not None and prev.startswith('S_') and prev[2:] in SERIES:
                    out[-1] = 'H(%r, %s)' % (prev[2:], conv_parts[0])
                else:
                    out.append('(%s,)' % ', '.join(conv_parts) if len(conv_parts) == 1 else '(%s)' % ', '.join(conv_parts))
            else:
                out.append('(%s)' % ', '.join(conv_parts))
            i = j + 1
            continue
        if t == 'na' and not (i + 1 < len(T) and T[i + 1] == '('): out.append('None')
        elif t == 'true': out.append('True')
        elif t == 'false': out.append('False')
        elif t == 'int': out.append('pint')
        elif t == 'float': out.append('pfloat')
        elif t in SERIES: out.append('S_' + t)
        elif t.endswith('.new') and t[:-4][:1].isupper(): out.append(t[:-4])     # UDT.new -> class
        else: out.append(t)
        i += 1
    return ' '.join(out)


def conv(e):
    return conv_toks(toks(e))


TYPES = r'(?:var\s+|varip\s+)?(?:(?:int|float|bool|string|color|line|label|table|box)|array<[\w<>]+>|map<[^>]*>|[A-Z]\w*)\s+'


def stmt(t):
    """one Pine statement (no block header) -> (python, is_assignment)"""
    m = re.match(r'^\[([^\]]*)\]\s*(?::=|=)\s*(.*)$', t)
    if m: return '%s = %s' % (m.group(1), conv(m.group(2))), True
    m = re.match(r'^' + TYPES + r'([A-Za-z_]\w*)\s*=\s*(.*)$', t)
    if m and m.group(1) not in ('not',): return '%s = %s' % (m.group(1), conv(m.group(2))), True
    m = re.match(r'^([A-Za-z_][\w.]*)\s*(:=|=|\+=|-=|\*=|/=)\s*(.*)$', t)
    if m and not t.startswith(('if ', 'while ')):
        op = {':=': '=', '=': '='}.get(m.group(2), m.group(2))
        tgt = m.group(1)
        if tgt in SERIES: tgt = 'S_' + tgt
        return '%s %s %s' % (tgt, op, conv(m.group(3))), True
    return conv(t), False


def translate(lines, classes):
    """lines: list of (indent, text) of one top-level item; returns python lines"""
    py = []

    def body(seq, ind, tail):
        """seq: list of (indent, text) at exactly indent ind and deeper; tail: last statement returns its value"""
        # group into statements with their children
        items = []
        k = 0
        while k < len(seq):
            n, t = seq[k]
            j = k + 1
            while j < len(seq) and seq[j][0] > n: j += 1
            items.append((t, seq[k + 1:j]))
            k = j
        # the tail = the last item, and with it the whole if / else if / else chain it ends
        first_tail = len(items) - 1
        while first_tail > 0 and (items[first_tail][0] == 'else' or items[first_tail][0].startswith('else if ')): first_tail -= 1
        for idx, (t, kids) in enumerate(items):
            last = tail and idx >= first_tail
            pad = ' ' * ind
            if t.startswith('if '):
                py.append(pad + 'if %s:' % conv(t[3:])); body(kids, ind + 4, last) if kids else py.append(pad + '    pass')
            elif t.startswith('else if '):
                py.append(pad + 'elif %s:' % conv(t[8:])); body(kids, ind + 4, last)
            elif t == 'else':
                py.append(pad + 'else:'); body(kids, ind + 4, last)
            elif t.startswith('while '):
                py.append(pad + 'while %s:' % conv(t[6:])); body(kids, ind + 4, False)
            elif re.match(r'^for\s+\[', t):
                m = re.match(r'^for\s+\[(\w+),\s*(\w+)\]\s+in\s+(.*)$', t)
                py.append(pad + 'for %s, %s in enumerate(%s):' % (m.group(1), m.group(2), conv(m.group(3)))); body(kids, ind + 4, False)
            elif re.match(r'^for\s+\w+\s+in\s', t):
                m = re.match(r'^for\s+(\w+)\s+in\s+(.*)$', t)
                py.append(pad + 'for %s in %s:' % (m.group(1), conv(m.group(2)))); body(kids, ind + 4, False)
            elif t.startswith('for '):
                m = re.match(r'^for\s+(\w+)\s*=\s*(.*?)\s+to\s+(.*)$', t)
                py.append(pad + 'for %s in rng(%s, %s):' % (m.group(1), conv(m.group(2)), conv(m.group(3)))); body(kids, ind + 4, False)
            elif t.startswith('switch '):
                py.append(pad + '_sw = %s' % conv(t[7:]))
                first = True
                for kt, kk in [(a[1], None) for a in kids]:
                    m = re.match(r'^(.*?)\s*=>\s*(.*)$', kt)
                    key, val = m.group(1).strip(), m.group(2)
                    v = ('return ' if last else '') + conv(val)
                    if key == '':
                        py.append(pad + 'else:'); py.append(pad + '    ' + v)
                    else:
                        py.append(pad + ('if' if first else 'elif') + ' _sw == %s:' % conv(key)); py.append(pad + '    ' + v)
                    first = False
            elif t in ('break', 'continue'):
                py.append(pad + t)
            else:
                s, asg = stmt(t)
                py.append(pad + ('return ' + s if last and not asg else s))

    n0, first = lines[0]
    if first.startswith('type '):
        name = first.split()[1]
        fields = []
        for n, t in lines[1:]:
            m = re.match(r'^(\S+)\s+(\w+)(?:\s*=\s*(.*))?$', t)
            fields.append((m.group(2), conv(m.group(3)) if m.group(3) else 'None'))
        classes.append(name)
        py.append('class %s(UDT):' % name)
        py.append('    _f = [%s]' % ', '.join('(%r, %s)' % f for f in fields))
        return py
    m = re.match(r'^(method\s+)?([A-Za-z_]\w*)\s*\((.*)\)\s*=>\s*(.*)$', first)
    if m:
        params = [re.sub(r'^.*\s', '', p.strip()) for p in m.group(3).split(',') if p.strip()]
        ptypes = [p.strip().split()[0] for p in m.group(3).split(',') if p.strip()]
        name = m.group(2)
        py.append('def %s(%s):' % (name, ', '.join(params)))
        if m.group(4):
            py.append('    return ' + conv(m.group(4)))
        else:
            body([(n, t) for n, t in lines[1:]], 4, True)
        if m.group(1):
            py.append('%s.%s = %s' % (ptypes[0], name, name))
        return py
    body(lines, 0, False)
    return py


def split_items(text, a, b):
    """top-level items of the file between line numbers a..b (1-based, inclusive)"""
    L = text.split('\n')[a - 1:b]
    R = []
    for raw in L:
        l = strip_comment(raw)
        if not l.strip(): continue
        R.append((len(l) - len(l.lstrip(' ')), l.strip()))
    items = []
    for n, t in R:
        if n == 0: items.append([(n, t)])
        else: items[-1].append((n, t))
    return items
