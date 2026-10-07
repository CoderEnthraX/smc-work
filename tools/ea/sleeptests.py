# v12.3 checks of the safe catch-up after a gap (the computer slept, the connection dropped, a restart a few candles ago).
# The whole EA runs in the fake MT5 (simmain) with sleeps: the broker goes on (pending orders fill, stops and targets hit),
# the EA hears nothing, then it wakes up at a random tick (sleepRestart 1 = the terminal is loaded again at the wake-up).
#  (a) no entry by the EA at the wake-up tick (only at a candle's very first price = TradingView's fill at the open)
#  (b) never a buy and a sell open together (one-direction modes)
#  (c) SEPARATE check of every catch-up, from the price bars and the deals: the candles read = the candles missed (and the
#      forming candle when ticks of it were missed); each candle's high / low (the forming one rebuilt from its ticks up to
#      the wake tick) = what the EA used; a setup is dropped exactly when an entry it was waiting with was reached (a rule 3
#      market entry: always) and the broker had not filled it
#  (d) trading goes on after the wake-ups (trades with sleeps vs without)
#  (e) the 02:00 IST force close is never skipped: a trade open across 02:00 is closed then, or at the wake-up when the
#      EA was asleep at 02:00 (or earlier by its stop / target); days with no candle at 02:00 (holidays) have no force close
#  The same sleeps with v12.2 (its sleep-capable build) show the old problem: late entries at the wake-up, buy + sell together.
# usage: python3 sleeptests.py <simmain of v12.2> <simmain of v12.3> [test names]
#        python3 sleeptests.py <simmain of v12.2> <simmain of v12.3> restarts
#   restarts: the terminal reloaded every ~1,500 bars (inside a candle) - every deal (time, price, lots, setup number in
#   the comment) = the run with no restarts; v12.2 lost the setup number when a restart kept a waiting setup
#   build:  python3 mql2cpp.py ../../SMC_Structure_EA_v12.2.mq5 ea_x.cpp && g++ -O2 -std=c++17 -o simmain122s simmain.cpp
#           python3 mql2cpp.py ../../SMC_Structure_EA_v12.3.mq5 ea_x.cpp && g++ -O2 -std=c++17 -o simmain simmain.cpp
import sys, os, subprocess, csv, math, datetime as dt
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sleep_out')
OLD, NEW = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
T = 'fcfg_touch.txt'   # user settings (CHOCH, rules 1 + 2, 25%, 3R, hours 06-23, force close 02:00, weekend), touch entries
TESTS = {   # name: (base settings, changes, sleep every ~N bars, sleep min, max bars)
    'touch_s2':    (T, {}, 120, 2, 2),
    'touch_s5':    (T, {}, 200, 5, 5),
    'touch_s30':   (T, {}, 600, 30, 30),
    'touch_s600':  (T, {}, 3000, 600, 600),
    'touch_mix':   (T, {}, 300, 1, 60),
    'pend_s5':     (T, {'exec': 1}, 200, 5, 5),
    'pend_s30':    (T, {'exec': 1}, 600, 30, 30),
    'pend_mix':    (T, {'exec': 1}, 300, 1, 60),
    'rev_mix':     (T, {'rev': 1}, 300, 1, 60),
    'r3_mix':      ('fcfg_ea_r3_touch.txt', {}, 300, 1, 60),
    'r3fb_pend':   ('fcfg_ea_r3fb_pend.txt', {}, 300, 1, 60),
    'hedge_mix':   ('fcfg_pend_hedge_own.txt', {'exec': 0}, 300, 1, 60),
    'spC_shared':  ('fcfg_ea_spC_hedge_shared.txt', {}, 300, 1, 60),
    'm15_mix':     (T, {'chartSec': 900, 'cs': 900, 'htfSec': 14400}, 600, 2, 120),
    'rs_s3':       (T, {'tester': 0, 'sleepRestart': 1, 'to': 200000}, 1500, 3, 3),
    'rs_mix':      (T, {'tester': 0, 'sleepRestart': 1, 'to': 200000}, 1500, 1, 10),
    'rs_pend_mix': (T, {'tester': 0, 'sleepRestart': 1, 'to': 200000, 'exec': 1}, 1500, 1, 10),
    'rs_many':     (T, {'tester': 0, 'sleepRestart': 1}, 600, 2, 5),
    'rs_pend_many': (T, {'tester': 0, 'sleepRestart': 1, 'exec': 1}, 600, 2, 5),
}


def read_cfg(fn):
    c = {}
    for ln in open(os.path.join(HERE, fn)):
        p = ln.split()
        if len(p) >= 2: c[p[0]] = p[1]
    return c


def run(args):
    name, ver, sleep = args
    base, ch, every, smin, smax = TESTS[name]
    c = read_cfg(base); c.update({k: str(v) for k, v in ch.items()})
    tag = '%s_%s_%s' % (name, ver, 'sleep' if sleep else 'none')
    f = lambda x: os.path.join(OUT, '%s.%s' % (tag, x))
    if sleep: c.update(sleepEvery=every, sleepMin=smin, sleepMax=smax, wakeLog=f('wake'), dealsOut=f('deals'))
    if sleep and ver == 'new': c['dropLog'] = f('drop')
    with open(f('cfg'), 'w') as o:
        for k, v in c.items(): o.write('%s %s\n' % (k, v))
    r = subprocess.run([OLD if ver == 'old' else NEW, f('cfg'), os.path.join(HERE, 'm1.bin'), f('csv')], capture_output=True, text=True, cwd=HERE)
    return tag, r.returncode, r.stderr.strip().split('\n')[-2:]


# ---------------- the price bars, rebuilt here (UTC in the file -> FxPro server time UTC+2 / +3 in EU summer time)
def last_sun(y, m):
    d = dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)
    return (d - dt.timedelta(days=(d.weekday() + 1) % 7) - dt.date(1970, 1, 1)).days


def load_bars(to):
    raw = np.fromfile(os.path.join(HERE, 'm1.bin'), dtype=np.dtype([('t', '<i8'), ('o', '<f8'), ('h', '<f8'), ('l', '<f8'), ('c', '<f8')]), count=to)
    t = raw['t'].astype(np.int64); off = np.full(len(t), 7200, dtype=np.int64)
    for y in range(2019, 2028):
        s, e = last_sun(y, 3) * 86400 + 3600, last_sun(y, 10) * 86400 + 3600
        off[(t >= s) & (t < e)] = 10800
    return t + off, raw['o'], raw['h'], raw['l'], raw['c']


def ticks_of(o, h, l, c):
    # the fake MT5's tick path: open -> nearer extreme -> other extreme -> close, in 0.01 steps (round half away from zero)
    rd = lambda x: math.floor(x + 0.5) if x >= 0 else -math.floor(-x + 0.5)
    path = [o, h, l, c] if abs(h - o) < abs(o - l) else [o, l, h, c]
    tk = [o]
    for g in range(1, 4):
        a, z = path[g - 1], path[g]
        n = rd(abs(z - a) / 0.01)
        for k in range(1, n + 1): tk.append(rd((a + (1 if z > a else -1) * 0.01 * k) * 100.0) / 100.0)
    return tk


def check(name):
    base, ch, every, smin, smax = TESTS[name]
    c = read_cfg(base); c.update({k: str(v) for k, v in ch.items()})
    hedge = int(c.get('dirMode', 0)) == 3
    cs = int(c.get('chartSec', 60)); to = int(c.get('to', 390000))
    st, O, H, L, C = BARS[0][:to], BARS[1][:to], BARS[2][:to], BARS[3][:to], BARS[4][:to]
    ck = st - st % cs                                          # chart candle of each minute
    cks, first = np.unique(ck, return_index=True)              # chart candles (open time) and their first minute
    cidx = {int(t): i for i, t in enumerate(cks)}
    chH = np.maximum.reduceat(H, first); chL = np.minimum.reduceat(L, first)
    res = {}
    for ver in ('old', 'new'):
        tag = lambda s: os.path.join(OUT, '%s_%s_%s' % (name, ver, s))
        deals = list(csv.DictReader(open(tag('sleep.deals'))))
        wakes = list(csv.DictReader(open(tag('sleep.wake'))))
        # (a) entries made by the EA at a wake-up tick that is not the candle's first price
        late = 0
        for w in wakes:
            if int(w['tick']) == 0: continue
            late += sum(1 for d in deals[int(w['deals_before']):int(w['deals_after'])] if d['entry'] == '0')
        # (b) a buy and a sell open at the same time
        pos = {}
        for d in deals:
            p = pos.setdefault(d['pid'], [None, 1 << 62, 0])
            if d['entry'] == '0': p[0] = int(d['time']); p[2] = int(d['type'])
            else: p[1] = int(d['time'])
        ps = sorted(v for v in pos.values() if v[0] is not None)
        both = 0
        if not hedge:
            for i, a in enumerate(ps):
                for b in ps[i + 1:]:
                    if b[0] >= a[1]: break
                    if b[2] != a[2] and b[0] < a[1] and a[0] < b[1]: both += 1
        # (e) flat at 02:00 IST (= 20:30 UTC): the close comes within a candle of 02:00, or of the wake-up if asleep then
        late02 = 0
        if c.get('sessMode', '0') == '0' and c.get('hrFlat', '2') == '2':
            sl = []
            for w in wakes:
                sb, sj = int(w['slept_bar']), int(w['slept_tick'])
                sl.append((int(st[sb]) + sj * 59 // len(ticks_of(O[sb], H[sb], L[sb], C[sb])), int(w['time'])))
            for a in ps:
                if a[1] >= 1 << 62: continue   # still open when the data ends (the EA may be asleep then)
                u = (a[0] - 7200) // 86400 * 86400 - 86400
                while True:
                    u += 86400
                    bu = u + 20 * 3600 + 1800                       # 20:30 UTC of this day
                    off = 10800 if any(last_sun(y, 3) * 86400 + 3600 <= bu < last_sun(y, 10) * 86400 + 3600 for y in (dt.datetime.fromtimestamp(bu, dt.timezone.utc).year,)) else 7200
                    B = bu + off
                    if B >= a[1]: break
                    if B <= a[0]: continue
                    k = int(np.searchsorted(st, B)); tB = int(st[k]) if k < len(st) else B
                    if tB - B >= cs: break   # the market was shut at 02:00 (a holiday): no force close, like TradingView
                    wk = [w for s0, w in sl if s0 <= tB < w]
                    if a[1] > max([tB] + wk) + cs + 180: late02 += 1
                    break
        tr = list(csv.DictReader(open(tag('sleep.csv')))); tr0 = list(csv.DictReader(open(tag('none.csv'))))
        lastWake = max(int(w['time']) for w in wakes) if wakes else 0
        after = sum(1 for d in deals if d['entry'] == '0' and int(d['time']) > lastWake - 30 * 86400)
        r = dict(wakes=len(wakes), late=late, both=both, late02=late02, trades=len(tr), trades0=len(tr0),
                 net=sum(float(x['pnl']) for x in tr), net0=sum(float(x['pnl']) for x in tr0), after=after)
        if ver == 'new': r.update(sep(name, c, wakes, deals, st, cs, ck, cks, cidx, chH, chL, O, H, L, C))
        res[ver] = r
    res['new']['same0'] = open(os.path.join(OUT, '%s_old_none.csv' % name)).read() == open(os.path.join(OUT, '%s_new_none.csv' % name)).read()
    return name, res


def sep(name, c, wakes, deals, st, cs, ck, cks, cidx, chH, chL, O, H, L, C):
    """(c) every catch-up worked out separately"""
    restart = c.get('sleepRestart') == '1'
    inIn = {}
    for d in deals:
        if d['entry'] == '0' and d['cmt'] not in inIn: inIn[d['cmt']] = int(d['time'])
    # the hook rows (the book at each check) and the EA's drop lines, in order
    calls = []
    for ln in open(os.path.join(OUT, '%s_new_sleep.drop' % name)):
        if ln.startswith('H,now'): continue
        if ln.startswith('H,'):
            f = ln.strip().split(',')
            key = (int(f[1]), int(f[2]))
            if not calls or calls[-1]['key'] != key or calls[-1]['drops']:
                calls.append(dict(key=key, hi=float(f[3]), lo=float(f[4]), rows=[], drops=[]))
            calls[-1]['rows'].append(dict(side=int(f[5]), sdir=int(f[6]), sseq=int(f[7]), piece=int(f[8]), on=int(f[9]), dir=int(f[10]),
                                          seq=int(f[11]), ent=float(f[12]), mkt=int(f[13])))
        elif 'dropped - its entry' in ln:
            tid = ln.split('setup ')[1].split(' ')[0]
            calls[-1]['drops'].append((1 if tid[0] == 'L' else -1, int(tid[1:])))
    byNow = defaultdict(list)
    for cl in calls: byNow[cl['key'][0]].append(cl)
    bad = []; nDrop = 0; nCatch = 0; nCand = 0
    dn = lambda p: math.floor(p * 100 + 1e-7) / 100
    up = lambda p: math.ceil(p * 100 - 1e-7) / 100
    for w in wakes:
        wt, wb, wj = int(w['time']), int(w['bar']), int(w['tick'])
        sb, sj = int(w['slept_bar']), int(w['slept_tick'])
        lastSeenMin = sb if sj > 0 else sb - 1                 # the last minute the EA saw a tick of
        Y = cidx[int(ck[lastSeenMin])]                         # the chart candle of the last tick seen: all before it were read
        Z = cidx[int(ck[wb])]                                  # the chart candle forming at the wake-up
        missed = list(range(Y, Z))
        doCatch = (1 <= len(missed) <= 5) if restart else len(missed) >= 2
        got = byNow.get(wt, [])
        if not doCatch:
            if got: bad.append('%s: wake %d - %d missed, no catch-up expected, got %d checks' % (name, wt, len(missed), len(got)))
            continue
        nCatch += 1
        t0 = int(cks[Z])
        # the forming candle up to the wake tick: the minutes before the wake minute + the wake minute's ticks so far
        tk = ticks_of(O[wb], H[wb], L[wb], C[wb])[:wj + 1]
        m0 = int(np.searchsorted(st, t0))
        fh = max([float(H[i]) for i in range(m0, wb)] + tk); fl = min([float(L[i]) for i in range(m0, wb)] + tk)
        want = [int(cks[i]) for i in missed] + ([t0] if (wt > t0 or fh > fl) else [])
        if [cl['key'][1] for cl in got] != want:
            bad.append('%s: wake %d - candles read %s, missed %s' % (name, wt, [cl['key'][1] for cl in got][:8], want[:8])); continue
        for cl in got:
            when = cl['key'][1]
            hi, lo = (fh, fl) if when == t0 else (float(chH[cidx[when]]), float(chL[cidx[when]]))
            if abs(hi - cl['hi']) > 0.005 or abs(lo - cl['lo']) > 0.005:
                bad.append('%s: wake %d candle %d - high/low %.2f/%.2f, EA used %.2f/%.2f' % (name, wt, when, hi, lo, cl['hi'], cl['lo']))
            exp = set()
            for rw in cl['rows']:
                if rw['sdir'] == 0 or not rw['on'] or rw['seq'] != rw['sseq']: continue
                nCand += 1
                reached = rw['mkt'] == 1 or (rw['dir'] == 1 and lo <= dn(rw['ent'])) or (rw['dir'] == -1 and hi >= up(rw['ent']))
                cmt = 'SMC %s%d%s' % ('L' if rw['dir'] == 1 else 'S', rw['seq'], 'p' if rw['piece'] == 1 else '')
                filled = cmt in inIn and inIn[cmt] <= wt
                if reached and not filled: exp.add((rw['sdir'], rw['sseq']))
            nDrop += len(cl['drops'])
            if exp != set(cl['drops']): bad.append('%s: wake %d candle %d - expected drops %s, EA dropped %s' % (name, wt, when, sorted(exp), sorted(cl['drops'])))
    seen = set(int(w['time']) for w in wakes)
    for k in byNow:
        if k not in seen: bad.append('%s: a catch-up at %d that is not a wake-up' % (name, k))
    return dict(catch=nCatch, checked=nCand, drops=nDrop, bad=bad)


RS = {   # restarts (the terminal reloaded every ~N bars inside a candle): every deal = no restarts, setup numbers included
    'rs_touch': ('rcfg_touch_user_plain.txt', {}),
    'rs_pend':  ('rcfg_pend_user_plain.txt', {}),
    'rs_hedge': ('rcfg_touch_hedge_own_plain.txt', {}),
}


def rs_run(args):
    name, ver, rs = args
    c = read_cfg(RS[name][0]); c.update(RS[name][1]); c.update(to='200000', draw='0', table='0')
    if rs: c['restartEvery'] = '1500'
    tag = os.path.join(OUT, '%s_%s_%s' % (name, ver, 'restart' if rs else 'plain'))
    c['dealsOut'] = tag + '.deals'
    with open(tag + '.cfg', 'w') as o:
        for k, v in c.items(): o.write('%s %s\n' % (k, v))
    r = subprocess.run([OLD if ver == 'old' else NEW, tag + '.cfg', os.path.join(HERE, 'm1.bin'), tag + '.csv'], capture_output=True, text=True, cwd=HERE)
    return name, ver, rs, r.returncode, r.stderr.strip().split('\n')[-1]


def restarts():
    jobs = [(n, v, rs) for n in RS for v in ('old', 'new') for rs in (False, True)]
    if not os.environ.get('NORUN'):
        with Pool(4) as pool:
            for name, ver, rs, rc, err in pool.imap_unordered(rs_run, jobs):
                if rc != 0: print('FAILED', name, ver, rs, err); sys.exit(1)
                print('  ', name, ver, 'restarts' if rs else 'plain', err)
    bad = 0
    for n in RS:
        line = []
        for ver in ('old', 'new'):
            rd = lambda k: [tuple(r[x] for x in ('time', 'type', 'entry', 'price', 'vol', 'cmt')) for r in csv.DictReader(open(os.path.join(OUT, '%s_%s_%s.deals' % (n, ver, k))))]
            a, b = rd('plain'), rd('restart')
            same = sum(1 for x, y in zip(a, b) if x == y)
            sameNoCmt = sum(1 for x, y in zip(a, b) if x[:5] == y[:5])
            line.append('%s: %d deals, %d same with the setup numbers, %d same without' % ('v12.2' if ver == 'old' else 'v12.3', len(a), same, sameNoCmt))
            if ver == 'new' and (len(a) != len(b) or same != len(a)): bad += 1
        print('%-9s' % n, ' | '.join(line))
    return bad


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[3:] == ['restarts']:
        b = restarts(); print('ALL OK' if b == 0 else 'PROBLEMS: %d' % b); sys.exit(0)
    names = sys.argv[3:] or list(TESTS)
    jobs = [(n, v, s) for n in names for v in ('old', 'new') for s in (False, True)]
    if not os.environ.get('NORUN'):   # NORUN=1: only check the files of the last run
        with Pool(4) as pool:
            for tag, rc, err in pool.imap_unordered(run, jobs):
                if rc != 0: print('FAILED', tag, err); sys.exit(1)
    BARS = load_bars(max(int(dict(read_cfg(TESTS[n][0]), **{k: str(v) for k, v in TESTS[n][1].items()}).get('to', 390000)) for n in names))
    allBad = 0
    print('%-12s %6s %6s | %-24s | %-22s | %-14s | %-30s | %s' % ('test', 'wakes', 'catch', 'entries at wake old/new', 'buy+sell old/new', '02:00 old/new', 'trades none/sleep (v12.3)', 'drops, checks'))
    for n in names:
        _, r = check(n)
        o, w = r['old'], r['new']
        print('%-12s %6d %6d | %10d / %-11d | %9d / %-10d | %5d / %-6d | %6d / %-6d net %9.0f / %-9.0f | %5d %6d %s' % (
            n, w['wakes'], w['catch'], o['late'], w['late'], o['both'], w['both'], o['late02'], w['late02'], w['trades0'], w['trades'], w['net0'], w['net'], w['drops'], w['checked'],
            'OK' if not w['bad'] and w['late'] == 0 and w['both'] == 0 and w['late02'] == 0 and w['after'] > 0 and w['same0'] else 'PROBLEM'))
        if not w['same0']: print('    no sleep: v12.2 and v12.3 trades DIFFER')
        for b in w['bad'][:5]: print('   ', b)
        allBad += len(w['bad']) + w['late'] + w['both'] + w['late02'] + (w['after'] == 0) + (not w['same0'])
    print('ALL OK' if allBad == 0 else 'PROBLEMS: %d' % allBad)
