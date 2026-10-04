# the whole EA with forced restarts (unload + load at random ticks) must trade exactly like the same EA without restarts
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
    a, sa = ea(name + '_plain', P, dict(extra, tester=0))
    b, sb = ea(name + '_restart', P, dict(extra, tester=0, restartEvery=1500))
    same = a == b
    print('%-22s no restarts: %s | with restarts: %s | %s' % (name, sa, sb, 'IDENTICAL' if same else 'DIFFER'))
    if not same:
        for x, y in zip(a, b):
            if x != y: print('   first diff', x, y); break
    return same
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
Y = {'from': 20000, 'to': 390000}
res = [test('pend_user', U, dict(Y, exec=1)), test('touch_user', U, dict(Y, exec=0)),
       test('pend_ruleC_pause', REC, dict(Y, exec=1)), test('touch_ruleC_pause', REC, dict(Y, exec=0)),
       test('pend_hedge_shared_C', REC, dict(Y, exec=1, dirMode=3, hedgeMoney=1)), test('touch_hedge_own', U, dict(Y, exec=0, dirMode=3)),
       test('pend_mvStep_part', dict(U, mvStep=True, partOn=True), dict(Y, exec=1)), test('touch_trail_rev', dict(U, trail='Swing', rev=True), dict(Y, exec=0)),
       test('pend_ruleCp_floor', dict(REC, seqMode='C+', flMode='Cap'), dict(Y, exec=1)), test('touch_daylimits', dict(U, maxTrades=2, dayLoss=100.0, lossN=2), dict(Y, exec=0))]
print('ALL IDENTICAL' if all(res) else 'SOME DIFFER %d of %d' % (sum(res), len(res)))
