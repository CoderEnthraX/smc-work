# Python port of SMC Structure Strategy v8.3 (main tier + 15m HTF + strategy + TradingView broker emulator)
# plus switches for the v9.0 ideas. One run = one strategy instance on 1m bars (UTC epoch seconds).
import math

IST = 19800  # +05:30

DEF = dict(
    sig="CHOCH", r1=True, r2=True, pb=50.0, rr=3.0, slbuf=0.0, rev=True, once=False,
    hrOn=6, hrOff=23, hrFlat=2, wkFlat=True, wkDow=4, wkHr=21,  # wkDow python weekday (Fri=4)
    risk=50.0, cmU=0.6, comm=0.3, unit=1.0, rndMax=25.0, lev=30.0, cmTgt=True, eq0=10000.0,
    cancelSig=True, expBars=0, minStop=0.0, maxStop=0.0, maxTrades=0, dayLoss=0.0, maxOpen=0,
    mvStep=False, mvBe=False,
    # v11.2: stop buffer unit - "Price" (as before) / "Pips" / "Pct"; pip = the pip of the market; tick = the smallest price step
    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,
    # v8.4 / v9.0
    direction="Both",          # Both / Longs / Shorts
    bosRiskPct=100.0,          # a: risk % for stacked BOS trades
    htfFilt=False,             # b: every trade must follow the HTF trend
    trail="Off",               # c: Off / Swing / Level
    trailBuf=None,
    liqTgt=False, liqMinR=1.0, liqMaxR=0.0,  # d
    partOn=False, partPct=50.0, partR=1.0, partBe=True,  # e
    pdOn=False, pdPct=50.0,    # f
    lossN=0,                   # g
    sess2=None,                # list of (fromMin, toMin) IST entry windows (London+NY test), None = normal
    htfTf=900,
    bosMode="Follow",
    seqMode="Off", seqAdd=50.0, split=1.0, flMode="Off", flAmt=2000.0, flLock=50.0, flPct=2.5, fav=False, agn=False, auto=False, ldOn=False, ldN=3, ldD=2, ldAll=False, eqOn=False, eqPct=50.0, seqMax=500.0, capAct="Perm", liveT=None,  # liveT: epoch s of the first counted close (None = whole history)   # seqMode Off / A91 / A90 / B ; capAct Clamp / Day / Perm          # Follow (v8.3) / Cancel / Freeze : a same-side BOS before the CHOCH order fills
)


class Trk:
    __slots__ = ("isHigh", "potential", "potentialBar", "count", "refLevel", "swept")

    def __init__(s, isHigh):
        s.isHigh = isHigh; s.potential = None; s.potentialBar = None; s.count = 0; s.refLevel = None; s.swept = False

    def update(s, o, h, l, c, bi):
        confP = confB = None
        pb = (c < o) if s.isHigh else (c > o)
        rf = l if s.isHigh else h
        newExt = s.potential is None or (h >= s.potential if s.isHigh else l <= s.potential)
        if newExt:
            s.potential = h if s.isHigh else l; s.potentialBar = bi
            s.count = 1 if pb else 0; s.refLevel = rf if pb else None; s.swept = False
        elif pb:
            beyond = s.refLevel is not None and (c < s.refLevel if s.isHigh else c > s.refLevel)
            if s.count == 0:
                s.count = 1; s.refLevel = rf
            elif s.count == 1 and beyond:
                s.count = 2; s.refLevel = rf
            elif s.count == 2 and beyond:
                confP = s.potential; confB = s.potentialBar
                s.potential = h if s.isHigh else l; s.potentialBar = bi
                s.count = 1; s.refLevel = rf; s.swept = False
        return confP, confB


class SL:
    __slots__ = ("price", "x1", "sid", "born", "swpP", "swpB", "refP", "swpT")

    def __init__(s, p, b, sid, born):
        s.price = p; s.x1 = b; s.sid = sid; s.born = born; s.swpP = None; s.swpB = None; s.refP = None; s.swpT = False


class Engine:
    """main-tier structure: trendDir, ceilS, florS, CHOCH/BOS events, mRunHi/Lo"""

    def __init__(s):
        s.bufHi = []; s.bufLo = []
        s.allHi = s.allLo = None
        s.hiT = Trk(True); s.loT = Trk(False)
        s.mnHiB = []; s.mnLoB = []
        s.trendDir = 0; s.ceilS = None; s.florS = None
        s.mRunHi = s.mRunLo = None
        # v9: unswept swing highs/lows (liquidity) and last confirmed swings
        s.liqHi = []; s.liqLo = []
        s.lastPh = None; s.lastPl = None

    def _retExt(s, bi, fromBar, findHigh, inc):
        sz = len(s.bufLo); jEnd = sz - 1
        p = b = None
        if (jEnd >= 0) if inc else (jEnd > 0):
            j0 = max(0, min(fromBar - bi + sz, jEnd if inc else jEnd - 1))
            src = s.bufHi if findHigh else s.bufLo
            base = bi - sz + 1
            last = jEnd if inc else jEnd - 1
            for j in range(j0, last + 1):
                v = src[j]
                if p is None or (v >= p if findHigh else v <= p):
                    p = v; b = base + j
        return p, b

    @staticmethod
    def _swpConf(arrB, swpB):
        if swpB is None:
            return False
        for cb in reversed(arrB):
            if cb == swpB:
                return True
            if cb < swpB:
                return False
        return False

    def step(s, bi, o, h, l, c):
        s.bufHi.append(h); s.bufLo.append(l)
        if len(s.bufHi) > 5150:
            s.bufHi = s.bufHi[-4900:]; s.bufLo = s.bufLo[-4900:]
        s.allHi = h if s.allHi is None else max(s.allHi, h)
        s.allLo = l if s.allLo is None else min(s.allLo, l)
        phP, phB = s.hiT.update(o, h, l, c, bi)
        plP, plB = s.loT.update(o, h, l, c, bi)
        if phP is not None:
            s.mnHiB.append(phB)
            if len(s.mnHiB) > 300: s.mnHiB.pop(0)
        if plP is not None:
            s.mnLoB.append(plB)
            if len(s.mnLoB) > 300: s.mnLoB.pop(0)
        evBU = evBD = evCU = evCD = False
        td = s.trendDir
        if phP is not None:
            cs = s.ceilS
            cSw = cs is not None and cs.swpP is not None
            cEq = cs is not None and phP == cs.price
            adopt = (phP >= s.allHi and not cSw and not cEq) if td == 0 else cs is None
            if adopt:
                s.ceilS = SL(phP, phB, 2 if td == -1 else 0, bi)
        if plP is not None:
            fs = s.florS
            fSw = fs is not None and fs.swpP is not None
            fEq = fs is not None and plP == fs.price
            adopt = (plP <= s.allLo and not fSw and not fEq) if td == 0 else fs is None
            if adopt:
                s.florS = SL(plP, plB, 3 if td == 1 else 1, bi)
        cs = s.ceilS
        if cs is not None and bi > cs.born:
            if c > cs.price:
                isCho = s.trendDir == -1
                evCU = isCho; evBU = not isCho
                rp, rb = s._retExt(bi, cs.x1, False, True)
                if rp is not None:
                    s.florS = SL(rp, rb, 3, bi)
                s.trendDir = 1; s.ceilS = None
            else:
                if h > cs.price:
                    if cs.swpP is None or h > cs.swpP:
                        cs.swpP = h; cs.swpB = bi; cs.swpT = False
                if cs.swpP is not None and cs.refP is None:
                    cs.refP = s._retExt(bi, cs.x1, False, False)[0]
                if cs.swpB is not None and cs.swpB == bi and s.trendDir == 1 and cs.refP is not None and l < cs.refP:
                    cs.swpT = True
                if s.trendDir == 1 and cs.swpP is not None and cs.refP is not None and l < cs.refP and (not cs.swpT or s._swpConf(s.mnHiB, cs.swpB)):
                    s.ceilS = SL(cs.swpP, cs.x1, cs.sid, bi)
        fs = s.florS
        if fs is not None and bi > fs.born:
            if c < fs.price:
                isCho = s.trendDir == 1
                evCD = isCho; evBD = not isCho
                rp, rb = s._retExt(bi, fs.x1, True, True)
                if rp is not None:
                    s.ceilS = SL(rp, rb, 2, bi)
                s.trendDir = -1; s.florS = None
            else:
                if l < fs.price:
                    if fs.swpP is None or l < fs.swpP:
                        fs.swpP = l; fs.swpB = bi; fs.swpT = False
                if fs.swpP is not None and fs.refP is None:
                    fs.refP = s._retExt(bi, fs.x1, True, False)[0]
                if fs.swpB is not None and fs.swpB == bi and s.trendDir == -1 and fs.refP is not None and h > fs.refP:
                    fs.swpT = True
                if s.trendDir == -1 and fs.swpP is not None and fs.refP is not None and h > fs.refP and (not fs.swpT or s._swpConf(s.mnLoB, fs.swpB)):
                    s.florS = SL(fs.swpP, fs.x1, fs.sid, bi)
        ev = evBU or evBD or evCU or evCD
        if ev:
            s.mRunHi = h; s.mRunLo = l
        else:
            s.mRunHi = h if s.mRunHi is None else max(s.mRunHi, h)
            s.mRunLo = l if s.mRunLo is None else min(s.mRunLo, l)
        # v9 liquidity pools: confirmed swing highs / lows not yet traded through
        if phP is not None:
            s.liqHi.append(phP); s.lastPh = phP
            if len(s.liqHi) > 60: s.liqHi.pop(0)
        if plP is not None:
            s.liqLo.append(plP); s.lastPl = plP
            if len(s.liqLo) > 60: s.liqLo.pop(0)
        if s.liqHi:
            s.liqHi = [p for p in s.liqHi if p > h]
        if s.liqLo:
            s.liqLo = [p for p in s.liqLo if p < l]
        s.newPh = phP; s.newPl = plP
        return evBU, evBD, evCU, evCD

    def anchors(s):
        mA = mO = None
        if s.trendDir == 1:
            mA = s.mRunHi; mO = s.mRunLo
            if s.florS is not None: mO = s.florS.price
        elif s.trendDir == -1:
            mA = s.mRunLo; mO = s.mRunHi
            if s.ceilS is not None: mO = s.ceilS.price
        return mA, mO


def retLvl(d, anch, orig, pct):
    if d == 1 and anch is not None and orig is not None and anch > orig:
        return anch - (anch - orig) * pct / 100.0
    if d == -1 and anch is not None and orig is not None and orig > anch:
        return anch + (orig - anch) * pct / 100.0
    return None


class HTF:
    def __init__(s):
        s.tkHi = Trk(True); s.tkLo = Trk(False)
        s.tAllHi = s.tAllLo = s.tRunLo = s.tRunHi = None
        s.tCeil = s.tCeilB = s.tFlor = s.tFlorB = None
        s.tTrend = 0; s.evN = 0

    def step(s, bi, o, h, l, c):
        s.tAllHi = h if s.tAllHi is None else max(s.tAllHi, h)
        s.tAllLo = l if s.tAllLo is None else min(s.tAllLo, l)
        s.tRunLo = l if s.tRunLo is None else min(s.tRunLo, l)
        s.tRunHi = h if s.tRunHi is None else max(s.tRunHi, h)
        cfH, _ = s.tkHi.update(o, h, l, c, bi)
        cfL, _ = s.tkLo.update(o, h, l, c, bi)
        if cfH is not None:
            ad = cfH >= s.tAllHi if s.tTrend == 0 else s.tCeil is None
            if ad or (s.tCeil is not None and cfH == s.tCeil):
                s.tCeil = cfH; s.tCeilB = bi; s.tRunLo = l
        if cfL is not None:
            ad = cfL <= s.tAllLo if s.tTrend == 0 else s.tFlor is None
            if ad or (s.tFlor is not None and cfL == s.tFlor):
                s.tFlor = cfL; s.tFlorB = bi; s.tRunHi = h
        if s.tCeil is not None and s.tCeilB is not None and bi > s.tCeilB and c > s.tCeil:
            s.tTrend = 1; s.tFlor = s.tRunLo; s.tFlorB = bi; s.tRunHi = h; s.tCeil = None; s.tCeilB = None; s.evN += 1
        elif s.tFlor is not None and s.tFlorB is not None and bi > s.tFlorB and c < s.tFlor:
            s.tTrend = -1; s.tCeil = s.tRunHi; s.tCeilB = bi; s.tRunLo = l; s.tFlor = None; s.tFlorB = None; s.evN += 1
        if s.tTrend == 1:
            lo, lx = (s.tFlor if s.tFlor is not None else s.tRunLo), s.tRunHi
        elif s.tTrend == -1:
            lo, lx = (s.tCeil if s.tCeil is not None else s.tRunHi), s.tRunLo
        else:
            lo = lx = None
        return (s.tTrend, lo, lx, s.evN)


def htf_series(bars, tf):
    """stT15 for every 1m bar: trend of the last CLOSED HTF bar (request.security lookahead_on + [1])"""
    keys = []; agg = []
    for t, o, h, l, c in bars:
        k = t // tf
        if not keys or keys[-1] != k:
            keys.append(k); agg.append([o, h, l, c])
        else:
            a = agg[-1]; a[1] = max(a[1], h); a[2] = min(a[2], l); a[3] = c
    e = HTF(); tr = []
    for i, (o, h, l, c) in enumerate(agg):
        tr.append(e.step(i, o, h, l, c))
    pos = {k: i for i, k in enumerate(keys)}
    out = []
    for t, *_ in bars:
        i = pos[t // tf]
        out.append(tr[i - 1] if i > 0 else (0, None, None, 0))
    return out


class Tr:
    __slots__ = ("id", "dir", "ep", "q", "ebar", "sl", "tgt", "xp", "xbar", "why", "pnl", "r0", "be", "step", "mv",
                 "mfe", "mae", "ent_t", "grp", "piece", "lsl")

    def __init__(s, **k):
        for a in s.__slots__: setattr(s, a, k.get(a))


def buf_at(p, lv):
    """v11.2: the stop buffer beyond the level lv, in price (Pine f_stBuf; math.round_to_mintick = nearest step, ties up)"""
    if p["buMode"] == "Pips": return math.floor(p["buPips"] * p["pip"] / p["tick"] + 0.5) * p["tick"]
    if p["buMode"] == "Pct": return math.floor(lv * p["buPct"] / 100.0 / p["tick"] + 0.5) * p["tick"]
    return p["slbuf"]


def lim_at(p, v, ent):
    """v11.2: a group 24 limit (skip closer / further than) in price - pips, or % of the entry price"""
    if p["buMode"] == "Pips": return v * p["pip"]
    if p["buMode"] == "Pct": return ent * v / 100.0
    return v


def run(bars, P=None, htf=None, log=False):
    p = dict(DEF)
    if P: p.update(P)
    if htf is None:
        htf = htf_series(bars, p["htfTf"])
    E = Engine()
    rr = p["rr"]; cmU = p["cmU"]; comm = p["comm"]
    cmPx = cmU * (rr + 1.0) if p["cmTgt"] else 0.0
    useCho = p["sig"] != "BOS"; useBos = p["sig"] != "CHOCH"; favMode = p["fav"]; agnMode = p["agn"]; autoMode = p["auto"]
    # broker state
    pend = {}      # id -> dict(dir, lim, q, sl, tgt, grp, piece)
    opn = []       # open Tr
    closed = []
    closeReq = {}  # id -> reason (market close at next open)
    eq_closed = p["eq0"]
    # script state
    stDir = 0; stRule = 0; stSl = None; stFix = None; stPend = []; stOrdLive = False
    stLast = None  # (ent, sl, tgt, q)
    stSeq = 0; stPlaced = False; stEntLock = None; stArmBar = None
    stCeilPrev = stFlorPrev = None
    stDayTrades = 0; stDayPnl = 0.0; stDayHalt = False; stLossRun = 0
    deadPrev = False; wkPrev = False; prevDay = None
    stAddRisk = 1.0
    stBosSeen = False; frozen = None; bosFill = {}
    seqLoss = 0.0; seqHalt = False; seqCapOn = False; seqLog = []; seqTot = 0.0; flPnl = 0.0; flPeak = 0.0
    ldRun = 0; ldUntil = None; ldLog = []; eqOpen = False; prevE = None; eqLog = []
    plus = p["seqMode"] in ("A+", "B+", "C+")
    car = lambda: max(0.0, -seqTot) if plus else seqLoss
    nClosedSeen = 0; entSeen = -1
    stLastSl = None; stLastTgt = None
    trk = []       # managed open trades (stop moves / trailing / partial BE)
    cnt = dict(arm=0, fill=0, canc=0, skip=0, pdSkip=0, dirSkip=0, htfSkip=0, lossHalt=0)
    kmax = max(0, int(math.ceil(rr - 1e-9)) - 1)
    sess2 = p["sess2"]

    def fill_close(tr, px, bi, why):
        nonlocal eq_closed
        tr.xp = px; tr.xbar = bi; tr.why = why
        tr.pnl = (px - tr.ep) * tr.dir * tr.q - 2 * comm * tr.q
        eq_closed += tr.pnl
        opn.remove(tr); closed.append(tr)

    for bi, (t, o, h, l, c) in enumerate(bars):
        # ---------------- broker: orders sent at the previous close ----------------
        for tr in list(opn):
            if tr.id in closeReq:
                fill_close(tr, o, bi, closeReq[tr.id])
        closeReq = {}
        path = (o, h, l, c) if abs(h - o) < abs(o - l) else (o, l, h, c)
        cur = o

        def trig_at(price):
            # everything that fires at this exact price (gap at the open)
            fired = False
            for oid in list(pend):
                od = pend[oid]
                if (od["dir"] == 1 and price <= od["lim"]) or (od["dir"] == -1 and price >= od["lim"]):
                    do_fill(oid, price); fired = True
            for tr in list(opn):
                if tr.dir == 1 and tr.sl is not None and price <= tr.sl: fill_close(tr, price, bi, "SL"); fired = True
                elif tr.dir == 1 and tr.tgt is not None and price >= tr.tgt: fill_close(tr, price, bi, "TP"); fired = True
                elif tr.dir == -1 and tr.sl is not None and price >= tr.sl: fill_close(tr, price, bi, "SL"); fired = True
                elif tr.dir == -1 and tr.tgt is not None and price <= tr.tgt: fill_close(tr, price, bi, "TP"); fired = True
            return fired

        def do_fill(oid, price):
            od = pend.pop(oid)
            opn.append(Tr(id=oid, dir=od["dir"], ep=price, q=od["q"], ebar=bi, sl=od["sl"], tgt=od["tgt"], ent_t=t,
                          grp=od["grp"], piece=od["piece"], lsl=od["sl"], mfe=0.0, mae=0.0))

        trig_at(o)
        for seg in range(1, 4):
            a = cur; b = path[seg]
            while True:
                best = None
                if b < a:  # falling: buy limits, long stops, short targets fire at level in [b, a)
                    for oid, od in pend.items():
                        if od["dir"] == 1 and b <= od["lim"] < a and (best is None or od["lim"] > best[0]): best = (od["lim"], "E", oid)
                    for tr in opn:
                        if tr.dir == 1 and tr.sl is not None and b <= tr.sl < a and (best is None or tr.sl > best[0]): best = (tr.sl, "SL", tr)
                        if tr.dir == -1 and tr.tgt is not None and b <= tr.tgt < a and (best is None or tr.tgt > best[0]): best = (tr.tgt, "TP", tr)
                elif b > a:
                    for oid, od in pend.items():
                        if od["dir"] == -1 and a < od["lim"] <= b and (best is None or od["lim"] < best[0]): best = (od["lim"], "E", oid)
                    for tr in opn:
                        if tr.dir == 1 and tr.tgt is not None and a < tr.tgt <= b and (best is None or tr.tgt < best[0]): best = (tr.tgt, "TP", tr)
                        if tr.dir == -1 and tr.sl is not None and a < tr.sl <= b and (best is None or tr.sl < best[0]): best = (tr.sl, "SL", tr)
                if best is None:
                    break
                lv, kind, x = best
                if kind == "E":
                    do_fill(x, lv)
                    # a second piece at the same price fills too
                    for oid in list(pend):
                        if pend[oid]["lim"] == lv and pend[oid]["dir"] == (1 if b < a else -1): do_fill(oid, lv)
                    trig_at(lv)
                else:
                    fill_close(x, lv, bi, kind)
                a = lv
            cur = b
        for tr in opn:
            fav = (h - tr.ep) if tr.dir == 1 else (tr.ep - l)
            adv = (tr.ep - l) if tr.dir == 1 else (h - tr.ep)
            tr.mfe = max(tr.mfe, fav); tr.mae = max(tr.mae, adv)

        # ---------------- script at the bar close ----------------
        evBU, evBD, evCU, evCD = E.step(bi, o, h, l, c)
        trendDir = E.trendDir
        mA, mO = E.anchors()
        hT, hO, hX, hE = htf[bi]
        stT15 = hT if (p["r2"] or p["htfFilt"] or favMode or p["eqOn"] or agnMode or autoMode) else 0
        pos = sum(tr.dir * tr.q for tr in opn)
        tc = t + 60 + IST
        tM = (tc // 60) % 1440
        dow = ((tc // 86400) + 3) % 7   # python weekday of the close time (epoch day 0 = Thursday)
        stWin = (p["hrOn"] == p["hrOff"]) or ((tM - p["hrOn"] * 60) % 1440 < (p["hrOff"] - p["hrOn"]) * 60 % 1440)
        if sess2 is not None:
            stWin = any((tM - a0) % 1440 < (b0 - a0) % 1440 for a0, b0 in sess2)
        fa, fb = p["hrFlat"] * 60, p["hrOn"] * 60
        dead = ((tM - fa) % 1440 < (fb - fa) % 1440) if p["hrFlat"] != p["hrOn"] else tM == fa
        flatNow = dead and not deadPrev; deadPrev = dead
        dayk = (t + IST) // 86400
        newDay = prevDay is not None and dayk != prevDay; prevDay = dayk
        wkB = p["wkFlat"] and ((dow == p["wkDow"] and tM >= p["wkHr"] * 60) or dow == 5 or dow == 6)
        wkNow = wkB and not wkPrev; wkPrev = wkB
        if newDay:
            stDayTrades = 0; stDayPnl = 0.0; stDayHalt = False; stLossRun = 0
            if seqHalt and p["capAct"] == "Day":
                seqHalt = False; seqLoss = 0.0; seqCapOn = False; seqTot = 0.0

        # fills (v8.1 way: newest entry bar)
        newOpen = [tr for tr in opn if tr.ebar == bi]
        newAll = newOpen + [tr for tr in closed[nClosedSeen:] if tr.ebar == bi]
        if newAll:
            for tr in newAll: bosFill[tr.id] = stBosSeen
            stDir = 0; stPend = []; stOrdLive = False
            cnt["fill"] += 1; stDayTrades += 1
        for tr in newOpen:
            r0 = abs(tr.ep - tr.lsl)
            tr.r0 = r0; tr.be = tr.ep + tr.dir * cmU; tr.step = 0; tr.mv = False
            trk.append(tr)
        # closed trades accounting
        if len(closed) > nClosedSeen:
            ssum = sum(tr.pnl for tr in closed[nClosedSeen:] if p["liveT"] is None or bars[tr.ebar][0] >= p["liveT"])
            debt = seqLoss - ssum
            seqLoss = 0.0 if debt < 0.005 else debt
            seqTot += ssum
            flPnl += ssum; flPeak = max(flPeak, flPnl)
            if car() <= 0.005 and p["capAct"] != "Perm":
                seqHalt = False; seqCapOn = False
        for tr in closed[nClosedSeen:]:
            stDayPnl += tr.pnl
            if tr.piece != "p":
                stLossRun = stLossRun + 1 if tr.pnl < 0 else 0
                xt = bars[tr.xbar][0]
                if p["ldOn"] and (p["liveT"] is None or bars[tr.ebar][0] >= p["liveT"]) and not (ldUntil is not None and xt < ldUntil):
                    ldRun = ldRun + 1 if tr.pnl < 0 else (0 if tr.pnl > 0 else ldRun)
                    if ldRun >= p["ldN"]:
                        d0 = (xt + IST) // 86400; ldn = ldk = 0
                        while ldn < p["ldD"]:
                            ldk += 1
                            if p["ldAll"] or (d0 + ldk + 3) % 7 < 5: ldn += 1
                        ldUntil = (d0 + ldk + 1) * 86400 - IST; ldRun = 0; ldLog.append((tr.xbar, xt, ldUntil))
        nClosedSeen = len(closed)
        # managed trades: step / BE / trailing / partial BE
        trk = [tr for tr in trk if tr in opn]
        for tr in trk:
            if tr.r0 is None or tr.r0 <= 0: continue
            ns = tr.sl
            if (p["mvStep"] or p["mvBe"]) and kmax >= 1:
                k = tr.step
                if p["mvStep"]:
                    ref = c if bi == tr.ebar else (h if tr.dir == 1 else l)
                    got = math.floor((ref - tr.ep) * tr.dir / tr.r0)
                    k = max(tr.step, min(got, kmax))
                elif tr.step == 0 and (c >= tr.ep + tr.r0 if tr.dir == 1 else c <= tr.ep - tr.r0):
                    k = 1
                cc = tr.be if k == 1 else (max(tr.be, tr.ep + (k - 1) * tr.r0) if tr.dir == 1 else min(tr.be, tr.ep - (k - 1) * tr.r0))
                if k > tr.step and (cc < tr.ep + k * tr.r0 if tr.dir == 1 else cc > tr.ep - k * tr.r0):
                    ns = max(ns, cc) if tr.dir == 1 else min(ns, cc)
                    tr.step = k
            if p["trail"] != "Off" and bi > tr.ebar:
                lvl = None
                if p["trail"] == "Swing":
                    lvl = E.newPl if tr.dir == 1 else E.newPh
                elif p["trail"] == "Level":
                    lvl = (E.florS.price if E.florS is not None and trendDir == 1 else None) if tr.dir == 1 else \
                          (E.ceilS.price if E.ceilS is not None and trendDir == -1 else None)
                if lvl is not None:
                    tb = buf_at(p, lvl) if p["trailBuf"] is None else p["trailBuf"]
                    lv2 = lvl - tb if tr.dir == 1 else lvl + tb
                    if tr.dir == 1 and lv2 < c: ns = max(ns, lv2)
                    if tr.dir == -1 and lv2 > c: ns = min(ns, lv2)
            if p["partOn"] and p["partBe"] and tr.piece == "m":
                # the runner goes to break-even once its partner (piece p) closed at its target
                if any(x.grp == tr.grp and x.piece == "p" and x.why in ("TP", "SL") and x.pnl > 0 for x in closed[-8:]):
                    ns = max(ns, tr.be) if tr.dir == 1 else min(ns, tr.be)
            if ns != tr.sl:
                tr.sl = ns; tr.mv = True

        riskNow = p["risk"]
        if p["seqMode"] == "A91":
            riskNow = seqLoss + p["seqAdd"] if seqLoss > 0 else p["risk"]
        elif p["seqMode"] in ("A10", "A+"):
            riskNow = max(p["risk"], (car() + p["seqAdd"]) / p["split"]) if car() > 0.005 else p["risk"]
        elif p["seqMode"] in ("C", "C+"):
            riskNow = max(p["risk"], car() / p["split"]) if car() > 0.005 else p["risk"]
        elif p["seqMode"] == "B+":
            riskNow = max(p["risk"], 2.0 * car() / p["split"]) if car() > 0.005 else p["risk"]
        elif p["seqMode"] == "A90":
            riskNow = (seqLoss + p["risk"]) / max(rr, 0.1) if seqLoss > 0 else p["risk"]
        elif p["seqMode"] == "B":
            riskNow = max(p["risk"], 2.0 * seqLoss / p["split"]) if seqLoss > 0 else p["risk"]
        if p["seqMode"] != "Off" and p["flMode"] != "Size" and riskNow > p["seqMax"]:
            if not seqCapOn: seqCapOn = True
            riskNow = p["seqMax"]
            if p["capAct"] != "Clamp": seqHalt = True
        else:
            seqCapOn = False
        flFloor = -p["flAmt"] + p["flLock"] / 100.0 * flPeak
        flCush = max(0.0, flPnl - flFloor); flRisk = p["flPct"] / 100.0 * flCush
        if p["flMode"] == "Size": riskNow = flRisk
        elif p["flMode"] == "Cap": riskNow = min(riskNow, flRisk)
        if p["dayLoss"] > 0 and stDayPnl <= -p["dayLoss"]: stDayHalt = True
        if p["maxTrades"] > 0 and stDayTrades >= p["maxTrades"]: stDayHalt = True
        if p["lossN"] > 0 and stLossRun >= p["lossN"] and not stDayHalt:
            stDayHalt = True; cnt["lossHalt"] += 1
        ldHalt = p["ldOn"] and ldUntil is not None and t < ldUntil
        if prevE is not None and hE != prevE: eqOpen = False
        prevE = hE
        eqLvl = retLvl(stT15, hX, hO, p["eqPct"])
        if (p["eqOn"] or autoMode) and not eqOpen and eqLvl is not None and ((stT15 == 1 and l <= eqLvl) or (stT15 == -1 and h >= eqLvl)):
            eqOpen = True; eqLog.append((bi, eqLvl))
        eqBlock = p["eqOn"] and not autoMode and not eqOpen
        autoDir = (stT15 if eqOpen else -stT15) if autoMode else 0
        stGo = not stDayHalt and not wkB and not seqHalt and not ldHalt and not eqBlock
        clsWhy = ""

        def cancel():
            nonlocal stOrdLive
            if stOrdLive:
                for oid in stPend: pend.pop(oid, None)
            stOrdLive = False

        if stDir != 0 and (not stGo or (trendDir != 0 and trendDir != stDir)):
            cancel(); cnt["canc"] += 1; stDir = 0
        if favMode and stDir != 0 and stT15 != stDir:
            cancel(); cnt["canc"] += 1; stDir = 0; cnt["favCanc"] = cnt.get("favCanc", 0) + 1
        if agnMode and stDir != 0 and stT15 != -stDir:
            cancel(); cnt["canc"] += 1; stDir = 0; cnt["agnCanc"] = cnt.get("agnCanc", 0) + 1
        if autoMode and stDir != 0 and stDir != autoDir:
            cancel(); cnt["canc"] += 1; stDir = 0; cnt["autoCanc"] = cnt.get("autoCanc", 0) + 1
        if stDir != 0 and stArmBar is not None and bi > stArmBar and ((stDir == 1 and evBU) or (stDir == -1 and evBD)) and not stBosSeen:
            stBosSeen = True
            if p["bosMode"] == "Cancel":
                cancel(); cnt["canc"] += 1; stDir = 0
            elif p["bosMode"] == "Freeze" and stLast is not None:
                frozen = (stLast[0], stLast[1])
        if stDir != 0 and stRule != 2 and not (p["once"] and stPlaced) and frozen is None:
            live = E.florS.price if stDir == 1 and E.florS is not None else (E.ceilS.price if stDir == -1 and E.ceilS is not None else None)
            if live is not None:
                stSl = live - buf_at(p, live) if stDir == 1 else live + buf_at(p, live)
        if wkNow:
            if opn: clsWhy = "Weekend flat"
            if stDir != 0: cnt["canc"] += 1
            cancel(); stDir = 0
        if p["expBars"] > 0 and stDir != 0 and stArmBar is not None and bi - stArmBar >= p["expBars"]:
            cancel(); cnt["canc"] += 1; stDir = 0
        if flatNow:
            if opn: clsWhy = "Time flat"
            if stDir != 0: cnt["canc"] += 1
            cancel(); stDir = 0
        if not stWin:
            cancel()
            if stDir != 0: cnt["canc"] += 1
            stDir = 0
        sigUp = (useCho and evCU) or (useBos and evBU)
        sigDn = (useCho and evCD) or (useBos and evBD)
        opp = (pos > 0 and sigDn) or (pos < 0 and sigUp)
        oppCh = (pos > 0 and evCD) or (pos < 0 and evCU)
        if p["rev"] and (opp or oppCh):
            clsWhy = "Opposite signal" if opp else "Opposite CHOCH"
        if (sigUp or sigDn) and stGo:
            if p["cancelSig"] and stDir != 0:
                cancel(); cnt["canc"] += 1; stDir = 0
            addB = useBos and ((pos > 0 and evBU) or (pos < 0 and evBD))
            full = addB and p["maxOpen"] > 0 and len(opn) >= p["maxOpen"]
            addB = addB and not full
            take = stWin and (pos == 0 or (opp and p["rev"]) or addB)
            d = 1 if sigUp else -1
            if take and p["direction"] != "Both" and d != (1 if p["direction"] == "Longs" else -1):
                take = False; cnt["dirSkip"] += 1
            if take:
                piv = stCeilPrev if sigUp else stFlorPrev
                opl = (E.florS.price if E.florS is not None else None) if d == 1 else (E.ceilS.price if E.ceilS is not None else None)
                agree = (d == 1 and stT15 == 1) or (d == -1 and stT15 == -1)
                use = ((p["r2"] and piv is not None) or (not p["r2"] and p["r1"])) if agree else p["r1"]
                if (p["htfFilt"] or favMode) and not agree and not agnMode:
                    use = False; cnt["htfSkip"] += 1
                if agnMode:
                    use = p["r1"] and stT15 == -d
                if autoMode:
                    use = autoDir != 0 and d == autoDir and ((((p["r2"] and piv is not None) or (not p["r2"] and p["r1"]))) if eqOpen else p["r1"])
                if use and opl is not None:
                    if stDir != 0: cnt["canc"] += 1
                    cancel()
                    cnt["arm"] += 1; stPlaced = False; stEntLock = None; stArmBar = bi
                    stSeq += 1
                    base = ("L" if d == 1 else "S") + str(stSeq)
                    stPend = [base]
                    stDir = d; stRule = 2 if (agree and p["r2"] and not agnMode) else 1
                    stSl = opl - buf_at(p, opl) if d == 1 else opl + buf_at(p, opl)
                    stFix = piv if stRule == 2 else None
                    stAddRisk = p["bosRiskPct"] / 100.0 if addB else 1.0
                    stBosSeen = False; frozen = None
                    stLast = None
                    if log is not False: log.append((bi, d, stRule, stSl, stFix, stT15, trendDir, mA, mO))
        stEnt = stTgt = None
        if stDir != 0:
            stEnt = stEntLock if (p["once"] and stPlaced and stEntLock is not None) else (stFix if stRule == 2 else retLvl(trendDir, mA, mO, p["pb"]))
            if frozen is not None:
                stEnt, stSl = frozen
            if stEnt is not None and stSl is not None:
                r = abs(stEnt - stSl)
                stTgt = stEnt + (r * rr + cmPx) * stDir
                if p["liqTgt"]:
                    pool = E.liqHi if stDir == 1 else E.liqLo
                    lo = stEnt + stDir * max(p["liqMinR"] * r, 0)
                    cand = [x for x in pool if (x >= lo if stDir == 1 else x <= lo)]
                    if p["liqMaxR"] > 0:
                        hi = stEnt + stDir * p["liqMaxR"] * r
                        cand = [x for x in cand if (x <= hi if stDir == 1 else x >= hi)]
                    if cand:
                        stTgt = min(cand) if stDir == 1 else max(cand)
        if stGo and stDir != 0 and (pos == 0 or (pos > 0 if stDir == 1 else pos < 0)) and stWin and stEnt is not None and stTgt is not None and stSl is not None:
            sane = stEnt > stSl if stDir == 1 else stEnt < stSl
            r = abs(stEnt - stSl)
            amt = riskNow * stAddRisk
            per = r + cmU
            q = amt / per if per > 0 else 0.0
            st = p["unit"]
            raw = q
            q = math.floor(raw / st + 0.5) * st
            if p["rndMax"] > 0 and q * per > amt * (1 + p["rndMax"] / 100.0):
                q = math.floor(raw / st) * st
            if p["flMode"] != "Off" and p.get("flStrict", False) and q * per > amt:
                q = math.floor(raw / st) * st
            eqNow = eq_closed + sum((c - tr.ep) * tr.dir * tr.q for tr in opn)
            lim = max(0.0, eqNow * p["lev"] / stEnt - abs(pos))
            if q > lim: q = math.floor(lim / st) * st
            dOk = (p["minStop"] <= 0 or r >= lim_at(p, p["minStop"], stEnt)) and (p["maxStop"] <= 0 or r <= lim_at(p, p["maxStop"], stEnt))
            pdOk = True
            if p["pdOn"]:
                eqL = retLvl(trendDir, mA, mO, p["pdPct"])
                pdOk = eqL is not None and (stEnt <= eqL + 1e-9 if stDir == 1 else stEnt >= eqL - 1e-9)
            place = sane and dOk and pdOk and q > 0 and r > 0 and (not p["once"] or not stPlaced)
            if place:
                stPlaced = True; stEntLock = stEnt
                key = (stEnt, stSl, stTgt, q)
                if not stOrdLive or key != stLast:
                    base = stPend[0]
                    grp = base
                    q1 = 0.0
                    if p["partOn"]:
                        q1 = math.floor(q * p["partPct"] / 100.0 / st + 0.5) * st
                        if q1 <= 0 or q - q1 <= 0 or q1 >= q: q1 = 0.0
                    if q1 > 0:
                        tp1 = stEnt + stDir * (p["partR"] * r + (cmU * (p["partR"] + 1.0) if p["cmTgt"] else 0.0))
                        tp1 = min(tp1, stTgt) if stDir == 1 else max(tp1, stTgt)
                        pend[base] = dict(dir=stDir, lim=stEnt, q=q - q1, sl=stSl, tgt=stTgt, grp=grp, piece="m")
                        pend[base + "p"] = dict(dir=stDir, lim=stEnt, q=q1, sl=stSl, tgt=tp1, grp=grp, piece="p")
                        stPend = [base, base + "p"]
                    else:
                        pend[base] = dict(dir=stDir, lim=stEnt, q=q, sl=stSl, tgt=stTgt, grp=grp, piece="")
                        pend.pop(base + "p", None)
                        stPend = [base]
                    stOrdLive = True; stLast = key
                    seqLog.append((bi, stPend[0], amt, seqLoss, riskNow, q * per, flFloor, flPnl))
            elif not sane or not dOk or not pdOk or q <= 0 or r <= 0:
                cancel()
                if not dOk: cnt["skip"] += 1
                if not pdOk: cnt["pdSkip"] += 1
                cnt["canc"] += 1; stDir = 0
        if clsWhy:
            for tr in opn: closeReq[tr.id] = clsWhy
        stCeilPrev = E.ceilS.price if E.ceilS is not None else stCeilPrev
        stFlorPrev = E.florS.price if E.florS is not None else stFlorPrev
    for tr in closed: tr.grp = bosFill.get(tr.id, False)
    cnt["ldLog"] = ldLog; cnt["eqLog"] = eqLog
    cnt["seqLog"] = seqLog; cnt["seqHalt"] = seqHalt; cnt["seqLoss"] = seqLoss
    return closed, opn, cnt


def stats(closed, eq0=10000.0):
    n = len(closed)
    if n == 0:
        return dict(n=0, net=0.0, win=0.0, pf=0.0, dd=0.0, comm=0.0)
    net = sum(tr.pnl for tr in closed)
    gw = sum(tr.pnl for tr in closed if tr.pnl > 0); gl = -sum(tr.pnl for tr in closed if tr.pnl < 0)
    eq = eq0; peak = eq0; dd = 0.0
    for tr in sorted(closed, key=lambda x: x.xbar):
        eq += tr.pnl; peak = max(peak, eq); dd = max(dd, peak - eq)
    return dict(n=n, net=net, win=100.0 * sum(1 for tr in closed if tr.pnl > 0) / n, pf=gw / gl if gl > 0 else 99.0, dd=dd,
                comm=sum(2 * 0.3 * tr.q for tr in closed))
