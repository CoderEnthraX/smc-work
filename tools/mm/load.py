import csv, pickle, math, datetime as dt, sys
U = "/home/user/smc-work/tools/data/uploads/"
FILES = {"2021-22 (reverse ON)": "04256fc8-SMC_STRAT_OANDA_XAUUSD_2026-09-29_13b5f.csv",
         "2023-24 (reverse ON)": "677548be-SMC_STRAT_OANDA_XAUUSD_2026-09-29_22e05.csv",
         "2025-26 CHOCH only (reverse ON)": "693e6914-29th_september_2025_to_29_september_2026_choch_only.csv",
         "Sep 2026 Off (reverse OFF)": "c8ae4cdf-SMC_STRAT_OANDA_XAUUSD_2026-09-30_3f666no_rules_off.csv"}

def load_csv(f):
    r = list(csv.DictReader(open(U + f, encoding='utf-8-sig')))
    k = [c for c in r[0] if c.startswith('Net P')][0]; tn = [c for c in r[0] if c.startswith('Trade')][0]
    dc = [c for c in r[0] if c.startswith('Date')][0]
    ex = {}
    for x in r:
        if x['Type'].lower().startswith('exit') and x['Signal'] != 'Open': ex[int(x[tn])] = x
    out = []
    for n in sorted(ex, key=lambda n: (ex[n][dc], n)):
        out.append((ex[n][dc], float(ex[n][k]) / 50.0, ex[n]['Signal']))
    return out

def load_sim(rev):
    sys.path.insert(0, "../sim2")
    import port103
    bars = pickle.load(open("../sim2/m1.pkl", "rb")); H = port103.htf_series(bars, 900)
    Q = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0, 'bosMode': 'Cancel', 'seqMax': 100000.0, 'capAct': 'Clamp', 'rev': rev, 'lev': 100.0, 'seqMode': 'Off'}
    cl, op, cnt = port103.run(bars, Q, H)
    out = []
    for t in sorted(cl, key=lambda t: t.xbar):
        d = dt.datetime.utcfromtimestamp(bars[t.xbar][0] + 19800).strftime("%Y-%m-%d %H:%M")
        out.append((d, t.pnl / 50.0, t.why))
    return out

if __name__ == "__main__":
    D = {k: load_csv(v) for k, v in FILES.items()}
    D["Sim Feb-May 2026 (reverse OFF)"] = load_sim(False)
    D["Sim Feb-May 2026 (reverse ON)"] = load_sim(True)
    pickle.dump(D, open("seqs.pkl", "wb"))
    for k, v in D.items(): print(k, len(v), v[0][0], v[-1][0], round(sum(x[1] for x in v), 2))
