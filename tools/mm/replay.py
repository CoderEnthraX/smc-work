import pickle, random, statistics as st
D = pickle.load(open("seqs.pkl", "rb"))
EQ0, BASE = 10000.0, 50.0

def replay(seq, m):
    eq = EQ0; pk = EQ0; lo = EQ0; dd = 0.0; tot = 0.0; day = None; dayp = 0.0; halt = False; n = 0; maxr = 0.0
    for (d, R, why) in seq:
        dk = d[:10]
        if dk != day:
            day = dk; dayp = 0.0
            if halt: halt = False; tot = 0.0          # 'stop for the rest of the day' clears the C+ total
        if eq <= 1: break
        if m == "fixed": r = BASE
        elif m == "pct": r = eq * 0.005
        elif m in ("C+1", "C+3"):
            if halt: continue
            sp = 1.0 if m == "C+1" else 3.0
            hole = max(0.0, -tot); r = max(BASE, hole / sp) if hole > 0.005 else BASE
            if m == "C+3" and r > 500: halt = True; continue
        elif m == "cppi":
            floor = EQ0 - 500 + 0.5 * max(0.0, pk - EQ0)   # never below 9,500, and keep half of every new high
            r = 0.10 * (eq - floor)
            if r < 5: continue
        elif m == "house":
            r = BASE + 0.05 * max(0.0, eq - EQ0)
        elif m == "halfdd":
            dwn = pk - eq; r = BASE if dwn < 500 else BASE / 2 if dwn < 1000 else BASE / 4
        elif m == "daystop":
            if dayp <= -2 * BASE: continue
            r = BASE
        elif m == "combo":   # CPPI floor + C+ split 3 inside the cushion
            floor = EQ0 - 500 + 0.5 * max(0.0, pk - EQ0)
            cush = eq - floor
            hole = max(0.0, -tot); want = max(BASE, hole / 3.0) if hole > 0.005 else BASE
            r = min(want, 0.10 * cush)
            if r < 5: continue
        r = min(r, eq); maxr = max(maxr, r)
        p = R * r; eq += p; tot += p; dayp += p; n += 1
        pk = max(pk, eq); lo = min(lo, eq); dd = max(dd, pk - eq)
    return dict(net=eq - EQ0, low=lo, dd=dd, n=n, maxr=maxr)

M = [("fixed", "Fixed 50 every trade"), ("C+1", "C+ split 1 (no cap)"), ("C+3", "C+ split 3, cap 500, stop day"), ("pct", "0.5% of the account"),
     ("halfdd", "Half risk in a drawdown"), ("daystop", "Stop the day at -2R"), ("house", "House money (50 + 5% of profit)"),
     ("cppi", "Floor 9,500 + lock half (CPPI)"), ("combo", "Floor + C+ split 3 inside it")]
if __name__ == "__main__":
    res = {}
    for k, seq in D.items():
        print("\n==", k, len(seq), "trades, fixed-50 result %+.0f" % (sum(x[1] for x in seq) * 50))
        for code, name in M:
            r = replay(seq, code); res[(k, code)] = r
            print("  %-34s net %+9.0f  lowest %8.0f  maxDD %7.0f  trades %4d  biggest risk %6.0f" % (name, r["net"], r["low"], r["dd"], r["n"], r["maxr"]))
    pickle.dump(res, open("replay.pkl", "wb"))
