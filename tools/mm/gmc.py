import pickle, random, math, statistics as st
G = pickle.load(open("gran.pkl", "rb"))
EQ0 = 10000.0
def qty(r, d):
    if r <= 0 or d <= 0: return 0
    raw = r / d; q = math.floor(raw + 0.5)
    if q * d > r * 1.25: q = math.floor(raw)
    return q
def run(seq, mode="fixed", amt=0, lock=50, pct=0, pause2=False, c3=False):
    pnl = pk = 0.0; low = 0.0; day = None; lr = 0; tot = 0.0; halt = False; n = 0
    for d_, ppo, d in seq:
        if d_[:10] != day:
            day = d_[:10]; lr = 0
            if halt: halt = False; tot = 0.0
        if pause2 and lr >= 2: continue
        r = 50.0
        if c3:
            if halt: continue
            hole = max(0.0, -tot); r = max(50.0, hole / 3) if hole > 0.005 else 50.0
            if r > 500: halt = True; continue
        if mode != "fixed":
            fl = -amt + lock / 100.0 * pk; fr = pct / 100.0 * max(0.0, pnl - fl)
            r = fr if mode == "size" else min(r, fr)
        q = qty(r, d)
        if q <= 0: continue
        p = q * ppo; pnl += p; tot += p; n += 1
        lr = lr + 1 if p <= 0 else 0
        pk = max(pk, pnl); low = min(low, pnl)
        if pnl <= -EQ0 + 1: break
    return pnl, low, n
M = [("Fixed 50", dict()), ("C+ split 3, cap 500, stop day", dict(c3=True)),
     ("Floor size 500 / 10%", dict(mode="size", amt=500, pct=10)), ("Floor size 2000 / 2.5%", dict(mode="size", amt=2000, pct=2.5)),
     ("Floor cap 1000 / 5%", dict(mode="cap", amt=1000, pct=5)), ("Floor cap 2000 / 2.5%", dict(mode="cap", amt=2000, pct=2.5)),
     ("Floor cap 2000 / 2.5% + C+ split 3", dict(mode="cap", amt=2000, pct=2.5, c3=True))]
print("REAL SEQUENCES (net / lowest / trades)")
for k, s in G.items():
    print("  " + k)
    for name, kw in M:
        p, lo, n = run(s, **kw); print("     %-36s %+8.0f %+8.0f %5d" % (name, p, lo, n))
def days(seq):
    g = {}
    for x in seq: g.setdefault(x[0][:10], []).append(x)
    return list(g.values())
W = {"A  your settings (reverse OFF, 2026)": days(G["Sim Feb-May 2026 (reverse OFF)"]) + days(G["Sep 2026 Off (reverse OFF)"]),
     "B  like 2025-26": days(G["2025-26 CHOCH only (reverse ON)"]), "C  like 2023-24": days(G["2023-24 (reverse ON)"])}
random.seed(5); NP = 2000
print("\nONE-YEAR MONTE CARLO WITH 1-OZ STEPS (profit chance / median / worst 5% / worst)")
for wn, dl in W.items():
    paths = [[x for _ in range(250) for x in random.choice(dl)] for _ in range(NP)]
    print("  " + wn)
    for name, kw in M:
        r = sorted(run(p, **kw)[0] for p in paths)
        print("     %-36s %4.0f%% %+8.0f %+8.0f %+8.0f" % (name, 100 * sum(1 for x in r if x > 0) / NP, r[NP // 2], r[NP // 20], r[0]), flush=True)
