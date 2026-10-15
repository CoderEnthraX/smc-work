# the TradingView zone engine (the Pine text, translated by pine2py) against the EA core's zone decisions:
# the same 1m bars, the same zone timeframe candles (broker clock, like v15sep / the harness), the higher timeframe values and the
# chart signals the core logged (B lines); every zone question the core answered (A lines) is asked to the Pine code too
import sys, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
import v15sep
import pine2py as P
import pinerun as R

PINE = os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.0.txt')
NAN = float('nan')


def load_pine(inputs):
    g = R.mk_env(inputs)
    g['na'] = lambda x: x is None or (isinstance(x, float) and x != x)
    syminfo = R.NS(); syminfo.mintick = 0.01
    g['syminfo'] = syminfo
    g['array'].fill = lambda a, v: a.__setitem__(slice(None), [v] * len(a))
    g['array'].remove = lambda a, i: a.pop(i)
    text = open(PINE).read()
    L = text.split('\n')
    a = [i for i, l in enumerate(L) if l.startswith('f_znUp(string tf) =>')][0] + 1
    b = [i for i, l in enumerate(L) if l == '        array.set(zL, 0, 2)'][0] + 1
    items = P.split_items(text, a, b)
    r = [i for i, l in enumerate(L) if l.startswith('f_retLvl(int dir')][0] + 1
    items = P.split_items(text, r, r + 7)[:1] + items
    keep = ('type ', 'f_retLvl', 'f_znDel', 'f_znAdd', 'f_znOb', 'f_znCandle', 'f_znStep', 'f_znBar', 'f_znAllow', 'f_znFrz', 'var ')
    for it in items:
        f = it[0][1]
        if not f.startswith(keep): continue
        src = '\n'.join(P.translate(it, []))
        exec(compile(src, PINE, 'exec'), g)
    return g


def run(name, extra, htf, binf='m1.bin'):
    log = HERE + '/x150_sep_%s.zn' % name
    a = np.fromfile(HERE + '/' + binf, dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    T = a['t']; O, H, L, C = (a['p'][:, k] for k in range(4))
    sig = int(extra['sig'])
    inp = dict(stZnPct=float(extra.get('znPct', 50)), stZnBig=bool(int(extra.get('znBig', 1))), stZnOb=bool(int(extra.get('znOb', 1))),
               stZnFvg=bool(int(extra.get('znFvg', 1))), stZnHalf=bool(int(extra.get('znHalf', 1))), stZnTwo=bool(int(extra.get('znTwo', 1))),
               stZnLine=bool(int(extra.get('znLine', 1))), stZnF=-1, stZnT=None, stZnB=None)
    cho, bos = (sig % 3) != 1, (sig % 3) != 0
    g = load_pine(inp)
    B = {}; A = {}
    for ln in open(log):
        f = ln.strip().split(',')
        if f[0] == 'B': B[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]))
        else: A.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6])))
    tfs = [htf, v15sep.up(htf), 0]
    tfs[2] = v15sep.up(tfs[1]) if tfs[1] else 0
    keys = [None] * 3; acc = [None] * 3; hist = [[], [], []]
    calls = bad = 0
    nanv = lambda v: NAN if v is None or abs(v) > 1e299 else v
    for i in range(len(T)):
        if i not in B: continue
        t = int(T[i])
        for j in range(3):
            if not tfs[j]: continue
            k = (t + (10800 if v15sep.eu_summer(t) else 7200)) // tfs[j] if (j == 0 and tfs[0] < 604800) else v15sep.bkey(t, tfs[j])
            if k != keys[j]:
                if acc[j] is not None:
                    cs = hist[j]; cs.insert(0, tuple(acc[j])); del cs[8:]
                    get = lambda n, f: cs[n - 1][f] if n - 1 < len(cs) else NAN      # Pine [n] of the zone timeframe: [1] = the candle that closed
                    ku = 3 if get(3, 3) < get(3, 0) else 4 if get(4, 3) < get(4, 0) else 5 if get(5, 3) < get(5, 0) else 0
                    kd = 3 if get(3, 3) > get(3, 0) else 4 if get(4, 3) > get(4, 0) else 5 if get(5, 3) > get(5, 0) else 0
                    g['f_znCandle'](j, get(1, 3), get(1, 2), get(1, 1), get(3, 2), get(3, 1), get(ku, 1) if ku else NAN, get(ku, 2) if ku else NAN,
                                    get(kd, 1) if kd else NAN, get(kd, 2) if kd else NAN)
                keys[j] = k
                acc[j] = [O[i], H[i], L[i], C[i]]
            else:
                acc[j][1] = max(acc[j][1], H[i]); acc[j][2] = min(acc[j][2], L[i]); acc[j][3] = C[i]
        d, hO, hX, hE, cu, cd, bu, bd = B[i]
        g['stT15'] = d; g['stHtO'] = nanv(hO); g['stHtX'] = nanv(hX); g['stHtE'] = hE
        g['S_low'] = float(L[i]); g['S_high'] = float(H[i])
        g['f_znBar']()
        for (dd, tf, kind, top, bot) in A.get(i, []):
            rf, rk, rt, rb = g['f_znAllow'](dd)
            calls += 1
            if tf in (0, 1, 2): same = (rf, rk) == (tf, kind) and abs(rt - top) < 1e-6 and abs(rb - bot) < 1e-6
            else: same = rf == tf
            if not same:
                bad += 1
                if bad <= 5: print('   %s bar %d d %d: pine %s | core %s' % (name, i, dd, (rf, rk, rt, rb), (tf, kind, top, bot)))
        sU = (cho and cu) or (bos and bu)
        sD = (cho and cd) or (bos and bd)
        if d != 0 and (sU if d == 1 else sD):
            g['f_znFrz'](d)
    return calls, bad


if __name__ == '__main__':
    import v15tests
    which = sys.argv[1:] or [c[0] for c in v15tests.SEP]
    for name, Pp, extra, cs, htf in v15tests.SEP:
        if name not in which: continue
        calls, bad = run(name, extra, htf, v15tests.BIN[cs])
        print('%-20s %6d zone questions -> %s' % (name, calls, 'PINE = CORE' if bad == 0 and calls else '%d DIFFER' % bad), flush=True)
