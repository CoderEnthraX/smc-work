# group 41 checks over the whole 2021-2026 data:
#  (1) the Python simulator with the news rules worked out separately (calflags.py) == the core harness (the EA's core)
#  (2) the WHOLE EA in the fake MT5 == the core harness: tester (reads the saved file), live (fake MT5 calendar, both clock kinds),
#      and live with restarts
import subprocess, csv, pickle, sys, time, bisect
from multiprocessing import Pool
from cmp import cfg_of, run_py, bars
from fullcmp import rows
import calflags
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
SIMCAL = 'simcal_rich.csv'
FILE_DIR = 'simfiles_rule_usd/'          # saved by the EA itself (calexport.py)
def write_cfg(fn, c):
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
def keyrows(rs): return [(r[1], r[2], round(r[3], 5), round(r[4], 4), r[5], round(r[6], 5)) for r in rs]
def harness_rows(tag, c, cs):
    write_cfg('ccfg_h_%s.txt' % tag, c)
    r = subprocess.run(['./harness', 'ccfg_h_%s.txt' % tag, 'm1.bin' if cs == 60 else 'm15.bin', 'cco_%s.csv' % tag], capture_output=True, text=True)
    if r.returncode: print(tag, 'harness failed', r.stderr); return None
    out = []
    for d in csv.DictReader(open('cco_%s.csv' % tag)):
        out.append((int(d['side']), int(d['dir']), int(d['ebar']), float(d['ep']), round(float(d['q']), 4), int(d['xbar']), float(d['xp']), d['why'], float(d['pnl'])))
    return sorted(out, key=lambda r: (r[2], r[5], r[1], r[3], r[4], r[6]))
def ea_rows(tag, c):
    write_cfg('ccfg_e_%s.txt' % tag, c)
    r = subprocess.run(['./simmain', 'ccfg_e_%s.txt' % tag, 'm1.bin', 'cea_%s.csv' % tag], capture_output=True, text=True)
    if r.returncode: print(tag, 'EA failed', r.stderr[-400:]); return None, ''
    return rows('cea_%s.csv' % tag), r.stderr.strip().split('\n')[-1]
def py_case(t):
    tag, P, ex, fl, cs = t
    T = bars(cs)
    news, pre = calflags.flags(T, cs=cs, **fl)
    P = dict(P, news=news, pre=pre)
    a = run_py(P, cs)
    c = cfg_of(dict(P, news=None, pre=None), cs); c.update(ex)
    b = harness_rows('py_' + tag, c, cs)
    same = b is not None and keyrows(a) == keyrows(b)
    nb = sum(1 for x in news if x); npb = sum(1 for x in pre if x)
    return '%-26s Python %5d trades %11.2f | core %5d trades %11.2f | %s   (bars in a window/holiday %d, before news %d)' % (
        tag, len(a), sum(r[8] for r in a), len(b or []), sum(r[8] for r in (b or [])), 'IDENTICAL' if same else 'DIFFER', nb, npb), same
def ea_case(t):
    tag, P, ex, kind = t
    c = cfg_of(P, 60); c.update(ex); c.update({'from': 20000, 'grid': 1, 'fixTies': 1, 'fileDir': FILE_DIR})
    if kind == 'tester': c.update({'tester': 1})
    elif kind == 'live_rule': c.update({'tester': 0, 'calMode': 0})
    elif kind == 'live_now': c.update({'tester': 0, 'calMode': 1})
    elif kind == 'live_now_restarts': c.update({'tester': 0, 'calMode': 1, 'restartEvery': 1500, 'draw': 1, 'table': 1})
    a, info = ea_rows(tag + '_' + kind, c)
    b = harness_rows('ea_' + tag + '_' + kind, c, 60)
    if a is None or b is None: return tag + ' FAILED', False
    ka = [(x[1], x[2], x[4], x[5]) for x in a]; kb = [(x[1], x[2], x[4], x[5]) for x in b]
    md = max([max(abs(x[3] - y[3]), abs(x[6] - y[6])) for x, y in zip(a, b)] + [0])
    same = ka == kb and md <= 0.0101
    return '%-24s %-18s EA %5d trades %11.2f | core %5d trades %11.2f | %s | %s' % (tag, kind, len(a), sum(x[7] for x in a), len(b), sum(x[8] for x in b),
           'SAME' if same else 'DIFFER', info), same
if __name__ == '__main__':
    hi, hol = calflags.load(SIMCAL, 'USD', 3)
    hm, _ = calflags.load(SIMCAL, 'USD', 2)
    au = calflags.all_au()
    print('calendar: %d high USD news, %d high+medium, %d USD holidays; group 29 releases %d; high list == group 29 list: %s' % (len(hi), len(hm), len(hol), len(au), hi == au))
    CAL = {'simCal': SIMCAL, 'auOn': 0}
    PY = [
        ('cal_high', U, dict(CAL, calOn=1, calImp=0), dict(cal=hi), 60),
        ('cal_himed_pre1_hol', U, dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=1.0), dict(cal=hm, hol=hol, ruleHol=True, preList=hm, preH=1.0), 60),
        ('au_pre2', U, {'auOn': 1, 'preOn': 1, 'preHrs': 2.0}, dict(au=au, preList=au, preH=2.0), 60),
        ('cal_au_pre05', U, dict(CAL, auOn=1, calOn=1, calImp=0, calPre=30, calPost=5, preOn=1, preHrs=0.5), dict(cal=hi, calPre=30, calPost=5, au=au, preList=sorted(set(hi + au)), preH=0.5), 60),
        ('rule_hol_only', U, dict(CAL, calOn=1, calImp=0, holTrade=0, calHol=0), dict(cal=hi, ruleHol=True), 60),
        ('m15_cal_pre2_hol', dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', wkHr=23, lev=100.0, eq0=10000.0, htfTf=14400, barSec=900),
         dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=2.0), dict(cal=hm, hol=hol, ruleHol=True, preList=hm, preH=2.0), 900),
    ]
    EA = []
    for k in ('tester', 'live_rule', 'live_now'):
        EA.append(('cal_high', U, dict(CAL, calOn=1, calImp=0), k))
        EA.append(('cal_himed_pre1_hol', U, dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=1.0), k))
    EA.append(('au_pre2', U, {'auOn': 1, 'preOn': 1, 'preHrs': 2.0, 'simCal': SIMCAL}, 'tester'))
    EA.append(('cal_au_pre05_pend', U, dict(CAL, auOn=1, calOn=1, calPre=30, calPost=5, preOn=1, preHrs=0.5, exec=1), 'tester'))
    EA.append(('hedge_cal_pre1_hol', dict(U, seqMode='C', split=3.0, seqMax=300.0, capAct='Clamp'), dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=1.0, dirMode=3, hedgeMoney=1), 'live_now'))
    EA.append(('cal_himed_pre1_hol', U, dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=1.0, exec=1, to=390000), 'live_now_restarts'))
    EA.append(('calEUR_hol', U, dict(CAL, calOn=1, calImp=0, calCur='EUR', holTrade=0, calHol=1, preOn=1, preHrs=1.0), 'live_now'))
    EA.append(('cal_retry', U, dict(CAL, calOn=1, calImp=1, holTrade=0, calHol=1, preOn=1, preHrs=1.0, calFailN=5, to=390000), 'live_now'))
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if len(sys.argv) > 2: EA = [e for e in EA if e[0] + '_' + e[3] in sys.argv[2].split(',')]
    if len(sys.argv) > 2 and which == 'py': PY = [e for e in PY if e[0] in sys.argv[2].split(',')]
    res = []
    with Pool(4) as pool:
        if which in ('all', 'py'):
            for line, ok in pool.imap(py_case, PY, chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d' % (sum(res), len(res)))
