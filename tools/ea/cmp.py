# run the Python simulator and the C++ core harness with the same settings and compare every closed trade
import sys, pickle, subprocess, csv, math, importlib.util, os
import os
SP = os.path.dirname(os.path.abspath(__file__))
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
porth = load(SP + '/porthp.py', 'porthp')
_bars = {}
def bars(cs):
    if cs not in _bars: _bars[cs] = pickle.load(open(SP + ('/fx.pkl' if cs == 60 else '/fx15.pkl'), 'rb'))
    return _bars[cs]
SIG = {'CHOCH': 0, 'BOS': 1, 'Both': 2}
SEQ = {'Off': 0, 'A10': 1, 'B': 2, 'C': 3, 'A+': 4, 'B+': 5, 'C+': 6, 'As': 7, 'Bs': 8, 'Cs': 9}
def cfg_of(P, cs):
    p = dict(porth.DEF); p.update(P)
    sig = SIG[p['sig']] + (3 if p['fav'] else 0) + (6 if p['agn'] else 0) + (9 if p['auto'] else 0)
    c = dict(sig=sig, r1=p['r1'], r2=p['r2'], pb=p['pb'], rr=p['rr'], slBuf=p['slbuf'], rev=p['rev'], once=p['once'],
             hrOn=p['hrOn'], hrOff=p['hrOff'], hrFlat=p['hrFlat'], wkFlat=p['wkFlat'], wkDay=(p['wkDow'] + 1) % 7 + 1, wkHr=p['wkHr'],
             risk=p['risk'], cmLot=p['cmU'] * 100 / 2, comm=p['comm'], lotStep=p['unit'] / 100, rndMax=p['rndMax'], lev=p['lev'], cmTgt=p['cmTgt'], eq0=p['eq0'],
             cancelSig=p['cancelSig'], expBars=p['expBars'], minStop=p['minStop'], maxStop=p['maxStop'], maxTrades=p['maxTrades'], dayLoss=p['dayLoss'],
             maxOpen=p['maxOpen'], mvStep=p['mvStep'], mvBe=p['mvBe'], dirMode={'Both': 0, 'Longs': 1, 'Shorts': 2}[p['direction']],
             bkOn=p['bosRiskPct'] != 100.0, bkPct=p['bosRiskPct'], hfOn=p['htfFilt'], trOn=p['trail'] != 'Off', trMode=1 if p['trail'] == 'Swing' else 0,
             lqOn=p['liqTgt'], lqMin=p['liqMinR'], ppOn=p['partOn'], ppPct=p['partPct'], ppR=p['partR'], ppBe=p['partBe'], pdOn=p['pdOn'], pdPct=p['pdPct'],
             lsOn=p['lossN'] > 0, lsN=max(1, p['lossN']), bosCnl=p['bosMode'] == 'Cancel', seqMode=SEQ[p['seqMode']], seqAdd=p['seqAdd'], split=p['split'],
             flMode={'Off': 0, 'Size': 1, 'Cap': 2}[p['flMode']], flAmt=p['flAmt'], flLock=p['flLock'], flPct=p['flPct'], ldOn=p['ldOn'], ldN=p['ldN'], ldD=p['ldD'],
             eqOn=p['eqOn'], eqPct=p['eqPct'], seqMax=p['seqMax'], capAct={'Clamp': 0, 'Day': 1, 'Perm': 2, 'Base': 3}[p['capAct']],
             seqFrom=0 if p['liveT'] is None else 2, seqFromT=p['liveT'] or 0, htfSec=p['htfTf'], cs=cs,
             auOn=bool(p.get('news') is not None), sessMode=2 if p.get('sessOff') else 0, minLot=0.01,
             pbSwp2=p['pbSwp2'], r3On=p['r3On'], r3BrkOn=p['r3BrkOn'], r3Brk=p['r3Brk'], r3Fb=p['r3Fb'], lmOn=p['lmOn'], lmAmt=p['lmAmt'], sp1=p['sp1'], spN1=p['spN1'], sp2=p['sp2'], spN2=p['spN2'], sp3=p['sp3'], spN3=p['spN3'], spInc=p['spInc'], spAdd=p['spAdd'])
    assert p['trailBuf'] is None and p['liqMaxR'] == 0 and p['sess2'] is None and not p['ldAll'] and p['seqMode'] != 'A91' and p['bosMode'] != 'Freeze'
    return c
def run_py(P, cs):
    closed, opn, cnt = porth.run(bars(cs), P)
    return sorted([(0 if True else 0, tr.dir, tr.ebar, round(tr.ep, 5), round(tr.q, 4), tr.xbar, round(tr.xp, 5), tr.why, tr.pnl) for tr in closed], key=lambda r: (r[2], r[5], r[1], r[3], r[4], r[6]))
def run_cpp(P, cs, extra=None, tag='x'):
    c = cfg_of(P, cs)
    if extra: c.update(extra)
    fn = 'cfg_%s.txt' % tag
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    out = 'out_%s.csv' % tag
    r = subprocess.run(['./harness', fn, 'm1.bin' if cs == 60 else 'm15.bin', out], capture_output=True, text=True)
    if r.returncode: print(r.stderr); raise SystemExit
    rows = []
    for d in csv.DictReader(open(out)):
        rows.append((int(d['side']), int(d['dir']), int(d['ebar']), round(float(d['ep']), 5), round(float(d['q']), 4), int(d['xbar']), round(float(d['xp']), 5), d['why'], float(d['pnl'])))
    return sorted(rows, key=lambda r: (r[2], r[5], r[1], r[3], r[4], r[6]))
def compare(name, P, cs=60, extra=None):
    a = run_py(P, cs); b = run_cpp(P, cs, extra, tag=name)
    ka = [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in a]; kb = [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in b]
    na, nb = sum(r[8] for r in a), sum(r[8] for r in b)
    same = ka == kb
    first = None
    if not same:
        for i, (x, y) in enumerate(zip(ka, kb)):
            if x != y: first = (i, x, y); break
        if first is None: first = (min(len(ka), len(kb)), ka[len(kb):len(kb)+1], kb[len(ka):len(ka)+1])
    print('%-28s py %5d trades %12.2f | core %5d trades %12.2f | %s' % (name, len(a), na, len(b), nb, 'IDENTICAL' if same else 'DIFF first at %s' % (first,)))
    return same
