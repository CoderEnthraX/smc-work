# v15.1 checks of the EA (SMC_Structure_EA_v15.1.mq5 = v15.0 + one box per zone / every zone that counted / show all zones, the zones
# made before a new higher timeframe leg go, a setup goes only when ALL its zones are gone, last zone only, order block type 2 / to the
# swing, MSS + its confirmation, the every-other-day mode after a pause, the force close on 1m only, every price distance off):
#  OFF    - python3 v13tests.py same old150 (folder with the v15.0 harness + simmain): every saved settings file byte-identical
#  equiv  - the new switches = the same settings by hand (price distances off, force close 1m only on the 1m chart)
#  sep    - the zone modes, boxes, last zone, MSS, confirmation, zones-gone cancels worked out AGAIN in Python (v151sep.py) from the bars
#           + the higher timeframe values the core logged (test hooks, key znLog); every decision compared
#  pause  - the every-other-day mode worked out again from the core's closed trades; no setup armed on a day it blocks
#  fl1m   - the force close on the 1-minute chart only: 15m = no 'Time flat' exits, 1m = unchanged
#  ea     - the whole EA in the fake MT5 == the core (zone modes + v15.1 settings)
#  rs     - restarts (live mode, 20,000-bar warm-up): every trade == no restarts
#  box    - the zone boxes the whole EA draws (one per zone, the newest 440) == the core's box records
# Settings files of these checks start with x151_.
import sys, os, csv, subprocess, time
import numpy as np
from multiprocessing import Pool
from cmp import cfg_of
import v131tests, v151sep, v15sep
HERE = os.path.dirname(os.path.abspath(__file__))
U = v131tests.U
Y = v131tests.Y
FULL = {'grid': 1, 'fixTies': 1}
HBIN = os.environ.get('H151') or HERE + '/harness'
BIN = v131tests.BIN


def write(tag, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    fn = os.path.join(HERE, 'x151_%s.txt' % tag)
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    return fn


def harness(fn, cs=60, exe=None):
    r = subprocess.run([exe or HBIN, fn, HERE + '/' + BIN[cs], fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: raise SystemExit('harness failed %s %s' % (fn, r.stderr[-300:]))
    return r


# ---------------- sep
M15 = dict(htfSec=14400, htfSrv=1)
SEP = [  # (name, settings, extra, chart seconds, higher timeframe seconds)
    ('choch_1m', U, dict(sig=12), 60, 900),
    ('nobig_1m', U, dict(sig=12, znBig=0), 60, 900),
    ('last_1m', U, dict(sig=12, znLast=1), 60, 900),
    ('ob2_sw_nobig_1m', U, dict(sig=12, znOb2=1, znSw=1, znBig=0), 60, 900),
    ('mss_1m', U, dict(sig=12, mssOn=1), 60, 900),
    ('mss_cf_first_1m', U, dict(sig=12, mssOn=1, mssCf=1, mssSt=0), 60, 900),
    ('mss_cf_new_ob2_last_both', U, dict(sig=14, mssOn=1, mssCf=1, mssSt=1, znOb2=1, znLast=1, mssN=3), 60, 900),
    ('mss_hedge_nobig_sw', U, dict(sig=12, dirMode=3, mssOn=1, znBig=0, znSw=1), 60, 900),
    ('mss_r3_fvg_whole', U, dict(sig=12, mssOn=1, r3On=1, znOb=0, znHalf=0, mssN=1), 60, 900),
    ('mss_bos_no2nd_pct40', U, dict(sig=13, mssOn=1, znTwo=0, znPct=40, mssCf=1), 60, 900),
    ('mss_cf_15m', dict(U, risk=1000.0), dict(sig=12, mssOn=1, mssCf=1, **M15), 900, 14400),
    ('last_ob2_15m', dict(U, risk=1000.0), dict(sig=14, znLast=1, znOb2=1, znSw=1, mssOn=1, **M15), 900, 14400),
]


def sep_case(t):
    name, P, extra, cs, htf = t
    t0 = time.time()
    e = dict(FULL, **extra)
    log = os.path.join(HERE, 'x151_sep_%s.zn' % name)
    e['znLog'] = log; e['htfSrv'] = 1
    fn = write('sep_' + name, P, e, cs)
    r = harness(fn, cs)
    a = np.fromfile(os.path.join(HERE, BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    sig = int(e['sig'])
    Pz = dict(pct=float(e.get('znPct', 50)), big=bool(int(e.get('znBig', 1))), ob=bool(int(e.get('znOb', 1))), fvg=bool(int(e.get('znFvg', 1))),
              half=bool(int(e.get('znHalf', 1))), two=bool(int(e.get('znTwo', 1))), line=bool(int(e.get('znLine', 1))),
              last=bool(int(e.get('znLast', 0))), sw=bool(int(e.get('znSw', 0))), ob2=bool(int(e.get('znOb2', 0))),
              mss=bool(int(e.get('mssOn', 0))), mssN=int(e.get('mssN', 2)), mssCf=bool(int(e.get('mssCf', 0))), mssSt=int(e.get('mssSt', 0)),
              slBuf=float(P.get('slbuf', 0)), cho=(sig % 3) != 1, bos=(sig % 3) != 0)
    st, bad = v151sep.run(a['t'], a['p'][:, 0], a['p'][:, 1], a['p'][:, 2], a['p'][:, 3], log, Pz, htf)
    trades = r.stderr.strip().split('\n')[-1]
    txt = 'counts %d, boxes %d, last-zone changes %d, MSS %d, setups %d (confirmed %d, failed %d, zones gone %d)' % (
        st['calls'], st['boxes'], st['last'], st['mss'], st['armed'], st['conf'], st['fail'], st['gone'])
    return '%-26s %s | %s | %s | %.0fs' % (name, txt, trades, 'ALL AGREE' if bad == 0 and st['calls'] > 0 else '%d DIFFER' % bad, time.time() - t0), bad == 0 and st['calls'] > 0


# ---------------- equiv: the new switches = the same settings turned off by hand (byte-identical)
PXB = dict(slBuf=1.0, minStop=6, maxStop=80, mnPct=0.2, lzMin=3, lzMax=60, r3On=1, r3BrkOn=1, r3Brk=2, bcMax=10, bcMax2=3, sprd=0.3, cmTgt=1, m1On=0)
PXS = dict(buMode=3, bfU=2, bfV=0.05, skU=1, skMin=20, skMax=300, r3U=2, r3V=0.5, spdU=1, spdV=3, lzU=0, lzMin=2, lzMax=80, bcU=0, bcMax=12, bcMax2=40,
           r3On=1, r3BrkOn=1, r3Fb=1, cmTgt=1, m1On=0)
EQ = [  # (name, settings, chart, with the switch, the same by hand)
    ('px_1m', U, 60, dict(PXB, pxOff=1), dict(slBuf=0.0, r3On=1, cmTgt=0, m1On=0)),
    ('px_zone_mss_1m', U, 60, dict(PXB, pxOff=1, sig=12, mssOn=1), dict(slBuf=0.0, r3On=1, cmTgt=0, m1On=0, sig=12, mssOn=1)),
    ('px_sep_15m', dict(U, risk=1000.0), 900, dict(PXS, pxOff=1, htfSec=14400, htfSrv=1),
     dict(buMode=3, bfU=2, bfV=0.0, skU=1, r3U=2, spdU=1, lzU=0, bcU=0, r3On=1, r3Fb=1, cmTgt=0, m1On=0, htfSec=14400, htfSrv=1)),
    ('fl1m_1m_same', U, 60, dict(fl1m=1), dict(fl1m=0)),
    ('fl1m_zone_1m_same', U, 60, dict(fl1m=1, sig=14, mssOn=1), dict(fl1m=0, sig=14, mssOn=1)),
]


def eq_case(t):
    name, P, cs, a, b = t
    out = []
    for tag, e in (('switch', a), ('hand', b)):
        fn = write('eq_%s_%s' % (name, tag), P, dict(FULL, **e), cs)
        r = harness(fn, cs)
        out.append((open(fn[:-4] + '.csv', 'rb').read(), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0] and out[0][0].count(b'\n') > 1
    return '%-18s switch: %-34s | by hand: %-34s | %s' % (name, out[0][1], out[1][1], 'BYTE-IDENTICAL' if same else 'DIFFER'), same


# ---------------- fl1m: the 02:00 force close only on the 1-minute chart (15m: no 'Time flat' exit with the switch ON, some with it OFF;
# the weekend close still works)
FL = [('fl1m_15m', dict(U, risk=1000.0), dict(htfSec=14400, htfSrv=1), 900),
      ('fl1m_15m_zone_mss', dict(U, risk=1000.0), dict(sig=14, mssOn=1, htfSec=14400, htfSrv=1), 900)]


def fl_case(t):
    name, P, extra, cs = t
    cnt = {}
    for tag, v in (('on', 1), ('off', 0)):
        fn = write('fl_%s_%s' % (name, tag), P, dict(FULL, fl1m=v, **extra), cs)
        harness(fn, cs)
        why = [d['why'] for d in csv.DictReader(open(fn[:-4] + '.csv'))]
        cnt[tag] = (len(why), why.count('Time flat'), why.count('Weekend flat'))
    ok = cnt['on'][1] == 0 and cnt['off'][1] > 0 and cnt['on'][2] > 0
    return '%-20s switch ON: %d trades, %d Time flat, %d Weekend flat | OFF: %d trades, %d Time flat, %d Weekend flat | %s' % (
        name, *cnt['on'], *cnt['off'], 'OK' if ok else 'WRONG'), ok


# ---------------- pause: the every-other-day mode worked out again from the core's closed trades; every signal note of the core
# (verbose) says 'loss pause (every other day)' exactly on the candles Python blocks, and 'loss pause (days)' exactly in the pauses
PA = [('n3_d1_n2_s1', U, dict(ldOn=1, ldN=3, ldD=1, ldN2=2, ldSkip=1)),
      ('n4_d2_n1_s2', U, dict(ldOn=1, ldN=4, ldD=2, ldN2=1, ldSkip=2)),
      ('n3_d1_n3_s1_247', U, dict(ldOn=1, ldN=3, ldD=1, ldN2=3, ldSkip=1, wk247=1)),
      ('zone_mss_n2_d1_n2_s3', U, dict(sig=14, mssOn=1, ldOn=1, ldN=2, ldD=1, ldN2=2, ldSkip=3))]


def pa_case(t):
    import re
    name, P, extra = t
    fn = write('pa_' + name, P, dict(FULL, verbose=1, **extra))
    r = harness(fn)
    T = v131tests.times(60)
    tz = 19800
    day = lambda u: (u + tz) // 86400
    dow = lambda dn: (dn + 4) % 7 + 1          # 1 = Sunday .. 7 = Saturday (days since 1970 -> MT5 day of week + 1)
    N, D, N2, SK, all7 = extra['ldN'], extra['ldD'], extra['ldN2'], extra['ldSkip'], bool(extra.get('wk247', 0))
    def until(gx):
        dn0 = day(gx); n = k = 0
        while n < D and k < 500:
            k += 1
            w = dow(dn0 + k)
            if all7 or (w != 7 and w != 1): n += 1
        return (dn0 + k + 1) * 86400 - tz
    def alt_halt(t, altD):
        dn = day(t)
        if dn <= altD: return True
        w = dow(dn)
        if not all7 and (w == 7 or w == 1): return True
        m = 0
        for d in range(altD + 1, dn + 1):
            if all7 or dow(d) not in (1, 7): m += 1
        return m % (SK + 1) != 0
    tr = sorted(((int(d['xbar']), int(d['side']), int(d['ebar']), float(d['pnl'])) for d in csv.DictReader(open(fn[:-4] + '.csv')) if d['why'] != 'open'))
    notes = []
    for ln in r.stdout.split('\n'):
        m = re.match(r'^NOTE bar (\d+) side (\d+): (\w+ (?:up|dn)): (.*)$', ln)
        if m: notes.append((int(m.group(1)), m.group(4)))
    st = dict(run=0, until=None, aft=False, alt=False, run2=0, altD=None, pauses=0, alts=0)
    ti = 0
    bad = 0; seen = dict(alt=0, pause=0, armed=0)
    for b, txt in notes:
        while ti < len(tr) and tr[ti][0] <= b:
            xb, _, _, gp = tr[ti]; ti += 1
            gx = int(T[xb])
            if st['until'] is not None and gx < st['until']: continue
            if st['alt']:
                if gp > 0: st.update(alt=False, aft=False, run=0)
            elif st['aft']:
                st['run2'] = st['run2'] + 1 if gp < 0 else (0 if gp > 0 else st['run2'])
                if gp > 0: st.update(aft=False, run2=0, run=0)
                elif st['run2'] >= N2: st.update(alt=True, altD=day(gx), run2=0); st['alts'] += 1
            else:
                st['run'] = st['run'] + 1 if gp < 0 else (0 if gp > 0 else st['run'])
                if st['run'] >= N: st.update(until=until(gx), run=0, aft=N2 > 0, run2=0); st['pauses'] += 1
        t = int(T[b])
        p_ld = st['until'] is not None and t < st['until']
        p_alt = st['alt'] and alt_halt(t, st['altD'])
        c_ld = txt == 'SKIP - loss pause (days)'
        c_alt = txt == 'SKIP - loss pause (every other day)'
        if c_ld or c_alt or 'ARMED' in txt or 'WAITING' in txt:
            want_ld, want_alt = p_ld, (not p_ld) and p_alt
            got_ld, got_alt = c_ld, c_alt
            if (want_ld, want_alt) != (got_ld, got_alt):
                bad += 1
                if bad <= 5: print('   %s bar %d: python pause %s every-other-day %s | core note: %s' % (name, b, want_ld, want_alt, txt))
            seen['alt'] += got_alt; seen['pause'] += got_ld; seen['armed'] += 'ARMED' in txt or 'WAITING' in txt
    ok = bad == 0 and st['alts'] > 0 and seen['alt'] > 0
    return '%-22s %d closed trades, pauses %d, every-other-day starts %d | notes: armed %d, skipped by the pause %d, by every-other-day %d | %s' % (
        name, len(tr), st['pauses'], st['alts'], seen['armed'], seen['pause'], seen['alt'], 'ALL AGREE' if ok else '%d DIFFER' % bad), ok


# ---------------- ea / rs: the whole EA in the fake MT5 == the core; restarts == no restarts
def ea_case(t):
    name, P, extra, cs = t
    return v131tests.ea_case(('151_' + name, P, extra, cs))


EA = [('mss_touch', U, dict(sig=12, mssOn=1, exec=0, znAll=1), 60),
      ('mss_cf_new_ob2_pend', U, dict(sig=14, mssOn=1, mssCf=1, mssSt=1, znOb2=1, exec=1), 60),
      ('last_sw_mss_hedge_touch', U, dict(sig=12, znLast=1, znSw=1, mssOn=1, dirMode=3, exec=0), 60),
      ('pause_px_touch', U, dict(ldOn=1, ldN=3, ldD=1, ldN2=2, ldSkip=1, pxOff=1, minStop=6, exec=0), 60),
      ('mss_cf_15m_touch', dict(U, risk=1000.0), dict(sig=12, mssOn=1, mssCf=1, fl1m=1, htfSec=14400, htfSrv=1, exec=0), 900),
      # stacked trades of one side closed in the same second + the loss pause (the close-order fix)
      ('pause_last_hedge_pend', U, dict(sig=14, dirMode=3, mssOn=1, znLast=1, ldOn=1, ldN=3, ldD=1, ldN2=2, ldSkip=1, exec=1), 60)]
RS = [('mss_cf_touch', U, dict(sig=12, mssOn=1, mssCf=1, exec=0, znAll=1)),
      ('pause_last_hedge_pend', U, dict(sig=14, dirMode=3, mssOn=1, znLast=1, ldOn=1, ldN=3, ldD=1, ldN2=2, ldSkip=1, exec=1))]


def rs_case(t):
    name, P, extra = t
    return v131tests.rs_case(('151_' + name, P, extra))


# ---------------- box: the zone boxes the whole EA draws (live mode, 20,000-bar warm-up) == the core's box records (Z lines):
# ONE box per zone (name = the zone), from its candle to its last signal, 'x N', green / red (darker when it was the last zone),
# an FVG with 'far half' drawn as its far half, the newest 440 kept
BOX = [('zone_touch', U, dict(sig=12, exec=0)),
       ('mss_last_ob2_sw_touch', U, dict(sig=14, mssOn=1, znLast=1, znOb2=1, znSw=1, exec=0, znAll=1)),
       ('fvg_whole_line_pend', U, dict(sig=12, exec=1, znOb=0, znHalf=0, znPct=30))]


def box_case(t):
    import re
    name, P, extra = t
    log = os.path.join(HERE, 'x151_box_%s.zn' % name)
    YB = dict(Y, **{'from': 1000000})       # about 3 years: more than 440 zones get a box, so the 'newest 440' limit works
    fh = write('box_co_' + name, P, dict(YB, znLog=log, htfSrv=1, **extra))
    harness(fh)
    half = bool(int(extra.get('znHalf', 1)))
    srv = lambda u: u + (10800 if v15sep.eu_summer(u) else 7200)
    tfs = [900, 3600, 14400]
    want = {}; order = []
    for ln in open(log):
        if not ln.startswith('Z,'): continue
        f = ln.strip().split(',')
        if int(f[1]) < YB['from'] - 20000: continue  # the core reads the whole history, the EA starts 20,000 bars before 'from'
        d, tf, kd, top, bot, t0, t1, n, last, leg = int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10]), int(f[11])
        key = (tf, kd, d, srv(t0) if tf == 9 else srv(t0) - srv(t0) % tfs[tf])   # the CHOCH* line: by its first touch (the EA names it by its leg number, counted from its own start)
        if key not in want: order.append(key)
        want[key] = (d, tf, kd, top, bot, t0, t1, n, last)
    od = os.path.join(HERE, 'x151_box_%s.obj' % name)
    fe = write('box_ea_' + name, P, dict(YB, tester=0, warm=20000, objDump=od, objPrefix='SMC', **extra))
    r = subprocess.run([HERE + '/simmain', fe, HERE + '/m1.bin', fe[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: return '%s FAILED %s' % (name, r.stderr[-300:]), False
    rect = {}; txt = {}
    for ln in open(od):
        f = ln.rstrip('\n').split('\t')
        m = re.search(r'_Z(\d)(\d)([ud])(\d+)(t?)$', f[0])
        if not m: continue
        k = (int(m.group(1)), int(m.group(2)), 1 if m.group(3) == 'u' else -1, int(m.group(4)))
        if m.group(5): txt[k] = (int(f[1]), float(f[2]), int(f[3]), f[6])
        else: rect[k] = (int(f[1]), float(f[2]), int(f[8]), float(f[9]), int(f[3]))
    got = {}
    for k in rect: got[(k[0], k[1], k[2], rect[k][0] if k[0] == 9 else srv(k[3]))] = (rect[k], txt.get(k))
    nm = {0: '15m', 1: '1h', 2: '4h'}
    exp = {}
    for key in order[-440:]:
        d, tf, kd, top, bot, t0, t1, n, last = want[key]
        if kd == 1 and half:
            m = (top + bot) / 2.0
            if d == 1: top = m
            else: bot = m
        left = srv(t0) if tf == 9 else key[3]
        col = (21 if last else 19) if d == 1 else (22 if last else 20)
        tx = ('HTF CHOCH* line' if tf == 9 else nm[tf] + (' OB' if kd == 0 else ' FVG')) + (' x%d' % n if n > 1 else '')
        exp[key] = ((left, top, srv(t1), bot, col), (left, top if d == 1 else bot, col, tx))
    def same(a, b):     # the object dump prints prices with 2 decimals (an FVG's middle 2326.105 -> 2326.1)
        if a is None or b is None or a[1] is None: return False
        (r1, t1), (r2, t2) = a, b
        return r1[0] == r2[0] and r1[2] == r2[2] and r1[4] == r2[4] and abs(r1[1] - r2[1]) < 0.006 and abs(r1[3] - r2[3]) < 0.006 and \
            t1[0] == t2[0] and abs(t1[1] - t2[1]) < 0.006 and t1[2:] == t2[2:]
    bad = [k for k in exp if not same(got.get(k), exp[k])] + [k for k in got if k not in exp]
    for k in bad[:3]: print('   %s %s: EA %s | core %s' % (name, k, got.get(k), exp.get(k)))
    za = sum(1 for ln in open(od) if re.search(r'_ZA\d\d[ud]\d+$', ln.split('\t')[0]))
    multi = sum(1 for k in exp if ' x' in exp[k][1][3])
    ok = not bad and len(exp) == min(440, len(order)) and len(order) > 440
    return '%-24s core %d zones boxed in 3 years (%d stretched), EA keeps %d: %s | show-all boxes now %d | %s' % (
        name, len(order), multi, len(got), 'ALL %d SAME (place, prices, colour, text)' % len(exp) if ok else '%d DIFFER' % len(bad), za, r.stderr.strip().split('\n')[-1]), ok


if __name__ == '__main__':
    which = sys.argv[1]
    only = sys.argv[2:]
    res = []
    with Pool(4) as pool:
        for fn, L in (('equiv', (eq_case, EQ)), ('sep', (sep_case, SEP)), ('fl1m', (fl_case, FL)), ('pause', (pa_case, PA)), ('ea', (ea_case, EA)), ('rs', (rs_case, RS)), ('box', (box_case, BOX))):
            if which == fn:
                for line, ok in pool.imap(L[0], [x for x in L[1] if not only or x[0] in only], chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
