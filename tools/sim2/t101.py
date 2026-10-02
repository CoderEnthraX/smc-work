import pickle, datetime as dt, sys
sys.path.insert(0, "../v10chk")
from port101 import *
from load4 import D
# ---- 1. your Rule C file, decisions only: what C and C+ ask for after each trade
L = 0.0; tot = 0.0
print("1. your Rule C file - next risk after each trade:   C (since the high)   C+ (total below 0)")
for d in D["C"][:19]:
    dd = L - d["pnl"]; L = 0.0 if dd < 0.005 else dd; tot += d["pnl"]
    c = max(50, L) if L > 0.005 else 50; cp = max(50, -tot) if -tot > 0.005 else 50
    if d["n"] in (7, 12, 14, 15, 16, 17, 18):
        print("   after trade %2d (total %+9.2f):   C %8.2f    C+ %8.2f" % (d["n"], tot, c, cp))
# ---- 2. real gold data: every order sized exactly by the rule, carried rebuilt independently
bars = pickle.load(open("m1.pkl", "rb")); H = htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp'}
tot_orders = tot_bad = 0
for m in ("A10", "B", "C", "A+", "B+", "C+"):
    Q = dict(BASE); Q["seqMode"] = m; cl, op, cnt = run(bars, Q, H)
    byx = sorted(cl, key=lambda t: t.xbar); bad = 0
    for (bi, oid, amt, loss, rn) in cnt["seqLog"]:
        Ld = 0.0; T = 0.0; lastx = None; acc = 0.0
        for t in byx:
            if t.xbar > bi: break
            if lastx is not None and t.xbar != lastx:
                d = Ld - acc; Ld = 0.0 if d < 0.005 else d; T += acc; acc = 0.0
            acc += t.pnl; lastx = t.xbar
        d = Ld - acc; Ld = 0.0 if d < 0.005 else d; T += acc
        car = max(0.0, -T) if m.endswith("+") else Ld
        r = m[0]
        exp = 50.0 if car <= 0.005 else {"A": max(50, car + 50), "B": max(50, 2 * car), "C": max(50, car)}[r]
        if abs(exp - amt) > 1e-6: bad += 1
    tot_orders += len(cnt["seqLog"]); tot_bad += bad
    s = stats(cl)
    print("2. %-3s orders %4d  differences %d  | trades %3d  net %9.0f  max drawdown %8.0f" % (m, len(cnt["seqLog"]), bad, s["n"], s["net"], s["dd"]))
print("   all orders", tot_orders, "differences", tot_bad)
