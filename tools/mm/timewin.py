import csv, math, statistics as st, datetime as dt
U = "/home/user/smc-work/tools/data/uploads/"
FILES = {"2021-22": "04256fc8-SMC_STRAT_OANDA_XAUUSD_2026-09-29_13b5f.csv",
         "2023-24": "677548be-SMC_STRAT_OANDA_XAUUSD_2026-09-29_22e05.csv",
         "2025-26": "693e6914-29th_september_2025_to_29_september_2026_choch_only.csv"}
T = {}
for k, f in FILES.items():
    r = list(csv.DictReader(open(U + f, encoding='utf-8-sig')))
    pc = [c for c in r[0] if c.startswith('Net P')][0]; tn = [c for c in r[0] if c.startswith('Trade')][0]
    dc = [c for c in r[0] if c.startswith('Date')][0]; cc = [c for c in r[0] if c.startswith('Cumulative P')][0]
    en = {int(x[tn]): x for x in r if x['Type'].lower().startswith('entry')}
    ex = {int(x[tn]): x for x in r if x['Type'].lower().startswith('exit') and x['Signal'] != 'Open'}
    rows = []
    for n in sorted(ex):
        e = dt.datetime.strptime(en[n][dc], "%Y-%m-%d %H:%M")
        eq = 10000 + float(ex[n][cc]) - float(ex[n][pc])     # account before this trade
        rows.append(dict(t=e, R=float(ex[n][pc]) / 50.0, eq=eq, why=ex[n]['Signal']))
    full = [x for x in rows if x["eq"] > 2000]               # sizes not yet cut by the shrinking account
    T[k] = full
    print(k, "trades", len(rows), "used", len(full), rows[0]["t"].date(), "->", full[-1]["t"].date())
import pickle; pickle.dump(T, open("timewin.pkl", "wb"))

def table(keyf, labels, title):
    print("\n" + title)
    print("%-12s" % "" + "".join("| %-24s" % k for k in T) + "| ALL 3 YEARS")
    print("%-12s" % "" + "".join("| %5s %5s %6s %6s " % ("n", "win%", "sumR", "avgR") for k in T) + "| %5s %6s %6s  %s" % ("n", "sumR", "avgR", "z"))
    for lab in labels:
        line = "%-12s" % lab; allv = []; neg = 0
        for k, rows in T.items():
            v = [x["R"] for x in rows if keyf(x) == lab]; allv += v
            if v:
                line += "| %5d %4.0f%% %+6.1f %+6.2f " % (len(v), 100 * sum(1 for y in v if y > 0) / len(v), sum(v), st.mean(v)); neg += st.mean(v) < 0
            else:
                line += "| %5s %5s %6s %6s " % ("-", "", "", "")
        if allv:
            m = st.mean(allv); se = st.pstdev(allv) / math.sqrt(len(allv)) if len(allv) > 1 else 1
            line += "| %5d %+6.1f %+6.2f %+5.1f %s" % (len(allv), sum(allv), m, m / se if se else 0, "<< LOSS in all 3" if neg == 3 else ("   profit in all 3" if neg == 0 else ""))
        print(line)

table(lambda x: x["t"].hour, list(range(0, 24)), "BY ENTRY HOUR (IST, your chart time)")
def dom(x):
    d = x["t"].day
    return "01-05" if d <= 5 else "06-10" if d <= 10 else "11-15" if d <= 15 else "16-20" if d <= 20 else "21-25" if d <= 25 else "26-31"
table(dom, ["01-05", "06-10", "11-15", "16-20", "21-25", "26-31"], "BY DAY OF THE MONTH (groups of 5 days)")
table(lambda x: x["t"].day, list(range(1, 32)), "BY DAY OF THE MONTH")
table(lambda x: x["t"].strftime("%a"), ["Mon", "Tue", "Wed", "Thu", "Fri"], "BY WEEKDAY")
def nfp(x):   # first Friday of the month = US jobs report (NFP)
    d = x["t"]; first = d.replace(day=1); ff = 1 + (4 - first.weekday()) % 7
    return "NFP Friday" if d.day == ff else "other Fridays" if d.weekday() == 4 else "Mon-Thu"
table(nfp, ["NFP Friday", "other Fridays", "Mon-Thu"], "THE US JOBS-REPORT FRIDAY (first Friday of the month)")
