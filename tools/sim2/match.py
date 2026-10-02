import pickle, sys, datetime as dt
sys.path.insert(0, "../ana")
from port import *
from load import load, FILES
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
def ist(t): return dt.datetime.utcfromtimestamp(t + IST)
t0 = ist(bars[0][0]) + dt.timedelta(days=2); t1 = ist(bars[-1][0])
usr = [d for d in load(FILES["C 2025-26 CHOCH only"]) if d.get("xt") and t0 <= d["et"] <= t1]
def score(P):
    cl, op, cnt = run(bars, P, H)
    sim = [tr for tr in cl if ist(bars[tr.ebar][0]) >= t0]
    S = {}
    for tr in sim: S[(ist(bars[tr.ebar][0]), tr.dir)] = tr
    m = mq = mx = 0
    for d in usr:
        tr = S.get((d["et"], d["side"]))
        if tr:
            m += 1
            if tr.q == d["q"]: mq += 1
            if ist(bars[tr.xbar][0]) == d["xt"]: mx += 1
    return len(sim), m, mq, mx, round(sum(tr.pnl for tr in sim)), round(sum(d["pnl"] for d in usr))
if __name__ == "__main__":
    for P in eval(sys.argv[1]):
        print(P, score(P))
