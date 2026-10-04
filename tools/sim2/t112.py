# v11.2 test: stop buffer unit (price / pips / % of price)
import pickle, json
import port111, port112
bars = pickle.load(open("m1.pkl", "rb")); H = port112.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 1e5, 'capAct': 'Clamp', 'lev': 100.0, 'rev': False}
key = lambda r: [(t.id, t.ebar, t.xbar, round(t.ep, 5), round(t.xp, 5), round(t.q, 6), round(t.pnl, 6)) for t in r[0]]
out = {}
# 1. unit 'Price' (default) = v11.1, also with the other features that use the buffer
same = True
for extra in ({}, {"trail": "Level"}, {"trail": "Swing"}, {"minStop": 3.0, "maxStop": 40.0}, {"sig": "BOTH", "rev": True}, {"auto": True}):
    P = dict(BASE); P.update(extra)
    same &= key(port111.run(bars, dict(P), H)) == key(port112.run(bars, dict(P), H))
print("unit Price = v11.1 (6 settings):", same, flush=True); out["priceSame"] = same
# 2. pips x the gold pip (0.10) = the same price buffer
eq = []
for pips, price in ((10.0, 1.0), (50.0, 5.0), (25.0, 2.5)):
    a = key(port112.run(bars, dict(BASE, buMode="Pips", buPips=pips), H)); b = key(port112.run(bars, dict(BASE, slbuf=price), H))
    eq.append((pips, price, a == b))
print("pips = price buffer:", eq, flush=True); out["pipsEq"] = eq
# 3. the group 24 limits in pips = the same limits in price
a = key(port112.run(bars, dict(BASE, buMode="Pips", buPips=10.0, minStop=30.0, maxStop=400.0), H)); b = key(port112.run(bars, dict(BASE, minStop=3.0, maxStop=40.0), H))
print("skip closer 30 / further 400 pips = 3 / 40 in price:", a == b, flush=True); out["limEq"] = a == b
# 4. results on these 3 months (OANDA, Feb 25 - May 26 2026, your settings)
res = []
for name, extra in (("price 1.0 (now)", {}), ("10 pips", dict(buMode="Pips", buPips=10.0)), ("50 pips", dict(buMode="Pips", buPips=50.0)),
                    ("0.02%", dict(buMode="Pct", buPct=0.02)), ("0.05%", dict(buMode="Pct", buPct=0.05)), ("0.1%", dict(buMode="Pct", buPct=0.1)), ("0.2%", dict(buMode="Pct", buPct=0.2))):
    cl, op, cnt = port112.run(bars, dict(BASE, **extra), H)
    pnl = sum(t.pnl for t in cl); w = sum(1 for t in cl if t.pnl > 0)
    r = dict(name=name, trades=len(cl), wins=w, net=round(pnl, 2)); res.append(r); print(r, flush=True)
out["three_months"] = res
json.dump(out, open("t112.json", "w"), indent=1)
