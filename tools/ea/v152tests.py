# v15.2 checks of the EA (SMC_Structure_EA_v15.2.mq5 = v15.1 + kill zones (section 9) + the C5 / C6 + RSI sets (section 4)):
#  OFF    - python3 v13tests.py same old151 (folder with the v15.1 harness + simmain): every saved settings file byte-identical
#  equiv  - the C5 / C6 + RSI sets = the same settings typed by hand (the boxes set to OTHER values, which the set must override);
#           the kill zone boxes with the master switch OFF = nothing
#  eqea   - the same in the whole EA (fake MT5): the C6 set also switches the RSI to the 1-hour MT5 candles
#  kz     - every bar's kill zone flag worked out AGAIN in Python (New York clock from zoneinfo, the next bar's minutes one by one)
#           = the core's (test hook, key kzLog); every setup armed inside a kill zone, every 'outside the kill zones' skip outside;
#           'when a kill zone ends' ON: every 'kill zone ended' cancel and 'Kill zone end' close on the first bar outside, no trade
#           open on a bar outside the kill zones; OFF: trades run on outside (counted)
#  ea     - the whole EA in the fake MT5 == the core (kill zones, end ON / OFF, hedge, C6, 15m)
#  rs     - restarts (live mode, 20,000-bar warm-up): every trade == no restarts
# Settings files of these checks start with x152_.
import sys, os, csv, subprocess, time, datetime
import numpy as np
from zoneinfo import ZoneInfo
from multiprocessing import Pool
from cmp import cfg_of
import v131tests
HERE = os.path.dirname(os.path.abspath(__file__))
U = v131tests.U
Y = v131tests.Y
C5 = dict(mnPct=0.5, fstOn=1, ydOn=1, legMin=12)
C6R = v131tests.C6R
FULL = {'grid': 1, 'fixTies': 1}
BIN = v131tests.BIN
M15 = dict(htfSec=14400, htfSrv=1)
U15 = dict(U, risk=1000.0)


def write(tag, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    fn = os.path.join(HERE, 'x152_%s.txt' % tag)
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    return fn


def harness(fn, cs=60):
    r = subprocess.run([HERE + '/harness', fn, HERE + '/' + BIN[cs], fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: raise SystemExit('harness failed %s %s' % (fn, r.stderr[-300:]))
    return r


# ---------------- equiv: the sets = by hand (the boxes hold OTHER values the set must override)
C5X = dict(mnPct=0.2, fstOn=0, ydOn=0, legMin=5)
C6X = dict(hrOn=6, hrOff=23, mnPct=0.1, ydOn=0, legMin=3, rsHOn=0, rsHTf=900, rsHLen=14, rsHMode=1, rsHLvl=70)
EQ = [  # (name, settings, chart, with the set, the same by hand)
    ('c5_1m', U, 60, dict(C5X, c5=1), dict(C5)),
    ('c6_1m', U, 60, dict(C6X, c6=1), dict(C6R)),
    ('c5_15m', U15, 900, dict(C5X, c5=1, **M15), dict(C5, **M15)),
    ('c6_zone_mss_15m', U15, 900, dict(C6X, c6=1, sig=12, mssOn=1, **M15), dict(C6R, sig=12, mssOn=1, **M15)),
    ('c6_kz_end_hedge_1m', U, 60, dict(C6X, c6=1, kzOn=1, kzEnd=1, dirMode=3), dict(C6R, kzOn=1, kzEnd=1, dirMode=3)),
    ('c5_first_rule3_1m', U, 60, dict(C5X, c5=1, r3On=1), dict(C5, r3On=1)),
    ('kz_master_off_1m', U, 60, dict(kzOn=0, kzAs=1, kzLo=0, kzNy=0, kzLc=1, kzEnd=1), dict()),
]


def eq_case(t):
    name, P, cs, a, b = t
    out = []
    for tag, e in (('set', a), ('hand', b)):
        fn = write('eq_%s_%s' % (name, tag), P, dict(FULL, **e), cs)
        r = harness(fn, cs)
        out.append((open(fn[:-4] + '.csv', 'rb').read(), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0] and out[0][0].count(b'\n') > 1
    return '%-22s set: %-34s | by hand: %-34s | %s' % (name, out[0][1], out[1][1], 'BYTE-IDENTICAL' if same else 'DIFFER'), same


EQEA = [  # the whole EA: (name, settings, with the set, by hand)
    ('c6_pend', U, dict(C6X, c6=1, exec=1), dict(C6R, exec=1)),
    ('c5_kz_touch', U, dict(C5X, c5=1, kzOn=1, exec=0), dict(C5, kzOn=1, exec=0)),
]


def eqea_case(t):
    name, P, a, b = t
    out = []
    for tag, e in (('set', a), ('hand', b)):
        fn = write('eqea_%s_%s' % (name, tag), P, dict(Y, **e))
        r = subprocess.run([HERE + '/simmain', fn, HERE + '/m1.bin', fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
        if r.returncode: return '%s FAILED %s' % (name, r.stderr[-300:]), False
        out.append((open(fn[:-4] + '.csv', 'rb').read(), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0] and out[0][0].count(b'\n') > 1
    return '%-14s whole EA set: %-34s | by hand: %-34s | %s' % (name, out[0][1], out[1][1], 'BYTE-IDENTICAL' if same else 'DIFFER'), same


# ---------------- kz: the kill zone flag + the arming / cancels / closes, worked out again
ZW = {'kzAs': (1200, 1440), 'kzLo': (120, 300), 'kzNy': (420, 600), 'kzLc': (600, 720)}
ZD = {'kzAs': 0, 'kzLo': 1, 'kzNy': 1, 'kzLc': 0}   # the defaults
NY = ZoneInfo('America/New_York')
H0 = int(datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
NH = 9 * 366 * 24
NYOFF = np.array([int(datetime.datetime.fromtimestamp(H0 + h * 3600, NY).utcoffset().total_seconds()) for h in range(NH)])


def kz_flags(T, cs, zones):
    """the bar may arm: the NEXT bar [close, close + bar) touches a chosen kill zone (New York minutes, one by one)"""
    tc = T + cs
    loc = tc + NYOFF[(tc - H0) // 3600]
    m = (loc % 86400) // 60
    ln = max(1, cs // 60)
    ok = np.zeros(len(T), dtype=bool)
    for a, b in zones:
        for x in range(ln):
            mm = (m + x) % 1440
            ok |= (mm >= a) & (mm < b)
    return ok


KZ = [  # (name, settings, extra, chart seconds)
    ('lo_ny_1m', U, dict(kzOn=1), 60),
    ('all4_end_1m', U, dict(kzOn=1, kzAs=1, kzLc=1, kzEnd=1), 60),
    ('asian_end_rule3_1m', U, dict(kzOn=1, kzAs=1, kzLo=0, kzNy=0, kzEnd=1, r3On=1), 60),
    ('ny_end_zone_mss_1m', U, dict(sig=12, mssOn=1, mssCf=1, kzOn=1, kzLo=0, kzEnd=1), 60),
    ('lc_end_bos_hedge_1m', U, dict(sig=2, dirMode=3, kzOn=1, kzLo=0, kzNy=0, kzLc=1, kzEnd=1), 60),
    ('lo_ny_end_c6_1m', U, dict(c6=1, kzOn=1, kzEnd=1), 60),
    ('lo_end_notime_15m', U15, dict(kzOn=1, kzNy=0, kzEnd=1, sessMode=2, **M15), 900),
    ('ny_lc_end_1h', dict(U, risk=1000.0), dict(kzOn=1, kzLo=0, kzLc=1, kzEnd=1, sessMode=2, htfSec=86400, htfSrv=1), 3600),
]


def kz_case(t):
    name, P, extra, cs = t
    t0 = time.time()
    log = os.path.join(HERE, 'x152_kz_%s.kz' % name)
    e = dict(FULL, **extra); e['kzLog'] = log; e['verbose'] = 1
    fn = write('kz_' + name, P, e, cs)
    r = harness(fn, cs)
    a = np.fromfile(os.path.join(HERE, BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    T = a['t'].astype(np.int64)
    zones = [ZW[k] for k in ZW if int(extra.get(k, ZD[k]))]
    py = kz_flags(T, cs, zones)
    co = np.ones(len(T), dtype=bool); seen = np.zeros(len(T), dtype=bool)
    for ln in open(log):
        bi, tt, f = ln.strip().split(',')
        bi = int(bi)
        if int(tt) != int(T[bi]): return '%s: the bar numbers do not match the times' % name, False
        co[bi] = f == '1'; seen[bi] = True
    bad = int(((py != co) & seen).sum())
    if bad:
        k = int(np.nonzero((py != co) & seen)[0][0])
        print('   %s bar %d %s: python %s core %s' % (name, k, datetime.datetime.utcfromtimestamp(int(T[k])), py[k], co[k]))
    # the notes
    arm = skip = canc = 0; nbad = 0
    for ln in r.stdout.split('\n'):
        if not ln.startswith('NOTE bar '): continue
        b = int(ln[9:ln.index(' side')])
        if ' ARMED' in ln or 'WAITING for the MSS' in ln:
            arm += 1; nbad += not py[b]
        elif 'SKIP - outside the kill zones' in ln:
            skip += 1; nbad += py[b]
        elif 'CANCELLED - kill zone ended' in ln:
            canc += 1; nbad += py[b] or not int(extra.get('kzEnd', 0))
    # the trades: with 'end' ON nothing is open on a bar outside the kill zones (closed at the next open), the reason is right
    end = bool(int(extra.get('kzEnd', 0)))
    out = np.nonzero(~py)[0]
    ntr = kzc = across = tbad = 0
    for d in csv.DictReader(open(fn[:-4] + '.csv')):
        ntr += 1
        eb, xb, why = int(d['ebar']), int(d['xbar']), d['why']
        k = np.searchsorted(out, eb)
        first_out = int(out[k]) if k < len(out) else 10 ** 9
        if why == 'Kill zone end':
            kzc += 1
            tbad += not end or xb - 1 != first_out
        if xb - 1 > first_out:
            across += 1
            tbad += end
    ok = bad == 0 and nbad == 0 and tbad == 0 and seen.sum() > 0 and arm > 0 and (not end or kzc > 0)
    return '%-22s %d bars, in the kill zones %4.1f%% (python = core: %s) | armed %d, skipped outside %d, cancelled at the end %d | trades %d, ' \
           'closed at the end %d, open across a bar outside %d | %s | %.0fs' % (
               name, int(seen.sum()), 100.0 * py.mean(), 'YES' if bad == 0 else '%d DIFFER' % bad, arm, skip, canc, ntr, kzc, across,
               'ALL AGREE' if ok else 'notes %d / trades %d WRONG' % (nbad, tbad), time.time() - t0), ok


# ---------------- ea / rs: the whole EA in the fake MT5 == the core; restarts == no restarts
def ea_case(t):
    name, P, extra, cs = t
    return v131tests.ea_case(('152_' + name, P, extra, cs))


EA = [('kz_lo_ny_touch', U, dict(kzOn=1, exec=0), 60),
      ('kz_all_end_pend', U, dict(kzOn=1, kzAs=1, kzLc=1, kzEnd=1, exec=1), 60),
      ('kz_end_bos_hedge_touch', U, dict(sig=2, dirMode=3, kzOn=1, kzEnd=1, exec=0), 60),
      ('c6_kz_end_pend', U, dict(c6=1, kzOn=1, kzEnd=1, exec=1), 60),
      ('kz_end_notime_15m_touch', U15, dict(kzOn=1, kzEnd=1, sessMode=2, fl1m=1, exec=0, **M15), 900),
      ('c6_kz_15m_pend', U15, dict(c6=1, kzOn=1, kzAs=1, exec=1, **M15), 900)]
RS = [('kz_end_touch', U, dict(kzOn=1, kzEnd=1, exec=0)),
      ('c6_kz_pend', U, dict(c6=1, kzOn=1, exec=1))]


def rs_case(t):
    name, P, extra = t
    return v131tests.rs_case(('152_' + name, P, extra))


if __name__ == '__main__':
    which = sys.argv[1]
    only = sys.argv[2:]
    res = []
    with Pool(4) as pool:
        for fn, L in (('equiv', (eq_case, EQ)), ('eqea', (eqea_case, EQEA)), ('kz', (kz_case, KZ)), ('ea', (ea_case, EA)), ('rs', (rs_case, RS))):
            if which == fn:
                for line, ok in pool.imap(L[0], [x for x in L[1] if not only or x[0] in only], chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
