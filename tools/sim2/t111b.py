import pickle, json
import port110, port111
bars = pickle.load(open("m1.pkl", "rb")); H = port111.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 1e5, 'capAct': 'Clamp', 'lev': 100.0}
seqno = lambda i: int(i.rstrip("p")[1:])
def gate_ref(pct, Hx):
    op = False; prev = None; res = []
    for i, (t, o, h, l, c) in enumerate(bars):
        T, O, X, E = Hx[i]
        if prev is not None and E != prev: op = False
        prev = E
        lvl = None
        if T == 1 and O is not None and X is not None and X > O: lvl = X - (X - O) * pct / 100
        if T == -1 and O is not None and X is not None and O > X: lvl = X + (O - X) * pct / 100
        if not op and lvl is not None and ((T == 1 and l <= lvl) or (T == -1 and h >= lvl)): op = True
        res.append(op)
    return res
out = {}
same = True
for extra in ({}, {"fav": True}, {"eqOn": True}, {"agn": True}, {"ldOn": True}, {"sig": "BOTH", "rev": True, "eqOn": True}):
    P = dict(BASE, rev=False); P.update(extra)
    a = port110.run(bars, dict(P), H) if "agn" not in extra else None
    b = port111.run(bars, dict(P), H)
    if a is not None:
        same &= [x[:3] for x in a[2]["seqLog"]] == [x[:3] for x in b[2]["seqLog"]] and [(t.id, round(t.pnl, 6)) for t in a[0]] == [(t.id, round(t.pnl, 6)) for t in b[0]]
print("auto mode OFF - identical to v11.0 (and the against mode unchanged):", same, flush=True); out["same"] = same
res = []
for pct in (50.0, 61.8):
    ref = gate_ref(pct, H)
    allowed = [(H[i][0] if ref[i] else -H[i][0]) for i in range(len(bars))]
    for sig in ("CHOCH", "BOS", "BOTH"):
        for rules in ((True, True), (True, False), (False, True)):
            for rev in (False, True):
                lg = []; cl, op, cnt = port111.run(bars, dict(BASE, sig=sig, r1=rules[0], r2=rules[1], rev=rev, auto=True, eqPct=pct), H, log=lg)
                arms = {i + 1: x for i, x in enumerate(lg)}
                wrongSide = sum(1 for x in lg if x[1] != allowed[x[0]] or allowed[x[0]] == 0)
                p1 = [x for x in lg if not ref[x[0]]]; p2 = [x for x in lg if ref[x[0]]]
                wrongRule = sum(1 for x in p1 if x[2] != 1) + sum(1 for x in p2 if x[2] != (2 if rules[1] else 1))
                filledWrong = sum(1 for tr in cl + op if any(allowed[b] != tr.dir for b in range(arms[seqno(tr.id)][0], tr.ebar)))
                r = dict(pct=pct, sig=sig, r1=rules[0], r2=rules[1], rev=rev, arms=len(lg), part1=len(p1), part2=len(p2), trades=len(cl),
                         wrongSide=wrongSide, wrongRule=wrongRule, filledAfterSwitch=filledWrong, cancelsOnSwitch=cnt.get("autoCanc", 0))
                res.append(r); print("AUTO", r, flush=True)
out["auto"] = res
lg = []; cl, op, cnt = port111.run(bars, dict(BASE, rev=False, auto=True, eqOn=True, ldOn=True), H, log=lg)
ref = gate_ref(50.0, H); allowed = [(H[i][0] if ref[i] else -H[i][0]) for i in range(len(bars))]
print("AUTO + group 37 switch on + pause: trades", len(cl), "wrong side", sum(1 for x in lg if x[1] != allowed[x[0]]), "part 1 arms", sum(1 for x in lg if not ref[x[0]]), flush=True)
ures = []
for name, extra in (("everything off", {}), ("AGAINST the 15m", dict(agn=True)), ("equilibrium 50%", dict(eqOn=True)),
                    ("AUTO 50% (rule 1 + 2)", dict(auto=True)), ("AUTO 50%, rule 1 only", dict(auto=True, r2=False)),
                    ("AUTO 61.8% (rule 1 + 2)", dict(auto=True, eqPct=61.8)), ("AUTO 50% + pause 3/2", dict(auto=True, ldOn=True))):
    lg = []; cl, op, cnt = port111.run(bars, dict(BASE, rev=False, **extra), H, log=lg)
    pnl = low = 0.0
    for tr in sorted(cl, key=lambda t: t.xbar): pnl += tr.pnl; low = min(low, pnl)
    w = sum(1 for tr in cl if tr.pnl > 0)
    r = dict(name=name, trades=len(cl), wins=w, winrate=round(100 * w / max(1, len(cl))), net=round(pnl, 2), lowest=round(low, 2))
    if extra.get("auto"):
        pct = extra.get("eqPct", 50.0); ref = gate_ref(pct, H); arms = {i + 1: x for i, x in enumerate(lg)}
        for part, flag in (("part1", False), ("part2", True)):
            v = [tr.pnl for tr in cl if ref[arms[seqno(tr.id)][0]] == flag]
            r[part] = dict(trades=len(v), wins=sum(1 for x in v if x > 0), net=round(sum(v), 2))
    ures.append(r); print("YOU", r, flush=True)
out["user"] = ures
json.dump(out, open("t111b.json", "w"), indent=1)
