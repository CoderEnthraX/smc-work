# v15.0 checks of the EA (SMC_Structure_EA_v15.0.mq5 = v14.0 + 1-minute-only section 4 rules, no loss mark, the HTF order block
# zone modes, news on the 1-minute chart only, 6 signal choices):
#  OFF   - python3 v13tests.py same <folder with the v14.0 harness + simmain>: every saved settings file byte-identical, except the
#          ones that use what v15.0 removed (the loss mark; favourable / against / auto modes)
#  equiv - the 1-minute-only switch and the news switch = the same settings turned off by hand (byte-identical), and no change
#          at all on the 1-minute chart
#  sep   - the zone modes worked out AGAIN in Python (v15sep.py) from the bars + the higher timeframe values the core read; every
#          zone decision compared
#  ea    - the whole EA in the fake MT5 == the core, zone modes ON (touch, pending, hedge, 15m)
#  rs    - restarts (live mode, 20,000-bar warm-up): every trade == no restarts
#  box   - the zone boxes the whole EA draws (the last 50) == the core's zone box records, place / prices / colour / text
# Settings files of these checks start with x150_.
import sys, os, csv, subprocess, time
import numpy as np
from multiprocessing import Pool
from cmp import cfg_of
import v131tests, v15sep
HERE = os.path.dirname(os.path.abspath(__file__))
U = v131tests.U
Y = v131tests.Y
FULL = {'grid': 1, 'fixTies': 1}
HBIN = os.environ.get('H150') or HERE + '/harness'
BIN = v131tests.BIN


def write(tag, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    fn = os.path.join(HERE, 'x150_%s.txt' % tag)
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    return fn


def harness(fn, cs=60, exe=None):
    r = subprocess.run([HERE + '/' + exe if exe else HBIN, fn, HERE + '/' + BIN[cs], fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: raise SystemExit('harness failed %s %s' % (fn, r.stderr[-300:]))
    return r


# ---------------- equiv: the switches = the same settings turned off by hand
NW = dict(auOn=1, holTrade=0, preOn=1, preHrs=2.0)
EQ = [  # (name, settings, chart, with the switch, the same by hand)
    ('m1_15m', dict(U, risk=1000.0), 900, dict(m1On=1, minStop=6, maxStop=80, mnPct=0.2, lzMin=3, lzMax=60, r3On=1, r3BrkOn=1, r3Brk=2, r3Fb=1, htfSec=14400, htfSrv=1),
     dict(m1On=0, r3On=1, r3Fb=1, htfSec=14400, htfSrv=1)),
    ('m1_1m_same', U, 60, dict(m1On=1, minStop=6, maxStop=80, mnPct=0.2, lzMin=3, lzMax=60), dict(m1On=0, minStop=6, maxStop=80, mnPct=0.2, lzMin=3, lzMax=60)),
    ('bc2_15m', dict(U, risk=1000.0), 900, dict(bcMax=1.0, bcMax2=12.0, htfSec=14400, htfSrv=1), dict(bcMax=12.0, htfSec=14400, htfSrv=1, exe='old140/harness')),
    ('bc2_1m', U, 60, dict(bcMax=10.0, bcMax2=1.0), dict(bcMax=10.0)),
    ('nw_15m', dict(U, risk=1000.0), 900, dict(NW, nw1m=1, htfSec=14400, htfSrv=1), dict(holTrade=0, htfSec=14400, htfSrv=1)),
    ('nw_1m_same', U, 60, dict(NW, nw1m=1), dict(NW, nw1m=0)),
]


def eq_case(t):
    name, P, cs, a, b = t
    out = []
    for tag, e in (('switch', a), ('hand', b)):
        e = dict(e); exe = e.pop('exe', None)   # bc2_15m: the hand run = v14.0 with its one box (v15.0 uses its box above 1 minute)
        fn = write('eq_%s_%s' % (name, tag), P, dict(FULL, **e), cs)
        r = harness(fn, cs, exe)
        out.append((open(fn[:-4] + '.csv', 'rb').read(), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0]
    return '%-11s switch: %-32s | by hand: %-32s | %s' % (name, out[0][1], out[1][1], 'BYTE-IDENTICAL' if same else 'DIFFER'), same


# ---------------- sep
SEP = [  # (name, settings, extra, chart seconds, higher timeframe seconds)
    ('choch_1m', U, dict(sig=12), 60, 900),
    ('both_1m', U, dict(sig=14), 60, 900),
    ('nobig_1m', U, dict(sig=12, znBig=0), 60, 900),
    ('ob_only_1m', U, dict(sig=12, znFvg=0, znLine=0), 60, 900),
    ('fvg_only_whole_1m', U, dict(sig=12, znOb=0, znHalf=0), 60, 900),
    ('no2nd_pct40_1m', U, dict(sig=12, znTwo=0, znPct=40), 60, 900),
    ('line_only_1m', U, dict(sig=12, znOb=0, znFvg=1, znLine=1, znPct=99), 60, 900),
    ('hedge_1m', U, dict(sig=12, dirMode=3), 60, 900),
    ('bos_15m', dict(U, risk=1000.0), dict(sig=13, htfSec=14400, htfSrv=1), 900, 14400),
    ('choch_15m_nobig', dict(U, risk=1000.0), dict(sig=12, znBig=0, htfSec=14400, htfSrv=1), 900, 14400),
]


def sep_case(t):
    name, P, extra, cs, htf = t
    t0 = time.time()
    e = dict(FULL, **extra)
    log = os.path.join(HERE, 'x150_sep_%s.zn' % name)
    e['znLog'] = log; e['htfSrv'] = 1
    fn = write('sep_' + name, P, e, cs)
    r = harness(fn, cs)
    a = np.fromfile(os.path.join(HERE, BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    sig = int(e['sig'])
    Pz = dict(pct=float(e.get('znPct', 50)), big=bool(int(e.get('znBig', 1))), ob=bool(int(e.get('znOb', 1))), fvg=bool(int(e.get('znFvg', 1))),
              half=bool(int(e.get('znHalf', 1))), two=bool(int(e.get('znTwo', 1))), line=bool(int(e.get('znLine', 1))),
              cho=(sig % 3) != 1, bos=(sig % 3) != 0)
    calls, bad, cnt = v15sep.run(a['t'], a['p'][:, 0], a['p'][:, 1], a['p'][:, 2], a['p'][:, 3], log, Pz, htf)
    trades = r.stderr.strip().split('\n')[-1]
    return '%-20s %6d zone questions (%s) | %s | %s | %.0fs' % (name, calls, ', '.join('%s %d' % kv for kv in sorted(cnt.items())), trades,
                                                              'ALL AGREE' if bad == 0 and calls > 0 else '%d DIFFER' % bad, time.time() - t0), bad == 0 and calls > 0


# ---------------- ea / rs
def ea_case(t):
    name, P, extra, cs = t
    return v131tests.ea_case(('150_' + name, P, extra, cs))


EA = [('zone_touch', U, dict(sig=12, exec=0), 60),
      ('zone_both_pend', U, dict(sig=14, exec=1, znTwo=0), 60),
      ('zone_hedge_touch', U, dict(sig=12, dirMode=3, exec=0, znBig=0), 60),
      ('zone_m1_news_touch', U, dict(sig=12, exec=0, m1On=1, nw1m=1, auOn=1, minStop=4), 60),
      ('zone_15m_touch', dict(U, risk=1000.0), dict(sig=12, exec=0, htfSec=14400, htfSrv=1, m1On=1, nw1m=1, auOn=1, minStop=6, bcMax2=30), 900)]
RS = [('zone_touch', U, dict(sig=12, exec=0)),
      ('zone_both_pend_hedge', U, dict(sig=14, exec=1, dirMode=3, znTwo=0))]


def rs_case(t):
    name, P, extra = t
    return v131tests.rs_case(('150_' + name, P, extra))


# ---------------- box: the zone boxes the whole EA draws (live mode, 20,000-bar warm-up, the last 50 kept) = the core's (Z lines)
BOX = [('zone_touch', U, dict(sig=12, exec=0)),
       ('zone_both_hedge_pend', U, dict(sig=14, exec=1, dirMode=3, znBig=0)),
       ('zone_fvg_whole_line', U, dict(sig=12, exec=0, znOb=0, znHalf=0, znPct=30))]


def box_case(t):
    import re
    name, P, extra = t
    log = os.path.join(HERE, 'x150_box_%s.zn' % name)
    fh = write('box_co_' + name, P, dict(Y, znLog=log, htfSrv=1, **extra))
    harness(fh)
    Zs = []
    for ln in open(log):
        if ln.startswith('Z,'):
            f = ln.strip().split(',')
            Zs.append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6]), int(f[7]), int(f[8])))
    od = os.path.join(HERE, 'x150_box_%s.obj' % name)
    fe = write('box_ea_' + name, P, dict(Y, tester=0, warm=20000, objDump=od, objPrefix='SMC', **extra))
    r = subprocess.run([HERE + '/simmain', fe, HERE + '/m1.bin', fe[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: return '%s FAILED %s' % (name, r.stderr[-300:]), False
    rect = {}; txt = {}
    for ln in open(od):
        f = ln.rstrip('\n').split('\t')
        m = re.search(r'_Z(\d+)(t?)$', f[0])
        if not m: continue
        if m.group(2): txt[int(m.group(1))] = (int(f[1]), float(f[2]), int(f[3]), f[6])
        else: rect[int(m.group(1))] = (int(f[1]), float(f[2]), int(f[8]), float(f[9]), int(f[3]))
    srv = lambda u: u + (10800 if v15sep.eu_summer(u) else 7200)
    tfs = [900, 3600, 14400]
    want = []
    for d, tf, k, top, bot, t0, t1 in Zs[-50:]:
        left = srv(t0) if tf == 9 else srv(t0) - srv(t0) % tfs[tf]
        name_ = 'HTF CHOCH* line' if tf == 9 else {0: 'M15', 1: 'H1', 2: 'H4'}[tf] + (' order block' if k == 0 else ' FVG')
        want.append(((left, top, srv(t1), bot, 19 if d == 1 else 20), (left, top if d == 1 else bot, 19 if d == 1 else 20, name_)))
    keys = sorted(rect)
    got = [(rect[i], txt.get(i)) for i in keys]
    same = got == want and len(keys) == len(set(keys)) and len(got) > 0
    if not same:
        for a, b in zip(got, want):
            if a != b: print('   %s EA %s | core %s' % (name, a, b)); break
    return '%-24s core %4d boxes in the year, EA keeps %2d: %s | %s' % (name, len(Zs), len(got), 'ALL 50 SAME (place, prices, colour, text)' if same else 'DIFFER', r.stderr.strip().split('\n')[-1]), same


if __name__ == '__main__':
    which = sys.argv[1]
    res = []
    with Pool(4) as pool:
        for fn, L in (('equiv', (eq_case, EQ)), ('sep', (sep_case, SEP)), ('ea', (ea_case, EA)), ('rs', (rs_case, RS)), ('box', (box_case, BOX))):
            if which == fn:
                for line, ok in pool.imap(L[0], L[1], chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
