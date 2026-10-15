# v14.0 checks of the EA (SMC_Structure_EA_v14.0.mq5 = v13.1 + section 1 'Separate unit for each setting' + the section 4
# leg size and big signal candle filters):
#  OFF   - python3 v13tests.py same <folder with the v13.1 harness + simmain>  (every saved settings file byte-identical)
#  equiv - 'Separate unit for each setting' with every box in the same unit = the old section 1 unit (price / pips / %):
#          byte-identical outputs over 2021 - Oct 2026; mixed units (buffer in pips, skip closer in %, rule 3 in price,
#          spread in price) = the same distances given the old way (buffer 1.0 price, v13.1 'min stop % of the price')
#  sep   - every leg size / big candle decision of the core worked out AGAIN in Python from the bars and the two levels the
#          core read (the broken level and the CHOCH* level, logged by a test hook that extract.py adds to the harness
#          copy only): leg = d x (broken level - CHOCH* level), candle = high - low, units, the first setup of the day after
#          them; every call compared with the core's own note (ARMED or SKIP - which filter)
#  ea    - the whole EA in the fake MT5 == the core with the new settings ON (touch, pending, hedge, rule 3, 15m chart)
#  rs    - restarts (live mode, 20,000-bar warm-up): every trade == no restarts
# Settings files of these checks start with x140_ (not part of the 'same' list of v13tests.py).
import sys, os, csv, subprocess, time, math
from multiprocessing import Pool
from cmp import cfg_of
import v131tests
HERE = os.path.dirname(os.path.abspath(__file__))
U = v131tests.U
Y = v131tests.Y
FULL = {'grid': 1, 'fixTies': 1}


def write(tag, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    fn = os.path.join(HERE, 'x140_%s.txt' % tag)
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    return fn


HBIN = os.environ.get('H140') or HERE + '/harness'   # a harness build with the test hook can be given here


def harness(fn, cs=60, verbose=False):
    r = subprocess.run([HBIN, fn, HERE + '/' + v131tests.BIN[cs], fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r.returncode: raise SystemExit('harness failed %s %s' % (fn, r.stderr[-300:]))
    return r


# ---------------- equiv
EQ = [  # (name, settings, old way, separate units way)
    ('price', U, dict(buMode=0, slBuf=1.0, minStop=6.0, maxStop=30.0, r3On=1, r3BrkOn=1, r3Brk=3.0, r3Fb=1, sprd=0.2),
     dict(buMode=3, slBuf=7.7, minStop=99, maxStop=1, r3On=1, r3BrkOn=1, r3Brk=0.1, r3Fb=1, sprd=9,
          bfU=0, bfV=1.0, skU=0, skMin=6.0, skMax=30.0, r3U=0, r3V=3.0, spdU=0, spdV=0.2)),
    ('pips', U, dict(buMode=1, buPips=10, minStop=60, maxStop=300, r3On=1, r3BrkOn=1, r3Brk=30, sprd=2),
     dict(buMode=3, buPips=3, minStop=1, maxStop=9, r3On=1, r3BrkOn=1, r3Brk=1, sprd=7,
          bfU=1, bfV=10, skU=1, skMin=60, skMax=300, r3U=1, r3V=30, spdU=1, spdV=2)),
    ('pct', U, dict(buMode=2, buPct=0.025, minStop=0.15, maxStop=0.7, r3On=1, r3BrkOn=1, r3Brk=0.08, sprd=0.005),
     dict(buMode=3, buPct=0.5, minStop=0.01, maxStop=5, r3On=1, r3BrkOn=1, r3Brk=2, sprd=0.1,
          bfU=2, bfV=0.025, skU=2, skMin=0.15, skMax=0.7, r3U=2, r3V=0.08, spdU=2, spdV=0.005)),
    ('mixed', U, dict(buMode=0, slBuf=1.0, mnPct=0.2, r3On=1, r3BrkOn=1, r3Brk=3.0, sprd=0.2),
     dict(buMode=3, slBuf=5.0, r3On=1, r3BrkOn=1, r3Brk=9.0, sprd=1.0,
          bfU=1, bfV=10, skU=2, skMin=0.2, skMax=0, r3U=0, r3V=3.0, spdU=0, spdV=0.2)),
    ('mixed_15m', dict(U, risk=1000.0), dict(buMode=0, slBuf=1.0, mnPct=0.3, sprd=0.2, cs=900, htfSec=14400, htfSrv=1),
     dict(buMode=3, slBuf=2.0, sprd=3.0, bfU=1, bfV=10, skU=2, skMin=0.3, skMax=0, spdU=0, spdV=0.2, cs=900, htfSec=14400, htfSrv=1)),
]


def eq_case(t):
    name, P, old, new = t
    cs = int(old.get('cs', 60))
    out = []
    for tag, e in (('old', old), ('new', new)):
        fn = write('eq_%s_%s' % (name, tag), P, dict(FULL, **e), cs)
        r = harness(fn, cs)
        out.append((open(fn[:-4] + '.csv', 'rb').read(), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0]
    return '%-10s old way: %-34s | separate units: %-34s | %s' % (name, out[0][1], out[1][1], 'BYTE-IDENTICAL' if same else 'DIFFER'), same


# ---------------- sep
def bars(cs):
    import numpy as np
    a = np.fromfile(os.path.join(HERE, v131tests.BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    return a['t'], a['p'][:, 1], a['p'][:, 2], a['p'][:, 3]


def conv(u, v, ref, pip=0.1):
    return v * pip if u == 1 else (ref * v / 100.0 if u == 2 else v)


SEP = [  # (name, settings, extra, chart seconds)
    ('leg_min8', U, dict(lzU=0, lzMin=8.0), 60),
    ('leg_5_30', U, dict(lzU=0, lzMin=5.0, lzMax=30.0), 60),
    ('leg_pips', U, dict(lzU=1, lzMin=60, lzMax=250), 60),
    ('leg_pct', U, dict(lzU=2, lzMin=0.15, lzMax=0.8), 60),
    ('candle_10', U, dict(bcU=0, bcMax=10.0), 60),
    ('candle_pct_leg_first', U, dict(bcU=2, bcMax=0.1, lzU=0, lzMin=4.0, fstOn=1), 60),
    ('rule3_fb_leg_candle_pips', U, dict(r3On=1, r3BrkOn=1, r3Brk=3.0, r3Fb=1, lzU=0, lzMin=6.0, bcU=1, bcMax=50), 60),
    ('both_sig_legmax_candle', dict(U, sig='Both'), dict(lzU=0, lzMax=20.0, bcU=0, bcMax=8.0), 60),
    ('hedge_leg_candle', U, dict(dirMode=3, lzU=0, lzMin=5.0, bcU=0, bcMax=12.0), 60),
    ('m15_pct', dict(U, risk=1000.0), dict(lzU=2, lzMin=0.3, lzMax=3.0, bcU=2, bcMax=0.4, htfSec=14400, htfSrv=1), 900),
]


def sep_case(t):
    name, P, extra, cs = t
    t0 = time.time()
    e = dict(FULL, **extra)
    log = os.path.join(HERE, 'x140_sep_%s.xs' % name)
    e['xsLog'] = log; e['verbose'] = 1
    fn = write('sep_' + name, P, e, cs)
    r = harness(fn, cs)
    notes = {}
    for ln in r.stdout.split('\n'):
        if not ln.startswith('NOTE bar '): continue
        head, msg = ln[5:].split(': ', 1)
        b, side = int(head.split()[1]), int(head.split()[3])
        if (msg.startswith('CHOCH') or msg.startswith('BOS')) and ('ARMED' in msg or ': SKIP - ' in msg): notes[(b, side)] = msg
    T, H, L, C = bars(cs)
    lzU, lzMin, lzMax = int(e.get('lzU', 0)), float(e.get('lzMin', 0)), float(e.get('lzMax', 0))
    bcU, bcMax = int(e.get('bcU', 0)), float(e.get('bcMax', 0))
    fst = bool(e.get('fstOn', 0)); fday = {0: None, 1: None}
    n = bad = 0; cnt = {}
    for ln in open(log):
        b, tt, side, d, piv, opl = ln.strip().split(',')
        b, tt, side, d, piv, opl = int(b), int(tt), int(side), int(d), float(piv), float(opl)
        assert int(T[b]) == tt, 'bar / time mismatch'
        pivNa = not math.isfinite(piv) or abs(piv) > 1e299
        want = 'pass'
        if (lzMin > 0 or lzMax > 0) and not pivNa:
            lg = d * (piv - opl)
            if lzMin > 0 and lg < conv(lzU, lzMin, opl) - 0.01 / 2: want = 'leg short'
            elif lzMax > 0 and lg > conv(lzU, lzMax, opl) + 0.01 / 2: want = 'leg long'
        if want == 'pass' and bcMax > 0 and H[b] - L[b] > conv(bcU, bcMax, C[b]) + 0.01 / 2: want = 'big'
        if want == 'pass' and fst:
            dy = (tt + cs + 19800) // 86400
            if fday[side] != dy: fday[side] = dy; want = 'first'
        msg = notes.get((b, side), '')
        got = ('leg short' if 'shorter than' in msg else 'leg long' if 'longer than' in msg else 'big' if 'big signal candle' in msg else
               'first' if 'first setup of the day' in msg else 'pass' if 'ARMED' in msg else 'other: ' + msg)
        n += 1; cnt[want] = cnt.get(want, 0) + 1
        if got != want:
            bad += 1
            if bad <= 5: print('   %s bar %d side %d: python %s | core %s' % (name, b, side, want, msg))
    trades = r.stderr.strip().split('\n')[-1]
    return '%-26s %6d filter checks (%s) | %s | %s | %.0fs' % (name, n, ', '.join('%s %d' % kv for kv in sorted(cnt.items())), trades,
                                                            'ALL AGREE' if bad == 0 and n > 0 else '%d DIFFER' % bad, time.time() - t0), bad == 0 and n > 0


# ---------------- ea / rs
def ea_case(t):
    name, P, extra, cs = t
    return v131tests.ea_case(('140_' + name, P, extra, cs))


MIX = dict(buMode=3, bfU=1, bfV=10, skU=2, skMin=0.15, skMax=0.8, spdU=0, spdV=0.2, lzU=0, lzMin=5.0, bcU=0, bcMax=12.0)
EA = [('mixed_touch', U, dict(MIX, exec=0), 60),
      ('pct_pend', U, dict(buMode=3, bfU=2, bfV=0.025, skU=0, skMin=6.0, spdU=1, spdV=2, lzU=2, lzMin=0.12, lzMax=0.9, bcU=2, bcMax=0.25, exec=1), 60),
      ('hedge_first_pend', U, dict(dirMode=3, fstOn=1, lzU=1, lzMin=50, lzMax=300, bcU=1, bcMax=100, exec=1), 60),
      ('rule3_touch', U, dict(buMode=3, bfU=0, bfV=1.0, r3On=1, r3BrkOn=1, r3U=1, r3V=30, r3Fb=1, lzU=0, lzMin=4.0, exec=0), 60),
      ('m15_pct_pend', dict(U, risk=1000.0), dict(lzU=2, lzMin=0.3, bcU=2, bcMax=0.4, exec=1, htfSec=14400, htfSrv=1), 900)]
RS = [('mixed_touch', U, dict(MIX, exec=0)),
      ('hedge_first_pend', U, dict(dirMode=3, fstOn=1, lzU=0, lzMin=5.0, lzMax=40.0, bcU=0, bcMax=10.0, exec=1))]


def rs_case(t):
    name, P, extra = t
    return v131tests.rs_case(('140_' + name, P, extra))


# ---------------- dup: a restart inside a candle after a touch fill must not enter the same setup again (old bug, fixed in v14.0)
def dup_case(t):
    """the same settings with a restart every ~150 bars (live mode), run by the v13.1 EA (folder old131) and by v14.0: count
    the setups whose entry (an IN deal with the same order comment) was sent more than once"""
    name, P, extra, cs = t
    out = []
    for tag, exe in (('v13.1', HERE + '/old131/simmain'), ('v14.0', HERE + '/simmain')):
        e = dict(Y, tester=0, warm=20000, restartEvery=300, chartSec=cs, **extra)
        e['dealsOut'] = os.path.join(HERE, 'x140_dup_%s_%s.deals' % (name, tag.replace('.', '')))
        fn = write('dup_%s_%s' % (name, tag.replace('.', '')), P, e, cs)
        r = subprocess.run([exe, fn, HERE + '/m1.bin', fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
        if r.returncode: return '%s FAILED %s' % (name, r.stderr[-300:]), False
        ins = {}
        for d in csv.DictReader(open(e['dealsOut'])):
            if d['entry'] == '0': ins[d['cmt']] = ins.get(d['cmt'], 0) + 1
        out.append((sum(1 for v in ins.values() if v > 1), len(ins), r.stderr.strip().split('\n')[-1]))
    ok = out[1][0] == 0
    return '%-14s %3s chart | v13.1: %d of %d setups entered twice | v14.0: %d of %d | %s' % (
        name, {60: '1m', 900: '15m'}[cs], out[0][0], out[0][1], out[1][0], out[1][1], 'NO DUPLICATES' if ok else 'DUPLICATES'), ok


DUP = [('touch_1m', U, dict(exec=0), 60),
       ('touch_15m', dict(U, risk=1000.0), dict(exec=0, htfSec=14400, htfSrv=1), 900),
       ('pend_15m', dict(U, risk=1000.0), dict(exec=1, htfSec=14400, htfSrv=1), 900),
       ('rule3_touch_1m', U, dict(exec=0, r3On=1), 60)]


if __name__ == '__main__':
    which = sys.argv[1]
    res = []
    with Pool(4) as pool:
        if which == 'equiv':
            for line, ok in pool.imap(eq_case, EQ, chunksize=1): print(line, flush=True); res.append(ok)
        if which == 'sep':
            for line, ok in pool.imap(sep_case, SEP, chunksize=1): print(line, flush=True); res.append(ok)
        if which == 'ea':
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
        if which == 'rs':
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
        if which == 'dup':
            for line, ok in pool.imap(dup_case, DUP, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
