# whole EA in the fake MT5 (simmain) vs the core harness (TradingView emulation), same settings and bars
import sys, csv, subprocess, time
from cmp import cfg_of
def rows(fn):
    return sorted([(int(d['side']), int(d['dir']), int(d['ebar']), float(d['ep']), round(float(d['q']), 4), int(d['xbar']), float(d['xp']), float(d['pnl'])) for d in csv.DictReader(open(fn))], key=lambda r: (r[2], r[1], r[5], r[4]))
def full(name, P, extra, cs=60, tol=0.0101):
    extra = dict(extra)
    c = cfg_of(P, cs); c.update(extra)
    fn = 'fcfg_%s.txt' % name
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    t0 = time.time()
    r1 = subprocess.run(['./simmain', fn, 'm1.bin', 'fea_%s.csv' % name], capture_output=True, text=True)
    r2 = subprocess.run(['./harness', fn, 'm1.bin', 'fco_%s.csv' % name], capture_output=True, text=True)
    if r1.returncode or r2.returncode: print(name, 'FAILED', r1.stderr, r2.stderr); return False
    a = rows('fea_%s.csv' % name); b = [r for r in rows('fco_%s.csv' % name)]
    # the harness counts trades closed by the end; the EA run may hold the last one open
    same_keys = [(x[1], x[2], x[4], x[5]) for x in a] == [(x[1], x[2], x[4], x[5]) for x in b]
    maxdp = max([max(abs(x[3] - y[3]), abs(x[6] - y[6])) for x, y in zip(a, b)] + [0])
    print('%-24s EA %5d trades %11.2f | core %5d trades %11.2f | bars/dir/size/exit bar %s | max price diff %.4f | %s | %.0fs' % (
        name, len(a), sum(x[7] for x in a), len(b), sum(x[7] for x in b), 'SAME' if same_keys else 'DIFFER', maxdp, r1.stderr.strip(), time.time() - t0))
    if not same_keys:
        for i, (x, y) in enumerate(zip(a, b)):
            if (x[1], x[2], x[4], x[5]) != (y[1], y[2], y[4], y[5]): print('   first diff', i, 'EA', x, 'core', y); break
    return same_keys and maxdp <= tol
if __name__ == '__main__':
    U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
    full('user_pending', U, {'exec': 1, 'from': 20000, 'to': 390000})
