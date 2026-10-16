# v15.1: the TradingView zone + MSS code (the Pine text itself, translated by pine2py) against the EA core's decisions.
# The same 1-minute bars; the zone timeframe candles built like the harness (broker clock; a candle's 'made' time = the first bar
# of the next candle, its open time = its first bar - the harness convention, so both get the same inputs); the higher timeframe
# values and the chart signals the core logged (B lines). Compared on every bar:
#   f_znReq (run on the zone timeframe candles) -> f_znCandle; the leg change (zones made before it go) -> f_znBar
#   the last zone (L lines), every zone count the core made (A lines: the same zones in the same order), the MSS (M lines: bar,
#   side, broken swing, MSS low / high and its bar), the boxes (Z lines: one per zone, its count 'xN', last zone) and the visits
# usage: python3 pinezone151.py [setting names of v151tests.SEP]   (needs the x151_sep_<name>.zn logs of 'v151tests.py sep')
import sys, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
import v15sep
import pine2py as P
import pinerun as R

PINE = os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.1.txt')
NAN = float('nan')
P.SERIES = ('open', 'high', 'low', 'close', 'time', 'time_close')


def isna(x):
    return x is None or (isinstance(x, float) and x != x)


class UDT:
    _f = []

    def __init__(self, *a, **kw):
        for i, (n, d) in enumerate(self._f):
            v = a[i] if i < len(a) else kw.get(n, d)
            setattr(self, n, NAN if v is None and n in self._fl else v)
    _fl = ('top', 'bot', 'ext')   # float fields of Zn: Pine na arithmetic gives na (NaN here)


class Box:
    def __init__(self, left, top, right, bottom, **kw):
        self.d = dict(left=left, top=top, right=right, bottom=bottom, **kw); self.dead = False


class AnyColor:
    def __getattr__(self, n): return n
    def new(self, c, t): return (c, t)


def load(inputs):
    g = R.mk_env(inputs)
    g['na'] = isna
    g['nz'] = lambda x, y=0: y if isna(x) else x
    g['UDT'] = UDT
    g['color'] = AnyColor()
    syminfo = R.NS(); syminfo.mintick = 0.01
    g['syminfo'] = syminfo
    ar = g['array']
    ar.remove = lambda a, i: a.pop(i)
    ar.afrom = lambda *a: list(a)
    def concat(a, b): a.extend(b); return a
    ar.concat = concat
    bx = R.NS()
    bx.new = lambda left, top, right, bottom, **kw: Box(left, top, right, bottom, **kw)
    def bset(k):
        def f(b, v): b.d[k] = v
        return f
    bx.set_right, bx.set_text, bx.set_border_color, bx.set_bgcolor, bx.set_text_color = (bset(k) for k in ('right', 'text', 'border_color', 'bgcolor', 'text_color'))
    def bdel(b):
        if b is not None: b.dead = True
    bx.delete = bdel
    g['box'] = bx
    xl = R.NS(); xl.bar_time = 'bar_time'; g['xloc'] = xl
    def mmin(*a): return NAN if any(isna(x) for x in a) else min(a)
    def mmax(*a): return NAN if any(isna(x) for x in a) else max(a)
    g['math'].min, g['math'].max = mmin, mmax
    import math as _m
    g['math'].floor = _m.floor
    g['f_tfName'] = lambda tf: str(tf)
    g['bufHi'], g['bufLo'] = [], []          # 'var array<float> bufHi / bufLo' of the chart engine
    text = open(PINE).read()
    text = re.sub(r'#[0-9A-Fa-f]{6}', lambda m: '"%s"' % m.group(0), text).replace('array.from(', 'array.afrom(')
    L = text.split('\n')

    def at(prefix, n=1):
        k = [i for i, l in enumerate(L) if l.startswith(prefix)]
        assert len(k) == n, (prefix, len(k))
        return k[0] + 1

    def items(a, b):
        return P.split_items(text, a, b)
    # functions / types / vars of the zone engine + the MSS (between their first and last line)
    want = []
    want += items(at('f_retExt(int fromBar'), at('f_retExt(int fromBar') + 14)[:1]
    want += items(at('f_retLvl(int dir'), at('f_retLvl(int dir') + 7)[:1]
    want += items(at('f_znTf(int tf) =>'), at('f_znTf(int tf) =>') + 1)[:1]
    a = at('f_znReq() =>'); b = at('f_znTxt(array<Zn> r) =>')
    want += [it for it in items(a, b + 4) if not it[0][1].startswith(('f_znGet', '['))]
    a = at('// v15.1 (section 2): MSS - the chart'); b = at('var int   stSrc = 0')
    mss = items(a, b - 1)
    per_bar = [it for it in mss if not it[0][1].startswith(('var ', 'f_mfAt', 'f_mfFirst'))]
    want += [it for it in mss if it[0][1].startswith(('var ', 'f_mfAt', 'f_mfFirst'))]
    defs, init, decl = [], [], []
    for it in want:
        f = it[0][1]
        src = '\n'.join(P.translate(it, []))
        if f.startswith('type ') or re.match(r'^(method\s+)?[A-Za-z_]\w*\s*\(.*\)\s*=>', f): defs.append(src)
        elif f.startswith('var '): init.append(src)
        else: raise SystemExit('unexpected item ' + f)
    for d in defs: exec(compile(d, PINE, 'exec'), g)
    for d in init: exec(compile(d, PINE, 'exec'), g)
    # the main-body pieces, run every bar: the leg change + f_znBar (inside 'if stZnOn'), the MSS, the boxes + closing the visits
    a = [i for i, l in enumerate(L) if l == 'if stZnOn']
    assert len(a) == 1
    a = a[0] + 1
    blk = items(a, a + 12)[0]
    k = [i for i, (n, t) in enumerate(blk) if t == 'if stHtE != zLeg'][0]
    leg = [(n - 4, t) for n, t in blk[k:]]
    leg = leg[:[i for i, (n, t) in enumerate(leg) if t == 'zLast := f_znBar()'][0] + 1]
    assert len(leg) == 6, leg
    code_leg = compile('\n'.join(P.translate(leg, [])), PINE, 'exec')
    code_mss = compile('\n'.join('\n'.join(P.translate(it, [])) for it in per_bar), PINE, 'exec')
    a = at('if stZnOn and stT15 != 0')
    code_frz = compile('\n'.join(P.translate(items(a, a + 6)[0], [])), PINE, 'exec')
    return g, code_leg, code_mss, code_frz


def run(name, extra, htf, binf):
    log = HERE + '/x151_sep_%s.zn' % name
    a = np.fromfile(HERE + '/' + binf, dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    T = a['t']; O, H, L, C = (a['p'][:, k].tolist() for k in range(4))
    sig = int(extra['sig'])
    cho, bos = (sig % 3) != 1, (sig % 3) != 0
    inp = dict(stZnPct=float(extra.get('znPct', 50)), stZnBig=bool(int(extra.get('znBig', 1))), stZnOb=bool(int(extra.get('znOb', 1))),
               stZnFvg=bool(int(extra.get('znFvg', 1))), stZnHalf=bool(int(extra.get('znHalf', 1))), stZnTwo=bool(int(extra.get('znTwo', 1))),
               stZnLine=bool(int(extra.get('znLine', 1))), stZnLast=bool(int(extra.get('znLast', 0))), stZnSw=bool(int(extra.get('znSw', 0))),
               stZnOb2=bool(int(extra.get('znOb2', 0))), stMssOn=bool(int(extra.get('mssOn', 0))), stMssN=int(extra.get('mssN', 2)),
               stZnBox=True, stZnOn=True, stHtfTf='h', stZnTf1='h1', stZnTf2='h2')
    g, code_leg, code_mss, code_frz = load(inp)
    B, A, Z, Lg, M = {}, {}, {}, {}, {}
    for ln in open(log):
        f = ln.strip().split(',')
        t = f[0]
        if t == 'B': B[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10]))
        elif t == 'A':
            zs = []
            for x in f[5:]:
                if x == 'L': zs.append('L')
                else:
                    q = x.split(':'); zs.append((int(q[0]), int(q[1]), float(q[2]), float(q[3]), int(q[4])))
            A.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), zs))
        elif t == 'Z': Z.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10])))
        elif t == 'L': Lg[int(f[1])] = None if f[2] == '-1' else (int(f[2]), int(f[3]), float(f[4]), float(f[5]), int(f[6]))
        elif t == 'M': M[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]))
    tfs = [htf, v15sep.up(htf), 0]
    tfs[2] = v15sep.up(tfs[1]) if tfs[1] else 0
    g['stZnTf1'] = 'h1' if tfs[1] else ''
    g['stZnTf2'] = 'h2' if tfs[2] else ''
    keys = [None] * 3; acc = [None] * 3; hist = [[], [], []]
    st = dict(calls=0, boxes=0, last=0, mss=0, candles=0)
    bad = [0]

    def bump(msg):
        bad[0] += 1
        if bad[0] <= 8: print('   %s: %s' % (name, msg))
    nanv = lambda v: NAN if v is None or abs(v) > 1e299 else v
    rec = []
    orig_box = g['f_znBox']

    def box_rec(z):
        r = orig_box(z)
        lz = g['zLast']
        rec.append((z.tf, z.k, z.top, z.bot, z.t0, g['S_time'], z.n, 1 if (z.tf != 9 and lz is not None and z.id == lz.id) else 0, z))
        return r
    g['f_znBox'] = box_rec
    LNONE = -(2 ** 63)
    lz_prev = -1
    bufHi, bufLo = g['bufHi'], g['bufLo']

    def zkey(z):
        return 'L' if z.tf == 9 else (z.tf, z.k, z.top, z.bot, z.t0)

    def same(got, want):
        if len(got) != len(want): return False
        for x, y in zip(got, want):
            if x == 'L' or y == 'L':
                if x != y: return False
                continue
            if x[:2] != y[:2] or abs(x[2] - y[2]) > 1e-7 or abs(x[3] - y[3]) > 1e-7 or x[4] != y[4]: return False
        return True
    for i in range(len(T)):
        t = int(T[i])
        g['bar_index'] = i
        g['S_open'], g['S_high'], g['S_low'], g['S_close'], g['S_time'] = O[i], H[i], L[i], C[i], t
        g['H'] = lambda s, j, i=i: NAN if i - j < 0 else {'open': O, 'high': H, 'low': L, 'close': C, 'time': T}[s][i - j]
        # the chart engine's buffers (pushed at the start of every confirmed bar; cut back to 4,900 above 5,150)
        bufHi.append(H[i]); bufLo.append(L[i])
        if len(bufHi) > 5150:
            del bufHi[:len(bufHi) - 4900]; del bufLo[:len(bufLo) - 4900]
        if i not in B: continue
        # the zone timeframe candles that closed: f_znReq on that timeframe's candles, then f_znCandle
        for j in range(3):
            if not tfs[j]: continue
            k = (t + (10800 if v15sep.eu_summer(t) else 7200)) // tfs[j] if (j == 0 and tfs[0] < 604800) else v15sep.bkey(t, tfs[j])
            if k != keys[j]:
                if acc[j] is not None:
                    cs = hist[j]; cs.insert(0, tuple(acc[j]) + (t,)); del cs[8:]
                    F = {'open': 0, 'high': 1, 'low': 2, 'close': 3, 'time': 4, 'time_close': 5}
                    g['H'] = lambda s, n, cs=cs: cs[n - 1][F[s]] if 0 < n <= len(cs) else NAN
                    r = g['f_znReq']()
                    g['H'] = lambda s, j2, i=i: NAN if i - j2 < 0 else {'open': O, 'high': H, 'low': L, 'close': C, 'time': T}[s][i - j2]
                    te, d, c, ft, fb, ot, ob, t1, oT = r
                    st['candles'] += 1
                    g['f_znCandle'](j, int(te), d, c, ft, fb, ot, ob, NAN if isna(t1) else int(t1), NAN if isna(oT) else int(oT))
                keys[j] = k
                acc[j] = [O[i], H[i], L[i], C[i], t]
            else:
                acc[j][1] = max(acc[j][1], H[i]); acc[j][2] = min(acc[j][2], L[i]); acc[j][3] = C[i]
        d, hO, hX, hE, cu, cd, bu, bd, hS = B[i]
        g['stT15'] = d; g['stHtO'] = nanv(hO); g['stHtX'] = nanv(hX); g['stHtE'] = hE; g['stHtS'] = NAN if hS == LNONE else hS
        g['_cU'] = (cho and cu == 1) or (bos and bu == 1)
        g['_cD'] = (cho and cd == 1) or (bos and bd == 1)
        exec(code_leg, g)
        lz = g['zLast']
        lid = lz.id if lz is not None else -1
        if lid != lz_prev:
            st['last'] += 1
            got = Lg.get(i, 'none')
            want = None if lz is None else (lz.tf, lz.k, lz.top, lz.bot, lz.t0)
            if got == 'none' or (want is None) != (got is None) or (want is not None and not same([got], [want])):
                bump('last zone bar %d: pine %s | core %s' % (i, want, got))
        elif i in Lg:
            bump('last zone bar %d: core logged %s, the pine zone did not change' % (i, Lg[i]))
        lz_prev = lid
        exec(code_mss, g)
        if g['msU'] or g['msD'] or i in M:
            st['mss'] += 1
            w = (1 if g['msU'] else -1, g['msPiv'], g['msLow'], g['msLowB']) if (g['msU'] or g['msD']) else None
            m = M.get(i)
            if w is None or m is None or w[0] != m[0] or abs(w[1] - m[1]) > 1e-7 or abs(w[2] - m[2]) > 1e-7 or w[3] != m[3]:
                bump('MSS bar %d: pine %s | core %s' % (i, w, m))
        for (dd, kind, zs) in A.get(i, []):
            st['calls'] += 1
            want = [zkey(z) for z in g['f_znCount'](dd, kind)]
            if not same(zs, want): bump('count bar %d d %d kind %d: pine %s | core %s' % (i, dd, kind, want, zs))
        rec.clear()
        exec(code_frz, g)
        got = Z.get(i, [])
        want = []
        for (tf, kd, top, bot, t0, t1, n, last, z) in rec:
            if tf == 9: want.append((d, 9, 2, g['stHtO'], g['stHtO'], t0, t1, n, 0))
            else: want.append((d, tf, kd, top, bot, t0, t1, n, last))
            # the box itself: left = the zone's candle (the line: its first touch), right = this candle, the count in the text
            b = z.bx
            if b is None or b.d['left'] != t0 or b.d['right'] != t or (n > 1) != (' x%d' % n in b.d['text']):
                bump('box object bar %d: %s' % (i, None if b is None else b.d))
        if want or got:
            st['boxes'] += len(want)
            ok = len(got) == len(want) and all(x[:3] == y[:3] and abs(x[3] - y[3]) < 1e-7 and abs(x[4] - y[4]) < 1e-7 and x[5:] == y[5:] for x, y in zip(got, want))
            if not ok: bump('boxes bar %d: pine %s | core %s' % (i, want, got))
    return st, bad[0]


if __name__ == '__main__' and not os.environ.get('CF'):
    import v151tests
    which = sys.argv[1:] or [c[0] for c in v151tests.SEP]
    allok = True
    for name, Pp, extra, cs, htf in v151tests.SEP:
        if name not in which: continue
        st, bad = run(name, extra, htf, v151tests.BIN[cs])
        ok = bad == 0 and st['calls'] > 0
        allok &= ok
        print('%-26s candles %d, counts %d, boxes %d, last-zone changes %d, MSS %d -> %s' % (name, st['candles'], st['calls'], st['boxes'], st['last'], st['mss'],
              'PINE = CORE' if ok else '%d DIFFER' % bad), flush=True)
    print('ALL PINE = CORE' if allok else 'SOME DIFFER')


# ---------------- the MSS confirmation (rule 4) block of the Pine, run on every MSS setup the core armed with the confirmation ON (W
# lines): from the next bar, until the core's setup ended; the Pine's 'confirmed' bar + stop and 'failed' bar = the core's (K / F lines)
def cf_run(name, extra, binf, slbuf=1.0):
    log = HERE + '/x151_sep_%s.zn' % name
    a = np.fromfile(HERE + '/' + binf, dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    T = a['t']; O, H, L, C = (a['p'][:, k].tolist() for k in range(4))
    g = R.mk_env(dict(stZnOb2=bool(int(extra.get('znOb2', 0)))))
    g['na'] = isna
    g['nz'] = lambda x, y=0: y if isna(x) else x
    g['f_audEnd'] = lambda t, c: None
    g['f_mt'] = lambda v: '%.2f' % v
    g['str'].startswith = lambda a, b: a.startswith(b)
    g['stAudit'] = False; g['stAudLb'] = None; g['stAudCancC'] = None
    g['stUBf'] = 0; g['stBfX'] = slbuf; g['stPipSz'] = 0.1
    g['stMssSt'] = 'Newest swing low / high (the pullback)' if int(extra.get('mssSt', 0)) == 1 else 'First MSS low / high'
    import math as _m
    g['math'].floor = _m.floor
    def mmin(*v): return NAN if any(isna(x) for x in v) else min(v)
    def mmax(*v): return NAN if any(isna(x) for x in v) else max(v)
    g['math'].min, g['math'].max = mmin, mmax
    text = open(PINE).read()
    Lt = text.split('\n')
    def at(prefix):
        k = [i for i, l in enumerate(Lt) if l.startswith(prefix)]
        assert len(k) == 1, prefix
        return k[0] + 1
    g['f_stBuf'] = lambda lv: slbuf        # the stop buffer in price (these settings); pine2py reads 'x == 1 ? ...' at a line start as an assignment
    for pre in ('f_mfAt(int d, int k) =>',):
        it = P.split_items(text, at(pre), at(pre) + 4)[:1]
        exec(compile('\n'.join(P.translate(it[0], [])), PINE, 'exec'), g)
    b0 = at('if stDir != 0 and stRule == 4')
    blk = P.split_items(text, b0, b0 + 30)[0]
    code = compile('\n'.join(P.translate(blk, [])), PINE, 'exec')
    W, K, F, E = {}, {}, {}, {}
    for ln in open(log):
        f = ln.strip().split(',')
        if f[0] == 'W': W[(int(f[2]), int(f[3]))] = (int(f[1]), int(f[4]), int(f[5]), float(f[6]), float(f[8]))
        elif f[0] == 'K': K[(int(f[2]), int(f[3]))] = (int(f[1]), float(f[5]))
        elif f[0] == 'F': F[(int(f[2]), int(f[3]))] = int(f[1])
        elif f[0] == 'E': E.setdefault((int(f[2]), int(f[3])), int(f[1]))
    n = bad = nk = nf = 0
    for key, (wb, d, rule, low, cft) in sorted(W.items()):
        if rule != 4: continue
        n += 1
        g.update(stDir=d, stRule=4, stCf=1, stCfTop=cft, stCfTch=None, stCfPb=None, stMsLow=low, stMsBar=wb, stSl=None,
                 stArmBar=wb, stMktBar=None, stCntMsCf=0, stCntMsF=0, stCntCanc=0)
        e = E.get(key, len(T))
        got = None
        for b in range(wb + 1, min(e + 1, len(T))):
            if b == e and key not in K and key not in F: break          # the core ended it before its rule 4 step (a cancel)
            g['bar_index'] = b
            g['S_open'], g['S_high'], g['S_low'], g['S_close'] = O[b], H[b], L[b], C[b]
            g['H'] = lambda s, j, b=b: NAN if b - j < 0 else {'open': O, 'high': H, 'low': L, 'close': C}[s][b - j]
            exec(code, g)
            if g['stDir'] == 0: got = ('F', b, None); break
            if g['stRule'] == 3: got = ('K', b, g['stSl']); break
        want = ('K', K[key][0], K[key][1]) if key in K else ('F', F[key], None) if key in F else None
        nk += key in K; nf += key in F
        same = (got is None and want is None) or (got is not None and want is not None and got[:2] == want[:2] and (got[2] is None or abs(got[2] - want[2]) < 1e-7))
        if not same:
            bad += 1
            if bad <= 5: print('   %s setup %s: pine %s | core %s' % (name, key, got, want))
    return n, nk, nf, bad


if __name__ == '__main__' and os.environ.get('CF'):
    import v151tests
    for name, Pp, extra, cs, htf in v151tests.SEP:
        if not int(extra.get('mssCf', 0)): continue
        n, nk, nf, bad = cf_run(name, extra, v151tests.BIN[cs], float(Pp.get('slbuf', 1.0)))
        print('%-26s %d MSS setups waiting for the confirmation (core: %d confirmed, %d failed) -> %s' % (name, n, nk, nf, 'PINE = CORE' if bad == 0 and n else '%d DIFFER' % bad), flush=True)
