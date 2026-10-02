import pickle, json, datetime as dt
from zoneinfo import ZoneInfo
import port104, port110
bars = pickle.load(open("m1.pkl", "rb"))
H4 = port104.htf_series(bars, 900); H = port110.htf_series(bars, 900)
IST = ZoneInfo("Asia/Kolkata")
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 1e5, 'capAct': 'Clamp', 'lev': 100.0}
out = {}
seqno = lambda i: int(i.rstrip("p")[1:])

# 1) everything OFF = v10.4 exactly (and the HTF trend is unchanged)
same = [h[0] for h in H] == H4
for sig in ("CHOCH", "BOTH", "BOS"):
    for rev in (False, True):
        for extra in ({}, {"r2": False}, {"htfFilt": True}):
            P = dict(BASE, sig=sig, rev=rev, **extra)
            a = port104.run(bars, dict(P), H4); b = port110.run(bars, dict(P), H)
            same &= [x[:3] for x in a[2]["seqLog"]] == [x[:3] for x in b[2]["seqLog"]] and [(t.id, round(t.pnl, 6)) for t in a[0]] == [(t.id, round(t.pnl, 6)) for t in b[0]]
print("all new features OFF - identical to v10.4:", same, flush=True); out["off_same"] = same

# 2) FEATURE 2 - favourable modes
f2 = []
for sig in ("CHOCH", "BOS", "BOTH"):
    for rules in ((True, True), (True, False), (False, True)):
        for rev in (False, True):
            P = dict(BASE, sig=sig, r1=rules[0], r2=rules[1], rev=rev, fav=True)
            lg = []; cl, op, cnt = port110.run(bars, dict(P), H, log=lg)
            arms = {i + 1: x for i, x in enumerate(lg)}
            badArm = sum(1 for x in lg if x[1] != x[5])                      # traded against the HTF
            expRule = 2 if rules[1] else 1
            badRule = sum(1 for x in lg if x[2] != expRule)
            badHold = 0                                                      # filled after the HTF stopped agreeing
            for tr in cl + op:
                a = arms[seqno(tr.id)]
                if any(H[b][0] != tr.dir for b in range(a[0], tr.ebar)): badHold += 1
            r = dict(sig=sig, r1=rules[0], r2=rules[1], rev=rev, arms=len(lg), trades=len(cl), against=badArm, wrongRule=badRule,
                     filledAfterFlip=badHold, flipCancels=cnt.get("favCanc", 0), skipped=cnt["htfSkip"])
            f2.append(r); print("F2", r, flush=True)
out["f2"] = f2

# 3) FEATURE 3 - higher timeframe equilibrium first
def gate_ref(pct):
    """the gate worked out again on its own from the HTF leg and the 1m candles"""
    op = False; prev = None; res = []
    for i, (t, o, h, l, c) in enumerate(bars):
        T, O, X, E = H[i]
        if prev is not None and E != prev: op = False
        prev = E
        lvl = None
        if T == 1 and O is not None and X is not None and X > O: lvl = X - (X - O) * pct / 100
        if T == -1 and O is not None and X is not None and O > X: lvl = X + (O - X) * pct / 100
        if not op and lvl is not None and ((T == 1 and l <= lvl) or (T == -1 and h >= lvl)): op = True
        res.append(op)
    return res
# the HTF leg itself: its extreme is the highest high (lowest low) of the HTF candles since its CHOCH / BOS
keys = []; agg = []
for t, o, h, l, c in bars:
    k = t // 900
    if not keys or keys[-1] != k: keys.append(k); agg.append([o, h, l, c])
    else:
        a = agg[-1]; a[1] = max(a[1], h); a[2] = min(a[2], l); a[3] = c
e = port110.HTF(); legs = [e.step(i, *x) for i, x in enumerate(agg)]
xbad = 0; start = None
for j, (T, O, X, E) in enumerate(legs):
    if j == 0 or E != legs[j - 1][3]: start = j
    if T == 1 and X != max(agg[m][1] for m in range(start, j + 1)): xbad += 1
    if T == -1 and X != min(agg[m][2] for m in range(start, j + 1)): xbad += 1
print("F3 HTF legs:", legs[-1][3], "CHOCH/BOS on 15m, leg extremes that differ from the highest high / lowest low since the break:", xbad, flush=True)
f3 = []
for pct in (50.0, 61.8):
    ref = gate_ref(pct)
    for sig, fav in (("CHOCH", False), ("CHOCH", True), ("BOTH", False)):
        for rev in (False, True):
            P = dict(BASE, sig=sig, fav=fav, rev=rev, eqOn=True, eqPct=pct)
            lg = []; cl, op, cnt = port110.run(bars, dict(P), H, log=lg)
            arms = {i + 1: x for i, x in enumerate(lg)}
            armClosed = sum(1 for x in lg if not ref[x[0]])
            fillClosed = sum(1 for tr in cl + op if any(not ref[b] for b in range(arms[seqno(tr.id)][0], tr.ebar)))
            opens = sum(1 for i in range(1, len(ref)) if ref[i] and not ref[i - 1])
            r = dict(pct=pct, sig=sig, fav=fav, rev=rev, arms=len(lg), trades=len(cl), armedWhileClosed=armClosed, filledWhileClosed=fillClosed,
                     gateOpenings=opens, simOpenings=len(cnt["eqLog"]), shareOfTimeOpen=round(sum(ref) / len(ref), 3))
            f3.append(r); print("F3", r, flush=True)
out["f3"] = f3

# 4) FEATURE 1 - pause for D days after N losses in a row
def until_ref(xt, d, alld):
    x = dt.datetime.fromtimestamp(xt, IST).date(); n = 0; k = 0
    while n < d:
        k += 1
        if alld or (x + dt.timedelta(days=k)).weekday() < 5: n += 1
    r = x + dt.timedelta(days=k + 1)
    return int(dt.datetime(r.year, r.month, r.day, tzinfo=IST).timestamp())
f1 = []
LIVE = int(dt.datetime(2026, 4, 1).timestamp())
for N, D, alld, live in ((3, 2, False, None), (2, 1, False, None), (2, 3, False, None), (2, 2, True, None), (2, 2, False, LIVE), (1, 1, False, None)):
    for rev in (False, True):
        P = dict(BASE, rev=rev, ldOn=True, ldN=N, ldD=D, ldAll=alld, liveT=live)
        cl, op, cnt = port110.run(bars, dict(P), H)
        # the pauses worked out again from the list of trades (closing order, counted trades only)
        exp = []; run_ = 0; until = None
        for tr in cl:
            if tr.piece == "p": continue
            xt = bars[tr.xbar][0]
            if live is not None and bars[tr.ebar][0] < live: continue
            if until is not None and xt < until: continue
            run_ = run_ + 1 if tr.pnl < 0 else (0 if tr.pnl > 0 else run_)
            if run_ >= N:
                until = until_ref(xt, D, alld); exp.append((tr.xbar, until)); run_ = 0
        got = [(a, c) for a, b, c in cnt["ldLog"]]
        fillsIn = sum(1 for tr in cl + op for a, c in got if bars[tr.ebar][0] > bars[a][0] and bars[tr.ebar][0] < c)
        wd = sorted({dt.datetime.fromtimestamp(c, IST).strftime("%a") for a, c in got})
        r = dict(N=N, D=D, allDays=alld, live=live is not None, rev=rev, trades=len(cl), pauses=len(got), pausesMatch=got == exp,
                 tradesInsidePauses=fillsIn, resumeDays=wd)
        f1.append(r); print("F1", r, flush=True)
out["f1"] = f1
# a worked example of one pause
cl, op, cnt = port110.run(bars, dict(BASE, rev=False, ldOn=True, ldN=3, ldD=2), H)
if cnt["ldLog"]:
    a, xt, u = cnt["ldLog"][0]
    ex = dict(trigger=dt.datetime.fromtimestamp(xt, IST).strftime("%a %d %b %H:%M"), resume=dt.datetime.fromtimestamp(u, IST).strftime("%a %d %b %H:%M"),
              nextTrade=dt.datetime.fromtimestamp(min(bars[tr.ebar][0] for tr in cl if bars[tr.ebar][0] > xt), IST).strftime("%a %d %b %H:%M"))
    print("F1 example", ex); out["f1ex"] = ex

# 5) all three together (plus the floor) - the same checks at once
P = dict(BASE, rev=False, fav=True, eqOn=True, ldOn=True, ldN=3, ldD=2, flMode="Cap")
lg = []; cl, op, cnt = port110.run(bars, dict(P), H, log=lg); ref = gate_ref(50.0); arms = {i + 1: x for i, x in enumerate(lg)}
comb = dict(trades=len(cl), against=sum(1 for x in lg if x[1] != x[5]), armedWhileClosed=sum(1 for x in lg if not ref[x[0]]),
            tradesInsidePauses=sum(1 for tr in cl + op for a, b, c in cnt["ldLog"] if bars[tr.ebar][0] > bars[a][0] and bars[tr.ebar][0] < c))
print("ALL THREE", comb, flush=True); out["comb"] = comb

# 6) your settings (CHOCH only, reverse OFF, Max leverage 100), 3 months
res = []
for name, extra in (("v10.4 / all off", {}), ("F2 CHOCH only favourable (rule 1 + 2)", dict(fav=True)), ("F2 favourable, rule 1 only", dict(fav=True, r2=False)),
                    ("F3 equilibrium 50%", dict(eqOn=True)), ("F1 pause 3 losses / 2 days", dict(ldOn=True)), ("F2 + F3", dict(fav=True, eqOn=True)),
                    ("all three", dict(fav=True, eqOn=True, ldOn=True))):
    cl, op, cnt = port110.run(bars, dict(BASE, rev=False, **extra), H)
    pnl = low = 0.0
    for tr in sorted(cl, key=lambda t: t.xbar): pnl += tr.pnl; low = min(low, pnl)
    w = sum(1 for tr in cl if tr.pnl > 0)
    r = dict(name=name, trades=len(cl), wins=w, net=round(pnl, 2), lowest=round(low, 2)); res.append(r); print("YOU", r, flush=True)
out["user"] = res
json.dump(out, open("t110.json", "w"), indent=1)
