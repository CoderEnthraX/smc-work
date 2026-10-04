# v11.2: what the stop buffer size did, 2021 - Oct 2026, your 1-minute settings (the EA's core = the v11.2 rules, rounded to 0.01)
import subprocess, csv, collections, datetime as dt, pickle
from multiprocessing import Pool
from cmp import cfg_of
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1.0,'rev':False,'eq0':1e6}
T = [b[0] for b in pickle.load(open('fx.pkl', 'rb'))]
def job(v):
    tag, slbuf, mode, pips, pct = v
    c = cfg_of(dict(U, slbuf=slbuf), 60); c.update({'buMode': mode, 'buPips': pips, 'buPct': pct, 'buPip': 0.1})
    fn = 'be_%s' % tag.replace(' ', '_').replace('%', 'p').replace('(', '').replace(')', '').replace('.', '_')
    with open(fn + '.txt', 'w') as f:
        for k, x in c.items(): f.write('%s %s\n' % (k, int(x) if isinstance(x, bool) else x))
    subprocess.run(['./harness', fn + '.txt', 'm1.bin', fn + '.csv'], check=True, capture_output=True)
    rs = list(csv.DictReader(open(fn + '.csv')))
    yr = collections.defaultdict(float)
    for r in rs: yr[dt.datetime.fromtimestamp(T[int(r['ebar'])], dt.timezone.utc).year] += float(r['pnl'])
    return tag, len(rs), sum(yr.values()), yr
V = [('1.0 (now)', 1.0, 0, 10, 0), ('10 pips', 0, 1, 10.0, 0), ('0.02%', 0, 2, 0, 0.02), ('0.05%', 0, 2, 0, 0.05), ('0.1%', 0, 2, 0, 0.1), ('0.2%', 0, 2, 0, 0.2),
     ('0.5%', 0, 2, 0, 0.5), ('50 pips', 0, 1, 50.0, 0)]
with Pool(4) as pool: res = pool.map(job, V)
for tag, n, tot, yr in res:
    lose = sum(1 for y in range(2021, 2027) if yr[y] < 0)
    print('%-10s %6d %9.0f %7.3fR  losing %d of 6 | %s' % (tag, n, tot, tot / n / 50, lose, '  '.join('%6.0f' % yr[y] for y in range(2021, 2027))))
