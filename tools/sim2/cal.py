import pickle, sys, datetime as dt, collections
sys.path.insert(0, "../ana")
from port import *
from load import load, FILES
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
closed, opn, cnt = run(bars, {}, H)
def ist(t): return dt.datetime.utcfromtimestamp(t + IST)
sim = sorted(closed, key=lambda x: x.ebar)
print("sim trades", len(sim), stats(sim), cnt)
usr = [d for d in load(FILES["C 2025-26 CHOCH only"]) if d.get("xt")]
t0 = ist(bars[0][0]); t1 = ist(bars[-1][0])
usr = [d for d in usr if t0 <= d["et"] <= t1]
print("user trades in window", len(usr), "net", round(sum(d["pnl"] for d in usr), 2))
# match by entry minute + side
S = {(ist(bars[tr.ebar][0]).replace(second=0), tr.dir): tr for tr in sim}
m = 0; mp = 0; mx = 0
for d in usr:
    k = (d["et"], d["side"])
    tr = S.get(k)
    if tr:
        m += 1
        if abs(tr.ep - d["ep"]) < 0.6: mp += 1
        if tr.xbar is not None and ist(bars[tr.xbar][0]) == d["xt"]: mx += 1
print("matched entries (time+side)", m, "price within 0.6", mp, "same exit time", mx)
