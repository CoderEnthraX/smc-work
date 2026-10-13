# v13.0 checks of the EA (SMC_Structure_EA_v13.0.mq5 = v12.3 + settings in 13 sections + one stop buffer box read in the
# section 1 unit + the hedge 'base' option + faster drawing):
#  same <folder with the v12.3 harness + simmain>   - EVERY saved settings file of tools/ea (cfg_, rcfg_, fcfg_, ccfg_, lcfg_,
#        ocfg_, xcfg_, pe_) run by v12.3 and by v13.0: every output file must be byte-identical (old keys buPips / buPct
#        give the one box its value in pips / % mode)
#  hgb  - the hedge + shared money option 'a trade opened while the other side chases the loss risks only the base',
#        checked by a SEPARATE replay of the order log (Rule C / C split / C+ memory, which side chases, the size each
#        order should have) + the whole EA in the fake MT5 = the core with the option ON
#  speed <folder with the v12.3 simmain>  - the whole EA with the table and the drawings ON, v12.3 vs v13.0 (time)
import sys, os, re, subprocess, shutil, glob, time, csv, math
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'v13_out')
PATHKEYS = ('printLog', 'objDump', 'dealsOut', 'wakeLog', 'dropLog', 'ordLog', 'calOut')


def kind(fn):
    b = os.path.basename(fn)
    if b.startswith('cfg_') or b.startswith('pe_') or '_h_' in b or b.startswith('ccfg_h_'): return 'harness'
    return 'simmain'


def cfgd(fn):
    d = {}
    for ln in open(fn):
        p = ln.split(None, 1)
        if len(p) == 2: d[p[0]] = p[1].strip()
    return d


def run_one(job):
    fn, folder, tag = job
    d = cfgd(fn)
    base = os.path.basename(fn)[:-4]
    wd = os.path.join(OUT, tag)
    os.makedirs(wd, exist_ok=True)
    side = []
    for k in PATHKEYS:
        if k in d:
            d[k] = os.path.join(wd, base + '.' + k)
            side.append(d[k])
    cf = os.path.join(wd, base + '.cfg')
    with open(cf, 'w') as o:
        for k, v in d.items(): o.write('%s %s\n' % (k, v))
    bars = os.path.join(HERE, 'm15.bin' if d.get('cs') == '900' else 'm1.bin')
    out = os.path.join(wd, base + '.csv')
    exe = os.path.join(folder, kind(fn))
    t0 = time.time()
    r = subprocess.run([exe, cf, bars, out], capture_output=True, text=True, cwd=HERE)
    return base, tag, r.returncode, (r.stderr.strip().split('\n') or [''])[-1], [out] + side, time.time() - t0


def same(old):
    files = sorted(sum([glob.glob(os.path.join(HERE, p + '*.txt')) for p in ('cfg_', 'rcfg_', 'fcfg_', 'ccfg_', 'lcfg_', 'ocfg_', 'xcfg_', 'pe_')], []))
    jobs = [(f, old, 'old') for f in files] + [(f, HERE, 'new') for f in files]
    res = {}
    with Pool(4) as pool:
        for base, tag, rc, err, outs, dt in pool.imap_unordered(run_one, jobs):
            res[(base, tag)] = (rc, err, outs)
    bad = 0; n = 0
    for f in files:
        base = os.path.basename(f)[:-4]
        o, nw = res[(base, 'old')], res[(base, 'new')]
        n += 1
        ok = o[0] == nw[0] and o[1] == nw[1]
        for a, b in zip(o[2], nw[2]):
            ea, eb = os.path.exists(a), os.path.exists(b)
            if ea != eb or (ea and open(a, 'rb').read() != open(b, 'rb').read()): ok = False
        if not ok:
            bad += 1
            print('   DIFFERENT %-50s %s | %s' % (base, o[1], nw[1]))
    print('%d settings files: %d byte-identical, %d different' % (n, n - bad, bad))
    return bad


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == 'same': sys.exit(1 if same(os.path.abspath(sys.argv[2])) else 0)


# ---------------------------------------------------------------- hgb: the hedge + shared 'base' option
def step_base(pf, P):
    a, n = 0.0, 1.0
    if P['sp1'] > 0 and pf >= P['sp1'] - 0.005 and P['sp1'] > a: a, n = P['sp1'], P['spN1']
    if P['sp2'] > 0 and pf >= P['sp2'] - 0.005 and P['sp2'] > a: a, n = P['sp2'], P['spN2']
    if P['sp3'] > 0 and pf >= P['sp3'] - 0.005 and P['sp3'] > a:
        a, n = P['sp3'], P['spN3']
        if P['spInc'] > 0:
            k = math.floor((pf - P['sp3'] + 0.005) / P['spInc'])
            a, n = P['sp3'] + k * P['spInc'], P['spN3'] + k * P['spAdd']
    return a / n if a > 0 else 0.0


def replay(olog, P):
    """the rule written out again from the order log: who chases the carried loss, the size each order should have"""
    ev = {}
    for ln in open(olog):
        f = ln.split()
        ev.setdefault(int(f[1]), []).append(f)
    mode, base, split, cmU = int(P['seqMode']), float(P['risk']), float(P['split']), 2 * float(P['cmLot']) / 100.0
    car = tot = flp = 0.0
    live = {0: None, 1: None}      # the live order of a side: its 'full' flag (sized to win back the loss)
    live_key = {0: None, 1: None}  # ... and which order it is (side, setup, piece)
    full_of = {}                   # (side, seq, piece) -> flag of its last placement
    nopen = {0: 0, 1: 0}
    chase_pos = {0: False, 1: False}
    checks = bad = based = ties = 0
    first_bad = None

    def risk_now():
        bas = max(base, min(step_base(flp, P), float(P['seqMax']))) if mode >= 7 else base
        c = max(0.0, -tot) if mode in (4, 5, 6) else car
        if c <= 0.005: r = bas
        elif mode in (1, 4, 7): r = max(bas, (c + float(P['seqAdd'])) / split)
        elif mode in (2, 5, 8): r = max(bas, 2.0 * c / split)
        else: r = max(bas, c / split)
        return min(r, float(P['seqMax'])), bas

    def qty(ent, sl, amt):
        per = abs(ent - sl) + cmU
        raw = amt / per if per > 0 else 0.0
        q = math.floor(raw + 0.5)
        if q * per > amt * 1.25: q = math.floor(raw)
        return float(q), abs(raw - math.floor(raw) - 0.5) < 1e-6   # (size, an exact half: C++ and Python may round it apart)

    def chasing(j):
        return (live[j] is not None and live[j]) or (chase_pos[j] and nopen[j] > 0)

    for b in sorted(ev):
        es = ev[b]
        # the price path of bar b: closes and fills (the core counts them at this bar's close)
        s = sum(float(f[6]) for f in es if f[0] == 'X')
        if any(f[0] == 'X' for f in es):
            d = car - s; car = 0.0 if d < 0.005 else d; tot += s; flp += s
        for f in es:
            if f[0] == 'F':
                k = int(f[2]); nopen[k] += 1
                if full_of.get((k, int(f[3]), int(f[4])), False): chase_pos[k] = True
                live[k] = None
            elif f[0] == 'X': nopen[int(f[2])] -= 1
        for k in (0, 1):
            if nopen[k] == 0: chase_pos[k] = False
        rn, bas = risk_now()
        for k in (0, 1):
            mine = [f for f in es if f[0] in 'CcP' and int(f[2]) == k]
            placed = False
            for f in mine:
                if f[0] == 'C': live[k] = None
                elif f[0] == 'P':
                    seq, piece, ent, sl, q, add = int(f[3]), int(f[4]), float(f[6]), float(f[7]), float(f[9]), float(f[11])
                    hb = bool(P['hgBase']) and mode != 0 and chasing(1 - k) and rn > bas + 0.005
                    want, tie = qty(ent, sl, (bas if hb else rn) * add)
                    checks += 1; based += hb
                    if abs(want - q) > 1e-6 and tie and abs(want - q) <= 1.0 + 1e-9: ties += 1
                    elif abs(want - q) > 1e-6:
                        bad += 1
                        if first_bad is None: first_bad = (b, k, seq, q, want, hb, rn, bas)
                    fl = (not hb) and rn > bas + 0.005
                    live[k] = fl; live_key[k] = (k, seq, piece); full_of[(k, seq, piece)] = fl; placed = True
            if not placed and live[k] is not None and nopen[k] == 0:
                # the core sizes a waiting order again at every close (no new order when the size is the same)
                hb = bool(P['hgBase']) and mode != 0 and chasing(1 - k) and rn > bas + 0.005
                live[k] = (not hb) and rn > bas + 0.005
                full_of[live_key[k]] = live[k]   # the order keeps its new flag when it fills later
    return checks, bad, based, first_bad, ties


HGB = dict(sig=0, r1=1, r2=1, pb=25.0, rr=1.0, slBuf=1.0, rev=0, once=0, hrOn=6, hrOff=23, hrFlat=2, wkFlat=1, wkDay=6, wkHr=23,
           risk=50.0, cmLot=3.5, comm=0.035, lotStep=0.01, rndMax=25.0, lev=500.0, cmTgt=1, eq0=1000000.0, cancelSig=1, expBars=0,
           minStop=0.0, maxStop=0.0, maxTrades=0, dayLoss=0.0, maxOpen=0, mvStep=0, mvBe=0, dirMode=3, hedgeMoney=1, bkOn=0, bkPct=100.0,
           hfOn=0, trOn=0, trMode=0, lqOn=0, lqMin=1.0, ppOn=0, ppPct=50.0, ppR=1.0, ppBe=1, pdOn=0, pdPct=50.0, lsOn=0, lsN=1, bosCnl=1,
           seqMode=3, seqAdd=50.0, split=1.0, flMode=0, flAmt=2000.0, flLock=50.0, flPct=2.5, ldOn=0, ldN=4, ldD=3, eqOn=0, eqPct=50.0,
           seqMax=1e9, capAct=0, seqFrom=0, seqFromT=0, htfSec=900, cs=60, auOn=0, sessMode=0, minLot=0.01, pbSwp2=1, r3On=0, r3BrkOn=0,
           r3Brk=3.0, r3Fb=0, lmOn=0, lmAmt=300.0, sp1=200.0, spN1=3.0, sp2=500.0, spN2=5.0, sp3=1000.0, spN3=8.0, spInc=500.0, spAdd=1.0,
           grid=1, fixTies=1, exec=1, hgBase=1, **{'from': 1500000, 'to': 1870000})
HGB_SETS = {
    'C1_1R':          {},
    'C3_3R_pause':    dict(split=3.0, rr=3.0, ldOn=1),
    'C1_1R_rule3':    dict(r3On=1),
    'Cplus2':         dict(seqMode=6, split=2.0),
    'Csplit_steps':   dict(seqMode=9, sp1=50.0, spN1=1.0, sp2=150.0, spN2=2.0, sp3=300.0, spN3=3.0, spInc=100.0),
    'A1':             dict(seqMode=1),
    'B2':             dict(seqMode=2, split=2.0),
    'C1_1R_6y':       {'from': 20000, 'to': 2037534, 'eq0': 1e9},   # a huge account: Rule C 1:1 reaches risks the leverage cap would cut
    'C1_1R_touch':    dict(exec=0),
}


def hgb_run(job):
    name, extra, exe_dir, tag = job
    P = dict(HGB); P.update(extra)
    wd = os.path.join(OUT, 'hgb'); os.makedirs(wd, exist_ok=True)
    cf = os.path.join(wd, '%s_%s.cfg' % (name, tag))
    if tag != 'ea': P['ordLog'] = os.path.join(wd, '%s_%s.olog' % (name, tag))
    with open(cf, 'w') as o:
        for k, v in P.items(): o.write('%s %s\n' % (k, v))
    out = os.path.join(wd, '%s_%s.csv' % (name, tag))
    exe = os.path.join(exe_dir, 'simmain' if tag == 'ea' else 'harness')
    r = subprocess.run([exe, cf, os.path.join(HERE, 'm1.bin'), out], capture_output=True, text=True, cwd=HERE)
    return name, tag, r.returncode, r.stderr.strip().split('\n')[-1], P


def trades(fn):
    return sorted([(int(d['side']), int(d['dir']), int(d['ebar']), float(d['ep']), round(float(d['q']), 4), int(d['xbar']), float(d['xp']), float(d['pnl']))
                   for d in csv.DictReader(open(fn))], key=lambda r: (r[2], r[1], r[5], r[4]))


def hgb(old):
    jobs = []
    for nm, ex in HGB_SETS.items():
        jobs += [(nm, ex, HERE, 'on'), (nm, dict(ex, hgBase=0), HERE, 'off'), (nm, dict(ex, hgBase=0), old, 'old')]
    for nm in ('C1_1R', 'C3_3R_pause', 'C1_1R_touch', 'C1_1R_rule3'):
        jobs.append((nm, HGB_SETS[nm], HERE, 'ea'))
    res = {}
    with Pool(4) as pool:
        for name, tag, rc, err, P in pool.imap_unordered(hgb_run, jobs):
            res[(name, tag)] = (rc, err, P)
            if rc: print('   FAILED', name, tag, err)
    probs = 0
    wd = os.path.join(OUT, 'hgb')
    print('option OFF = v12.3 (core, byte-identical trade lists):')
    for nm in HGB_SETS:
        same = open(os.path.join(wd, nm + '_off.csv'), 'rb').read() == open(os.path.join(wd, nm + '_old.csv'), 'rb').read()
        print('   %-14s %s' % (nm, 'SAME' if same else 'DIFFERENT')); probs += not same
    print('option ON - every order size worked out again from the order log (separate replay):')
    for nm in HGB_SETS:
        P = res[(nm, 'on')][2]
        c, bad, based, fb, ti = replay(os.path.join(wd, nm + '_on.olog'), P)
        c0, bad0, based0, fb0, ti0 = replay(os.path.join(wd, nm + '_off.olog'), res[(nm, 'off')][2])
        on, off = trades(os.path.join(wd, nm + '_on.csv')), trades(os.path.join(wd, nm + '_off.csv'))
        print('   %-14s ON: %6d orders checked, %4d at the base, %d wrong (+%d exact-half ties)%s | OFF: %6d checked, %d wrong (+%d ties) | trades %d / %d, net %+10.2f / %+10.2f' % (
            nm, c, based, bad, ti, '' if not fb else ' first ' + str(fb), c0, bad0, ti0, len(on), len(off), sum(r[7] for r in on), sum(r[7] for r in off)))
        probs += bad + bad0 + (based == 0)
    print('whole EA in the fake MT5 = the core, option ON:')
    for nm in ('C1_1R', 'C3_3R_pause', 'C1_1R_touch', 'C1_1R_rule3'):
        a, b = trades(os.path.join(wd, nm + '_ea.csv')), trades(os.path.join(wd, nm + '_on.csv'))
        same = [(x[1], x[2], x[4], x[5]) for x in a] == [(x[1], x[2], x[4], x[5]) for x in b]
        dp = max([max(abs(x[3] - y[3]), abs(x[6] - y[6])) for x, y in zip(a, b)] + [0])
        print('   %-14s EA %5d trades %+10.2f | core %5d trades %+10.2f | %s, max price diff %.4f' % (nm, len(a), sum(x[7] for x in a), len(b), sum(x[7] for x in b), 'SAME' if same else 'DIFFER', dp))
        probs += (not same) or dp > 0.0101
    print('ALL OK' if probs == 0 else 'PROBLEMS: %d' % probs)
    return probs


if __name__ == '__main__' and sys.argv[1] == 'hgb': sys.exit(1 if hgb(os.path.abspath(sys.argv[2])) else 0)


# ---------------------------------------------------------------- rs: restarts with the hedge 'base' option ON
def rs_run(job):
    name, extra = job
    d = cfgd(os.path.join(HERE, 'rcfg_touch_hedge_own_plain.txt'))
    d.update(dict(hedgeMoney=1, seqMode=3, split=1.0, rr=1.0, hgBase=1, eq0=1000000.0, lev=500.0, table=0, draw=0))
    d.update(extra)
    wd = os.path.join(OUT, 'rs'); os.makedirs(wd, exist_ok=True)
    cf = os.path.join(wd, name + '.cfg')
    with open(cf, 'w') as o:
        for k, v in d.items(): o.write('%s %s\n' % (k, v))
    out = os.path.join(wd, name + '.csv')
    r = subprocess.run([os.path.join(HERE, 'simmain'), cf, os.path.join(HERE, 'm1.bin'), out], capture_output=True, text=True, cwd=HERE)
    return name, r.returncode, r.stderr.strip().split('\n')[-1]


def rs():
    jobs = [('touch_none', {}), ('touch_rs', dict(restartEvery=1500)), ('pend_none', dict(exec=1)), ('pend_rs', dict(exec=1, restartEvery=1500))]
    with Pool(4) as pool:
        res = {n: (rc, e) for n, rc, e in pool.imap_unordered(rs_run, jobs)}
    probs = 0
    wd = os.path.join(OUT, 'rs')
    for a in ('touch', 'pend'):
        x = open(os.path.join(wd, a + '_none.csv'), 'rb').read(); y = open(os.path.join(wd, a + '_rs.csv'), 'rb').read()
        n = x.count(b'\n') - 1
        print('   %-6s hedge shared Rule C 1:1, base option ON: %d trades, restarts: %s | %s' % (a, n, res[a + '_rs'][1], 'SAME as no restarts' if x == y else 'DIFFERENT'))
        probs += x != y
    return probs


if __name__ == '__main__' and sys.argv[1] == 'rs': sys.exit(1 if rs() else 0)
