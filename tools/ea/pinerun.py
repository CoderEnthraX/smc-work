# runs the chart structure engine of the OLD (uncompacted) and NEW (compacted) v15.0 Pine side by side on real 1m bars and
# compares, after every bar, the main tier, the internal / inner tier levels and every line / label drawn
import sys, os, re, math as _m
import numpy as np
import pine2py as P

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = (HERE + '/x150_pine_full.txt', 'intDefOn = true', '    f_innClear()')
import os
NEW = (os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.0.txt'), 'f_xClamp(int b) =>', 'f_cutOld(tN.ln, tN.lb, tN.cnt, 10)')
SKIP = ('f_tfPack(', 'plot(')


class Obj:
    reg = None

    def __init__(self, kind, **kw):
        self.kind = kind; self.d = dict(kw); self.dead = False
        Obj.reg.append(self)

    def snap(self): return (self.kind, self.dead, tuple(sorted((k, repr(v)) for k, v in self.d.items())))


class Line(Obj):
    def set_x2(self, x): self.d['x2'] = x
    def set_extend(self, e): self.d['extend'] = e
    def set_color(self, c): self.d['color'] = c
    def set_width(self, w): self.d['width'] = w
    def set_style(self, s): self.d['style'] = s
    def delete(self): self.dead = True


class Label(Obj):
    def set_x(self, x): self.d['x'] = x
    def delete(self): self.dead = True


class NS:
    pass


def mk_env(inputs):
    g = {}
    line = NS()
    line.style_solid, line.style_dotted, line.style_dashed = 'solid', 'dotted', 'dashed'
    line.new = lambda x1, y1, x2, y2, **kw: Line('line', x1=x1, y1=y1, x2=x2, y2=y2, **kw)
    def ldel(l):
        if l is not None: l.dead = True
    line.delete = ldel
    def sxy1(l, x, y): l.d['x1'] = x; l.d['y1'] = y
    def sxy2(l, x, y): l.d['x2'] = x; l.d['y2'] = y
    line.set_xy1, line.set_xy2 = sxy1, sxy2
    line.set_color = lambda l, c: l.set_color(c)
    line.set_width = lambda l, w: l.set_width(w)
    line.set_style = lambda l, s: l.set_style(s)
    label = NS()
    label.style_none, label.style_label_down, label.style_label_up = 'none', 'down', 'up'
    label.new = lambda x, y, text, **kw: Label('label', x=x, y=y, text=text, **kw)
    label.delete = ldel
    def lxy(b, x, y): b.d['x'] = x; b.d['y'] = y
    label.set_xy = lxy
    def lset(k):
        def f(b, v): b.d[k] = v
        return f
    label.set_text, label.set_textcolor, label.set_style, label.set_size, label.set_color = lset('text'), lset('textcolor'), lset('style'), lset('size'), lset('color')
    label.get_text = lambda b: b.d['text']

    class Color:
        black, blue, yellow, gray, white, red = ('black', 0), ('blue', 0), ('yellow', 0), ('gray', 0), ('white', 0), ('red', 0)
        def __call__(self, x): return x
        def new(self, c, t): return (c[0], t)
    color = Color()
    size = NS(); size.tiny, size.small, size.normal, size.large, size.huge = 'tiny', 'small', 'normal', 'large', 'huge'
    yloc = NS(); yloc.belowbar, yloc.abovebar = 'below', 'above'
    extend = NS(); extend.right, extend.none = 'right', 'none'
    array = NS()
    array.new = lambda *a: [] if not a else [a[1] if len(a) > 1 else None] * a[0]
    array.new_float = array.new_int = array.new
    array.push = lambda a, v: a.append(v)
    array.get = lambda a, i: a[i]
    def aset(a, i, v): a[i] = v
    array.set = aset
    array.size = len
    array.shift = lambda a: a.pop(0)
    array.pop = lambda a: a.pop()
    array.clear = lambda a: a.clear()
    array.copy = lambda a: list(a)
    array.slice = lambda a, i, j: a[i:j]
    math = NS()
    def nn(f):
        def h(*a): return None if any(x is None for x in a) else f(*a)
        return h
    math.max, math.min, math.abs = nn(max), nn(min), nn(abs)
    math.avg = nn(lambda *a: sum(a) / len(a))
    st = NS()
    def tostring(v, fmt=None):
        if fmt == '#.##':
            s = ('%.2f' % v).rstrip('0').rstrip('.')
            return s
        return repr(v)
    st.tostring = tostring
    barstate = NS(); barstate.isconfirmed = True

    class UDT:
        _f = []
        def __init__(self, *a):
            for i, (n, d) in enumerate(self._f): setattr(self, n, a[i] if i < len(a) else d)

    def rng(a, b):
        if a is None or b is None: raise ValueError('na loop bound')
        return range(a, b + 1) if a <= b else range(a, b - 1, -1)
    g.update(line=line, label=label, color=color, size=size, yloc=yloc, extend=extend, array=array, math=math, str=st, barstate=barstate,
             UDT=UDT, rng=rng, na=lambda x: x is None, pint=lambda x: None if x is None else int(x), pfloat=lambda x: None if x is None else float(x))
    g.update(inputs)
    return g


def build(path, a_txt, b_txt, g):
    text = open(path).read()
    L = text.split('\n')
    a = [i for i, l in enumerate(L) if l.startswith(a_txt)][0] + 1
    b = [i for i, l in enumerate(L) if l == b_txt]
    b = b[0] + 1
    items = P.split_items(text, a, b)
    methods = set()
    for it in items:
        m = re.match(r'^method\s+(\w+)\s*\(', it[0][1])
        if m: methods.add(m.group(1))
    init, per, defs = [], [], []
    classes = []
    for it in items:
        f = it[0][1]
        if f.startswith(SKIP): continue
        py = P.translate(it, classes)
        src = '\n'.join(py)
        # user method calls -> function calls (Pine calls a method on an na object too)
        for mn in methods:
            src = re.sub(r'([A-Za-z_][\w.]*)\.%s \(\s*\)' % mn, r'%s(\1)' % mn, src)
            src = re.sub(r'([A-Za-z_][\w.]*)\.%s \(' % mn, r'%s(\1, ' % mn, src)
        if f.startswith('type ') or re.match(r'^(method\s+)?[A-Za-z_]\w*\s*\(.*\)\s*=>', f): defs.append(src)
        elif f.startswith('var '): init.append(src)
        else: per.append(src)
    for d in defs: exec(compile(d, path, 'exec'), g)
    for d in init: exec(compile(d, path, 'exec'), g)
    return compile('\n'.join(per), path, 'exec')


def state(g, new):
    def lv(l):
        return None if l is None else (l.price, l.x1, l.sid, l.born, l.done, l.swpP, l.swpB, l.refP, l.idmP, l.idmB, l.idmHit, l.swpT)
    if new:
        tiers = []
        for t in (g['tI'], g['tN']):
            tiers.append((t.tr, t.anc) + tuple((x.p, x.b, x.born, x.swp, x.swpB, x.swpT, x.ref, x.idmP, x.idmHit) for x in (t.c, t.f)))
    else:
        tiers = []
        for k in ('i', 'n'):
            tiers.append((g[k + 'Trend'], g[k + 'AncB']) + tuple(tuple(g[k + s + f] for f in ('P', 'B', 'Born', 'Swp', 'SwpB', 'SwpT', 'Ref', 'IdmP', 'IdmHit')) for s in ('Ceil', 'Flor')))
    return (g['trendDir'], lv(g['ceilS']), lv(g['florS']), g['evBosUp'], g['evBosDn'], g['evChoUp'], g['evChoDn'], g['stSwH'], g['stSwL'],
            g['mRunHi'], g['mRunLo'], tuple(tiers))


def main(n0, n, inputs, live):
    a = np.fromfile(HERE + '/m1.bin', dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))[n0:n0 + n]
    O, Hh, Lw, C = (a['p'][:, k].tolist() for k in range(4))
    envs = []
    for path, x, y in (OLD, NEW):
        reg = []
        Obj.reg = reg
        g = mk_env(inputs)
        code = build(path, x, y, g)
        envs.append((g, code, reg))
    bad = 0
    nmarks = [0, 0]
    for i in range(n):
        snaps = []
        for k, (g, code, reg) in enumerate(envs):
            Obj.reg = reg
            g['bar_index'] = i
            g['last_bar_index'] = i if live else n - 1
            g['S_open'], g['S_high'], g['S_low'], g['S_close'] = O[i], Hh[i], Lw[i], C[i]
            g['H'] = lambda s, j, i=i: None if i - j < 0 else {'open': O, 'high': Hh, 'low': Lw, 'close': C}[s][i - j]
            try:
                exec(code, g)
            except Exception as e:
                print('bar', i, 'OLD' if k == 0 else 'NEW', 'error', repr(e)); raise
            snaps.append((state(g, k == 1), [o.snap() for o in reg if not o.dead], sum(1 for o in reg if o.dead), len(reg)))
        if snaps[0] != snaps[1]:
            bad += 1
            if bad <= 3:
                print('DIFFER at bar', i)
                if snaps[0][0] != snaps[1][0]:
                    print('  old state', snaps[0][0]); print('  new state', snaps[1][0])
                else:
                    o, w = snaps[0][1], snaps[1][1]
                    print('  objects', len(o), len(w))
                    for j in range(max(len(o), len(w))):
                        if j >= len(o) or j >= len(w) or o[j] != w[j]:
                            print('   old', o[j] if j < len(o) else None); print('   new', w[j] if j < len(w) else None); break
    reg_old, reg_new = envs[0][2], envs[1][2]
    def cnt(reg, t):
        return sum(1 for o in reg if o.kind == 'label' and isinstance(o.d.get('text'), str) and o.d['text'].startswith(t))
    return bad, len(reg_old), {t: cnt(reg_old, t) for t in ('iB', 'iC', 'nB', 'nC', '+', '#', 'BOS', 'CHOCH', 'EQ')}


if __name__ == '__main__':
    n0, n = int(sys.argv[1]), int(sys.argv[2])
    live = sys.argv[3] == 'live'
    inp = dict(altMode=False, pbBodyOn=False, pbBodyRef=False, pbSwp2=False)
    for kv in sys.argv[4:]:
        k, v = kv.split('='); inp[k] = v == '1'
    bad, nobj, marks = main(n0, n, inp, live)
    print('bars %d-%d %s %s: objects %d, marks %s -> %s' % (n0, n0 + n, 'live' if live else 'end', ' '.join('%s=%d' % (k, v) for k, v in inp.items()), nobj, marks,
                                                        'IDENTICAL' if bad == 0 else '%d bars DIFFER' % bad))
