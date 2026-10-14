# v13.1 'sep' check (run by: python3 v131tests.py sep): the v13.1 core (./harness) vs a SEPARATE test copy of the v13.0
# core with the section 4 filters written again from their definitions (not the v13.1 code):
#   day = the New York trading day of the bar OPEN (17:00 New York); average daily range = mean of the last 14 complete
#   days; first setup of the day (session timezone, per side); yesterday's high / low; candles of the move; today's move;
#   min stop % of the entry price - and the RSI / EMA filters as allowed directions per minute worked out in Python
#   (broker-clock candles that closed before the bar's own candle, or the chart's own candles up to the bar).
# Every trade must be identical. The user's 1m settings (Rule C off), 1m and 15m charts, every filter and timeframe.
import os, sys, subprocess, datetime as dt
import numpy as np
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, 'v131_sep')
BASE = dict(x.split(' ') for x in (
    'sig 0|r1 1|r2 1|pb 25.0|rr 3.0|slBuf 1.0|rev 0|once 0|hrOn 6|hrOff 23|hrFlat 2|wkFlat 1|wkDay 6|wkHr 23|risk 50.0|cmLot 38.0|comm 0.3|lotStep 0.01|'
    'rndMax 25.0|lev 10.0|cmTgt 1|eq0 100000.0|cancelSig 1|expBars 0|minStop 0.0|maxStop 0.0|maxTrades 0|dayLoss 0.0|maxOpen 0|mvStep 0|mvBe 0|dirMode 0|'
    'bkOn 0|bkPct 100.0|hfOn 0|trOn 0|trMode 0|lqOn 0|lqMin 1.0|ppOn 0|ppPct 50.0|ppR 1.0|ppBe 1|pdOn 0|pdPct 50.0|lsOn 0|lsN 1|bosCnl 1|seqMode 0|'
    'seqAdd 50.0|split 3.0|flMode 0|flAmt 2000.0|flLock 50.0|flPct 2.5|ldOn 1|ldN 4|ldD 3|eqOn 0|eqPct 75.0|seqMax 100000.0|capAct 1|seqFrom 0|'
    'seqFromT 0|htfSec 900|cs 60|auOn 1|sessMode 0|minLot 0.01|pbSwp2 1|from 20000|to 2037534').split('|'))


def build():
    """the separate copy: the v13.0 core + its own filters, compiled with this harness (the v13.1 keys are not seen by it)"""
    os.makedirs(TMP, exist_ok=True)
    src = open(os.path.join(HERE, '..', '..', 'SMC_Structure_EA_v13.0.mq5')).read()
    s = src[src.index('//==CORE-BEGIN=='):src.index('//==CORE-END==')]
    def rep(old, new):
        nonlocal s
        assert s.count(old) == 1, old[:60]
        s = s.replace(old, new)
    rep('bool SideChasing(int k);', '''double g_xMinPct = 0, g_xToday = -99.0, g_xYday = 0, g_xFirst = 0, g_xLegMin = 0;
long   g_xDay = LONG_MIN, g_xFirstDay[2] = {LONG_MIN, LONG_MIN};
double g_xO = 0, g_xH = 0, g_xL = 0, g_xyH = 0, g_xyL = 0, g_xAvg = 0;
bool   g_xHaveY = false;
std::deque<double> g_xRng;
signed char *g_xFlg = 0; long g_xFlgT0 = 0, g_xFlgN = 0;
void XDay(long t, double o, double h, double l)
{
   long ny = t + TzOff(t, -18000, 2) - 17 * 3600;
   long k = ny >= 0 ? ny / 86400 : -((-ny + 86399) / 86400);
   if (k != g_xDay)
   {
      if (g_xDay != LONG_MIN)
      {
         g_xyH = g_xH; g_xyL = g_xL; g_xHaveY = true;
         g_xRng.push_back(g_xH - g_xL);
         if (g_xRng.size() > 14) g_xRng.pop_front();
         if (g_xRng.size() == 14) { double sm = 0; for (double v : g_xRng) sm += v; g_xAvg = sm / 14.0; }
      }
      g_xDay = k; g_xO = o; g_xH = h; g_xL = l;
   }
   else { if (h > g_xH) g_xH = h; if (l < g_xL) g_xL = l; }
}
bool XOk(int side, int d, double c, int legBars, long day)
{
   if (g_xFlg) { long i = (g_t - g_xFlgT0) / 60; if (i >= 0 && i < g_xFlgN) { int f = g_xFlg[i]; if ((d == 1 && !(f & 1)) || (d == -1 && !(f & 2))) return false; } }
   if (g_xToday > -98 && g_xAvg > 0 && d * (c - g_xO) < g_xToday * g_xAvg) return false;
   if (g_xYday > 0.5 && g_xHaveY && (d == 1 ? c < g_xyL : c > g_xyH)) return false;
   if (g_xLegMin > 0 && legBars < g_xLegMin) return false;
   if (g_xFirst > 0.5 && day != g_xFirstDay[side]) { g_xFirstDay[side] = day; return false; }
   return true;
}
bool SideChasing(int k);''')
    rep('         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent))',
        '         bool dOk   = (g_xMinPct <= 0 || r >= ent * g_xMinPct / 100.0) && (S.minStop <= 0 || r >= LimAt(S.minStop, ent))')
    rep('   EN.Step(o, h, l, c);\n', '   EN.Step(o, h, l, c);\n   XDay(t, o, h, l);\n')
    rep('            if (use && !IsNa(opl))\n', '''            if (use && !IsNa(opl) && !XOk(k, d, g_c, d == 1 ? EN.bi - EN.flr.x1 : EN.bi - EN.cel.x1, FloorDivL(SessLoc(g_t + S.cs), 86400))) use = false;
            if (use && !IsNa(opl))
''')
    open(os.path.join(TMP, 'core_s.inc'), 'w').write('#define CORE_V13 1\n#include <deque>\n#include <climits>\n' + s)
    h = open(os.path.join(HERE, 'harness.cpp')).read().replace('#include "core_x.inc"', '#include "core_s.inc"')
    k = '   if (cfg.count("ordLog")) olog = fopen(cfg["ordLog"].c_str(), "w");\n'
    assert h.count(k) == 1
    h = h.replace(k, k + '   g_xMinPct = cd("xMinPct", 0); g_xToday = cd("xToday", -99); g_xYday = cd("xYday", 0); g_xFirst = cd("xFirst", 0); g_xLegMin = cd("xLegMin", 0);\n'
                        '   if (cfg.count("xFlags")) { FILE *ff = fopen(cfg["xFlags"].c_str(), "rb"); long hd[2]; if (!ff || fread(hd, 8, 2, ff) != 2) return 1; g_xFlgT0 = hd[0]; g_xFlgN = hd[1]; g_xFlg = new signed char[g_xFlgN]; if (fread(g_xFlg, 1, g_xFlgN, ff) != (size_t)g_xFlgN) return 1; fclose(ff); }\n')
    open(os.path.join(TMP, 'harness_s.cpp'), 'w').write(h)
    subprocess.run(['g++', '-O2', '-std=c++17', '-I', HERE, '-o', os.path.join(TMP, 'sepcore'), os.path.join(TMP, 'harness_s.cpp')], check=True, capture_output=True)


# ---------------- the RSI / EMA allowed directions, worked out in Python
def _last_sunday(y, m):
    d = dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)
_eu = {}
def srv_off(t):
    y = dt.datetime.utcfromtimestamp(int(t)).year
    if y not in _eu:
        a = dt.datetime.combine(_last_sunday(y, 3), dt.time(1)).replace(tzinfo=dt.timezone.utc).timestamp()
        b = dt.datetime.combine(_last_sunday(y, 10), dt.time(1)).replace(tzinfo=dt.timezone.utc).timestamp()
        _eu[y] = (a, b)
    a, b = _eu[y]
    return 10800 if a <= t < b else 7200
def rsi_seq(c, n):
    out = np.full(len(c), np.nan); au = ad = None; su = sd = 0.0; cnt = 0
    for i in range(1, len(c)):
        u = max(c[i] - c[i - 1], 0.0); d = max(c[i - 1] - c[i], 0.0)
        if au is None:
            su += u; sd += d; cnt += 1
            if cnt >= n: au = su / n; ad = sd / n
        else:
            au = (au * (n - 1) + u) / n; ad = (ad * (n - 1) + d) / n
        if au is not None: out[i] = 100.0 if ad == 0 else (0.0 if au == 0 else 100.0 - 100.0 / (1.0 + au / ad))
    return out
def ema_seq(c, n):
    out = np.empty(len(c)); e = None
    for i, v in enumerate(c):
        e = v if e is None else e + 2.0 / (n + 1) * (v - e); out[i] = e
    return out
def candle_key(T, tf):
    """the candle of each bar on the broker clock: weeks from Sunday 00:00, months from the 1st, else every tf seconds"""
    srv = T + np.array([srv_off(t) for t in T])
    if tf == 604800: return (srv - 3 * 86400) // 604800
    if tf == 2592000:
        d = [dt.datetime.utcfromtimestamp(int(x)) for x in srv]
        return np.array([x.year * 12 + x.month for x in d], dtype=np.int64)
    return srv // tf
def at_bars(T, C, cs, tf, fn):
    if tf <= cs: return fn(C)
    key = candle_key(T, tf)
    idx = np.r_[0, np.flatnonzero(np.diff(key)) + 1]; end = np.r_[idx[1:], len(T)]
    v = fn(C[end - 1])
    j = np.searchsorted(key[idx], key, side='left') - 1
    out = np.full(len(T), np.nan); ok = j >= 0; out[ok] = v[j[ok]]
    return out
def flags(T, C, cs, cfg):
    lo = np.ones(len(T), bool); sh = np.ones(len(T), bool)
    on = lambda k: cfg.get(k, '0') in ('1', 'true', 'True')
    for s in ('L', 'H'):
        if on('rs%sOn' % s):
            tf = int(cfg.get('rs%sTf' % s, 0 if s == 'L' else 3600)); n = int(cfg.get('rs%sLen' % s, 14 if s == 'L' else 2))
            md = int(cfg.get('rs%sMode' % s, 0)); lv = float(cfg.get('rs%sLvl' % s, 50))
            v = at_bars(T, C, cs, tf, lambda x: rsi_seq(x, n)); ok = ~np.isnan(v)
            a, b = (v < lv, v > 100 - lv) if md == 0 else (v > lv, v < 100 - lv)
            lo &= ~ok | a; sh &= ~ok | b
        if on('em%sOn' % s):
            tf = int(cfg.get('em%sTf' % s, 0 if s == 'L' else 3600)); n = int(cfg.get('em%sLen' % s, 200))
            md = int(cfg.get('em%sMode' % s, 0)); nf = int(cfg.get('em%sFast' % s, 50))
            slow = at_bars(T, C, cs, tf, lambda x: ema_seq(x, n)); ok = ~np.isnan(slow)
            fast = at_bars(T, C, cs, tf, lambda x: ema_seq(x, nf)) if md == 1 else C
            lo &= ~ok | (fast > slow); sh &= ~ok | (fast < slow)
    return lo, sh
def write_flags(path, T, lo, sh):
    t0 = int(T[0]); n = int((T[-1] - t0) // 60 + 1)
    fl = np.full(n, 3, np.int8); fl[(T - t0) // 60] = lo.astype(np.int8) | (sh.astype(np.int8) << 1)
    with open(path, 'wb') as fh: np.array([t0, n], dtype=np.int64).tofile(fh); fl.tofile(fh)


# ---------------- the cases
_raw = {}
BIN = {60: 'm1.bin', 300: 'm5.bin', 900: 'm15.bin', 3600: 'h1.bin'}
def bars(cs):
    if cs not in _raw: _raw[cs] = np.fromfile(os.path.join(HERE, BIN[cs]), dtype=np.dtype([('t', '<i8'), ('p', '<f8', 4)]))
    return _raw[cs]
def run(exe, d, tag):
    fn = os.path.join(TMP, tag + '.txt'); out = fn[:-4] + '.csv'
    open(fn, 'w').write(''.join('%s %s\n' % kv for kv in d.items()))
    r = subprocess.run([exe, fn, os.path.join(HERE, BIN[int(d.get('cs', 60))]), out], capture_output=True, text=True)
    rows = open(out).read(); os.remove(fn); os.remove(out)
    return rows, r.stderr.strip().split('\n')[-1]
def one(job):
    name, kw = job
    d = dict(BASE); d.update({k: str(v) for k, v in kw.items()})
    a, ea = run(os.path.join(HERE, 'harness'), d, 'n_' + name)
    e = {k: v for k, v in d.items() if not (k in ('mnPct', 'fstOn', 'ydOn', 'legMin', 'tdOn', 'tdAtr') or k.startswith('rs') or k.startswith('em'))}
    e['xMinPct'] = d.get('mnPct', '0'); e['xFirst'] = d.get('fstOn', '0'); e['xYday'] = d.get('ydOn', '0'); e['xLegMin'] = d.get('legMin', '0')
    if d.get('tdOn', '0') in ('1', 'true'): e['xToday'] = d.get('tdAtr', '0.15')
    if any(k.startswith('rs') or k.startswith('em') for k in kw):
        rb = bars(int(d.get('cs', 60))); lo, sh = flags(rb['t'], rb['p'][:, 3], int(d.get('cs', 60)), d)
        e['xFlags'] = os.path.join(TMP, 'fl_%s.bin' % name); write_flags(e['xFlags'], rb['t'], lo, sh)
    b, eb = run(os.path.join(TMP, 'sepcore'), e, 's_' + name)
    if 'xFlags' in e: os.remove(e['xFlags'])
    return '%-30s %s  trades %5d | v13.1: %s | separate: %s' % (name, 'IDENTICAL' if a == b else 'DIFFERENT', len(a.strip().split('\n')) - 1, ea, eb), a == b
# only the timeframes of the v13.1 lists: 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M (seconds; 1M = 2,592,000 like MT5)
M5 = dict(risk=200, cs=300, htfSec=3600, htfSrv=1, **{'from': 4000})
M15 = dict(risk=1000, cs=900, htfSec=14400, htfSrv=1)
H1 = dict(risk=1000, cs=3600, htfSec=86400, htfSrv=1, sessMode=2, **{'from': 400})
JOBS = [('C5_1R', dict(mnPct=0.5, fstOn=1, ydOn=1, legMin=12, rr=1.0)),
        ('C6_rsiH1h_1R', dict(hrOn=13, hrOff=21, ydOn=1, legMin=12, mnPct=0.35, rsHOn=1, rsHTf=3600, rsHLen=2, rsHMode=0, rsHLvl=50, rr=1.0)),
        ('C4_today', dict(tdOn=1, tdAtr=0.15, hrOn=13, hrOff=21, fstOn=1)),
        ('today0_yday', dict(tdOn=1, tdAtr=0.0, ydOn=1)),
        ('rsiL1m14_emaH1h200', dict(rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=0, rsLLvl=50, emHOn=1, emHTf=3600, emHMode=0, emHLen=200)),
        ('emaL5m_9_20_rsiH15m_mom', dict(emLOn=1, emLTf=300, emLMode=1, emLLen=20, emLFast=9, rsHOn=1, rsHTf=900, rsHLen=14, rsHMode=1, rsHLvl=55)),
        ('emaH4h50_rsiD1', dict(emHOn=1, emHTf=14400, emHMode=0, emHLen=50, rsHOn=1, rsHTf=86400, rsHLen=3, rsHMode=0, rsHLvl=60, ydOn=1)),
        ('emaH1W20_rsiH1M3', dict(emHOn=1, emHTf=604800, emHMode=0, emHLen=20, rsLOn=1, rsLTf=2592000, rsLLen=3, rsLMode=1, rsLLvl=50)),
        ('emaD1_50_200_rsiL15m', dict(emHOn=1, emHTf=86400, emHMode=1, emHLen=200, emHFast=50, rsLOn=1, rsLTf=900, rsLLen=7, rsLMode=0, rsLLvl=55)),
        ('emaL1M6_first', dict(emLOn=1, emLTf=2592000, emLMode=0, emLLen=6, fstOn=1)),
        ('m5_C6_rsiH1h', dict(M5, hrOn=13, hrOff=21, ydOn=1, legMin=6, rsHOn=1, rsHTf=3600, rsHLen=2, rsHLvl=50, emLOn=1, emLTf=900, emLLen=50)),
        ('m5_rsiL1m_chart_emaH4h', dict(M5, rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=1, rsLLvl=50, emHOn=1, emHTf=14400, emHLen=100, tdOn=1, tdAtr=0.05)),
        ('m15_rsiH1h', dict(M15, rsHOn=1, rsHTf=3600, rsHLen=2, rsHLvl=50)),
        ('m15_emaH4h_cross_leg5', dict(M15, emHOn=1, emHTf=14400, emHMode=1, emHLen=200, emHFast=50, legMin=5)),
        ('m15_emaL5m_chart_first_mn', dict(M15, emLOn=1, emLTf=300, emLLen=50, fstOn=1, mnPct=0.4)),
        ('m15_rsiL_chart_mom', dict(M15, rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=1, rsLLvl=50, ydOn=1)),
        ('m15_first_yday_today', dict(M15, fstOn=1, ydOn=1, tdOn=1, tdAtr=0.05, mnPct=0.3)),
        ('m15_rsiH1W_emaH1M', dict(M15, rsHOn=1, rsHTf=604800, rsHLen=2, rsHLvl=50, emLOn=1, emLTf=2592000, emLLen=4)),
        ('h1_rsiH4h_mom_emaD1_leg2', dict(H1, rsHOn=1, rsHTf=14400, rsHLen=14, rsHMode=1, rsHLvl=45, emHOn=1, emHTf=86400, emHLen=50, legMin=2, ydOn=1)),
        ('h1_emaW1_cross', dict(H1, emHOn=1, emHTf=604800, emHMode=1, emHLen=20, emHFast=5, rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=1, rsLLvl=50)),
        ('rsiL1m_chart_mom', dict(rsLOn=1, rsLTf=60, rsLLen=14, rsLMode=1, rsLLvl=55)),
        ('hedge_first_rsi', dict(dirMode=3, fstOn=1, rsHOn=1, rsHTf=3600, rsHLen=2, ydOn=1, legMin=8, rev=0)),
        ('rule3_filters', dict(r3On=1, r1=0, r2=0, fstOn=1, tdOn=1, tdAtr=0.1, emHOn=1, emHTf=3600, emHLen=50, mnPct=0.3)),
        ('rsiH1h_mom_lvl70', dict(rsHOn=1, rsHTf=3600, rsHLen=14, rsHMode=1, rsHLvl=70))]
def main():
    build()
    with ThreadPoolExecutor(4) as ex:
        for line, ok in ex.map(one, JOBS): yield line, ok
