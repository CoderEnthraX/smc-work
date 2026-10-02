import pickle, sys, datetime as dt
sys.path.insert(0, "../ana")
from port import *
from load import load, FILES
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
P = eval(sys.argv[1]) if len(sys.argv) > 1 else {}
closed, opn, cnt = run(bars, P, H)
def ist(t): return dt.datetime.utcfromtimestamp(t + IST)
sim = sorted(closed, key=lambda x: x.ebar)
usr = [d for d in load(FILES["C 2025-26 CHOCH only"]) if d.get("xt")]
t0 = ist(bars[0][0]); t1 = ist(bars[-1][0])
usr = [d for d in usr if t0 <= d["et"] <= t1]
ev = []
for d in usr: ev.append((d["et"], "U", d["side"], d["ep"], d["q"], d["xt"], d["xs"], d["xp"], d["pnl"]))
for tr in sim: ev.append((ist(bars[tr.ebar][0]), "S", tr.dir, tr.ep, tr.q, ist(bars[tr.xbar][0]), tr.why, tr.xp, round(tr.pnl, 2)))
ev.sort(key=lambda x: (x[0], x[1]))
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
for e in ev[lo:lo + 60]:
    print(e[0].strftime("%m-%d %H:%M"), e[1], "%+d" % e[2], "%9.3f" % e[3], "%4.0f" % e[4], e[5].strftime("%m-%d %H:%M"), "%-16s" % e[6][:16], e[7], e[8])
