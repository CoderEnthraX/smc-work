# v13.1 checks of the EA (SMC_Structure_EA_v13.1.mq5 = v13.0 + the new section 4 filters: min stop % of the price, first
# setup of the day, yesterday's high / low, the CHOCH / BOS move in candles, today's move, RSI and EMA filters for a lower
# and a higher timeframe):
#  OFF  - python3 v13tests.py same <folder with the v13.0 harness + simmain>  (every saved settings file byte-identical)
#  sep  - the core vs a SEPARATE test copy of the v13.0 core with the filters written again from their definitions
#         (v131sep.py) + the RSI / EMA allowed directions worked out in Python: every trade identical
#  ea   - the whole EA in the fake MT5 == the core, filters ON (touch, pending, hedge, higher timeframes 3m .. 1D)
#  rs   - restarts (live mode, 20,000-bar warm-up like the EA's default): every trade == no restarts
# Settings files of these checks start with x131_ (not part of the 'same' list of v13tests.py).
import sys, os, csv, subprocess, time
from multiprocessing import Pool
from cmp import cfg_of
HERE = os.path.dirname(os.path.abspath(__file__))
U = dict(sig='CHOCH', r1=True, r2=True, pb=25.0, rr=3.0, slbuf=1.0, rev=False, wkHr=23, cmU=0.76, comm=0.3, lev=100.0, eq0=10000.0,
         bosMode='Cancel', seqMax=1e5, capAct='Clamp', pbSwp2=True)
Y = {'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1}
C5 = dict(mnPct=0.5, fstOn=1, ydOn=1, legMin=12)
C6R = dict(hrOn=13, hrOff=21, ydOn=1, legMin=12, mnPct=0.35, rsHOn=1, rsHTf=3600, rsHLen=2, rsHMode=0, rsHLvl=50)


def write(tag, P, extra, cs=60):
    c = cfg_of(P, cs); c.update(extra)
    fn = os.path.join(HERE, 'x131_%s.txt' % tag)
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    return fn


def rows(fn):
    return sorted([(int(d['side']), int(d['dir']), int(d['ebar']), float(d['ep']), round(float(d['q']), 4), int(d['xbar']), float(d['xp']), float(d['pnl']))
                   for d in csv.DictReader(open(fn))], key=lambda r: (r[2], r[1], r[5], r[4]))


BIN = {60: 'm1.bin', 300: 'm5.bin', 900: 'm15.bin', 3600: 'h1.bin'}
_T = {}
def times(cs):
    if cs not in _T:
        import numpy as np
        _T[cs] = np.fromfile(os.path.join(HERE, BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))['t']
    return _T[cs]


def ea_case(t):
    """the whole EA (1-minute ticks, chart of cs seconds) vs the core harness (chart bars), compared by candle time"""
    import numpy as np
    name, P, extra, cs = t
    e = dict(Y, **extra); e['chartSec'] = cs
    fe = write('ea_' + name, P, e, cs)
    T1, Tc = times(60), times(cs)
    h = dict(e)
    if cs != 60:
        h['from'] = int(np.searchsorted(Tc, T1[e['from']])); h['to'] = int(np.searchsorted(Tc, T1[e['to'] - 1])) + 1
    fh = write('co_' + name, P, h, cs)
    t0 = time.time()
    r1 = subprocess.run([HERE + '/simmain', fe, HERE + '/m1.bin', fe[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    r2 = subprocess.run([HERE + '/harness', fh, HERE + '/' + BIN[cs], fh[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
    if r1.returncode or r2.returncode: return '%s FAILED %s %s' % (name, r1.stderr[-300:], r2.stderr[-300:]), False
    a = [(x[0], x[1], int(T1[x[2]]) // cs, x[3], x[4], int(T1[x[5]]) // cs, x[6], x[7]) for x in rows(fe[:-4] + '.csv')]
    b = [(x[0], x[1], int(Tc[x[2]]) // cs, x[3], x[4], int(Tc[x[5]]) // cs, x[6], x[7]) for x in rows(fh[:-4] + '.csv')]
    a.sort(key=lambda r: (r[2], r[1], r[5], r[4])); b.sort(key=lambda r: (r[2], r[1], r[5], r[4]))
    same = [(x[1], x[2], x[4], x[5]) for x in a] == [(x[1], x[2], x[4], x[5]) for x in b]
    mdp = max([max(abs(x[3] - y[3]), abs(x[6] - y[6])) for x, y in zip(a, b)] + [0])
    ok = same and mdp <= 0.0101 and len(a) > 0
    return '%-28s %3s chart: EA %4d trades %10.2f | core %4d trades %10.2f | candles / dir / size / exit %s | max price diff %.4f | %.0fs' % (
        name, {60: '1m', 300: '5m', 900: '15m', 3600: '1h'}[cs], len(a), sum(x[7] for x in a), len(b), sum(x[7] for x in b), 'SAME' if same else 'DIFFER', mdp, time.time() - t0), ok


def rs_case(t):
    name, P, extra = t
    out = []
    for tag, more in (('plain', {}), ('restarts', {'restartEvery': 1500})):
        fn = write('rs_%s_%s' % (name, tag), P, dict(Y, tester=0, warm=20000, **extra, **more))
        r = subprocess.run([HERE + '/simmain', fn, HERE + '/m1.bin', fn[:-4] + '.csv'], capture_output=True, text=True, cwd=HERE)
        if r.returncode: return '%s FAILED %s' % (name, r.stderr[-300:]), False
        out.append((sorted(tuple(d.values()) for d in csv.DictReader(open(fn[:-4] + '.csv'))), r.stderr.strip().split('\n')[-1]))
    same = out[0][0] == out[1][0]
    return '%-26s no restarts: %s | with restarts: %s | %s' % (name, out[0][1], out[1][1], 'IDENTICAL' if same else 'DIFFER'), same


# only the timeframes of the v13.1 lists: 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M (seconds; 1M = 2,592,000 like MT5)
EA = [('c5_touch', dict(U, rr=1.0), dict(C5, exec=0), 60),
      ('c6rsi_pend', dict(U, rr=1.0), dict(C6R, exec=1), 60),
      ('mixed_touch', U, dict(emLOn=1, emLTf=300, emLMode=1, emLLen=20, emLFast=9, rsHOn=1, rsHTf=900, rsHLen=14, rsHMode=1, rsHLvl=55,
                              emHOn=1, emHTf=14400, emHMode=0, emHLen=50, tdOn=1, tdAtr=0.1, exec=0), 60),
      ('hedge_first_pend', U, dict(dirMode=3, fstOn=1, rsHOn=1, rsHTf=3600, rsHLen=2, ydOn=1, exec=1), 60),
      ('d1_w1_mn1_touch', U, dict(rsHOn=1, rsHTf=86400, rsHLen=3, rsHLvl=60, emHOn=1, emHTf=604800, emHMode=1, emHLen=20, emHFast=5,
                                  rsLOn=1, rsLTf=2592000, rsLLen=3, rsLMode=1, rsLLvl=50, exec=0), 60),
      ('chart_rsi_ema1m_pend', U, dict(rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=1, rsLLvl=52, emLOn=1, emLTf=60, emLLen=200, legMin=6, mnPct=0.2, exec=1), 60),
      ('m5_rsiH1h_emaL15m_touch', dict(U, risk=200.0), dict(rsHOn=1, rsHTf=3600, rsHLen=2, rsHLvl=50, emLOn=1, emLTf=900, emLLen=50, fstOn=1, ydOn=1, exec=0, htfSec=3600, htfSrv=1), 300),
      ('m15_emaH4h_rsiW1_pend', dict(U, risk=1000.0), dict(emHOn=1, emHTf=14400, emHMode=1, emHLen=200, emHFast=50, rsLOn=1, rsLTf=604800, rsLLen=2, rsLLvl=50, legMin=5, exec=1, htfSec=14400, htfSrv=1), 900),
      ('h1_emaD1_rsiH4h_touch', dict(U, risk=1000.0, sessOff=True), dict(emHOn=1, emHTf=86400, emHLen=50, rsHOn=1, rsHTf=14400, rsHLen=14, rsHMode=1, rsHLvl=45, exec=0, htfSec=86400, htfSrv=1, **{'from': 400000}), 3600),
      ('h1_rsiW1_today_pend', dict(U, risk=1000.0, sessOff=True, r2=False), dict(rsHOn=1, rsHTf=604800, rsHLen=2, rsHLvl=50, tdOn=1, tdAtr=0.0, exec=1, htfSec=86400, htfSrv=1, **{'from': 400000}), 3600)]
RS = [('c5_touch', dict(U, rr=1.0), dict(C5, exec=0)),
      ('rsi_ema_today_pend', U, dict(rsHOn=1, rsHTf=3600, rsHLen=2, emHOn=1, emHTf=14400, emHLen=200, tdOn=1, tdAtr=0.1, fstOn=1, exec=1)),
      ('hedge_first_touch', U, dict(dirMode=3, fstOn=1, ydOn=1, emLOn=1, emLTf=60, emLLen=200, exec=0)),
      ('w1_mn1_pend', U, dict(emHOn=1, emHTf=604800, emHLen=20, rsLOn=1, rsLTf=2592000, rsLLen=3, rsLMode=1, rsLLvl=50, ydOn=1, exec=1))]

if __name__ == '__main__':
    which = sys.argv[1]
    res = []
    with Pool(4) as pool:
        if which == 'sep':
            import v131sep
            for line, ok in v131sep.main(): print(line, flush=True); res.append(ok)
        if which == 'ea':
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
        if which == 'rs':
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
