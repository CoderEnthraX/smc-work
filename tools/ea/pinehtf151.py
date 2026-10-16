# v15.1: the TradingView higher timeframe function f_tfPack (the Pine text, translated by pine2py) against the EA core: run on the
# same higher timeframe candles (built like the harness: the candle's open time = its first bar), its 5 values after each closed
# candle - trend, leg start, leg extreme, CHOCH / BOS count and (new in v15.1) the open time of the candle where the leg started -
# must equal what the core read on every chart bar of the next candle (the B lines of a 'v151tests.py sep' log).
# usage: NEWPINE=<file> python3 pinehtf151.py [setting names of v151tests.SEP]
import sys, os, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
import v15sep
import pine2py as P
import pinerun as R
from pinezone151 import UDT, isna

PINE = os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.1.txt')
LNONE = -(2 ** 63)


def load(inputs):
    g = R.mk_env(inputs)
    g['na'] = isna
    g['UDT'] = UDT
    text = open(PINE).read()
    L = text.split('\n')
    a = [i for i, l in enumerate(L) if l.startswith('type SwingTracker')][0] + 1
    b = [i for i, l in enumerate(L) if l.startswith('method update(SwingTracker t')][0] + 1
    items = P.split_items(text, a, a + 8)[:1] + P.split_items(text, b, b + 45)[:1]
    for it in items:
        src = '\n'.join(P.translate(it, []))
        exec(compile(src, PINE, 'exec'), g)
    # the body of f_tfPack inside 'if on', dedented: 'var' lines once, the rest on every candle
    f = [i for i, l in enumerate(L) if l.startswith('f_tfPack(bool on) =>')][0]
    k = f + 1
    while L[k].strip() != 'if on': k += 1
    body = []
    j = k + 1
    while j < len(L) and (L[j].startswith('        ') or not L[j].strip()):
        if L[j].strip(): body.append(L[j][8:])
        j += 1
    tail = L[j].strip()
    assert tail == '[trOut, loOut, lxOut, ecOut, lgOut]', tail
    its = P.split_items('\n'.join(body), 1, len(body))
    init, per = [], []
    for it in its:
        src = '\n'.join(P.translate(it, []))
        src = re.sub(r'([A-Za-z_][\w.]*)\.update \(', r'update(\1, ', src)
        (init if it[0][1].startswith('var ') else per).append(src)
    for s in init: exec(compile(s, PINE, 'exec'), g)
    return g, compile('\n'.join(per), PINE, 'exec')


def run(name, extra, htf, binf):
    import v151tests
    log = HERE + '/x151_sep_%s.zn' % name
    a = np.fromfile(HERE + '/' + binf, dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    T = a['t']; O, H, L, C = (a['p'][:, k].tolist() for k in range(4))
    g, code = load(dict(pbSwp2=True, pbBodyOn=False, pbBodyRef=False))
    B = {}
    for ln in open(log):
        if ln.startswith('B,'):
            f = ln.strip().split(',')
            B[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]), int(f[10]))
    key = None; acc = None; nb = -1
    out = (0, None, None, 0, None)
    n = bad = legs = 0
    for i in range(len(T)):
        t = int(T[i])
        k = (t + (10800 if v15sep.eu_summer(t) else 7200)) // htf if htf < 604800 else v15sep.bkey(t, htf)
        if k != key:
            if acc is not None:
                nb += 1
                g['bar_index'] = nb
                g['S_open'], g['S_high'], g['S_low'], g['S_close'], g['S_time'] = acc
                g['trOut'], g['loOut'], g['lxOut'], g['ecOut'], g['lgOut'] = 0, None, None, 0, None
                exec(code, g)
                out = (g['trOut'], g['loOut'], g['lxOut'], g['ecOut'], g['lgOut'])
            key = k
            acc = [O[i], H[i], L[i], C[i], t]
        else:
            acc[1] = max(acc[1], H[i]); acc[2] = min(acc[2], L[i]); acc[3] = C[i]
        if i not in B: continue
        d, hO, hX, hE, hS = B[i]
        n += 1
        tr, lo, lx, ec, lg = out
        same = tr == d and ec == hE and ((lo is None and abs(hO) > 1e299) or (lo is not None and abs(lo - hO) < 1e-7)) and \
            ((lx is None and abs(hX) > 1e299) or (lx is not None and abs(lx - hX) < 1e-7)) and ((lg is None and hS in (LNONE, -1)) or lg == hS)   # -1 = no leg yet in the core (the kill rule 'made <= leg start' can never fire, like Pine's na)
        legs += 1 if lg is not None and lg == hS else 0
        if not same:
            bad += 1
            if bad <= 5: print('   %s bar %d: pine %s | core %s' % (name, i, out, B[i]))
    return n, bad


if __name__ == '__main__':
    import v151tests
    which = sys.argv[1:] or [c[0] for c in v151tests.SEP]
    allok = True
    for name, Pp, extra, cs, htf in v151tests.SEP:
        if name not in which: continue
        n, bad = run(name, extra, htf, v151tests.BIN[cs])
        allok &= bad == 0 and n > 0
        print('%-26s %d chart bars: trend, leg start, leg extreme, count, leg start time -> %s' % (name, n, 'PINE = CORE' if bad == 0 and n else '%d DIFFER' % bad), flush=True)
    print('ALL PINE = CORE' if allok else 'SOME DIFFER')
