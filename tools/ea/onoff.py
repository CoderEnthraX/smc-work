# the same EA with the table + drawings ON (and restarts) must give the same trades as with them OFF
import subprocess, csv
from cmp import cfg_of
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
def run(tag, P, extra):
    c = cfg_of(P, 60); c.update(extra)
    with open('t_%s.cfg' % tag, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    r = subprocess.run(['./simmain', 't_%s.cfg' % tag, 'm1.bin', 't_%s.csv' % tag], capture_output=True, text=True)
    if r.returncode: print(tag, 'FAILED', r.stderr[-300:])
    return sorted(tuple(d.values()) for d in csv.DictReader(open('t_%s.csv' % tag))), r.stderr.strip().split('\n')[-1]
res = []
for nm, P, ex in (('touch', U, {'exec': 0}), ('pend_hedge_ruleC', REC, {'exec': 1, 'dirMode': 3, 'hedgeMoney': 1}),
                  ('touch_short_table', REC, {'exec': 0, 'tableRows': 1, 'tablePos': 4, 'tableSize': 2}),
                  ('pend_news_auto', dict(U, news=[], auto=True), {'exec': 1, 'tablePos': 1, 'htfMarks': 0})):
    base = dict(ex, **{'from': 20000, 'to': 390000})
    a, sa = run(nm + '_off', P, dict(base, tester=1))
    b, sb = run(nm + '_on', P, dict(base, tester=0, draw=1, table=1, restartEvery=3000))
    res.append(a == b)
    print('%-20s drawing+table OFF: %s | ON + restarts: %s | %s' % (nm, sa, sb, 'IDENTICAL' if a == b else 'DIFFER'))
print('ALL IDENTICAL' if all(res) else 'SOME DIFFER')
