import pickle, json
import port104
bars = pickle.load(open("m1.pkl", "rb")); H = port104.htf_series(bars, 900)
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp', 'lev': 100.0}
res = []
for rev in (False, True):
    for name, P in (("Fixed 50", dict(flMode="Off")), ("Fixed 50 + pause 2", dict(flMode="Off", lossN=2)),
                    ("Size 500/10% strict", dict(flMode="Size")), ("Size 500/10%", dict(flMode="Size", flStrict=False)),
                    ("Size 1000/5%", dict(flMode="Size", flStrict=False, flAmt=1000.0, flPct=5.0)),
                    ("Size 2000/2.5%", dict(flMode="Size", flStrict=False, flAmt=2000.0, flPct=2.5)),
                    ("Size 2000/2.5% + pause 2", dict(flMode="Size", flStrict=False, flAmt=2000.0, flPct=2.5, lossN=2)),
                    ("Cap 1000/5%", dict(flMode="Cap", flStrict=False, flAmt=1000.0, flPct=5.0)),
                    ("Cap 2000/2.5%", dict(flMode="Cap", flStrict=False, flAmt=2000.0, flPct=2.5)),
                    ("Cap 2000/2.5% + pause 2", dict(flMode="Cap", flStrict=False, flAmt=2000.0, flPct=2.5, lossN=2))):
        cl, op, cnt = port104.run(bars, dict(BASE, rev=rev, **P), H)
        pnl = low = pk = dd = 0.0
        for t in sorted(cl, key=lambda t: t.xbar):
            pnl += t.pnl; low = min(low, pnl); pk = max(pk, pnl); dd = max(dd, pk - pnl)
        r = dict(rev=rev, name=name, trades=len(cl), net=round(pnl), lowest=round(low), maxdd=round(dd), maxrisk=round(max(x[2] for x in cnt["seqLog"])))
        res.append(r); print(r, flush=True)
json.dump(res, open("t104b.json", "w"), indent=1)
