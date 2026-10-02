import pickle, random, statistics as st
D = pickle.load(open("seqs.pkl", "rb"))
EQ0, BASE = 10000.0, 50.0

def replay(seq, sz, pause2=False, daylim=None):
    eq = pk = EQ0; lo = EQ0; dd = 0.0; tot = 0.0; day = None; dp = 0.0; lrun = 0; halt = False
    for (d, R, w) in seq:
        if d[:10] != day:
            day = d[:10]; dp = 0.0; lrun = 0
            if halt: halt = False; tot = 0.0
        if eq <= 1: break
        if pause2 and lrun >= 2: continue
        if daylim is not None and dp <= -daylim: continue
        floor = EQ0 - 500 + 0.5 * max(0.0, pk - EQ0); cush = eq - floor
        hole = max(0.0, -tot)
        if sz == "fixed": r = BASE
        elif sz == "pct": r = 0.005 * eq
        elif sz == "C+1": r = max(BASE, hole) if hole > 0.005 else BASE
        elif sz == "C+3":
            if halt: continue
            r = max(BASE, hole / 3) if hole > 0.005 else BASE
            if r > 500: halt = True; continue
        elif sz == "halfdd": dw = pk - eq; r = BASE if dw < 500 else BASE / 2 if dw < 1000 else BASE / 4
        elif sz == "cppi":
            r = 0.10 * cush
            if r < 5: continue
        elif sz == "cppiC3":
            r = min(max(BASE, hole / 3) if hole > 0.005 else BASE, 0.10 * cush)
            if r < 5: continue
        r = min(r, eq); p = R * r; eq += p; tot += p; dp += p
        lrun = lrun + 1 if R <= 0 else 0
        pk = max(pk, eq); lo = min(lo, eq); dd = max(dd, pk - eq)
    return eq - EQ0, dd

def days(seq):
    g = {}
    for x in seq: g.setdefault(x[0][:10], []).append(x)
    return list(g.values())

WORLDS = {"A  your current settings (reverse OFF, +0.14R)": days(D["Sim Feb-May 2026 (reverse OFF)"]) + days(D["Sep 2026 Off (reverse OFF)"]),
          "B  like 2025-26 (-0.04R)": days(D["2025-26 CHOCH only (reverse ON)"]),
          "C  like 2023-24 (-0.13R)": days(D["2023-24 (reverse ON)"])}
METHODS = [("Fixed 50", "fixed", False, None), ("C+ split 1 (no cap)", "C+1", False, None), ("C+ split 3, cap 500, stop day", "C+3", False, None),
           ("0.5% of the account", "pct", False, None), ("Half risk in a drawdown", "halfdd", False, None),
           ("Fixed 50 + stop day after 2 losses", "fixed", True, None), ("Fixed 50 + stop day at -1R", "fixed", False, 50.0),
           ("FLOOR 9,500 + lock half", "cppi", False, None), ("FLOOR + stop day after 2 losses", "cppi", True, None),
           ("FLOOR + 2 losses + C+ split 3 inside", "cppiC3", True, None)]
random.seed(7); NP, NDAY = 3000, 250
out = {}
for wn, dl in WORLDS.items():
    paths = []
    for _ in range(NP):
        seq = []
        for i in range(NDAY):
            dd_ = random.choice(dl); seq += [("%04d" % i + x[0][4:], x[1], x[2]) for x in dd_]
        paths.append(seq)
    print("\n== WORLD", wn, "| %d one-year paths, %d trades a year on average" % (NP, st.mean(len(p) for p in paths)))
    print("   %-38s %8s %9s %9s %9s %9s" % ("method", "profit%", "median", "worst 5%", "lose>1k%", "lose>5k%"))
    for name, sz, p2, dl_ in METHODS:
        res = sorted(replay(p, sz, p2, dl_)[0] for p in paths)
        prof = 100 * sum(1 for r in res if r > 0) / NP
        l1 = 100 * sum(1 for r in res if r < -1000) / NP; l5 = 100 * sum(1 for r in res if r < -5000) / NP
        out[(wn, name)] = dict(profit=prof, median=res[NP // 2], w5=res[int(NP * 0.05)], l1=l1, l5=l5)
        print("   %-38s %7.0f%% %+9.0f %+9.0f %8.0f%% %8.0f%%" % (name, prof, res[NP // 2], res[int(NP * 0.05)], l1, l5), flush=True)
pickle.dump(out, open("mc.pkl", "wb"))
