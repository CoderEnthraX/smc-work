import csv, subprocess, time, pickle, bisect
from cmp import cfg_of
from fullcmp import rows
m1 = pickle.load(open('fx.pkl', 'rb')); T1 = [b[0] for b in m1]
m15 = pickle.load(open('fx15.pkl', 'rb')); T15 = [b[0] for b in m15]
def run(name, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    ce = dict(c); ch = dict(c)
    if cs == 900:   # the EA run walks 1-minute ticks; the core harness walks 15-minute bars
        ch['from'] = bisect.bisect_left(T15, T1[c['from']]); ch['to'] = bisect.bisect_left(T15, T1[c['to'] - 1]) + 1 if c['to'] < len(T1) else len(T15)
    for fn, d in (('lcfg_e_%s.txt' % name, ce), ('lcfg_h_%s.txt' % name, ch)):
        with open(fn, 'w') as f:
            for k, v in d.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    t0 = time.time()
    r1 = subprocess.run(['./simmain', 'lcfg_e_%s.txt' % name, 'm1.bin', 'lea_%s.csv' % name], capture_output=True, text=True)
    r2 = subprocess.run(['./harness', 'lcfg_h_%s.txt' % name, 'm1.bin' if cs == 60 else 'm15.bin', 'lco_%s.csv' % name], capture_output=True, text=True)
    a = rows('lea_%s.csv' % name); b = rows('lco_%s.csv' % name)
    if cs == 900:   # bar numbers differ between the two runs: compare by time
        a = [(x[0], x[1], m1[x[2]][0] // 900, x[3], x[4], m1[x[5]][0] // 900, x[6], x[7]) for x in a]
        b = [(x[0], x[1], m15[x[2]][0] // 900, x[3], x[4], m15[x[5]][0] // 900, x[6], x[7]) for x in b]
    ka = [(x[1], x[2], x[4], x[5]) for x in a]; kb = [(x[1], x[2], x[4], x[5]) for x in b]
    md = max([max(abs(x[3] - y[3]), abs(x[6] - y[6])) for x, y in zip(a, b)] + [0])
    print('%-26s EA %5d trades %11.2f | core %5d trades %11.2f | %s | max price diff %.4f | %.0fs' % (name, len(a), sum(x[7] for x in a), len(b), sum(x[7] for x in b),
          'SAME TRADES' if ka == kb else 'DIFFER', md, time.time() - t0))
    if ka != kb:
        for i, (x, y) in enumerate(zip(a, b)):
            if (x[1], x[2], x[4], x[5]) != (y[1], y[2], y[4], y[5]): print('   first diff', i, x, y); break
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':100.0,'rev':False,'eq0':10000.0}
B15 = dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', seqMode='C', split=1.0,
           seqMax=300.0, capAct='Clamp', ldOn=True, ldN=4, ldD=3, wkHr=23, lev=100.0, eq0=10000.0, htfTf=14400)
N = len(T1)
run('user_1m_pending_6y', dict(U, lev=500.0, eq0=1e6), {'exec': 1, 'from': 20000, 'to': N, 'grid': 1, 'fixTies': 1})
run('user_1m_touch_6y', dict(U, lev=500.0, eq0=1e6), {'exec': 0, 'from': 20000, 'to': N, 'grid': 1, 'fixTies': 1})
run('best_15m_pending_6y', B15, {'exec': 1, 'from': 20000, 'to': N, 'grid': 1, 'fixTies': 1, 'chartSec': 900, 'htfSrv': 1}, cs=900)
run('best_15m_touch_6y', B15, {'exec': 0, 'from': 20000, 'to': N, 'grid': 1, 'fixTies': 1, 'chartSec': 900, 'htfSrv': 1}, cs=900)
