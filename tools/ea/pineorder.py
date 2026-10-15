# declared-before-use check of a Pine file (TradingView refuses a function / global variable / type used above its declaration):
# every top-level function, method, type and global variable is found with its line; every use of that name in an earlier
# line (outside strings and comments, not after a '.', not a named argument) is reported.
import re, sys
TOK = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[A-Za-z_][\w.]*|\S')


def strip_comment(l):
    out = []; q = None; i = 0
    while i < len(l):
        c = l[i]
        if q:
            out.append(c)
            if c == '\\' and i + 1 < len(l): out.append(l[i + 1]); i += 2; continue
            if c == q: q = None
        else:
            if c in '"\'': q = c
            elif l.startswith('//', i): break
            out.append(c)
        i += 1
    return ''.join(out)


def check(path):
    L = [strip_comment(x) for x in open(path).read().split('\n')]
    decl = {}
    for i, l in enumerate(L, 1):
        if not l or l[0].isspace(): continue
        m = re.match(r'^(?:method\s+)?([A-Za-z_]\w*)\s*\(.*\)\s*=>', l) or re.match(r'^type\s+([A-Za-z_]\w*)', l)
        if m:
            decl.setdefault(m.group(1), i); continue
        m = re.match(r'^(?:var\s+|varip\s+)?(?:[A-Za-z_][\w.]*(?:<[^>]*>)?\s+)?([A-Za-z_]\w*)\s*=[^=>]', l)
        if m and m.group(1) not in ('if', 'for', 'while', 'switch'):
            decl.setdefault(m.group(1), i); continue
        m = re.match(r'^\[([^\]]*)\]\s*=', l)
        if m:
            for n in m.group(1).split(','): decl.setdefault(n.strip(), i)
    # local names (function parameters and declarations inside blocks) shadow nothing here: only top-level names are checked,
    # and a use counts only when no local of the same name is declared earlier in the same function / block
    bad = []
    fn_start = 0; locals_ = set()
    for i, l in enumerate(L, 1):
        if not l.strip(): continue
        if not l[0].isspace():
            locals_ = set()
            m = re.match(r'^(?:method\s+)?[A-Za-z_]\w*\s*\((.*)\)\s*=>', l)
            if m:
                for p in m.group(1).split(','):
                    p = p.strip()
                    if p: locals_.add(re.sub(r'\s*=.*$', '', p).split()[-1])
        else:
            m = re.match(r'^\s+(?:var\s+|varip\s+)?(?:[A-Za-z_][\w.]*(?:<[^>]*>)?\s+)?([A-Za-z_]\w*)\s*=[^=>]', l)
            if m: locals_.add(m.group(1))
            m = re.match(r'^\s+\[([^\]]*)\]\s*=', l)
            if m:
                for n in m.group(1).split(','): locals_.add(n.strip())
            m = re.match(r'^\s+for\s+(?:\[([^\]]*)\]|(\w+))', l)
            if m:
                for n in (m.group(1) or m.group(2)).split(','): locals_.add(n.strip())
        T = TOK.findall(l)
        for k, t in enumerate(T):
            if t[0] in '"\'' or not re.match(r'^[A-Za-z_]', t): continue
            name = t.split('.')[0]
            if name not in decl or decl[name] <= i: continue
            if k > 0 and T[k - 1] == '.': continue
            if k + 1 < len(T) and T[k + 1] == '=' and (k == 0 or T[k - 1] in '(,'): continue   # named argument
            if name in locals_: continue
            bad.append((i, name, decl[name]))
    return bad


if __name__ == '__main__':
    for p in sys.argv[1:]:
        b = check(p)
        print('%s: %s' % (p.split('/')[-1], 'every name declared before use' if not b else '%d USED BEFORE DECLARED' % len(b)))
        for i, n, d in b[:30]: print('   line %d uses %s (declared on line %d)' % (i, n, d))
