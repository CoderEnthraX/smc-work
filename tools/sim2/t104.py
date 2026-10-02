import pickle, json
import port103, port104
bars = pickle.load(open("m1.pkl", "rb")); H = port104.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp'}
out = {}

def check(cl, cnt, P):
    """every order's risk worked out again from the closed trades; the size never rounds past it; the floor never broken"""
    byx = sorted(cl, key=lambda t: t.xbar); bad = over = 0
    for rec in cnt["seqLog"]:
        bi, amt, q_per = rec[0], rec[2], rec[5]
        pnl = peak = 0.0; tot = 0.0; ld = 0.0; lastx = None; acc = 0.0
        for t in byx:
            if t.xbar > bi: break
            if lastx is not None and t.xbar != lastx:
                pnl += acc; peak = max(peak, pnl); d = ld - acc; ld = 0.0 if d < 0.005 else d; tot += acc; acc = 0.0
            acc += t.pnl; lastx = t.xbar
        pnl += acc; peak = max(peak, pnl); d = ld - acc; ld = 0.0 if d < 0.005 else d; tot += acc
        fl = -P["flAmt"] + P["flLock"] / 100.0 * peak; frisk = P["flPct"] / 100.0 * max(0.0, pnl - fl)
        if P["flMode"] == "Size": exp = frisk
        else:
            car = max(0.0, -tot) if P["seqMode"].endswith("+") else ld
            rule = 50.0 if car <= 0.005 else max(50.0, car / P.get("split", 1.0))
            exp = min(rule, frisk) if P["flMode"] == "Cap" else rule
        if abs(exp - amt) > 1e-6: bad += 1
        if q_per > amt + 1e-6: over += 1
    # the floor along the path, after every closed trade (same-candle closes added first)
    pnl = peak = 0.0; margin = 1e9; low = 0.0
    for t in byx:
        pnl += t.pnl; low = min(low, pnl)
        margin = min(margin, pnl - (-P["flAmt"] + P["flLock"] / 100.0 * peak)); peak = max(peak, pnl)
    return bad, over, margin, low

# 1) floor Off = v10.3 exactly
same = True
for m in ("Off", "C+"):
    for rev in (True, False):
        Q = dict(BASE, seqMode=m, split=3.0 if m == "C+" else 1.0, rev=rev, lev=100.0)
        a = port103.run(bars, dict(Q), H); b = port104.run(bars, dict(Q), H)
        same &= [x[:3] for x in a[2]["seqLog"]] == [x[:3] for x in b[2]["seqLog"]] and [round(t.pnl, 6) for t in a[0]] == [round(t.pnl, 6) for t in b[0]]
print("floor Off identical to v10.3:", same, flush=True); out["same"] = same

# 2) Size / Cap, normal and stressed, both directions and reverse ON/OFF
tot_o = tot_b = tot_over = 0; minmargin = 1e9
for direction in ("Both", "Longs", "Shorts"):
    for rev in (False, True):
        for fm, amt, lock, pct, sm in (("Size", 500, 50, 10, "Off"), ("Size", 200, 75, 30, "Off"), ("Cap", 500, 50, 10, "C+"), ("Cap", 150, 0, 40, "C+")):
            P = dict(BASE, direction=direction, rev=rev, lev=100.0, flMode=fm, flAmt=float(amt), flLock=float(lock), flPct=float(pct), seqMode=sm, split=3.0)
            cl, op, cnt = port104.run(bars, dict(P), H)
            bad, over, margin, low = check(cl, cnt, P)
            tot_o += len(cnt["seqLog"]); tot_b += bad; tot_over += over; minmargin = min(minmargin, margin / amt)
            r = dict(dir=direction, rev=rev, mode=fm, amt=amt, lock=lock, pct=pct, rule=sm, trades=len(cl), orders=len(cnt["seqLog"]), bad=bad, over=over,
                     net=round(sum(t.pnl for t in cl), 2), lowest=round(low, 2), margin=round(margin, 2))
            out.setdefault("runs", []).append(r); print(r, flush=True)
print("orders", tot_o, "differences", tot_b, "rounded past the floor risk", tot_over, "closest to the floor (share of the amount)", round(minmargin, 3))
out["tot"] = [tot_o, tot_b, tot_over, minmargin]

# 3) your settings (CHOCH only, reverse OFF, lev 100): Off vs floor
for name, P in (("Fixed 50", dict(flMode="Off")), ("Floor 500 / lock 50 / 10%", dict(flMode="Size")),
                ("Floor + pause after 2 losses", dict(flMode="Size", lossN=2)), ("Fixed 50 + pause after 2 losses", dict(flMode="Off", lossN=2)),
                ("C+ split 3 capped by the floor", dict(flMode="Cap", seqMode="C+", split=3.0))):
    Q = dict(BASE, rev=False, lev=100.0, **P)
    cl, op, cnt = port104.run(bars, Q, H)
    pnl = 0.0; low = 0.0; pk = 0.0; dd = 0.0
    for t in sorted(cl, key=lambda t: t.xbar):
        pnl += t.pnl; low = min(low, pnl); pk = max(pk, pnl); dd = max(dd, pk - pnl)
    r = dict(name=name, trades=len(cl), net=round(pnl, 2), lowest=round(low, 2), maxdd=round(dd, 2), maxrisk=round(max(x[2] for x in cnt["seqLog"]), 2))
    out.setdefault("user", []).append(r); print(r, flush=True)
json.dump(out, open("t104.json", "w"), indent=1)
