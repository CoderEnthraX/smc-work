import csv, pickle, sys, math, random, statistics as st, datetime as dt
from load import U, FILES
sys.path.insert(0, "../sim2")
def load_q(f):
    r = list(csv.DictReader(open(U + f, encoding='utf-8-sig')))
    k = [c for c in r[0] if c.startswith('Net P')][0]; tn = [c for c in r[0] if c.startswith('Trade')][0]
    dc = [c for c in r[0] if c.startswith('Date')][0]; qc = [c for c in r[0] if c.startswith('Size (qty)') or c == 'Size (qty)' or c.startswith('Position size')][0]
    ex = {int(x[tn]): x for x in r if x['Type'].lower().startswith('exit') and x['Signal'] != 'Open'}
    out = []
    for n in sorted(ex, key=lambda n: (ex[n][dc], n)):
        x = ex[n]; q = abs(float(x[qc])); pnl = float(x[k])
        if q <= 0: continue
        sl = 'exit' in x['Signal'] and pnl < 0
        d = abs(pnl) / q if sl else 50.0 / q          # money at risk per unit (oz) at the stop
        out.append((x[dc], pnl / q, d))
    return out
def load_sim(rev):
    import port104
    bars = pickle.load(open("../sim2/m1.pkl", "rb")); H = port104.htf_series(bars, 900)
    cl, op, cnt = port104.run(bars, {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 1e5, 'capAct': 'Clamp', 'rev': rev, 'lev': 100.0}, H)
    out = []
    for t in sorted(cl, key=lambda t: t.xbar):
        d = dt.datetime.utcfromtimestamp(bars[t.xbar][0] + 19800).strftime("%Y-%m-%d %H:%M")
        out.append((d, t.pnl / t.q, abs(t.ep - t.lsl) + 0.6))
    return out
G = {k: load_q(v) for k, v in FILES.items()}
G["Sim Feb-May 2026 (reverse OFF)"] = load_sim(False); G["Sim Feb-May 2026 (reverse ON)"] = load_sim(True)
pickle.dump(G, open("gran.pkl", "wb"))
for k, v in G.items(): print(k, len(v), "median risk per oz %.1f" % st.median(x[2] for x in v))
