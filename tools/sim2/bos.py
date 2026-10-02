import pickle, datetime as dt, sys
from port_bos import *
bars = pickle.load(open("m1.pkl", "rb")); H = htf_series(bars, 900)
T0 = bars[0][0] + 2 * 86400
cuts = [int(dt.datetime(2026, m, d).timestamp()) for m, d in ((3, 26), (4, 25))]
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0}
def go(P):
    Q = dict(BASE); Q.update(P); cl, op, cnt = run(bars, Q, H)
    return [t for t in cl if bars[t.ebar][0] >= T0]
for label, P in (("v8.3 now (Follow)", {}), ("Cancel at the BOS", {'bosMode': 'Cancel'}), ("Freeze at the BOS", {'bosMode': 'Freeze'}),
                 ("rev OFF, Follow", {'rev': False}), ("rev OFF, Cancel", {'rev': False, 'bosMode': 'Cancel'}), ("rev OFF, Freeze", {'rev': False, 'bosMode': 'Freeze'})):
    cl = go(P); s = stats(cl)
    a = [t for t in cl if t.grp]; b = [t for t in cl if not t.grp]
    m = [0, 0, 0]
    for t in cl: x = bars[t.ebar][0]; m[0 if x < cuts[0] else 1 if x < cuts[1] else 2] += t.pnl
    print("%-20s n %3d net %6.0f PF %.2f DD %5.0f months %s | filled AFTER a BOS: %3d trades net %6.0f win %4.1f%% | before: %3d net %6.0f" % (
        label, s["n"], s["net"], s["pf"], s["dd"], [round(x) for x in m], len(a), sum(t.pnl for t in a), 100 * sum(1 for t in a if t.pnl > 0) / max(1, len(a)), len(b), sum(t.pnl for t in b)))
