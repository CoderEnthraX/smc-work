# v11.2: the whole EA with the stop buffer in % / pips and forced restarts (unload + load at random ticks) must trade exactly like the same EA without restarts
import subprocess, csv
from cmp import cfg_of
def ea(name, P, extra):
    c = cfg_of(P, 60); c.update(extra)
    fn = 'rcfg_%s.txt' % name
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    r = subprocess.run(['./simmain', fn, 'm1.bin', 'rea_%s.csv' % name], capture_output=True, text=True)
    rows = sorted([tuple(d.values()) for d in csv.DictReader(open('rea_%s.csv' % name))])
    return rows, r.stderr.strip().split('\n')[-1]
def test(name, P, extra):
    a, sa = ea(name + '_plain', P, dict(extra, tester=0, draw=1, table=1, tableRows=0))
    b, sb = ea(name + '_restart', P, dict(extra, tester=0, restartEvery=1500, draw=1, table=1, tableRows=1, tablePos=0, htfMarks=0))
    same = a == b
    print('%-22s no restarts: %s | with restarts: %s | %s' % (name, sa, sb, 'IDENTICAL' if same else 'DIFFER'))
    if not same:
        for x, y in zip(a, b):
            if x != y: print('   first diff', x, y); break
    return same
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
Y = {'from': 20000, 'to': 390000}
res = [test('pend_pct01_trail', dict(U, trail='Level', minStop=0.05), dict(Y, exec=1, buMode=2, buPct=0.1)),
       test('touch_pips50_ruleC', REC, dict(Y, exec=0, buMode=1, buPips=50.0))]
print('ALL IDENTICAL' if all(res) else 'SOME DIFFER')
