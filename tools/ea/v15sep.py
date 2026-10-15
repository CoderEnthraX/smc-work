# v15.0: the order block zone modes worked out AGAIN in Python, separately from the EA core, and compared with every zone decision
# the core made. Input: the 1-minute bars (m1.bin) and the harness log of the test hook (extract.py, key znLog):
#   B,bar,htTrend,htLegStart,htLegExtreme,htEvents,choUp,choDn,bosUp,bosDn   - every chart bar (the higher timeframe engine's
#                                                                              values and the chart's structure events)
#   A,bar,d,tf,kind,top,bottom                                                - every zone question of a signal and the core's answer
# Everything about the zones is done here from the bars alone: the candles of the zone timeframes (broker clock FxPro UTC+2 / +3
# EU summer time; weeks from Sunday, months from the 1st), FVGs (candle 1 and 3 apart), the order block (last opposite candle among
# candles 3 - 5 back), a zone gone at a close of its own timeframe beyond its far side, 10 per timeframe and side, the leg's zone,
# the touch line (order block near edge; FVG 50% or near edge), touches, visits, liquidity taken, the biggest timeframe, the
# CHOCH* line.
import datetime, math
import numpy as np

LADDER = [900, 3600, 14400, 86400, 604800, 2592000]


def eu_summer(t):
    """FxPro clock: UTC+3 from the last Sunday of March 01:00 UTC to the last Sunday of October 01:00 UTC, else UTC+2"""
    y = datetime.datetime.utcfromtimestamp(t).year

    def last_sun(m):
        d = datetime.datetime(y, m, 31 if m in (3, 10) else 30)
        while d.weekday() != 6: d -= datetime.timedelta(days=1)
        return int(d.replace(hour=1, tzinfo=datetime.timezone.utc).timestamp())
    return last_sun(3) <= t < last_sun(10)


def bkey(t, tf):
    s = t + (10800 if eu_summer(t) else 7200)
    if tf == 604800: return (s - 3 * 86400) // 604800
    if tf == 2592000:
        d = datetime.datetime.utcfromtimestamp(s)
        return d.year * 12 + d.month
    return s // tf


def up(sec):
    for v in LADDER:
        if sec < v: return v
    return 0


def ret_lvl(d, anch, orig, pct):
    if d == 1 and anch is not None and orig is not None and anch > orig: return anch - (anch - orig) * pct / 100.0
    if d == -1 and anch is not None and orig is not None and orig > anch: return anch + (orig - anch) * pct / 100.0
    return None


class Zone:
    def __init__(self, tf, d, kind, top, bot, t0=None):
        self.tf, self.d, self.kind, self.top, self.bot, self.t0 = tf, d, kind, top, bot, t0
        self.tt = None
        self.clear()

    def clear(self):
        self.q = False; self.tch = False; self.frz = False; self.spent = False; self.ext = None


def run(T, O, H, L, C, log, P, htf):
    tick = 0.01
    e = tick / 2
    tfs = [htf, up(htf), 0]
    tfs[2] = up(tfs[1]) if tfs[1] else 0
    zones = []
    candles = [[], [], []]          # newest first: (o, h, l, c, open time)
    last_ob = [[None, None], [None, None], [None, None]]
    line = Zone(9, 0, 2, None, None)
    leg_e = None
    keys = [None, None, None]
    acc = [None, None, None]
    B = {}
    A = {}
    Z = {}
    for ln in open(log):
        f = ln.strip().split(',')
        if f[0] == 'B':
            b = int(f[1])
            B[b] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]))
        elif f[0] == 'Z':
            Z.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6]), int(f[7]), int(f[8])))
        else:
            A.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6])))
    na = lambda v: v is None or abs(v) > 1e299

    def add(j, d, kind, top, bot, t0):
        same = [z for z in zones if z.tf == j and z.d == d]
        if len(same) >= 10: zones.remove(same[0])
        if len(zones) >= 60: zones.pop(0)
        zones.append(Zone(j, d, kind, top, bot, t0))

    def candle(j, o, h, l, c, t):
        for z in [z for z in zones if z.tf == j]:
            if (c < z.bot) if z.d == 1 else (c > z.top): zones.remove(z)
        cs = candles[j]
        cs.insert(0, (o, h, l, c, t))
        del cs[6:]
        if len(cs) < 3: return
        for a, d in ((0, 1), (1, -1)):
            if not ((cs[0][2] > cs[2][1]) if d == 1 else (cs[0][1] < cs[2][2])): continue
            if P['fvg']:
                if d == 1: add(j, 1, 1, cs[0][2], cs[2][1], cs[2][4])
                else: add(j, -1, 1, cs[2][2], cs[0][1], cs[2][4])
            if not P['ob']: continue
            for k in (2, 3, 4):
                if k >= len(cs): break
                ok, hk, lk, ck, tk = cs[k]
                if (ck < ok) if d == 1 else (ck > ok):
                    if last_ob[j][a] != (hk, lk):
                        add(j, d, 0, hk, lk, tk)
                        last_ob[j][a] = (hk, lk)
                    break

    def tl_of(z):
        if z.kind == 1 and P['half']: return (z.top + z.bot) / 2.0
        return z.top if z.d == 1 else z.bot

    def step(z, tl, lo, hi, t):
        x = lo if z.d == 1 else hi
        if not z.tch:
            if z.q and ((x <= tl) if z.d == 1 else (x >= tl)):
                z.tch = True; z.frz = False; z.ext = x; z.tt = t
            return
        if z.spent: return
        if not z.frz:
            z.ext = min(z.ext, x) if z.d == 1 else max(z.ext, x)
            return
        if (x < z.ext) if z.d == 1 else (x > z.ext):
            if P['two']: z.frz = False; z.ext = x
            else: z.spent = True

    n = bad = calls = 0
    nbox = [0]
    cnt = {}
    for i in range(len(T)):
        if i not in B: continue
        t = int(T[i])
        for j in range(3):
            if not tfs[j]: continue
            k = (t + (10800 if eu_summer(t) else 7200)) // tfs[j] if (j == 0 and tfs[0] < 604800) else bkey(t, tfs[j])
            if k != keys[j]:
                if acc[j] is not None: candle(j, *acc[j])
                keys[j] = k
                acc[j] = [O[i], H[i], L[i], C[i], t]
            else:
                acc[j][1] = max(acc[j][1], H[i]); acc[j][2] = min(acc[j][2], L[i]); acc[j][3] = C[i]
        d, hO, hX, hE, cu, cd, bu, bd = B[i]
        hO = None if na(hO) else hO
        hX = None if na(hX) else hX
        if hE != leg_e:
            leg_e = hE
            for z in zones: z.clear()
            line.clear()
        Lz = ret_lvl(d, hX, hO, P['pct'])
        for z in zones:
            z.q = False
            if d == 0 or z.d != d or Lz is None or hO is None: continue
            tl = tl_of(z)
            if z.kind == 0: z.q = (z.bot <= Lz + e and z.top >= hO - e) if d == 1 else (z.top >= Lz - e and z.bot <= hO + e)
            else: z.q = (tl <= Lz + e and tl >= hO - e) if d == 1 else (tl >= Lz - e and tl <= hO + e)
            step(z, tl, L[i], H[i], t)
        line.d = d
        line.q = P['line'] and d != 0 and hO is not None
        if line.q: step(line, hO, L[i], H[i], t)
        def pick(dd):
            big = -1
            if P['big']:
                for z in zones:
                    if z.d == dd and z.q and not z.spent: big = max(big, z.tf)
            best = None
            for z in zones:
                if z.d != dd or not z.tch or z.spent: continue
                if P['big'] and z.tf != big: continue
                if best is None or z.tf > best.tf: best = z
            if best is not None: return (best.tf, best.kind, best.top, best.bot, best.t0)
            if P['line'] and line.d == dd and line.tch and not line.spent: return (9, 2, hO, hO, line.tt)
            return None
        for (dd, tf, kind, top, bot) in A.get(i, []):
            big = -1
            if P['big']:
                for z in zones:
                    if z.d == dd and z.q and not z.spent: big = max(big, z.tf)
            best = None
            for z in zones:
                if z.d != dd or not z.tch or z.spent: continue
                if P['big'] and z.tf != big: continue
                if best is None or z.tf > best.tf: best = z
            want = (best.tf, best.kind, best.top, best.bot) if best is not None else ((9, -1) if (P['line'] and line.d == dd and line.tch and not line.spent) else (-1, -1))
            got = (tf, kind, top, bot) if tf in (0, 1, 2) else (tf, kind)
            if len(want) == 4: same = got[:2] == want[:2] and abs(got[2] - want[2]) < 1e-6 and abs(got[3] - want[3]) < 1e-6
            else: same = got == want
            calls += 1
            key = 'none' if want[0] == -1 else ('line' if want[0] == 9 else 'tf%d %s' % (want[0], 'OB' if want[1] == 0 else 'FVG'))
            cnt[key] = cnt.get(key, 0) + 1
            if not same:
                bad += 1
                if bad <= 5: print('   bar %d (%s) d %d: python %s | core %s' % (i, datetime.datetime.utcfromtimestamp(t), dd, want, got))
        sU = (P['cho'] and cu) or (P['bos'] and bu)
        sD = (P['cho'] and cd) or (P['bos'] and bd)
        if d != 0 and ((d == 1 and sU) or (d == -1 and sD)):
            # the zone box: the zone this signal came from (before its visit is closed)
            want = pick(d)
            got = Z.get(i, [])
            if want is None: same = not got
            else:
                same = len(got) == 1 and got[0][0] == d and got[0][1:3] == want[:2] and abs(got[0][3] - want[2]) < 1e-6 and abs(got[0][4] - want[3]) < 1e-6 and got[0][5] == want[4] and got[0][6] == t
            calls += 1
            nbox[0] += 1 if want is not None else 0
            if not same:
                bad += 1
                if bad <= 5: print('   box bar %d (%s) d %d: python %s | core %s' % (i, datetime.datetime.utcfromtimestamp(t), d, want, got))
            for z in zones:
                if z.d == d and z.tch: z.frz = True
            if line.d == d and line.tch: line.frz = True
    cnt['boxes'] = nbox[0]
    zl = set(Z) - set(i for i in B if B[i][0] != 0)
    if zl:
        bad += len(zl); print('   box lines on bars without a higher timeframe direction:', sorted(zl)[:5])
    return calls, bad, cnt
