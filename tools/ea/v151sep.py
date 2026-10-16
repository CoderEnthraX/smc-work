# v15.1: the zone modes, the zone boxes, the last zone, the zones of an old leg, MSS and its confirmation worked out AGAIN in Python,
# separately from the EA core, and compared with every decision the core made. Input: the 1-minute bars and the harness log of the
# test hooks (extract.py, key znLog):
#   B,bar,htTrend,htLegStart,htLegExtreme,htEvents,choUp,choDn,bosUp,bosDn,legStartTime   every chart bar
#   A,bar,d,kind,n,zone,...      every zone count (kind 1 = a chart CHOCH / BOS, 2 = an MSS); zone = tf:kind:top:bottom:time or L
#   Z,bar,d,tf,kind,top,bottom,left,right,signals,last,leg     every zone box
#   L,bar,tf,kind,top,bottom,time  /  L,bar,-1                 the last zone when it changes
#   M,bar,d,swing,low,lowBar                                    an MSS
#   R,bar,side,d,kind,zones  W,bar,side,d,rule,low,anchor,firstFvgEdge,sl,fix  K,bar,side,d,sl,pullbackLow  F,bar,side,d
#   X,bar,side,d  E,bar,side,f|d                                the sides: armed, MSS waiting, confirmed, failed, zones all gone, ended
# Everything is done here from the bars alone (plus the higher timeframe values and the chart's CHOCH / BOS that the core logged):
# zone candles on the broker clock (a candle's close = the first bar of the next candle, like the harness), FVGs, order blocks (type 1
# / type 2 one per burst / to the swing), deaths, the zones made before a new leg, the leg's zone, touches, visits, liquidity, the
# biggest timeframe, the last zone, the CHOCH* line, the one-signal-per-visit rule, the chart swings / FVGs / MSS, the confirmation.
import datetime
from v15sep import eu_summer, bkey, up, ret_lvl

LNONE = -1


class Zone:
    def __init__(self, tf, d, kind, top, bot, t0, te):
        self.tf, self.d, self.kind, self.top, self.bot, self.t0, self.te = tf, d, kind, top, bot, t0, te
        self.n = 0
        self.tt = None
        self.clear()

    def clear(self):
        self.q = False; self.tch = False; self.frz = False; self.spent = False; self.ext = None; self.vs = 0

    def key(self):
        return (self.tf, self.kind, self.d, self.top, self.bot, self.t0)


def run(T, O, H, L, C, log, P, htf):
    """P: pct, big, ob, fvg, half, two, line, last, sw, ob2, cho, bos, mss, mssN, mssCf, mssSt, slBuf"""
    tick = 0.01
    e = tick / 2
    tfs = [htf, up(htf), 0]
    tfs[2] = up(tfs[1]) if tfs[1] else 0
    zones = []
    cands = [[], [], []]                  # newest first: (o, h, l, c, open time)
    seq = [0, 0, 0]
    fc = [[-100, -100], [-100, -100], [-100, -100]]
    last_ob = [[None, None], [None, None], [None, None]]
    line = Zone(9, 0, 2, None, None, None, None)
    leg_e = -1
    keys = [None, None, None]
    acc = [None, None, None]
    # the log
    B, A, Z, Lg, M, R, W, K, F, X, E = {}, {}, {}, {}, {}, [], {}, {}, {}, {}, {}
    for ln in open(log):
        f = ln.strip().split(',')
        t = f[0]
        if t == 'B': B[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10]))
        elif t == 'A':
            zs = []
            for x in f[5:]:
                if x == 'L': zs.append('L')
                else:
                    g = x.split(':'); zs.append((int(g[0]), int(g[1]), float(g[2]), float(g[3]), int(g[4])))
            A.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), zs))
        elif t == 'Z': Z.setdefault(int(f[1]), []).append((int(f[2]), int(f[3]), int(f[4]), float(f[5]), float(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10]), int(f[11])))
        elif t == 'L': Lg[int(f[1])] = None if f[2] == '-1' else (int(f[2]), int(f[3]), float(f[4]), float(f[5]), int(f[6]))
        elif t == 'M': M[int(f[1])] = (int(f[2]), float(f[3]), float(f[4]), int(f[5]))
        elif t == 'R': R.append((int(f[1]), int(f[2]), int(f[3]), int(f[4]), int(f[5]), int(f[6])))
        elif t == 'W': W[(int(f[2]), int(f[3]))] = (int(f[1]), int(f[4]), int(f[5]), float(f[6]), float(f[7]), float(f[8]), float(f[9]), float(f[10]))
        elif t == 'K': K[(int(f[2]), int(f[3]))] = (int(f[1]), int(f[4]), float(f[5]), float(f[6]))
        elif t == 'F': F[(int(f[2]), int(f[3]))] = int(f[1])
        elif t == 'X': X[(int(f[2]), int(f[3]))] = int(f[1])
        elif t == 'E': E.setdefault((int(f[2]), int(f[3])), int(f[1]))
    na = lambda v: v is None or abs(v) > 1e299
    gone = set()                          # the zones gone on this bar
    gone_at = {}                          # bar -> the zones gone on it (for the setups' zones)

    def add(j, d, kind, top, bot, t0, te):
        same = [z for z in zones if z.tf == j and z.d == d]
        if len(same) >= 10: zones.remove(same[0])
        if len(zones) >= 60: zones.pop(0)
        zones.append(Zone(j, d, kind, top, bot, t0, te))

    def candle(j, o, h, l, c, t0, te):
        for z in [z for z in zones if z.tf == j]:
            if (c < z.bot) if z.d == 1 else (c > z.top):
                gone.add(z.key()); zones.remove(z)
        cs = cands[j]
        cs.insert(0, (o, h, l, c, t0))
        del cs[6:]
        seq[j] += 1
        if len(cs) < 3: return
        for a, d in ((0, 1), (1, -1)):
            if not ((cs[0][2] > cs[2][1]) if d == 1 else (cs[0][1] < cs[2][2])): continue
            c1 = seq[j] - 2
            burst = fc[j][a] <= c1 <= fc[j][a] + 2
            fc[j][a] = c1
            if P['fvg']:
                if d == 1: add(j, 1, 1, cs[0][2], cs[2][1], cs[2][4], te)
                else: add(j, -1, 1, cs[2][2], cs[0][1], cs[2][4], te)
            if not P['ob']: continue
            kb = None
            if P['ob2']:
                if not burst: kb = 2
            else:
                for k in (2, 3, 4):
                    if k >= len(cs): break
                    if (cs[k][3] < cs[k][0]) if d == 1 else (cs[k][3] > cs[k][0]): kb = k; break
            if kb is None: continue
            if not P['ob2'] and last_ob[j][a] == cs[kb][4]: continue
            tp, bt = cs[kb][1], cs[kb][2]
            if P['sw']:
                for k in range(kb):
                    if d == 1: bt = min(bt, cs[k][2])
                    else: tp = max(tp, cs[k][1])
            add(j, d, 0, tp, bt, cs[kb][4], te)
            last_ob[j][a] = cs[kb][4]

    def tl_of(z):
        if z.kind == 1 and P['half']: return (z.top + z.bot) / 2.0
        return z.top if z.d == 1 else z.bot

    def step(z, tl, lo, hi, t):
        x = lo if z.d == 1 else hi
        if not z.tch:
            if z.q and ((x <= tl) if z.d == 1 else (x >= tl)):
                z.tch = True; z.frz = False; z.ext = x; z.tt = t; z.vs = 0
            return
        if z.spent: return
        if not z.frz:
            z.ext = min(z.ext, x) if z.d == 1 else max(z.ext, x)
            return
        if (x < z.ext) if z.d == 1 else (x > z.ext):
            if P['two']: z.frz = False; z.ext = x; z.vs = 0
            else: z.spent = True

    def last_zone(d):
        best = None
        if d == 0: return None
        for z in zones:
            if z.d != d or z.kind != 0 or not z.q or z.spent: continue
            if best is None or z.tf > best.tf or (z.tf == best.tf and ((z.bot < best.bot) if d == 1 else (z.top > best.top))): best = z
        return best

    def count(d, kind):
        big = -1
        if P['big'] and not P['last']:
            for z in zones:
                if z.d == d and z.q and not z.spent: big = max(big, z.tf)
        lz = last_zone(d) if P['last'] else None
        out = []
        for z in zones:
            if z.d != d or not z.tch or z.spent: continue
            if (z.vs == 2) if kind == 1 else (z.vs != 0): continue
            if P['last']:
                if z is not lz: continue
            elif P['big'] and z.tf != big: continue
            out.append(z)
        if not out and P['line'] and line.d == d and line.tch and not line.spent and ((line.vs != 2) if kind == 1 else (line.vs == 0)): out.append('L')
        return out

    def freeze(d, kind):
        for z in zones:
            if z.d == d and z.tch:
                z.frz = True
                if z.vs == 0: z.vs = kind
        if line.d == d and line.tch:
            line.frz = True
            if line.vs == 0: line.vs = kind

    # the chart's FVGs with their order block and its swings (MSS)
    mf = [[], []]                         # (candle 1 bar, near edge)
    sw = [None, None]
    swb = [None, None]
    buf_sz = 0
    st = dict(calls=0, bad=0, boxes=0, mss=0, last=0, conf=0, fail=0, gone=0, armed=0)
    bad = [0]
    arm = {}                              # (side, setup) -> (armed bar, d, kind, its zones, its MSS)
    fv_at = {}                            # bar -> {side: candle 1 bar} of a chart FVG with its order block completed on it
    lz_prev = None
    predM = {}

    def bump(msg):
        bad[0] += 1
        if bad[0] <= 8: print('   ' + msg)

    def zt(z, hO):
        return ('L',) if z == 'L' else (z.tf, z.kind, z.top, z.bot, z.t0)

    def same_list(got, want):
        if len(got) != len(want): return False
        for g, w in zip(got, want):
            if g == 'L' or w == ('L',):
                if not (g == 'L' and w == ('L',)): return False
                continue
            if g[0] != w[0] or g[1] != w[1] or abs(g[2] - w[2]) > 1e-7 or abs(g[3] - w[3]) > 1e-7 or g[4] != w[4]: return False
        return True

    for i in range(len(T)):
        if i not in B: continue
        t = int(T[i])
        buf_sz += 1
        if buf_sz > 5150: buf_sz = 4900
        gone = set()
        for j in range(3):
            if not tfs[j]: continue
            k = (t + (10800 if eu_summer(t) else 7200)) // tfs[j] if (j == 0 and tfs[0] < 604800) else bkey(t, tfs[j])
            if k != keys[j]:
                if acc[j] is not None: candle(j, acc[j][0], acc[j][1], acc[j][2], acc[j][3], acc[j][4], t)
                keys[j] = k
                acc[j] = [O[i], H[i], L[i], C[i], t]
            else:
                acc[j][1] = max(acc[j][1], H[i]); acc[j][2] = min(acc[j][2], L[i]); acc[j][3] = C[i]
        d, hO, hX, hE, cu, cd, bu, bd, hS = B[i]
        hO = None if na(hO) else hO
        hX = None if na(hX) else hX
        if hE != leg_e:
            if leg_e >= 0: gone.add((9, 2, 0, 0.0, 0.0, leg_e))
            if hS != LNONE:
                for z in [z for z in zones if z.te <= hS]:
                    gone.add(z.key()); zones.remove(z)
            leg_e = hE
            for z in zones: z.clear()
            line.clear(); line.n = 0
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
        lz = last_zone(d)
        # the last zone when it changes
        if lz is not lz_prev:
            want = None if lz is None else (lz.tf, lz.kind, lz.top, lz.bot, lz.t0)
            got = Lg.get(i, 'none')
            st['last'] += 1
            if got == 'none' or (want is None) != (got is None) or (want is not None and not same_list([got], [want])):
                bump('last zone bar %d: python %s | core %s' % (i, want, got))
        elif i in Lg:
            bump('last zone bar %d: core logged %s, python has no change' % (i, Lg[i]))
        lz_prev = lz
        # the chart: FVGs with their order block, swings, the MSS
        msU = msD = False
        mnew = [False, False]
        if P['mss']:
            for a, dd in ((0, 1), (1, -1)):
                if i < 2 or not ((L[i] > H[i - 2]) if dd == 1 else (H[i] < L[i - 2])): continue
                ob = P['ob2']
                for k in (2, 3, 4):
                    if ob or i - k < 0: break
                    if (C[i - k] < O[i - k]) if dd == 1 else (C[i - k] > O[i - k]): ob = True
                if ob:
                    mf[a].append((i - 2, L[i] if dd == 1 else H[i])); mnew[a] = True
                    fv_at.setdefault(i, {})[a] = i - 2
            N = P['mssN']
            if i >= 2 * N:
                c = i - N
                if all(H[j] < H[c] for j in range(i - 2 * N, i + 1) if j != c): sw[0] = H[c]; swb[0] = c
                if all(L[j] > L[c] for j in range(i - 2 * N, i + 1) if j != c): sw[1] = L[c]; swb[1] = c
            sU = (P['cho'] and cu) or (P['bos'] and bu)
            sD = (P['cho'] and cd) or (P['bos'] and bd)
            for a, dd in ((0, 1), (1, -1)):
                if sw[a] is None or not ((C[i] > sw[a]) if dd == 1 else (C[i] < sw[a])): continue
                piv, pb = sw[a], swb[a]
                sw[a] = None
                if dd != d or sU or sD: continue
                j0 = max(pb, i - buf_sz + 1)
                lp, lb = None, None
                for j in range(j0, i + 1):
                    v = L[j] if dd == 1 else H[j]
                    if lp is None or ((v <= lp) if dd == 1 else (v >= lp)): lp, lb = v, j
                if not mf[a] or mf[a][-1][0] < lb: continue
                if not count(dd, 2): continue
                if dd == 1: msU = True
                else: msD = True
                predM[i] = (dd, piv, lp, lb)
        # the MSS
        if i in predM or i in M:
            st['mss'] += 1
            w, g = predM.get(i), M.get(i)
            if w is None or g is None or w[0] != g[0] or abs(w[1] - g[1]) > 1e-7 or abs(w[2] - g[2]) > 1e-7 or w[3] != g[3]:
                bump('MSS bar %d: python %s | core %s' % (i, w, g))
        # every zone count the core made on this bar
        for (dd, kind, n, zs) in A.get(i, []):
            want = [zt(z, hO) for z in count(dd, kind)]
            st['calls'] += 1
            if not same_list(zs, want): bump('count bar %d d %d kind %d: python %s | core %s' % (i, dd, kind, want, zs))
        # the setups armed on this bar: their zones (for 'all gone'), the MSS they came from
        for (rb, side, sq, dd, kind, nz) in R:
            if rb != i: continue
            ks = set(('L', leg_e) if z == 'L' else z.key() for z in count(dd, kind))
            st['armed'] += 1
            if len(ks) != nz: bump('arming bar %d side %d: python %d zones | core %d' % (i, side, len(ks), nz))
            arm[(side, sq)] = (i, dd, kind, ks, predM.get(i))
        # the boxes + closing the visits
        sU = (P['cho'] and cu) or (P['bos'] and bu)
        sD = (P['cho'] and cd) or (P['bos'] and bd)
        wantZ = []
        if d != 0:
            kind = 1 if ((d == 1 and sU) or (d == -1 and sD)) else (2 if (msU or msD) else 0)
            if kind:
                for z in count(d, kind):
                    if z == 'L':
                        line.n += 1
                        wantZ.append((d, 9, 2, hO, hO, line.tt, t, line.n, 0, leg_e))
                    else:
                        z.n += 1
                        wantZ.append((d, z.tf, z.kind, z.top, z.bot, z.t0, t, z.n, 1 if z is lz else 0, 0))
                freeze(d, kind)
        got = Z.get(i, [])
        if wantZ or got:
            st['boxes'] += len(wantZ)
            okz = len(got) == len(wantZ) and all(g[:3] == w[:3] and abs(g[3] - w[3]) < 1e-7 and abs(g[4] - w[4]) < 1e-7 and g[5:] == w[5:] for g, w in zip(got, wantZ))
            if not okz: bump('boxes bar %d: python %s | core %s' % (i, wantZ, got))
        gone_at[i] = set(gone)
        # gone tuples of the line use ('L', leg)
        if any(g[0] == 9 for g in gone): gone_at[i].add(('L', [g for g in gone if g[0] == 9][0][5]))
    # a waiting setup whose zones are ALL gone (broken by a close / a new leg): the core's X lines
    n = len(T)
    for (side, sq), (ra, dd, kind, ks, ms) in arm.items():
        if not ks: continue
        e = E.get((side, sq))
        left = set(ks)
        p = None
        for b in range(ra + 1, n if e is None else e + 1):
            g = gone_at.get(b)
            if g: left -= g
            if not left: p = b; break
        x = X.get((side, sq))
        st['gone'] += 1 if x is not None else 0
        if x is not None:
            if p != x: bump('zones gone side %d setup %d: python bar %s | core bar %s' % (side, sq, p, x))
        elif p is not None and (e is None or p < e):
            bump('zones gone side %d setup %d: python bar %s, the core kept it to bar %s' % (side, sq, p, e))
    # an MSS waiting for its confirmation: failed (the price beyond the MSS low / high) or confirmed (a pullback to the first FVG of the
    # MSS move, then a NEW chart FVG with its order block whose candle 1 is at or after the pullback candle) - the stop
    for (side, sq), (ra, dd, rule, low, anch, cft, sl, fix) in W.items():
        a = arm.get((side, sq))
        ms = a[4] if a else None
        if ms is None or abs(ms[2] - low) > 1e-7: bump('MSS setup side %d %d: armed without its MSS (%s, low %s)' % (side, sq, ms, low)); continue
        lb = ms[3]
        aa = 0 if dd == 1 else 1
        first = [fv for fv in mf[aa] if fv[0] >= lb]
        want_top = min(first)[1] if first else None
        hi = max(H[lb:ra + 1]) if dd == 1 else min(L[lb:ra + 1])
        if rule == 4 and (want_top is None or abs(want_top - cft) > 1e-7 or abs(hi - anch) > 1e-7):
            bump('MSS setup side %d %d: first FVG edge / extreme python %s %s | core %s %s' % (side, sq, want_top, hi, cft, anch)); continue
        if rule != 4: continue
        e = E.get((side, sq))
        cf, tch, pb, pred = 1, None, None, None
        for b in range(ra + 1, n if e is None else e + 1):
            if (L[b] < low) if dd == 1 else (H[b] > low): pred = ('F', b, None); break
            pb = (L[b] if pb is None else min(pb, L[b])) if dd == 1 else (H[b] if pb is None else max(pb, H[b]))
            fa = fv_at.get(b, {})
            if cf == 2 and aa in fa and fa[aa] >= tch:
                lv = pb if P['mssSt'] == 1 else low
                pred = ('K', b, lv - P['slBuf'] if dd == 1 else lv + P['slBuf']); break
            if cf == 1 and ((L[b] <= cft) if dd == 1 else (H[b] >= cft)): cf, tch = 2, b
        k_, f_ = K.get((side, sq)), F.get((side, sq))
        if k_ is not None:
            st['conf'] += 1
            if pred is None or pred[0] != 'K' or pred[1] != k_[0] or abs(pred[2] - k_[2]) > 1e-7: bump('MSS confirmation side %d %d: python %s | core bar %d stop %.2f' % (side, sq, pred, k_[0], k_[2]))
        elif f_ is not None:
            st['fail'] += 1
            if pred is None or pred[0] != 'F' or pred[1] != f_: bump('MSS failed side %d %d: python %s | core bar %d' % (side, sq, pred, f_))
        elif pred is not None and (e is None or pred[1] < e):
            bump('MSS setup side %d %d: python %s, the core kept waiting to bar %s' % (side, sq, pred, e))
    return st, bad[0]
