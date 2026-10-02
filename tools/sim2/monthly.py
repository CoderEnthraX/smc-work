import pickle, sys, datetime as dt
from port import *
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
T0 = bars[0][0] + 2 * 86400
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0}
cuts = [int(dt.datetime(2026, m, d).timestamp()) for m, d in ((3, 26), (4, 25))]
def months(P):
    Q = dict(BASE); Q.update(P)
    cl, op, cnt = run(bars, Q, H)
    cl = [tr for tr in cl if bars[tr.ebar][0] >= T0]
    out = [0.0, 0.0, 0.0]
    for tr in cl:
        t = bars[tr.ebar][0]; k = 0 if t < cuts[0] else 1 if t < cuts[1] else 2
        out[k] += tr.pnl
    return out, stats(cl)
base, bs = months({})
print("%-36s %7s %7s %7s | %6s %5s" % ("", "Feb26-Mar25", "Mar26-Apr24", "Apr25-May25", "net", "PF"))
print("%-36s %7.0f %11.0f %11.0f | %6.0f %5.2f" % ("YOUR SETTINGS", *base, bs["net"], bs["pf"]))
for name, P in eval(open(sys.argv[1]).read()):
    m, s = months(P)
    better = sum(1 for a, b in zip(m, base) if a > b)
    print("%-36s %7.0f %11.0f %11.0f | %6.0f %5.2f  better in %d/3 months" % (name, *m, s["net"], s["pf"], better), flush=True)
