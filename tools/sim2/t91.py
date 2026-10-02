import pickle, datetime as dt
from port91 import *
# ---- 1. the ladder arithmetic, your example (base 50, amount 50)
def ladder(results, base=50.0, add=50.0):
    L = 0.0; out = []
    for pnl in results:
        out.append(L + add if L > 0 else base)
        d = L - pnl; L = 0.0 if d < 0.005 else d
    out.append(L + add if L > 0 else base)
    return out
print("1. your example  results -50,-30,-30,+20,+420 -> risks", ladder([-50, -30, -30, 20, 420]))
print("   amount 10     same results               -> risks", ladder([-50, -30, -30, 20, 420], add=10))
print("   five full losses (loss = risk)            ->", end=" ")
L = 0; rs = []
for k in range(6):
    r = L + 50 if L > 0 else 50; rs.append(r); L += r
print(rs, "(cap 500 stops at the 5th trade: 800 > 500)")
bars = pickle.load(open("m1.pkl", "rb")); H = htf_series(bars, 900)
T0 = bars[0][0] + 2 * 86400
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0}
def go(P):
    Q = dict(BASE); Q.update(P); return run(bars, Q, H)
# ---- 2. on real data: every order's risk = carried + 50 (or 50 when nothing is carried), carried rebuilt independently
for P in ({'seqMode': 'A91', 'bosMode': 'Cancel'}, {'seqMode': 'A91', 'bosMode': 'Cancel', 'seqAdd': 10.0}, {'seqMode': 'A91', 'bosMode': 'Cancel', 'seqMax': 300.0}):
    cl, op, cnt = go(P)
    bad = 0; n = 0
    byx = sorted(cl, key=lambda t: (t.xbar, t.ebar))
    for (bi, oid, amt, loss, rn) in cnt["seqLog"]:
        L = 0.0
        for t in byx:
            if t.xbar > bi: break
            d = L - t.pnl; L = 0.0 if d < 0.005 else d
        exp = L + P.get('seqAdd', 50.0) if L > 0 else 50.0
        exp = min(exp, P.get('seqMax', 500.0))
        n += 1
        if abs(exp - amt) > 1e-6: bad += 1
    # realised risk of each filled trade vs the planned amount (lot rounding)
    s = stats([t for t in cl if bars[t.ebar][0] >= T0])
    last = max(t.ebar for t in cl)
    print("2.", P, "orders checked", n, "mismatches", bad, "| trades", s["n"], "net %.0f" % s["net"], "maxDD %.0f" % s["dd"],
          "| halted at end:", cnt["seqHalt"], "carried %.2f" % cnt["seqLoss"], "last entry", dt.datetime.utcfromtimestamp(bars[last][0] + IST).strftime("%d %b"))
# ---- 3. the BOS cancel: no CHOCH order fills after a BOS
for P in ({}, {'bosMode': 'Cancel'}, {'bosMode': 'Cancel', 'sig': 'BOTH'}, {'bosMode': 'Cancel', 'sig': 'BOS'}):
    cl, op, cnt = go(P)
    print("3.", P, "trades", len(cl), "filled after a same-side BOS since arming:", sum(1 for t in cl if t.grp))
