# what 'no new trades before news' would have done, 2021-2026, your 1-minute settings, with the 4 US releases of group 29
# (NFP, jobless claims, ISM M, ISM S) - the only news list with history here. Core harness = the EA's core.
import subprocess, csv, collections, datetime as dt, pickle
from cmp import cfg_of
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1.0,'rev':False,'eq0':1e6}
T = [b[0] for b in pickle.load(open('fx.pkl', 'rb'))]
def run(tag, extra):
    c = cfg_of(U, 60); c.update(extra)
    with open('pe_%s.txt' % tag, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    subprocess.run(['./harness', 'pe_%s.txt' % tag, 'm1.bin', 'pe_%s.csv' % tag], check=True, capture_output=True)
    rs = list(csv.DictReader(open('pe_%s.csv' % tag)))
    yr = collections.defaultdict(float)
    for r in rs: yr[dt.datetime.fromtimestamp(T[int(r['ebar'])], dt.timezone.utc).year] += float(r['pnl'])
    net = sum(float(r['pnl']) for r in rs)
    return len(rs), net, yr
rows = [('no news blocks (your settings now)', {}),
        ('group 29 windows (-10 / +20 min)', {'auOn': 1}),
        ('  + no new trades 1 h before', {'auOn': 1, 'preOn': 1, 'preHrs': 1.0}),
        ('  + no new trades 2 h before', {'auOn': 1, 'preOn': 1, 'preHrs': 2.0}),
        ('  + no new trades 4 h before', {'auOn': 1, 'preOn': 1, 'preHrs': 4.0})]
print('%-36s %6s %10s %8s  %s' % ('2021 - Oct 2026, 1m, risk 50', 'trades', 'net', 'R/trade', '  '.join(str(y) for y in range(2021, 2027))))
for nm, ex in rows:
    n, net, yr = run(nm.strip().split()[0] + str(len(ex)) + str(ex.get('preHrs', '')), ex)
    print('%-36s %6d %10.0f %8.3f  %s' % (nm, n, net, net / n / 50.0, '  '.join('%5.0f' % yr[y] for y in range(2021, 2027))))
