import pickle, datetime as dt
from port10 import *
def ladder(results, rule, base=50.0, add=50.0):
    L = 0.0; out = []
    f = {"A": lambda L: max(base, L + add), "B": lambda L: max(base, 2 * L), "C": lambda L: max(base, L)}[rule]
    for pnl in results:
        out.append(f(L) if L > 0 else base)
        d = L - pnl; L = 0.0 if d < 0.005 else d
    out.append(f(L) if L > 0 else base)
    return out
print("1. your Rule B example  (-50, -100, +50, -10):", ladder([-50, -100, 50, -10], "B"), " expected 50 100 300 200 220")
print("   your Rule C example  (-10, -50, +20)      :", ladder([-10, -50, 20], "C"), " expected 50 50 60 50")
print("   your Rule A example  (-50,-30,-30,+20,+420):", ladder([-50, -30, -30, 20, 420], "A"), " expected 50 100 130 160 140 50")
print("   Rule A, amount 10, a -2 loss             :", ladder([-2], "A", add=10), " expected 50 50 (never below the base)")
bars = pickle.load(open("m1.pkl", "rb")); H = htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel'}
LIVE = int(dt.datetime(2026, 4, 1).timestamp())
def check(P):
    Q = dict(BASE); Q.update(P); cl, op, cnt = run(bars, Q, H)
    rule = {"A10": "A", "B": "B", "C": "C"}[P["seqMode"]]
    f = {"A": lambda L: max(50, L + P.get("seqAdd", 50)), "B": lambda L: max(50, 2 * L), "C": lambda L: max(50, L)}[rule]
    byx = sorted(cl, key=lambda t: t.xbar)
    bad = pre = preBad = 0
    for (bi, oid, amt, loss, rn) in cnt["seqLog"]:
        L = 0.0; lastx = None; acc = 0.0
        for t in byx:
            if t.xbar > bi: break
            if P.get("liveT") is not None and bars[t.xbar][0] < P["liveT"]: continue
            if lastx is not None and t.xbar != lastx:
                d = L - acc; L = 0.0 if d < 0.005 else d; acc = 0.0
            acc += t.pnl; lastx = t.xbar
        d = L - acc; L = 0.0 if d < 0.005 else d
        exp = min(f(L) if L > 0 else 50.0, P.get("seqMax", 500.0))
        if abs(exp - amt) > 1e-6: bad += 1
        if P.get("liveT") is not None and bars[bi][0] < P["liveT"]:
            pre += 1
            if amt != 50.0: preBad += 1
    halt_bar = None
    print("2.", P.get("seqMode"), "from", "whole history" if P.get("liveT") is None else "Apr 1 (live)", "| orders", len(cnt["seqLog"]), "mismatches", bad,
          "| orders before live", pre, "not at 50:", preBad, "| halted at end", cnt["seqHalt"], "carried %.2f" % cnt["seqLoss"],
          "| trades", len(cl), "last entry", dt.datetime.utcfromtimestamp(bars[max(t.ebar for t in cl)][0] + IST).strftime("%d %b"))
for m in ("A10", "B", "C"):
    check({'seqMode': m})
    check({'seqMode': m, 'liveT': LIVE})
check({'seqMode': 'C', 'liveT': LIVE, 'capAct': 'Day'})
