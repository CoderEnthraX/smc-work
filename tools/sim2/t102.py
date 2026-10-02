import pickle, datetime as dt
from port101 import *
bars = pickle.load(open("m1.pkl", "rb")); H = htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp'}
LIVE = int(dt.datetime(2026, 4, 1).timestamp())
allo = allbad = 0
for live in (None, LIVE):
    for m in ("A10", "B", "C", "A+", "B+", "C+"):
        Q = dict(BASE); Q["seqMode"] = m; Q["liveT"] = live; cl, op, cnt = run(bars, Q, H)
        byx = sorted(cl, key=lambda t: t.xbar); bad = pre = preBad = 0
        for (bi, oid, amt, loss, rn) in cnt["seqLog"]:
            Ld = 0.0; T = 0.0; lastx = None; acc = 0.0
            for t in byx:
                if t.xbar > bi: break
                if live is not None and bars[t.ebar][0] < live: continue
                if lastx is not None and t.xbar != lastx:
                    d = Ld - acc; Ld = 0.0 if d < 0.005 else d; T += acc; acc = 0.0
                acc += t.pnl; lastx = t.xbar
            d = Ld - acc; Ld = 0.0 if d < 0.005 else d; T += acc
            car = max(0.0, -T) if m.endswith("+") else Ld
            exp = 50.0 if car <= 0.005 else {"A": max(50, car + 50), "B": max(50, 2 * car), "C": max(50, car)}[m[0]]
            if abs(exp - amt) > 1e-6: bad += 1
            if live is not None and bars[bi][0] < live:
                pre += 1; preBad += amt != 50.0
        allo += len(cnt["seqLog"]); allbad += bad
        print("%-3s from %-13s orders %4d differences %d | orders before live %3d not at base: %d" % (m, "whole history" if live is None else "Apr 1 (live)", len(cnt["seqLog"]), bad, pre, preBad))
print("all", allo, "orders, differences", allbad)
