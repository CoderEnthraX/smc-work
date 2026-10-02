import pickle, json, datetime as dt
from port import *
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
T0 = bars[0][0] + 2 * 86400
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0}
cuts = [int(dt.datetime(2026, m, d).timestamp()) for m, d in ((3, 26), (4, 25))]
ROWS = [
 ("base", "Your settings (v8.3: CHOCH only, R 3, pullback 25, stop buffer 1)", {}),
 ("rev", "Close-and-reverse OFF", {'rev': False}),
 ("r2", "Target R 2 instead of 3", {'rr': 2.0}),
 ("ln", "London + New York: entries 13:00-23:00", {'hrOn': 13}),
 ("ny", "New York only: entries 17:00-23:00", {'hrOn': 17}),
 ("r2only", "Rule 2 only (higher timeframe must agree)", {'r1': False}),
 ("mo2", "CHOCH and BOS, max 2 trades open", {'sig': 'BOTH', 'maxOpen': 2}),
 ("mo3", "CHOCH and BOS, max 3 trades open", {'sig': 'BOTH', 'maxOpen': 3}),
 ("be", "Break-even at 1R (group 32)", {'mvBe': True}),
 ("step", "Step stop (group 32)", {'mvStep': True}),
 ("min6", "Minimum stop distance 6", {'minStop': 6.0}),
 ("a", "a. Stacked BOS trades at 50% risk (CHOCH and BOS, max 3)", {'sig': 'BOTH', 'maxOpen': 3, 'bosRiskPct': 50.0}),
 ("b", "b. Higher-timeframe filter (rule 1 in the HTF direction)", {'htfFilt': True, 'r2': False}),
 ("c1", "c. Trailing stop behind the CHOCH* level", {'trail': 'Level'}),
 ("c2", "c. Trailing stop behind every new swing", {'trail': 'Swing'}),
 ("d", "d. Target at the next liquidity, at least 1.5R", {'liqTgt': True, 'liqMinR': 1.5}),
 ("e", "e. Partial profit: 50% at 1R, rest to break-even", {'partOn': True}),
 ("f0", "f. Premium / discount filter with pullback 25 (yours)", {'pdOn': True}),
 ("f", "f. Premium / discount filter 50 + pullback 50", {'pdOn': True, 'pb': 50.0}),
 ("pb50", "   (pullback 50 alone, no filter)", {'pb': 50.0}),
 ("g", "g. Pause for the day after 3 losses in a row", {'lossN': 3}),
 ("hedge", "Hedge: LONG copy + SHORT copy, reverse OFF", None),
 ("cost3", "Your settings with costs 0.3 per ounce instead of 0.6", {'cmU': 0.3, 'comm': 0.15}),
 ("C", "COMBINATION: reverse OFF + pullback 50 + filter f + step stop", {'rev': False, 'pb': 50.0, 'pdOn': True, 'mvStep': True}),
 ("Cny", "COMBINATION above + New York hours 17-23", {'rev': False, 'pb': 50.0, 'pdOn': True, 'mvStep': True, 'hrOn': 17}),
]
def one(P):
    Q = dict(BASE); Q.update(P); cl, op, cnt = run(bars, Q, H)
    return [tr for tr in cl if bars[tr.ebar][0] >= T0]
out = []
for key, name, P in ROWS:
    cl = one({'direction': 'Longs', 'rev': False}) + one({'direction': 'Shorts', 'rev': False}) if P is None else one(P)
    m = [0.0, 0.0, 0.0]
    for tr in cl:
        t = bars[tr.ebar][0]; m[0 if t < cuts[0] else 1 if t < cuts[1] else 2] += tr.pnl
    s = stats(cl)
    out.append(dict(key=key, name=name, n=s["n"], net=round(s["net"]), pf=round(s["pf"], 2), dd=round(s["dd"]), win=round(s["win"], 1), m=[round(x) for x in m]))
    r = out[-1]
    print("%-6s %-62s %4d %7d %5.2f %6d %5.1f%%  %s" % (key, name, r["n"], r["net"], r["pf"], r["dd"], r["win"], r["m"]), flush=True)
json.dump(out, open("final.json", "w"), indent=1)
