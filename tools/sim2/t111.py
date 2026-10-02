import pickle, json
import port110, port111
bars = pickle.load(open("m1.pkl", "rb")); H = port111.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 1e5, 'capAct': 'Clamp', 'lev': 100.0}
seqno = lambda i: int(i.rstrip("p")[1:])
out = {}
# 1) the against modes OFF = v11.0 exactly
same = True
for extra in ({}, {"fav": True}, {"eqOn": True}, {"ldOn": True}, {"sig": "BOTH", "rev": True}, {"r2": False, "fav": True, "eqOn": True}):
    P = dict(BASE, rev=False); P.update(extra)
    a = port110.run(bars, dict(P), H); b = port111.run(bars, dict(P), H)
    same &= [x[:3] for x in a[2]["seqLog"]] == [x[:3] for x in b[2]["seqLog"]] and [(t.id, round(t.pnl, 6)) for t in a[0]] == [(t.id, round(t.pnl, 6)) for t in b[0]]
print("against modes OFF - identical to v11.0:", same, flush=True); out["same"] = same
# 2) the against modes
def chk(Hx, P):
    lg = []; cl, op, cnt = port111.run(bars, dict(P), Hx, log=lg)
    arms = {i + 1: x for i, x in enumerate(lg)}
    return dict(arms=len(lg), trades=len(cl),
                notAgainst=sum(1 for x in lg if Hx[x[0]][0] != -x[1]),
                notRule1=sum(1 for x in lg if x[2] != 1),
                filledAfterAgree=sum(1 for tr in cl + op if any(Hx[b][0] != -tr.dir for b in range(arms[seqno(tr.id)][0], tr.ebar))),
                cancelsOnAgree=cnt.get("agnCanc", 0), skipped=cnt["htfSkip"])
r2 = []
for sig in ("CHOCH", "BOS", "BOTH"):
    for rules in ((True, True), (True, False), (False, True)):
        for rev in (False, True):
            r = dict(sig=sig, r1=rules[0], r2=rules[1], rev=rev, **chk(H, dict(BASE, sig=sig, r1=rules[0], r2=rules[1], rev=rev, agn=True)))
            r2.append(r); print("AGN", r, flush=True)
out["agn"] = r2
for per in (7, 23, 61):
    Hf = [((1 if (i // per) % 2 == 0 else -1), None, None, i // per) for i in range(len(bars))]
    r = dict(flipEvery=per, **chk(Hf, dict(BASE, rev=False, agn=True)))
    print("AGN forced flips", r, flush=True); out.setdefault("forced", []).append(r)
# 3) with the equilibrium gate and the pause
lg = []; cl, op, cnt = port111.run(bars, dict(BASE, rev=False, agn=True, eqOn=True, ldOn=True), H, log=lg)
print("AGN + equilibrium + pause: trades", len(cl), "not against", sum(1 for x in lg if H[x[0]][0] != -x[1]), "gate openings", len(cnt["eqLog"]), "pauses", len(cnt["ldLog"]), flush=True)
# 4) your settings, 3 months
res = []
for name, extra in (("everything off", {}), ("favourable (rule 1 + 2)", dict(fav=True)), ("AGAINST the 15m", dict(agn=True)),
                    ("equilibrium 50%", dict(eqOn=True)), ("AGAINST + equilibrium 50%", dict(agn=True, eqOn=True)),
                    ("AGAINST + equilibrium + pause 3/2", dict(agn=True, eqOn=True, ldOn=True))):
    cl, op, cnt = port111.run(bars, dict(BASE, rev=False, **extra), H)
    pnl = low = 0.0
    for tr in sorted(cl, key=lambda t: t.xbar): pnl += tr.pnl; low = min(low, pnl)
    w = sum(1 for tr in cl if tr.pnl > 0)
    r = dict(name=name, trades=len(cl), wins=w, winrate=round(100 * w / max(1, len(cl))), net=round(pnl, 2), lowest=round(low, 2)); res.append(r); print("YOU", r, flush=True)
out["user"] = res
json.dump(out, open("t111.json", "w"), indent=1)
