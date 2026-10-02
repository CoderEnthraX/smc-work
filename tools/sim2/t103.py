import pickle, datetime as dt, json, time, sys
import port101, port103
bars = pickle.load(open("m1.pkl", "rb")); H = port103.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp'}
LIVE = int(dt.datetime(2026, 4, 1).timestamp())
out = {"check": [], "cmp": []}
allo = allbad = 0

def expect(cnt, cl, m, split, base, add, live):
    byx = sorted(cl, key=lambda t: t.xbar); bad = 0
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
        exp = base if car <= 0.005 else {"A": max(base, (car + add) / split), "B": max(base, 2 * car / split), "C": max(base, car / split)}[m[0]]
        if abs(exp - amt) > 1e-6: bad += 1
    return bad

# 1) every order sized by its rule: split 1 / 2.5 / 3, base 50 (Rule A amount 50) and base 75 (Rule A amount 40)
for base, add in ((50.0, 50.0), (75.0, 40.0)):
    for split in (1.0, 2.5, 3.0):
        for live in (None, LIVE):
            for m in ("A10", "B", "C", "A+", "B+", "C+"):
                Q = dict(BASE, seqMode=m, liveT=live, split=split, risk=base, seqAdd=add)
                cl, op, cnt = port103.run(bars, Q, H)
                bad = expect(cnt, cl, m, split, base, add, live)
                n = len(cnt["seqLog"]); allo += n; allbad += bad
                rec = dict(base=base, add=add, split=split, live=live is not None, mode=m, orders=n, bad=bad,
                           above=sum(1 for x in cnt["seqLog"] if x[2] > base + 1e-9))
                if split == 1.0:   # the same orders as v10.2
                    cl0, op0, cnt0 = port101.run(bars, dict(Q), H)
                    rec["same_as_v102"] = [x[:3] for x in cnt0["seqLog"]] == [x[:3] for x in cnt["seqLog"]] and \
                                          [round(t.pnl, 6) for t in cl0] == [round(t.pnl, 6) for t in cl]
                out["check"].append(rec); print(rec, flush=True)
print("all", allo, "orders, differences", allbad, flush=True)
out["all"] = [allo, allbad]

# 2) the user's settings: CHOCH only, close and reverse OFF, Max leverage 100, cap 100,000 / 500, stop for the day
for cap in (100000.0, 500.0):
    for m, split in (("Off", 1.0), ("C+", 1.0), ("C+", 3.0), ("A+", 3.0)):
        Q = dict(BASE, rev=False, lev=100.0, seqMax=cap, capAct="Day", seqMode=m, split=split)
        cl, op, cnt = port103.run(bars, Q, H)
        byx = sorted(cl, key=lambda t: t.xbar); eq = 10000.0; pk = eq; dd = 0.0; lo = eq
        for t in byx:
            eq += t.pnl; pk = max(pk, eq); dd = max(dd, pk - eq); lo = min(lo, eq)
        rec = dict(cap=cap, mode=m, split=split, trades=len(cl), net=round(eq - 10000.0, 2), maxdd=round(dd, 2), lowest=round(lo, 2),
                   maxrisk=round(max([x[2] for x in cnt["seqLog"]] + [0]), 2), orders=len(cnt["seqLog"]))
        out["cmp"].append(rec); print(rec, flush=True)
json.dump(out, open("t103.json", "w"), indent=1)
