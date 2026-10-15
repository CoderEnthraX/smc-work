# TradingView v15.0 = v14.0 + (the same rules as the MT5 EA v15.0):
#   1. section 4: 'Use these on the 1-minute chart only' (ON) + the big candle box for charts above 1 minute
#   2. the loss mark (section 7) removed
#   3. section 2: three 'HTF order block zone' modes + their settings (zone line, biggest timeframe, order blocks, FVGs, FVG far
#      half, second visit, CHOCH* line)
#   4. section 10: 'News on the 1-minute chart only' (ON)
#   5. 'Take trades on' keeps 6 choices (favourable / against / auto removed)
# Patched on the FINAL v14.0 file. A second file without the RSI / EMA filters is made with 'nofilters' as the 3rd argument.
# usage: python3 pine150.py SMC_Structure_Strategy_v14.0.txt SMC_Structure_Strategy_v15.0.txt [nofilters]
# The size steps (TradingView token limit) are in pine150c.py, the 'no RSI / EMA' cut in pine150lite.py.
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src, dst = sys.argv[1], sys.argv[2]
LITE = len(sys.argv) > 3 and sys.argv[3] == 'nofilters'
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


def setline(prefix, new):
    """replace the one whole line that starts (after its indent) with prefix"""
    global s
    L = s.split('\n')
    hit = [i for i, l in enumerate(L) if l.lstrip().startswith(prefix)]
    if len(hit) != 1: raise SystemExit('line %r found %d x' % (prefix[:80], len(hit)))
    L[hit[0]] = new
    s = '\n'.join(L)


def after_line(start, text):
    global s
    assert s.count('\n' + start) == 1, start
    a = s.index('\n' + start) + 1
    e = s.index('\n', a) + 1
    s = s[:e] + text + s[e:]


# ---- line 2 (version) and the settings banner
rep('// SMC Structure Strategy  -  v14.0  -  main-tier CHOCH/BOS (v14.0: own unit for each distance, leg size and big signal candle filters),',
    '// SMC Structure Strategy  -  v15.0' + (' (no RSI / EMA filters)' if LITE else '') + '  -  main-tier CHOCH/BOS (v15.0: HTF order block zone modes, 1-minute-only filters and news, loss mark and favourable / against / auto modes removed),')
rep('// ==== SETTINGS (v14.0) - 13 sections, the same order as the MT5 EA v14.0.', '// ==== SETTINGS (v15.0) - 13 sections, the same order as the MT5 EA v15.0.')

# ---- 5. the 6 signal choices + 3. the zone settings (end of section 2)
setline('stSigSrc = input.string(', 'stSigSrc = input.string("CHOCH only", "Take trades on", options = ["CHOCH only", "BOS only", "CHOCH and BOS", "CHOCH only - HTF order block zone", "BOS only - HTF order block zone", "CHOCH and BOS - HTF order block zone"], group = gx02, tooltip = "Which main-tier structure events may start a trade.\\n\\nHTF ORDER BLOCK ZONE (the last three): only WITH the higher timeframe, and only after the price touched a zone in the pullback zone of the higher timeframe leg (from the zone line below, 50%, to the leg start, 100%): an order block or an FVG of the higher timeframe or the two timeframes above it, or the higher timeframe\'s CHOCH* line. Then the chart\'s CHOCH / BOS starts the trade. Example, 1m chart: the 15m leg goes up 4,000 -> 4,040 (50% = 4,020); a 1h order block 4,008 - 4,012 is touched, then a 1m CHOCH up -> buy. A zone goes when a candle of its own timeframe closes beyond it.")')
after_line('pbSwp2 = input.bool(',
    'stZnPct  = input.float(50.0, "HTF order block zone modes - the zone line, % pullback of the higher timeframe leg", minval = 1.0, maxval = 99.0, step = 5.0, group = gx02, tooltip = "Order blocks touching this line or beyond it (up to the leg start, 100%) count; FVGs only beyond it. 50 = the equilibrium. Used only by the 3 order block zone modes above.")\n'
    'stZnBig  = input.bool(true, "  - only the biggest timeframe\'s zones count", group = gx02, tooltip = "ON: of the higher timeframe and the two above it (1m chart: 15m, 1h, 4h), only the zones of the BIGGEST one that has a zone in the leg\'s zone count. OFF: the zones of all three count.")\n'
    'stZnOb   = input.bool(true, "  - use order blocks", group = gx02, tooltip = "An order block = the last opposite candle before a move that leaves an FVG (its high to low). Touched at its near edge.")\n'
    'stZnFvg  = input.bool(true, "  - use FVGs (only beyond the zone line)", group = gx02, tooltip = "An FVG = candles 1 and 3 of a move do not overlap.")\n'
    'stZnHalf = input.bool(true, "  - FVG: only its far half counts (touched at its 50% line)", group = gx02, tooltip = "OFF: the whole FVG counts - touched at its near edge.")\n'
    'stZnTwo  = input.bool(true, "  - a second visit counts (it took the first visit\'s liquidity)", group = gx02, tooltip = "After a touch every CHOCH with the higher timeframe counts while the zone lives. When the price later goes beyond the low (buy) / high (sell) of the first visit: ON = the zone works again, OFF = the zone stops.")\n'
    'stZnLine = input.bool(true, "  - the higher timeframe\'s CHOCH* line counts as a zone", group = gx02, tooltip = "The leg start (100%): the price reaches it, no higher timeframe candle closes beyond it, then the chart\'s CHOCH with the higher timeframe -> trade.")\n')

# ---- 1. section 4 end
after_line('stBcMax = input.float(',
    'stM1On   = input.bool(true, "Use skip closer / further, min stop %, the rule 3 distance and the leg size on the 1-minute chart only", group = gx04, tooltip = "ON (default): on charts ABOVE 1 minute these are not used: skip if the stop is closer / further than (both kinds), skip if the stop is closer than X % of the price, the rule 3 \'near the broken level\' distance (rule 3 itself still works) and the leg size. Seconds charts count as 1 minute.")\n'
    'stBcMax2 = input.float(0.0, "Big signal candle on charts ABOVE 1 minute - skip if BIGGER than this (unit above; 0 = off)", minval = 0.0, step = 0.00000001, group = gx04, tooltip = "The box above is for the 1-minute chart; this one for every chart above 1 minute (5m, 15m, 1h ...). Example 25: a 15m signal candle of 30 is skipped.")\n')

# ---- 4. section 10 end
after_line('stPreHrs = input.float(',
    'stNw1m   = input.bool(true, "News on the 1-minute chart only (above 1 minute: no news windows, no news closes)", group = gx10, tooltip = "ON (default): on charts above 1 minute the news windows 1 - 3, the automatic US news and \'no new trades before news\' do nothing - trades are not closed by news. US holidays still work.")\n')

# ---- the zone box setting (end of section 13)
after_line('stAudSz  = input.string(',
    'stZnBox  = input.bool(true, "Zone modes: draw the zone that was touched and gave the signal as a box", group = gx13, tooltip = "Order block zone modes only: when the chart\'s CHOCH / BOS with the higher timeframe comes after a zone was touched, that zone is drawn as a box - from the zone\'s candle (the CHOCH* line: from its first touch) to the signal candle. Green = buy zone, red = sell zone. TradingView keeps the last 50 boxes.")\n')

# ---- 2. the loss mark
setline('stLmOn  = input.bool(', '\x00')
setline('stLmAmt = input.float(', '\x00')
rep('\x00\n\x00\n', '')
setline('var int   stCntLm = 0', '\x00')
rep('\x00\n', '')
rep('''    // v12.1: group 42 - the losses carried reached the mark: they are forgotten, the next trade risks the base again
    if stLmOn and stSeqMode != "Off" and f_stCar() >= stLmAmt - 0.005
        stSeqLoss := 0.0
        stSeqTot  := 0.0
        stCntLm   += 1
''', '')

# ---- 5. the old modes
rep('''// v11.0: a 'higher timeframe favourable' mode works like filter b (group 34); the equilibrium gate needs the higher timeframe too
bool   stFav   = str.contains(stSigSrc, "favourable")
// v11.1: the 'against the higher timeframe' modes - only signals the other way to the higher timeframe, entered by rule 1
bool   stAgn   = str.contains(stSigSrc, "against the higher timeframe")
// v11.1: the 'auto' modes - against the higher timeframe until its equilibrium is touched, then with it
bool   stAutoM = str.contains(stSigSrc, "auto: against HTF")
bool   stHfEff = stHfOn or stFav
bool   _u15    = stOn and (stR2On or stHfEff or stEqOn or stAgn or stAutoM) and stHtfOk''',
    '''// v15.0: the order block zone modes (only with the higher timeframe, after a zone touch)
bool   stObM   = str.contains(stSigSrc, "order block")
bool   _u15    = stOn and (stR2On or stHfOn or stEqOn or stObM) and stHtfOk''')
rep('''if (stEqOn or stAutoM) and not stEqOpen and not na(stEqLvl)''', '''if stEqOn and not stEqOpen and not na(stEqLvl)''')
rep('''bool stEqBlock = stEqOn and not stAutoM and not stEqOpen
// v11.1: auto modes - the side that may trade now: against the higher timeframe before the touch, with it after (0 = none)
int  stAutoDir = stAutoM ? (stEqOpen ? stT15 : -stT15) : 0
''', '''bool stEqBlock = stEqOn and not stEqOpen
''')
rep('''// v11.0: feature 2 - in a 'higher timeframe favourable' mode a waiting order is cancelled when the higher timeframe no
// longer agrees with it (an open trade keeps running)
if stFav and stDir != 0 and stT15 != stDir
    f_audEnd("CANCELLED - higher timeframe flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
// v11.1: in an 'against the higher timeframe' mode a waiting order is cancelled when the higher timeframe is no longer
// the other way to it (an open trade keeps running)
if stAgn and stDir != 0 and stT15 != -stDir
    f_audEnd("CANCELLED - higher timeframe now agrees", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
// v11.1: in an 'auto' mode a waiting order is cancelled when the side it may trade changes (an open trade keeps running)
if stAutoM and stDir != 0 and stDir != stAutoDir
    f_audEnd("CANCELLED - auto mode switched side", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
''', '''// v15.0: the zone modes - a waiting order goes when the higher timeframe flips or its zone is broken by a close (an open trade
// keeps running)
if stObM and stDir != 0 and (stT15 != stDir or stZnBrk)
    f_audEnd(stT15 != stDir ? "CANCELLED - higher timeframe flipped" : "CANCELLED - its zone was broken by a close", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
''')
rep('''        // v9.0 b: with the higher-timeframe filter a signal against it is skipped; with rule 2 OFF an agreeing signal uses rule 1
        bool _agst  = (_d == 1 and stT15 == -1) or (_d == -1 and stT15 == 1)
''', '''        // v9.0 b: with the higher-timeframe filter a signal against it is skipped; with rule 2 OFF an agreeing signal uses rule 1
''')
setline('bool _use   = stAutoM ?', '        bool _use   = _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfOn)')
setline('bool _hfSkip = (stAutoM and not _use)', '        bool _hfSkip = not _agree and stR1On and stHfOn')
setline('bool  _useM  = stAutoM ?', '        bool  _useM  = _agree or not stHfOn')
setline('_audS := not _use ? (stAutoM ?', '        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : stHfOn and stR1On ? "SKIP - against the higher timeframe (filter)" : "SKIP - HTF not agreeing (rule 2 only)") : na(_opl) ? "SKIP - no stop level" : ((_agree and stR2On ? "R2" : "R1") + " ARMED")')
setline('_audS := not _useM ? (stAutoM ?', '                _audS := not _useM ? "SKIP - against the higher timeframe (filter)" : na(_opl) ? "SKIP - no stop level" : "R3 ARMED - entry at the close"')
rep('stRule := _r3Use ? 3 : (_agree and stR2On and not stAgn ? 2 : 1)', 'stRule := _r3Use ? 3 : (_agree and stR2On ? 2 : 1)')
rep('(not stR2On and not stHfEff and not stEqOn and not stAgn and not stAutoM ? "off"', '(not stR2On and not stHfOn and not stEqOn and not stObM ? "off"')
setline('f_stCell(_t, 21, "ENTRY rules in use (1 / 2)"', '    f_stCell(_t, 21, "ENTRY rules in use (1 / 2)", (stR1On and stR2On ? "1 + 2 (dynamic)" : stR1On ? "1 only (pullback %)" : stR2On ? "2 only (HTF must agree)" : "NONE - both off") + (stObM ? "  |  HTF order block zone" : ""), stR1On or stR2On ? color.aqua : color.red)')
rep('f_stCell(_t, 22, "RULE 2 / filter higher timeframe", stR2On or stHfEff or stEqOn or stAgn or stAutoM ?', 'f_stCell(_t, 22, "RULE 2 / filter higher timeframe", stR2On or stHfOn or stEqOn or stObM ?')
rep('(stR2On or stHfEff or stEqOn or stAgn or stAutoM) and stHtfOk ? color.aqua : color.gray)', '(stR2On or stHfOn or stEqOn or stObM) and stHtfOk ? color.aqua : color.gray)')
setline('string _eqT = stAutoM ?', '    string _eqT = not stEqOn ? "off" : not stHtfOk ? "higher timeframe not above the chart - no trades" : stEqOpen ? ("OPEN - pulled back to " + str.tostring(stEqPct) + "%") : na(stEqLvl) ? "WAITING - no higher timeframe leg yet" : ("WAITING - needs " + str.tostring(stEqLvl, format.mintick))')
rep('f_stCell(_t, 46, "HTF EQUILIBRIUM FIRST (section 4)", _eqT, not stEqOn and not stAutoM ? color.gray', 'f_stCell(_t, 46, "HTF EQUILIBRIUM FIRST (section 4)", _eqT, not stEqOn ? color.gray')

# ---- 1. the 1-minute-only rules: the boxes in use
rep('''var float stMnX = stBuSepM ? stSkMin : stMinStop
var float stMxX = stBuSepM ? stSkMax : stMaxStop''', '''// v15.0: on charts above 1 minute (switch ON) skip closer / further, min stop %, the rule 3 distance and the leg size are not used
var bool  stX1m = stM1On and timeframe.in_seconds() > 60
var float stMnX = stX1m ? 0.0 : stBuSepM ? stSkMin : stMinStop
var float stMxX = stX1m ? 0.0 : stBuSepM ? stSkMax : stMaxStop
var float stMnP = stX1m ? 0.0 : stMnPct
var float stLzN = stX1m ? 0.0 : stLzMin
var float stLzX = stX1m ? 0.0 : stLzMax
var bool  stR3B = stR3BrkOn and not stX1m
var float stBcE = timeframe.in_seconds() > 60 ? stBcMax2 : stBcMax''')
for a, b in (('stMnPct', 'stMnP'), ('stLzMin', 'stLzN'), ('stLzMax', 'stLzX'), ('stR3BrkOn', 'stR3B'), ('stBcMax', 'stBcE')):
    # every use after the inputs and the lines above
    head, tail = s.split('var float stBcE = timeframe.in_seconds() > 60 ? stBcMax2 : stBcMax', 1)
    tail = re.sub(r'\b%s\b' % a, b, tail)
    s = head + 'var float stBcE = timeframe.in_seconds() > 60 ? stBcMax2 : stBcMax' + tail

# ---- 4. news on the 1-minute chart only
rep('bool stAuNow  = _auUse and stAuOn and (', 'var bool stNwX = stNw1m and timeframe.in_seconds() > 60   // v15.0: news on the 1-minute chart only\nbool stAuNow  = _auUse and stAuOn and not stNwX and (')
rep('bool stPreNow = _auUse and stAuOn and stPreOn and (', 'bool stPreNow = _auUse and stAuOn and stPreOn and not stNwX and (')
rep('bool stNwNow = stNewsOn and ((_stIntra and (f_nw(', 'bool stNwNow = stNewsOn and ((_stIntra and not stNwX and (f_nw(')

# ---- 3. the zone engine
rep('''int   stHtE = nz(_htE, 0)
''', '''int   stHtE = nz(_htE, 0)

// ---- v15.0 (section 2): the HTF order block zone modes - the same rules as the MT5 EA v15.0. Zones come from the CLOSED
// candles of the higher timeframe and the two above it (of 15m, 1h, 4h, 1D, 1W, 1M): an FVG = candles 1 and 3 apart; its
// order block = the last opposite candle among the 3 candles before the move. A zone goes when a candle of its own timeframe
// closes beyond its far side. At each bar a zone of the higher timeframe direction in the pullback zone of the leg (from the
// zone line to the leg start; FVGs beyond the line) is touched when the low (high) reaches its touch line; a chart signal
// with the higher timeframe after a touch may trade and closes the visit; a later bar beyond the visit's low (high) took its
// liquidity (second visit ON: works again, OFF: stops). A new higher timeframe leg starts all touches again.
f_znUp(string tf) =>
    int sec = timeframe.in_seconds(tf)
    sec < 900 ? "15" : sec < 3600 ? "60" : sec < 14400 ? "240" : sec < 86400 ? "1D" : sec < 604800 ? "1W" : sec < 2592000 ? "1M" : ""
string stZnTf1 = f_znUp(stHtfTf)
string stZnTf2 = stZnTf1 == "" ? "" : f_znUp(stZnTf1)
bool   stZnOn  = stObM and stHtfOk
// the last CLOSED candle: time, close, low, high, the low / high 2 candles before it, the order block before a gap up / down;
// the open times of the first FVG candle and of the two order blocks (for the zone box)
f_znReq() =>
    int ku = close[3] < open[3] ? 3 : close[4] < open[4] ? 4 : close[5] < open[5] ? 5 : 0
    int kd = close[3] > open[3] ? 3 : close[4] > open[4] ? 4 : close[5] > open[5] ? 5 : 0
    [time[1], close[1], low[1], high[1], low[3], high[3], ku > 0 ? high[ku] : na, ku > 0 ? low[ku] : na, kd > 0 ? high[kd] : na, kd > 0 ? low[kd] : na, time[3], ku > 0 ? time[ku] : na, kd > 0 ? time[kd] : na]
f_znGet(bool on, string tf) =>
    request.security(syminfo.tickerid, on ? tf : timeframe.period, f_znReq(), lookahead = barmerge.lookahead_on)
[_z0t, _z0c, _z0l, _z0h, _z0al, _z0ah, _z0ut, _z0ub, _z0dt, _z0db, _z0f, _z0uT, _z0dT] = f_znGet(stZnOn, stHtfTf)
[_z1t, _z1c, _z1l, _z1h, _z1al, _z1ah, _z1ut, _z1ub, _z1dt, _z1db, _z1f, _z1uT, _z1dT] = f_znGet(stZnOn and stZnTf1 != "", stZnTf1)
[_z2t, _z2c, _z2l, _z2h, _z2al, _z2ah, _z2ut, _z2ub, _z2dt, _z2db, _z2f, _z2uT, _z2dT] = f_znGet(stZnOn and stZnTf2 != "", stZnTf2)
// one zone: its timeframe (0 = the higher timeframe, 1 / 2 = the ones above), side, kind (0 order block, 1 FVG), top, bottom,
// the open time of its candle,
// the visit's low (buy) / high (sell), state (0 fresh, 1 touched - visit open, 2 a signal closed the visit, 3 stopped) and
// whether it is in the leg's zone on this bar
type Zn
    int   tf
    int   d
    int   k
    float top
    float bot
    int   t0
    float ext
    int   st = 0
    bool  q = false
var array<Zn>    zA = array.new<Zn>()
var array<float> zL = array.new<float>(4, na)   // the CHOCH* line: state, visit low / high; the leg's event count; first touch
var array<float> zO = array.new<float>(12, na)  // the last order block per timeframe and side (top, bottom)
var int   stZnF = -1
var float stZnT = na
var float stZnB = na
var int   stCntOb = 0
f_znAdd(int j, int d, int kd, float tp, float bt, int t0) =>
    int same = 0
    int old = -1
    for [i, z] in zA
        if z.tf == j and z.d == d
            same += 1
            old := old < 0 ? i : old
    if same >= 10
        array.remove(zA, old)
    if array.size(zA) >= 60
        array.remove(zA, 0)
    array.push(zA, Zn.new(j, d, kd, tp, bt, t0))
f_znOb(int j, int d, float tp, float bt, int t0) =>
    int o = j * 4 + (d == 1 ? 0 : 2)
    if stZnOb and not na(tp) and (na(array.get(zO, o)) or tp != array.get(zO, o) or bt != array.get(zO, o + 1))
        f_znAdd(j, d, 0, tp, bt, t0)
        array.set(zO, o, tp)
        array.set(zO, o + 1, bt)
// one closed candle of zone timeframe j; true = the zone of the waiting setup was broken
f_znCandle(int j, float c, float cl, float ch, float al, float ah, float ut, float ub, float dt, float db, int ft, int uT, int dT) =>
    bool hit = false
    int n = array.size(zA)
    if n > 0
        for i = n - 1 to 0
            Zn z = array.get(zA, i)
            if z.tf == j and (z.d == 1 ? c < z.bot : c > z.top)
                hit := hit or (j == stZnF and z.top == stZnT and z.bot == stZnB)
                array.remove(zA, i)
    if cl > ah
        if stZnFvg
            f_znAdd(j, 1, 1, cl, ah, ft)
        f_znOb(j, 1, ut, ub, uT)
    if ch < al
        if stZnFvg
            f_znAdd(j, -1, 1, al, ch, ft)
        f_znOb(j, -1, dt, db, dT)
    hit
// this bar against one zone: touch, the visit's low / high, its liquidity taken
f_znStep(int st, float ext, bool q, int d, float tl) =>
    float x = d == 1 ? low : high
    int   s2 = st
    float e2 = ext
    if st == 0
        if q and (d == 1 ? x <= tl : x >= tl)
            s2 := 1
            e2 := x
    else if st == 1
        e2 := d == 1 ? math.min(ext, x) : math.max(ext, x)
    else if st == 2 and (d == 1 ? x < ext : x > ext)
        s2 := stZnTwo ? 1 : 3
        e2 := x
    [s2, e2]
f_znBar() =>
    int d = stT15
    if na(array.get(zL, 2)) or stHtE != array.get(zL, 2)
        array.set(zL, 2, stHtE)
        for z in zA
            z.st  := 0
            z.ext := na
        array.set(zL, 0, 0)
        array.set(zL, 1, na)
    float L = f_retLvl(d, stHtX, stHtO, stZnPct)
    float e = syminfo.mintick / 2
    for z in zA
        bool q = false
        if d != 0 and z.d == d and not na(L) and not na(stHtO)
            float tl = z.k == 1 and stZnHalf ? (z.top + z.bot) / 2 : d == 1 ? z.top : z.bot
            q := z.k == 0 ? (d == 1 ? z.bot <= L + e and z.top >= stHtO - e : z.top >= L - e and z.bot <= stHtO + e) : (d == 1 ? tl <= L + e and tl >= stHtO - e : tl >= L - e and tl <= stHtO + e)
            [s2, x2] = f_znStep(z.st, z.ext, q, d, tl)
            z.st  := s2
            z.ext := x2
        z.q := q
    if stZnLine and d != 0 and not na(stHtO)
        [s2, x2] = f_znStep(int(array.get(zL, 0)), array.get(zL, 1), true, d, stHtO)
        if s2 == 1 and array.get(zL, 0) == 0
            array.set(zL, 3, time)
        array.set(zL, 0, s2)
        array.set(zL, 1, x2)
// the zone a signal in direction d may trade from: [timeframe (9 = the CHOCH* line, -1 = none), kind, top, bottom, the open
// time of its candle (the line: its first touch)]
f_znAllow(int d) =>
    int big = -1
    for z in zA
        if stZnBig and z.d == d and z.q and z.st != 3
            big := math.max(big, z.tf)
    float ls = array.get(zL, 0)
    bool  ln = stZnLine and (ls == 1 or ls == 2)
    int   rf = ln ? 9 : -1
    int   rk = -1
    float rt = ln ? stHtO : na
    float rb = rt
    int   r0 = ln ? int(array.get(zL, 3)) : na
    int   bf = -1
    for z in zA
        if z.d == d and (z.st == 1 or z.st == 2) and (not stZnBig or z.tf == big) and z.tf > bf
            bf := z.tf
            rf := z.tf
            rk := z.k
            rt := z.top
            rb := z.bot
            r0 := z.t0
    [rf, rk, rt, rb, r0]
// a chart signal with the higher timeframe closes the visit of every touched zone of that side
f_znFrz(int d) =>
    for z in zA
        if z.d == d and z.st == 1
            z.st := 2
    if array.get(zL, 0) == 1
        array.set(zL, 0, 2)
''')
# every bar: the closed zone candles, then the zones against this bar (before the cancels and the signal)
rep('''bool stEqBlock = stEqOn and not stEqOpen
''', '''bool stEqBlock = stEqOn and not stEqOpen
// v15.0: the zone candles that closed, then this bar against the zones
bool stZnBrk = false
if stZnOn
    if _z0t != nz(_z0t[1])
        stZnBrk := f_znCandle(0, _z0c, _z0l, _z0h, _z0al, _z0ah, _z0ut, _z0ub, _z0dt, _z0db, _z0f, _z0uT, _z0dT)
    if stZnTf1 != "" and _z1t != nz(_z1t[1])
        stZnBrk := f_znCandle(1, _z1c, _z1l, _z1h, _z1al, _z1ah, _z1ut, _z1ub, _z1dt, _z1db, _z1f, _z1uT, _z1dT) or stZnBrk
    if stZnTf2 != "" and _z2t != nz(_z2t[1])
        stZnBrk := f_znCandle(2, _z2c, _z2l, _z2h, _z2al, _z2ah, _z2ut, _z2ub, _z2dt, _z2db, _z2f, _z2uT, _z2dT) or stZnBrk
    f_znBar()
''')
rep('''        // v13.1 (section 4): the new setup filters; the first setup of the day is checked LAST, so a setup that another
        // filter skips is never the day's first''', '''        // v15.0: the zone modes - only with the higher timeframe, and only after a zone was touched
        int   _zf = -1
        int   _zk = -1
        float _zt = na
        float _zb = na
        if stObM
            [_a1, _a2, _a3, _a4, _a5] = f_znAllow(_d)
            _zf := _d == stT15 ? _a1 : -1
            _zk := _a2
            _zt := _a3
            _zb := _a4
            if _use and _zf < 0
                _use := false
                stCntOb += 1
                _audS := "SKIP - zone mode: " + (_d != stT15 ? "not with the higher timeframe" : "no zone touched")
        // v13.1 (section 4): the new setup filters; the first setup of the day is checked LAST, so a setup that another
        // filter skips is never the day's first''')
rep('''            stFix  := stRule == 2 ? _piv : na
''', '''            stFix  := stRule == 2 ? _piv : na
            stZnF  := _zf
            stZnT  := _zt
            stZnB  := _zb
            if stObM
                _audS += _zf == 9 ? " (CHOCH* line)" : " (" + (_zf == 0 ? "HTF" : _zf == 1 ? "HTF+1" : "HTF+2") + (_zk == 0 ? " order block)" : " FVG)")
''')
rep('''if stAudit and (stSigUp or stSigDn)
    bool   _aCh = stUseCho''', '''// v15.0: a chart signal with the higher timeframe closes the visit of the touched zones; the zone it came from is drawn as a
// box (from the zone's candle - the CHOCH* line: from its first touch - to this candle; green = buy zone, red = sell zone)
if stZnOn and stT15 != 0 and (stT15 == 1 ? stSigUp : stSigDn)
    [_bf, _bk, _bt, _bb, _b0] = f_znAllow(stT15)
    if stZnBox and _bf >= 0
        color _bc = stT15 == 1 ? color.green : color.red
        box.new(_b0, _bt, time, _bb, xloc = xloc.bar_time, border_color = _bc, bgcolor = color.new(_bc, 85), text = _bf == 9 ? "HTF CHOCH* line" : f_tfName(_bf == 0 ? stHtfTf : _bf == 1 ? stZnTf1 : stZnTf2) + (_bk == 0 ? " order block" : " FVG"), text_size = size.small, text_color = _bc)
    f_znFrz(stT15)
if stAudit and (stSigUp or stSigDn)
    bool   _aCh = stUseCho''')
setline('f_stCell(_t, 50, "LOSS MARK - BACK TO THE BASE (section 7)"', '    f_stCell(_t, 50, "ORDER BLOCK ZONES (section 2)", not stObM ? "off" : not stHtfOk ? "on - but the higher timeframe is not above the chart - no trades" : str.tostring(array.size(zA)) + " zones (" + f_tfName(stHtfTf) + (stZnTf1 != "" ? " + " + f_tfName(stZnTf1) : "") + (stZnTf2 != "" ? " + " + f_tfName(stZnTf2) : "") + ")  |  skipped (no zone) " + str.tostring(stCntOb), stObM ? color.aqua : color.gray)')
setline('string _lmT = not stLmOn', '\x00')
rep('\x00\n', '')
rep('    // v12.1: group 41 (no new trades before news) and group 42 (the loss mark)\n', '    // v12.1: group 41 (no new trades before news); v15.0: the order block zones\n')

assert 'stFav' not in s and 'stAgn' not in s and 'stAutoM' not in s and 'stAutoDir' not in s and 'stHfEff' not in s and 'stLm' not in s and 'stCntLm' not in s, 'old names left'

# ---- the zone box names the timeframe: the timeframe-name helper must be declared before that (TradingView reads top down)
_tfn = 'f_tfName(string tf) =>\n    tf == "15" ? "15m" : tf == "60" ? "1h" : tf == "240" ? "4h" : tf\n'
rep(_tfn, '')
rep('f_znUp(string tf) =>\n', _tfn + 'f_znUp(string tf) =>\n')

# the table title still said v13.1
rep('"STRATEGY v13.1"', '"STRATEGY v15.0"')

import pine150c
if not os.environ.get('NOCOMPACT'):   # NOCOMPACT=1: the file before the size steps (for the old / new engine check)
    s = pine150c.compact(s)

if LITE:
    import pine150lite
    s = pine150lite.strip(s)

assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)
