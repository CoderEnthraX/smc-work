# TradingView v15.1 = v15.0 + the same rules as the MT5 EA v15.1 (see ea151.py):
#   one box per zone (stretched, 'x3'), every zone that counted is drawn, show all zones + its look (section 13), the zones made
#   before a new higher timeframe leg go, a setup goes only when ALL its zones are gone, only the last zone, order block type 2 /
#   to the swing, MSS + its confirmation (section 2), every-other-day mode after a pause (section 8), force close on 1m only
#   (section 9), every price distance off (section 1)
# usage: python3 pine151.py SMC_Structure_Strategy_v15.0.txt SMC_Structure_Strategy_v15.1.txt
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:160]))
    s = s.replace(old, new)


def after_line(prefix, add):
    """insert the text add after the ONE line that starts with prefix"""
    global s
    L = s.split('\n')
    k = [i for i, l in enumerate(L) if l.startswith(prefix)]
    if len(k) != 1: raise SystemExit('line %r found %d x' % (prefix, len(k)))
    L[k[0] + 1:k[0] + 1] = add.rstrip('\n').split('\n')
    s = '\n'.join(L)


def line_sub(prefix, old, new):
    """replace old by new inside the ONE line that starts with prefix"""
    global s
    L = s.split('\n')
    k = [i for i, l in enumerate(L) if l.startswith(prefix)]
    if len(k) != 1 or L[k[0]].count(old) != 1: raise SystemExit('line %r / %r' % (prefix, old))
    L[k[0]] = L[k[0]].replace(old, new)
    s = '\n'.join(L)


# ---------------------------------------------------------------- version (line 2), boxes
rep('// SMC Structure Strategy  -  v15.0  -  main-tier CHOCH/BOS (v15.0: ',
    '// SMC Structure Strategy  -  v15.1  -  main-tier CHOCH/BOS (v15.1: one box per zone with every zone that counted, show all zones, '
    'the zones of an old higher timeframe leg go, a setup goes only when all its zones are gone, only the last zone, order block type 2 / '
    'to the swing, MSS + its confirmation, every-other-day mode after a pause, force close on 1m only, every price distance off; v15.0: ')
rep('     max_bars_back = 2000, max_lines_count = 500, max_labels_count = 500, dynamic_requests = true,',
    '     max_bars_back = 2000, max_lines_count = 500, max_labels_count = 500, max_boxes_count = 500, dynamic_requests = true,')
rep('// ==== SETTINGS (v15.0) - 13 sections, the same order as the MT5 EA v15.0.', '// ==== SETTINGS (v15.1) - 13 sections, the same order as the MT5 EA v15.1.')

# ---------------------------------------------------------------- inputs at the END of their section
after_line('stBuPip  = input.float(', '''stPxOff  = input.bool(false, "Switch OFF every price-distance setting on every chart (other markets: forex, crypto, metals)", group = gx01, tooltip = "OFF (default): nothing changes.\\n\\nON: on EVERY chart, also 1 minute, these are not used, so their gold values cannot spoil a backtest on another market: the stop buffer (old and separate box), skip closer / further (old and separate boxes), the min stop % of the price, the rule 3 'near the broken level' distance (rule 3 itself still enters at the close), the leg size, the big signal candle (both boxes), the spread for sizing and 'Push the target out to cover the commission'.\\n\\nExample: EURUSD at 1.0850 with a stop buffer of 1.0 (made for gold) = a stop 10,000 pips away; with this switch ON the stop is exactly at the CHOCH* level.\\n\\nThe commission itself, the lot step and the leverage still work - set the commission for each market.")''')
after_line('stZnLine = input.bool(', '''stZnLast = input.bool(false, "  - only trade from the LAST zone (the deepest order block of the biggest timeframe)", group = gx02, tooltip = "OFF (default): every touched zone counts (see 'only the biggest timeframe').\\n\\nON: a CHOCH / BOS (or MSS) trades only when the LAST zone was touched. The last zone = among the ORDER BLOCKS in the pullback zone of the higher timeframe leg: the biggest timeframe that has one (4h before 1h before 15m on a 1m chart), and of those the deepest (nearest the leg start). FVGs and the CHOCH* line are never the last zone; the CHOCH* line still trades on its own switch. Worked out again on every candle. This switch decides instead of 'only the biggest timeframe'.\\n\\nExample (buy, leg 4,000 -> 4,040, line 4,020): 15m OB 4,016-4,018, 1h OB 4,010-4,013, 4h OB 4,006-4,009, 15m OB 4,002-4,004 -> the last zone is the 4h OB (the deeper 15m OB is only 15m). A dip to 4,015 + CHOCH up = no trade; a dip to 4,008 + CHOCH up = trade.")
stZnSw   = input.bool(false, "  - order block box reaches the swing low (buy) / high (sell)", group = gx02, tooltip = "OFF (default): an order block is its candle's high - low.\\n\\nON: a buy order block reaches down to the lowest low from its candle to the 3rd FVG candle (a sell one up to the highest high); the rules use this bigger box too (in the leg's zone, touch, the close that breaks it, the last zone).\\n\\nExample: order block candle 4,001 - 4,006, the next candle wicks to 3,998, then the move up -> the box is 3,998 - 4,006.")
stZnOb2  = input.bool(false, "  - order block type 2: the FIRST candle of the FVG (one per burst)", group = gx02, tooltip = "OFF (default): the order block = the last opposite candle among the 3 candles before the move.\\n\\nON (type 2): the order block = candle 1 of the 3 FVG candles, any colour - one per burst: an FVG whose candle 1 is one of the last FVG's 3 candles is the same burst (no new order block); after a pause a new FVG starts a new burst.\\n\\nExample: green candles A B C D E (FVGs A-C, B-D, C-E), a pause F G, then G-I, H-J -> order blocks A and G.")
stMssOn  = input.bool(false, "  - also trade a market structure shift (MSS) after a zone touch", group = gx02, tooltip = "OFF (default): only the chart's CHOCH / BOS trade in the zone modes.\\n\\nON: after a fast move into a zone the chart's CHOCH level can be far away. An MSS also counts: a close above the newest swing high (below the newest swing low for a sell) WITH the higher timeframe, when the move from the lowest low since that swing (the MSS low) holds a chart FVG with its order block, and a zone counts for it. Stop beyond the MSS low; entry by rules 1 / 2 / 3 (pullback of the MSS move / the broken swing / the close). One trade per zone visit: a visit that gave an MSS gives no CHOCH / BOS trade, and the other way round.\\n\\nExample: zone 4,006-4,009, swing high 4,013, low 4,005, a 1m FVG 4,008-4,010, a close at 4,014 = MSS up; rule 2 = buy 4,013, stop 4,004 (buffer 1).")
stMssN   = input.int(2, "  - MSS swing: candles on each side", minval = 1, maxval = 10, group = gx02, tooltip = "A swing high = a candle whose high is above the highs of this many candles on EACH side (2 = the usual 5-candle swing). The MSS breaks the newest one not closed above yet.")
stMssCf  = input.bool(false, "  - MSS: enter on the confirmation", group = gx02, tooltip = "OFF (default): an MSS enters by rules 1 / 2 / 3.\\n\\nON: no entry on the MSS itself. Wait for a pullback to the FIRST FVG of the MSS move (its near edge), then a NEW chart FVG with its order block (its candle 1 at or after the pullback candle) -> enter at the close of that candle. The price beyond the MSS low (buy) before that = the MSS failed, no trade.\\n\\nExample: MSS low 4,005, first FVG 4,008-4,010, MSS close 4,014; pullback to 4,009, then a new FVG; its 3rd candle closes at 4,015 = buy there; stop below 4,005 (or below 4,009 with 'newest swing').")
stMssSt  = input.string("First MSS low / high", "  - MSS confirmation: the stop", options = ["First MSS low / high", "Newest swing low / high (the pullback)"], group = gx02, tooltip = "Where the stop goes for an entry on the MSS confirmation: beyond the low (buy) / high (sell) the MSS started from (default, wider), or beyond the lowest low / highest high of the pullback (tighter, a bigger position).")''')
after_line('stLdD   = input.int(', '''stLdN2   = input.int(0, "  - after the pause: losses in a row that start the every-other-day mode (0 = off)", minval = 0, maxval = 50, group = gx08, tooltip = "0 (default) = off: after the pause the count starts again as usual.\\n\\nN: after a pause, N losses in a row (instead of the normal number) start the every-other-day mode: no new trades the rest of that day, then trading only every (skip + 1)-th trading day (Monday - Friday; every day for crypto / 24-7), until ONE winning trade - then back to normal. No new pause starts in that mode.\\n\\nExample 3 losses / 3 days, then 2, skip 1: Mon 3rd loss -> pause Tue-Thu; Fri loss, loss -> Mon skip, Tue trade (loss), Wed skip, Thu trade (win) -> normal again.")
stLdSkip = input.int(1, "  - that mode: days skipped between trading days (1 = every other day)", minval = 1, maxval = 10, group = gx08)''')
after_line('stWk247     = input.bool(', '''stFl1m   = input.bool(true, "Force-close hour on the 1-minute chart only", group = gx09, tooltip = "ON (default): the force-close hour above works only on the 1-minute chart (and seconds charts); on higher charts open trades are not closed at that hour (the entry hours and the weekend rule still work).\\n\\nOFF: the force-close hour works on every chart, as in v15.0.")''')
line_sub('stZnBox  = input.bool(', '"Zone modes: draw the zone that was touched and gave the signal as a box"', '"Zone modes: draw every zone that gave a signal as a box (one box per zone)"')
after_line('stZnBox  = input.bool(', '''stZnAll  = input.bool(false, "Zone modes: show ALL zones (every live zone the settings can use)", group = gx13, tooltip = "OFF (default): only the zones that gave a signal are drawn (their boxes, above).\\n\\nON: every live order block / FVG of the higher timeframe direction in the pullback zone of its leg is drawn too, up to the last candle: order blocks and FVGs in their own colours, the higher timeframe's zones with a border, the two above it lighter and without a border (their label in the label colour), the LAST zone darker. A zone that is gone is not drawn.")
stZnV0   = input.int(50, "  - fill visible %: higher timeframe zones (e.g. 15m)", minval = 0, maxval = 100, group = gx13)
stZnV1   = input.int(30, "  - fill visible %: the timeframe above (e.g. 1h)", minval = 0, maxval = 100, group = gx13)
stZnV2   = input.int(15, "  - fill visible %: two above (e.g. 4h)", minval = 0, maxval = 100, group = gx13)
stZnCObB = input.color(color.green, "  - order block colour, buy", group = gx13)
stZnCObS = input.color(color.red, "  - order block colour, sell", group = gx13)
stZnCFvB = input.color(color.teal, "  - FVG colour, buy", group = gx13)
stZnCFvS = input.color(color.orange, "  - FVG colour, sell", group = gx13)
stZnCLb  = input.color(color.white, "  - label colour of the two timeframes above", group = gx13)''')

# ---------------------------------------------------------------- section 1: every price distance off; section 9: force close on 1m
rep('var float stBfX = stBuSepM ? stBfV : stSlBuf', 'var float stBfX = stPxOff ? 0.0 : stBuSepM ? stBfV : stSlBuf')
rep('var bool  stX1m = stM1On and timeframe.in_seconds() > 60', 'var bool  stX1m = (stM1On and timeframe.in_seconds() > 60) or stPxOff   // v15.1: or every price distance off')
rep('var float stBcE = timeframe.in_seconds() > 60 ? stBcMax2 : stBcMax', 'var float stBcE = stPxOff ? 0.0 : timeframe.in_seconds() > 60 ? stBcMax2 : stBcMax')
rep('var float stSpX = stBuSepM ? stSpdV : stSprd', 'var float stSpX = stPxOff ? 0.0 : stBuSepM ? stSpdV : stSprd')
rep('stCmTgt and _stPvA > 0', 'stCmTgt and not stPxOff and _stPvA > 0', 3)
rep('bool _stDead = stTimeOn and (stHrFlat != stHrOn ?', 'bool _stDead = stTimeOn and not (stFl1m and _stCs > 60) and (stHrFlat != stHrOn ?')

# ---------------------------------------------------------------- the higher timeframe engine: the time of the leg start
rep('''    int   ecOut = 0
''', '''    int   ecOut = 0
    int   lgOut = na
''')
rep('''        var float tRunHi = na
''', '''        var float tRunHi = na
        var int   tRLoT = na
        var int   tRHiT = na
        var int   tLegT = na
''')
rep('''        tRunLo := na(tRunLo) ? low  : math.min(tRunLo, low)
        tRunHi := na(tRunHi) ? high : math.max(tRunHi, high)
''', '''        if na(tRunLo) or low < tRunLo
            tRunLo := low
            tRLoT  := time
        if na(tRunHi) or high > tRunHi
            tRunHi := high
            tRHiT  := time
''')
rep('''                tCeilB := bar_index
                tRunLo := low
''', '''                tCeilB := bar_index
                tRunLo := low
                tRLoT  := time
''')
rep('''                tFlorB := bar_index
                tRunHi := high
''', '''                tFlorB := bar_index
                tRunHi := high
                tRHiT  := time
''')
rep('''            tFlor  := tRunLo
            tFlorB := bar_index
            tRunHi := high
''', '''            tFlor  := tRunLo
            tFlorB := bar_index
            tLegT  := tRLoT
            tRunHi := high
            tRHiT  := time
''')
rep('''            tCeil  := tRunHi
            tCeilB := bar_index
            tRunLo := low
''', '''            tCeil  := tRunHi
            tCeilB := bar_index
            tLegT  := tRHiT
            tRunLo := low
            tRLoT  := time
''')
rep('''        ecOut := tEvN
''', '''        ecOut := tEvN
        lgOut := tLegT
''')
rep('''    [trOut, loOut, lxOut, ecOut]''', '''    [trOut, loOut, lxOut, ecOut, lgOut]''')
rep('''    [_tA, _tO, _tX, _tE] = f_tfPack(on)
    [_tA[1], _tO[1], _tX[1], _tE[1]]''', '''    [_tA, _tO, _tX, _tE, _tS] = f_tfPack(on)
    [_tA[1], _tO[1], _tX[1], _tE[1], _tS[1]]''')
rep('''[_htT, _htO, _htX, _htE] = request.security(''', '''[_htT, _htO, _htX, _htE, _htS] = request.security(''')
rep('''int   stHtE = nz(_htE, 0)
''', '''int   stHtE = nz(_htE, 0)
int   stHtS = _htS   // v15.1: the open time of the higher timeframe candle where its leg started
bool  stUseCho = not str.startswith(stSigSrc, "BOS only")
bool  stUseBos = not str.startswith(stSigSrc, "CHOCH only")
bool  _cU = (stUseCho and evChoUp) or (stUseBos and evBosUp)   // the chart's CHOCH / BOS signals
bool  _cD = (stUseCho and evChoDn) or (stUseBos and evBosDn)
''')
rep('''bool stUseCho = not str.startswith(stSigSrc, "BOS only")
bool stUseBos = not str.startswith(stSigSrc, "CHOCH only")
bool stSigUp = (stUseCho and evChoUp) or (stUseBos and evBosUp)
bool stSigDn = (stUseCho and evChoDn) or (stUseBos and evBosDn)
''', '''bool stSigUp = _cU or msU   // v15.1: an MSS is a signal too (never on a candle with a chart CHOCH / BOS signal)
bool stSigDn = _cD or msD
bool _isMs   = msU or msD
''')

# ---------------------------------------------------------------- the zone engine
a = s.index('// ---- v15.0 (section 2): the HTF order block zone modes - the same rules as the MT5 EA v15.0.')
b = s.index('bool  _stIntra = _stCs < 86400')
ZONE = r'''// ---- v15.0 / v15.1 (section 2): the HTF order block zone modes - the same rules as the MT5 EA v15.1. Zones come from the CLOSED
// candles of the higher timeframe and the two above it (of 15m, 1h, 4h, 1D, 1W, 1M): an FVG = candles 1 and 3 apart; its
// order block = the last opposite candle among the 3 candles before the move (type 2: candle 1, one per burst; 'to the swing':
// down / up to the swing low / high). A zone goes when a candle of its own timeframe closes beyond its far side, and when a new
// higher timeframe leg starts after it was made. At each bar a zone of the higher timeframe direction in the pullback zone of
// the leg (from the zone line to the leg start; FVGs beyond the line) is touched when the low (high) reaches its touch line; a
// signal with the higher timeframe after a touch may trade and closes the visit; a later bar beyond the visit's low (high) took
// its liquidity (second visit ON: works again, OFF: stops). A visit that gave an MSS gives no CHOCH / BOS trade and the other way.
f_tfName(string tf) =>
    tf == "15" ? "15m" : tf == "60" ? "1h" : tf == "240" ? "4h" : tf
f_znUp(string tf) =>
    int sec = timeframe.in_seconds(tf)
    sec < 900 ? "15" : sec < 3600 ? "60" : sec < 14400 ? "240" : sec < 86400 ? "1D" : sec < 604800 ? "1W" : sec < 2592000 ? "1M" : ""
string stZnTf1 = f_znUp(stHtfTf)
string stZnTf2 = stZnTf1 == "" ? "" : f_znUp(stZnTf1)
bool   stZnOn  = stObM and stHtfOk
// the last CLOSED candle: its close time, the side of a gap between it and candle 1 (2 before it: 1 up, -1 down, 0 none), its close,
// the FVG (top, bottom), the order block of that gap (type 1: the last opposite candle of candle 1 and the 2 before it; type 2:
// candle 1; 'to the swing': down / up to the lowest low / highest high from it to the closed candle), the open times of candle 1
// and of the order block (one candle cannot make a gap up and a gap down at once)
f_znReq() =>
    int d = low[1] > high[3] ? 1 : high[1] < low[3] ? -1 : 0
    int k = stZnOb2 ? 3 : (close[3] - open[3]) * d < 0 ? 3 : (close[4] - open[4]) * d < 0 ? 4 : (close[5] - open[5]) * d < 0 ? 5 : 0
    float tp = k > 0 ? high[k] : na
    float bt = k > 0 ? low[k] : na
    if stZnSw and k > 0
        if d == 1
            bt := math.min(low[1], low[2], low[3], low[math.min(k, 4)], low[k])
        else
            tp := math.max(high[1], high[2], high[3], high[math.min(k, 4)], high[k])
    [time_close[1], d, close[1], d == 1 ? low[1] : low[3], d == 1 ? high[3] : high[1], tp, bt, time[3], k > 0 ? time[k] : na]
f_znGet(bool on, string tf) =>
    request.security(syminfo.tickerid, on ? tf : timeframe.period, f_znReq(), lookahead = barmerge.lookahead_on)
[_z0e, _z0d, _z0c, _z0t, _z0b, _z0ot, _z0ob, _z0f, _z0oT] = f_znGet(stZnOn, stHtfTf)
[_z1e, _z1d, _z1c, _z1t, _z1b, _z1ot, _z1ob, _z1f, _z1oT] = f_znGet(stZnOn and stZnTf1 != "", stZnTf1)
[_z2e, _z2d, _z2c, _z2t, _z2b, _z2ot, _z2ob, _z2f, _z2oT] = f_znGet(stZnOn and stZnTf2 != "", stZnTf2)
// one zone: its timeframe (0 = the higher timeframe, 1 / 2 = the ones above, 9 = the CHOCH* line), side, kind (0 order block,
// 1 FVG), top, bottom, the open time of its candle (the line: its first touch), when it was made (the close of the 3rd FVG
// candle), the visit's low (buy) / high (sell), state (0 fresh, 1 touched - visit open, 2 a signal closed the visit, 3 stopped),
// in the leg's zone on this bar, the signal that closed this visit (1 CHOCH / BOS, 2 MSS), signals counted, gone, its box, number
type Zn
    int   tf
    int   d
    int   k
    float top
    float bot
    int   t0
    int   te
    float ext
    int   st = 0
    bool  q = false
    int   vs = 0
    int   n = 0
    bool  dead = false
    box   bx
    int   id
var array<Zn>  zA = array.new<Zn>()
var Zn         zLn = Zn.new(9, 0, 2)
var array<int> zO = array.new<int>(13, na)   // per timeframe and side: the last order block's candle time, the last FVG's candle 1 number; zone numbers
var array<int> zS = array.new<int>(3, 0)     // candles fed per timeframe
var int        zLeg = -1                      // the leg (its event count)
var array<box> stZbx = array.new<box>()       // the signal boxes (the newest 440)
var array<box> stZax = array.new<box>()       // 'show all zones'
var array<Zn>  stSup = array.new<Zn>()        // the zones that allowed the waiting setup
var int   stCntOb = 0
f_znAdd(int j, int d, int kd, float tp, float bt, int t0, int te) =>
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
    int id = nz(array.get(zO, 12)) + 1
    array.set(zO, 12, id)
    array.push(zA, Zn.new(j, d, kd, tp, bt, t0, te, id = id))
// one closed candle of zone timeframe j (te = its close; d = the side of its gap, ft / fb = the FVG, ot / ob = its order block)
f_znCandle(int j, int te, int d, float c, float ft, float fb, float ot, float ob, int t1, int oT) =>
    int n = array.size(zA)
    if n > 0
        for i = n - 1 to 0
            Zn z = array.get(zA, i)
            if z.tf == j and (z.d == 1 ? c < z.bot : c > z.top)
                z.dead := true
                array.remove(zA, i)
    int sq = array.get(zS, j) + 1
    array.set(zS, j, sq)
    if d != 0
        int o  = j * 4 + (d == 1 ? 0 : 2)
        int f1 = nz(array.get(zO, o + 1), -100)
        array.set(zO, o + 1, sq - 2)
        if stZnFvg
            f_znAdd(j, d, 1, ft, fb, t1, te)
        if stZnOb and not na(ot) and (stZnOb2 ? sq - 2 > f1 + 2 or sq - 2 < f1 : oT != nz(array.get(zO, o), -1))
            f_znAdd(j, d, 0, ot, ob, oT, te)
            array.set(zO, o, oT)
// this bar against one zone: touch, the visit's low / high, its liquidity taken
f_znStep(Zn z, bool q, float tl) =>
    float x = z.d == 1 ? low : high
    if z.st == 0
        if q and (z.d == 1 ? x <= tl : x >= tl)
            z.st  := 1
            z.ext := x
            z.vs  := 0
            if z.tf == 9
                z.t0 := time
    else if z.st == 1
        z.ext := z.d == 1 ? math.min(z.ext, x) : math.max(z.ext, x)
    else if z.st == 2 and (z.d == 1 ? x < z.ext : x > z.ext)
        z.st  := stZnTwo ? 1 : 3
        z.ext := x
        z.vs  := 0
    true
// a new higher timeframe leg: the zones made before it started go (ls = the open of the candle that started it); the rest start again
f_znKill(int ls) =>
    int n = array.size(zA)
    if n > 0
        for i = n - 1 to 0
            Zn z = array.get(zA, i)
            if not na(ls) and z.te <= ls
                z.dead := true
                array.remove(zA, i)
                z.vs  := 0
            else
                z.st  := 0
                z.ext := na
                z.vs  := 0
    true
// which zones are in the leg's zone, touches, visits; returns the last zone (the deepest order block of the biggest timeframe)
f_znBar() =>
    int d = stT15
    float L = f_retLvl(d, stHtX, stHtO, stZnPct)
    float e = syminfo.mintick / 2
    Zn lz = na
    for z in zA
        bool q = false
        if d != 0 and z.d == d and not na(L) and not na(stHtO)
            float tl = z.k == 1 and stZnHalf ? (z.top + z.bot) / 2 : d == 1 ? z.top : z.bot
            q := z.k == 0 ? (d == 1 ? z.bot <= L + e and z.top >= stHtO - e : z.top >= L - e and z.bot <= stHtO + e) : (d == 1 ? tl <= L + e and tl >= stHtO - e : tl >= L - e and tl <= stHtO + e)
            f_znStep(z, q, tl)
        z.q := q
        if q and z.k == 0 and z.st != 3 and (na(lz) or z.tf > lz.tf or (z.tf == lz.tf and (d == 1 ? z.bot < lz.bot : z.top > lz.top)))
            lz := z
    zLn.d := d
    if stZnLine and d != 0 and not na(stHtO)
        f_znStep(zLn, true, stHtO)
    lz
var Zn zLast = na
// the zones a signal in direction d may trade from (kind 1 = a chart CHOCH / BOS, 2 = an MSS): every touched zone (only the biggest
// timeframe's with 'biggest' ON, only the last zone with 'last zone' ON); a visit that gave an MSS does not count for a CHOCH / BOS,
// a visit that gave any signal does not count for an MSS; none = the CHOCH* line when it was touched
f_znCount(int d, int kind) =>
    array<Zn> r = array.new<Zn>()
    int big = -1
    for z in zA
        if stZnBig and not stZnLast and z.d == d and z.q and z.st != 3
            big := math.max(big, z.tf)
    for z in zA
        if z.d == d and (z.st == 1 or z.st == 2) and (kind == 1 ? z.vs != 2 : z.vs == 0) and (stZnLast ? (not na(zLast) and z.id == zLast.id) : not stZnBig or z.tf == big)
            array.push(r, z)
    if array.size(r) == 0 and stZnLine and zLn.d == d and (zLn.st == 1 or zLn.st == 2) and (kind == 1 ? zLn.vs != 2 : zLn.vs == 0)
        array.push(r, zLn)
    r
// a with-HTF signal (kind 1 / 2) closes the visit of every touched zone of that side
f_znFrz(int d, int kind) =>
    for z in zA
        if z.d == d and z.st != 0
            z.st := z.st == 1 ? 2 : z.st
            z.vs := z.vs == 0 ? kind : z.vs
    if zLn.d == d and zLn.st != 0
        zLn.st := zLn.st == 1 ? 2 : zLn.st
        zLn.vs := zLn.vs == 0 ? kind : zLn.vs
// the box of a zone that counted for a signal: ONE per zone (a later signal stretches it, 'x3'), from its candle (the CHOCH* line:
// its first touch) to the signal; green = buy, red = sell, darker when it is the last zone; an FVG with 'far half' as its far half
f_znBox(Zn z) =>
    z.n += 1
    if stZnBox
        bool  hf = z.k == 1 and stZnHalf
        float m  = (z.top + z.bot) / 2
        color c  = z.d == 1 ? (not na(zLast) and z.id == zLast.id ? #006400 : color.green) : (not na(zLast) and z.id == zLast.id ? #800000 : color.red)
        if na(z.bx)
            z.bx := box.new(z.t0, z.tf == 9 ? stHtO : hf and z.d == 1 ? m : z.top, time, z.tf == 9 ? stHtO : hf and z.d == -1 ? m : z.bot, xloc = xloc.bar_time, text_size = size.small)
            array.push(stZbx, z.bx)
            if array.size(stZbx) > 440
                box.delete(array.shift(stZbx))
        box.set_right(z.bx, time)
        box.set_text(z.bx, (z.tf == 9 ? "HTF CHOCH* line" : f_tfName(z.tf == 0 ? stHtfTf : z.tf == 1 ? stZnTf1 : stZnTf2) + (z.k == 0 ? " OB" : " FVG")) + (z.n > 1 ? " x" + str.tostring(z.n) : ""))
        box.set_border_color(z.bx, c)
        box.set_bgcolor(z.bx, color.new(c, 85))
        box.set_text_color(z.bx, c)
// the note of a setup: the zone of the biggest timeframe that allowed it (+ how many)
f_znTxt(array<Zn> r) =>
    Zn b = na
    for z in r
        b := na(b) or z.tf > b.tf ? z : b
    na(b) ? "" : b.tf == 9 ? " (CHOCH* line)" : " (" + (b.tf == 0 ? "HTF" : b.tf == 1 ? "HTF+1" : "HTF+2") + (b.k == 0 ? " order block" : " FVG") + (array.size(r) > 1 ? ", " + str.tostring(array.size(r)) + " zones)" : ")")

'''
s = s[:a] + ZONE + s[b:]

# ---------------------------------------------------------------- the zone candles, the leg, the MSS (main body, before the blocks)
a = s.index('// v15.0: the zone candles that closed, then this bar against the zones\n')
b = s.index('bool stGo   = ')
MAIN = r'''// v15.0 / v15.1: the zone candles that closed, a new higher timeframe leg, then this bar against the zones
if stZnOn
    if _z0e != nz(_z0e[1])
        f_znCandle(0, _z0e, _z0d, _z0c, _z0t, _z0b, _z0ot, _z0ob, _z0f, _z0oT)
    if stZnTf1 != "" and _z1e != nz(_z1e[1])
        f_znCandle(1, _z1e, _z1d, _z1c, _z1t, _z1b, _z1ot, _z1ob, _z1f, _z1oT)
    if stZnTf2 != "" and _z2e != nz(_z2e[1])
        f_znCandle(2, _z2e, _z2d, _z2c, _z2t, _z2b, _z2ot, _z2ob, _z2f, _z2oT)
    if stHtE != zLeg
        zLn.dead := true
        zLn := Zn.new(9, 0, 2)
        f_znKill(stHtS)
        zLeg := stHtE
    zLast := f_znBar()
// v15.1 (section 2): MSS - the chart's FVGs with their order block, its swings (N candles on each side), the first close beyond
// the newest swing WITH the higher timeframe when the move from the MSS low holds such an FVG and a zone counts for it
var float msSwH = na
var int   msSwHB = na
var float msSwL = na
var int   msSwLB = na
bool  msU = false
bool  msD = false
float msPiv = na
float msLow = na
int   msLowB = na
// a chart FVG with its order block (type 1: an opposite candle among candle 1 and the 2 before it; type 2: always) completed k
// candles ago (d = 1 up): its near edge (up: the 3rd candle's low), na = none
f_mfAt(int d, int k) =>
    bool ok = d == 1 ? low[k] > high[k + 2] and (stZnOb2 or close[k + 2] < open[k + 2] or close[k + 3] < open[k + 3] or close[k + 4] < open[k + 4]) : high[k] < low[k + 2] and (stZnOb2 or close[k + 2] > open[k + 2] or close[k + 3] > open[k + 3] or close[k + 4] > open[k + 4])
    ok ? (d == 1 ? low[k] : high[k]) : na
// the first of them whose candle 1 is at or after bar b: its near edge (na = none)
f_mfFirst(int d, int b) =>
    float e = na
    int   n = math.min(bar_index - b - 2, 1900)
    if n >= 0
        for k = n to 0
            e := f_mfAt(d, k)
            if not na(e)
                break
    e
if stZnOn and stMssOn
    if bar_index >= 2 * stMssN
        bool _ph = true
        bool _pl = true
        for _j = 0 to 2 * stMssN
            if _j != stMssN
                _ph := _ph and high[_j] < high[stMssN]
                _pl := _pl and low[_j] > low[stMssN]
        if _ph
            msSwH  := high[stMssN]
            msSwHB := bar_index - stMssN
        if _pl
            msSwL  := low[stMssN]
            msSwLB := bar_index - stMssN
    for _a = 0 to 1
        int   _d  = _a == 0 ? 1 : -1
        float _sw = _a == 0 ? msSwH : msSwL
        if not na(_sw) and (_d == 1 ? close > _sw : close < _sw)
            int _pb = _a == 0 ? msSwHB : msSwLB
            if _a == 0
                msSwH := na
            else
                msSwL := na
            if _d == stT15 and not _cU and not _cD
                [_lp, _lb] = f_retExt(_pb - 1, _d == -1, true)
                if not na(_lp) and not na(f_mfFirst(_d, _lb)) and array.size(f_znCount(_d, 2)) > 0
                    msU    := _d == 1
                    msD    := _d == -1
                    msPiv  := _sw
                    msLow  := _lp
                    msLowB := _lb
// v15.1: the setup's MSS (its low / high, the move's extreme since for rule 1, the bar) and its confirmation (0 none, 1 waiting
// for the pullback to the first FVG's near edge, 2 for a new FVG; the pullback's low / high)
var int   stSrc = 0
var float stMsLow = na
var float stMsAnch = na
var int   stMsBar = na
var int   stCf = 0
var float stCfTop = na
var int   stCfTch = na
var float stCfPb = na
var int   stCntMs = 0
var int   stCntMsCf = 0
var int   stCntMsF = 0
// v15.1 (section 8): the every-other-day mode after a pause - no new trades the rest of the day it started, then only on every
// (skip + 1)-th trading day (Monday - Friday; every day for crypto / 24-7)
f_ldAlt(int t) =>
    bool off = false
    if stLdAlt
        int  dn  = int(timestamp("UTC", year(t, stTz), month(t, stTz), dayofmonth(t, stTz), 0, 0) / 86400000)
        bool all = stCls == 4 or stWk247
        int  w   = dayofweek(t, stTz)
        off := dn <= stLdAltD or (not all and (w == dayofweek.saturday or w == dayofweek.sunday))
        if not off
            int full = int(math.floor((dn - stLdAltD) / 7))
            int m    = full * (all ? 7 : 5)
            int rem  = dn - stLdAltD - full * 7
            if rem > 0
                for k = 1 to rem
                    int ww = dayofweek((stLdAltD + full * 7 + k) * 86400000 + 43200000, "UTC")
                    m += all or (ww != dayofweek.saturday and ww != dayofweek.sunday) ? 1 : 0
            off := m % (stLdSkip + 1) != 0
    off
bool stLdAltH = stLdOn and f_ldAlt(time)
'''
s = s[:a] + MAIN + s[b:]
rep('bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt and not stLdHalt and not stEqBlock and not stPreNow',
    'bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt and not stLdHalt and not stEqBlock and not stPreNow and not stLdAltH')

# ---------------------------------------------------------------- the pause: after the pause, the every-other-day mode
rep('''var int    stCntLd   = 0
''', '''var int    stCntLd   = 0
// v15.1: after a pause (counting losses in a row again), the every-other-day mode, its losses, its start day, how many
var bool   stLdAft  = false
var bool   stLdAlt  = false
var int    stLd2Run = 0
var int    stLdAltD = na
var int    stCntLd2 = 0
''')
rep('''            if stLdOn and f_stSeqCounts(strategy.closedtrades.entry_time(_i)) and not (not na(stLdUntil) and _gX < stLdUntil)
                stLdRun := _gP < 0 ? stLdRun + 1 : _gP > 0 ? 0 : stLdRun
                if stLdRun >= stLdN
                    stLdUntil := f_ldUntil(_gX, stLdD, stCls == 4 or stWk247)
                    stLdRun   := 0
                    stCntLd   += 1''', '''            if stLdOn and f_stSeqCounts(strategy.closedtrades.entry_time(_i)) and not (not na(stLdUntil) and _gX < stLdUntil)
                if stLdAlt
                    if _gP > 0
                        stLdAlt := false
                        stLdAft := false
                        stLdRun := 0
                else if stLdAft
                    stLd2Run := _gP < 0 ? stLd2Run + 1 : _gP > 0 ? 0 : stLd2Run
                    if _gP > 0
                        stLdAft  := false
                        stLd2Run := 0
                        stLdRun  := 0
                    else if stLd2Run >= stLdN2
                        stLdAlt  := true
                        stLdAltD := int(timestamp("UTC", year(_gX, stTz), month(_gX, stTz), dayofmonth(_gX, stTz), 0, 0) / 86400000)
                        stLd2Run := 0
                        stCntLd2 += 1
                else
                    stLdRun := _gP < 0 ? stLdRun + 1 : _gP > 0 ? 0 : stLdRun
                    if stLdRun >= stLdN
                        stLdUntil := f_ldUntil(_gX, stLdD, stCls == 4 or stWk247)
                        stLdRun   := 0
                        stCntLd   += 1
                        stLdAft   := stLdN2 > 0
                        stLd2Run  := 0''')

# ---------------------------------------------------------------- cancels
rep('''if stDir != 0 and (not stGo or (trendDir != 0 and trendDir != stDir))
    f_audEnd(not stGo ? "CANCELLED - blocked" : "CANCELLED - trend flipped", stAudCancC)''', '''if stDir != 0 and (not stGo or (stSrc == 0 and trendDir != 0 and trendDir != stDir) or (stSrc == 1 and (stDir == 1 ? _cD : _cU)))
    f_audEnd(not stGo ? "CANCELLED - blocked" : stSrc == 1 ? "CANCELLED - CHOCH / BOS the other way" : "CANCELLED - trend flipped", stAudCancC)''')
rep('''// v15.0: the zone modes - a waiting order goes when the higher timeframe flips or its zone is broken by a close (an open trade
// keeps running)
if stObM and stDir != 0 and (stT15 != stDir or stZnBrk)
    f_audEnd(stT15 != stDir ? "CANCELLED - higher timeframe flipped" : "CANCELLED - its zone was broken by a close", stAudCancC)''', '''// v15.0 / v15.1: the zone modes - a waiting order goes when the higher timeframe flips, or when ALL the zones that allowed it are
// gone (broken by a close, made before a new leg); an open trade keeps running
bool _zAlive = array.size(stSup) == 0
for _z in stSup
    _zAlive := _zAlive or not _z.dead
if stObM and stDir != 0 and (stT15 != stDir or not _zAlive)
    f_audEnd(stT15 != stDir ? "CANCELLED - higher timeframe flipped" : "CANCELLED - its zones are gone (broken by a close / a new higher timeframe leg)", stAudCancC)''')
rep('''if stBosCnl and stDir != 0 and not na(stArmBar)''', '''if stBosCnl and stDir != 0 and stSrc == 0 and not na(stArmBar)''')
rep('''// RULE 1 follows the live level (Continuous mode). RULE 2 keeps the stop it was armed with: its entry is the
// fixed broken pivot, and a stop that kept moving could end up beyond that entry and silently kill the setup.
if stDir != 0 and stRule != 2 and stRule != 3 and not (stOnce and stPlaced)''', '''// v15.1: an MSS waiting for its confirmation (rule 4): the price beyond the MSS low (high) = it failed; a pullback to the first FVG
// of the MSS move, then a NEW chart FVG with its order block (candle 1 at or after the pullback candle) = enter at its close
if stDir != 0 and stRule == 4
    if stDir == 1 ? low < stMsLow : high > stMsLow
        f_audEnd("CANCELLED - MSS failed (the price went beyond the MSS " + (stDir == 1 ? "low " : "high ") + f_mt(stMsLow) + ")", stAudCancC)
        stCntMsF  += 1
        stCntCanc += 1
        stDir := 0
    else
        if bar_index > stMsBar
            stCfPb := na(stCfPb) ? (stDir == 1 ? low : high) : stDir == 1 ? math.min(stCfPb, low) : math.max(stCfPb, high)
        if stCf == 2 and bar_index - 2 >= stCfTch and not na(f_mfAt(stDir, 0))
            float _lv = str.startswith(stMssSt, "Newest") ? stCfPb : stMsLow
            stSl      := stDir == 1 ? _lv - f_stBuf(_lv) : _lv + f_stBuf(_lv)
            stRule    := 3
            stCf      := 3
            stArmBar  := bar_index
            stMktBar  := na
            stCntMsCf += 1
            if stAudit and not na(stAudLb)
                label.set_text(stAudLb, label.get_text(stAudLb) + "\\nMSS CONFIRMED - entry at the close, stop " + f_mt(stSl))
        if stCf == 1 and bar_index > stMsBar and not na(stCfTop) and (stDir == 1 ? low <= stCfTop : high >= stCfTop)
            stCf    := 2
            stCfTch := bar_index
if stDir != 0 and stSrc == 1
    stMsAnch := stDir == 1 ? math.max(stMsAnch, high) : math.min(stMsAnch, low)

// RULE 1 follows the live level (Continuous mode). RULE 2 keeps the stop it was armed with: its entry is the
// fixed broken pivot, and a stop that kept moving could end up beyond that entry and silently kill the setup.
if stDir != 0 and stSrc == 0 and stRule != 2 and stRule != 3 and not (stOnce and stPlaced)''')

# ---------------------------------------------------------------- signals, arming
rep('''stLdHalt ? "loss pause (days)" : stEqBlock''', '''stLdHalt ? "loss pause (days)" : stLdAltH ? "loss pause (every other day)" : stEqBlock''', 2)
rep('''    if stCancelSig and stDir != 0
        f_audEnd("CANCELLED - new signal", stAudCancC)''', '''    // v15.1: a CHOCH / BOS the same way that no zone allows (its visit gave the MSS) leaves a waiting MSS setup alone
    if stCancelSig and stDir != 0 and not (stSrc == 1 and not _isMs and stDir == (stSigUp ? 1 : -1) and array.size(f_znCount(stDir, 1)) == 0)
        f_audEnd("CANCELLED - new signal", stAudCancC)''')
rep('''        float _piv = stSigUp ? stCeilPrev : stFlorPrev
        float _opl = na
        if _d == 1 and not na(florS)
            _opl := florS.price
        if _d == -1 and not na(ceilS)
            _opl := ceilS.price''', '''        float _piv = _isMs ? msPiv : stSigUp ? stCeilPrev : stFlorPrev
        float _opl = _isMs ? msLow : na
        if not _isMs and _d == 1 and not na(florS)
            _opl := florS.price
        if not _isMs and _d == -1 and not na(ceilS)
            _opl := ceilS.price''')
rep('''        if _r3Use
            _hfSkip := not _r3Far and not _useM
            _use    := not _r3Far and _useM
''', '''        if _r3Use
            _hfSkip := not _r3Far and not _useM
            _use    := not _r3Far and _useM
        // v15.1: an MSS entered on its confirmation uses none of rules 1 / 2 / 3
        if _isMs and stMssCf
            _use    := true
            _hfSkip := false
            _r3Use  := false
            _r3Far  := false
            _r3Fb   := false
''')
rep('''        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : stHfOn and stR1On ? "SKIP - against the higher timeframe (filter)" : "SKIP - HTF not agreeing (rule 2 only)") : na(_opl) ? "SKIP - no stop level" : ((_agree and stR2On ? "R2" : "R1") + " ARMED")
        if stR3On''', '''        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : stHfOn and stR1On ? "SKIP - against the higher timeframe (filter)" : "SKIP - HTF not agreeing (rule 2 only)") : na(_opl) ? "SKIP - no stop level" : _isMs and stMssCf ? "WAITING for the MSS confirmation" : ((_agree and stR2On ? "R2" : "R1") + " ARMED")
        if stR3On and not (_isMs and stMssCf)''')
rep('''        int   _zf = -1
        int   _zk = -1
        float _zt = na
        float _zb = na
        if stObM
            [_a1, _a2, _a3, _a4, _a5] = f_znAllow(_d)
            _zf := _d == stT15 ? _a1 : -1
            _zk := _a2
            _zt := _a3
            _zb := _a4
            if _use and _zf < 0''', '''        array<Zn> _zc = stObM and _d == stT15 ? f_znCount(_d, _isMs ? 2 : 1) : array.new<Zn>()
        if stObM
            if _use and array.size(_zc) == 0''')
rep('''            int _lb = _d == 1 ? bar_index - florS.x1 : bar_index - ceilS.x1''', '''            int _lb = _isMs ? bar_index - msLowB : _d == 1 ? bar_index - florS.x1 : bar_index - ceilS.x1''')
rep('''            stZnF  := _zf
            stZnT  := _zt
            stZnB  := _zb
            if stObM
                _audS += _zf == 9 ? " (CHOCH* line)" : " (" + (_zf == 0 ? "HTF" : _zf == 1 ? "HTF+1" : "HTF+2") + (_zk == 0 ? " order block)" : " FVG)")''', '''            stSup  := _zc
            stSrc  := _isMs ? 1 : 0
            stCf   := 0
            if _isMs
                [_ap, _ab] = f_retExt(msLowB - 1, _d == 1, true)
                stMsLow  := _opl
                stMsAnch := _ap
                stMsBar  := bar_index
                stCntMs  += 1
                if stMssCf
                    stRule  := 4
                    stCf    := 1
                    stCfTop := f_mfFirst(_d, msLowB)
                    stCfTch := na
                    stCfPb  := na
                    stFix   := na
                    _audS   += " (pullback to " + f_mt(stCfTop) + ")"
            if stObM
                _audS += f_znTxt(_zc)''')
a = s.index('// v15.0: a chart signal with the higher timeframe closes the visit of the touched zones; the zone it came from is drawn as a')
b = s.index('if stAudit and (stSigUp or stSigDn)\n')
s = s[:a] + '''// v15.1: a with-HTF CHOCH / BOS (or an MSS): every zone that counted for it gets its box (one per zone, stretched), then the visits
// of the touched zones of that side close
if stZnOn and stT15 != 0
    int _sk = (stT15 == 1 ? _cU : _cD) ? 1 : msU or msD ? 2 : 0
    if _sk > 0
        for _z in f_znCount(stT15, _sk)
            f_znBox(_z)
        f_znFrz(stT15, _sk)
// v15.1 'show all zones': every live zone of the leg's zone that has not given a signal yet, to the last candle
if bar_index == last_bar_index and stZnOn
    while array.size(stZax) > 0
        box.delete(array.pop(stZax))
    if stZnAll
        for _z in zA
            if _z.q and _z.st != 3 and _z.n == 0
                bool  _lz = not na(zLast) and _z.id == zLast.id
                color _c  = _z.k == 0 ? (_z.d == 1 ? stZnCObB : stZnCObS) : (_z.d == 1 ? stZnCFvB : stZnCFvS)
                int   _v  = _z.tf == 0 ? stZnV0 : _z.tf == 1 ? stZnV1 : stZnV2
                float _m  = (_z.top + _z.bot) / 2
                bool  _hf = _z.k == 1 and stZnHalf
                array.push(stZax, box.new(_z.t0, _hf and _z.d == 1 ? _m : _z.top, time, _hf and _z.d == -1 ? _m : _z.bot, xloc = xloc.bar_time, border_color = _z.tf == 0 or _lz ? _c : na, border_width = _lz ? 2 : 1, bgcolor = color.new(_c, 100 - (_lz ? math.min(90, _v + 25) : _v)), text = f_tfName(_z.tf == 0 ? stHtfTf : _z.tf == 1 ? stZnTf1 : stZnTf2) + (_z.k == 0 ? " OB" : " FVG") + (_lz ? " (last)" : ""), text_size = size.small, text_color = _z.tf == 0 ? _c : stZnCLb))
''' + s[b:]
rep('''    string _aHd = (_aCh and _aBo ? "CHOCH+BOS" : _aCh ? "CHOCH" : "BOS")''', '''    string _aHd = (_isMs ? "MSS" : _aCh and _aBo ? "CHOCH+BOS" : _aCh ? "CHOCH" : "BOS")''')
rep('''    stEnt := stRule == 3 ? close : stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : f_retLvl(trendDir, mAnch, mOrig, stPbPct))''',
    '''    stEnt := stRule == 4 ? na : stRule == 3 ? close : stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : stSrc == 1 ? f_retLvl(stDir, stMsAnch, stMsLow, stPbPct) : f_retLvl(trendDir, mAnch, mOrig, stPbPct))''')
rep('''    float _pdL  = stPdOn ? f_retLvl(trendDir, mAnch, mOrig, stPdPct) : na''', '''    float _pdL  = stPdOn ? (stSrc == 1 ? f_retLvl(stDir, stMsAnch, stMsLow, stPdPct) : f_retLvl(trendDir, mAnch, mOrig, stPdPct)) : na''')

# ---------------------------------------------------------------- the table
line_sub('    f_stCell(50, "ORDER BLOCK ZONES (section 2)"', 'skipped (no zone) " + str.tostring(stCntOb)',
         'skipped (no zone) " + str.tostring(stCntOb) + (na(zLast) ? "" : "  |  last zone " + f_tfName(zLast.tf == 0 ? stHtfTf : zLast.tf == 1 ? stZnTf1 : stZnTf2) + " OB " + f_mt(zLast.bot) + " - " + f_mt(zLast.top)) + (stMssOn ? "  |  MSS " + str.tostring(stCntMs) + (stMssCf ? " (confirmed " + str.tostring(stCntMsCf) + ", failed " + str.tostring(stCntMsF) + ")" : "") : "")')
rep('''    string _ldT = not stLdOn ? "off" : (stLdHalt ? ("PAUSED until " + str.format_time(stLdUntil, "EEE dd MMM HH:mm", stTz)) : (str.tostring(stLdRun) + " of " + str.tostring(stLdN) + " losses in a row")) + "  |  pauses so far " + str.tostring(stCntLd)
    f_stCell(45, "PAUSE AFTER LOSSES (section 8)", _ldT, not stLdOn ? color.gray : stLdHalt ? color.red : color.aqua)''',
    '''    string _ldT = not stLdOn ? "off" : (stLdHalt ? ("PAUSED until " + str.format_time(stLdUntil, "EEE dd MMM HH:mm", stTz)) : stLdAlt ? (stLdAltH ? "EVERY OTHER DAY - not today" : "EVERY OTHER DAY - a trading day") + " (until a winning trade)" : stLdAft ? "after the pause: " + str.tostring(stLd2Run) + " of " + str.tostring(stLdN2) + " losses in a row" : (str.tostring(stLdRun) + " of " + str.tostring(stLdN) + " losses in a row")) + "  |  pauses so far " + str.tostring(stCntLd) + (stLdN2 > 0 ? " / every-other-day " + str.tostring(stCntLd2) : "")
    f_stCell(45, "PAUSE AFTER LOSSES (section 8)", _ldT, not stLdOn ? color.gray : stLdHalt or stLdAltH ? color.red : color.aqua)''')
rep("// v15.0 checks", "// v15.0 checks", 0)

assert 'stZnBrk' not in s and 'f_znAllow' not in s and 'stZnF ' not in s, 'old names left'
assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)

# ---------------------------------------------------------------- v15.1 size: dead code in the higher timeframe function
# f_tfPack carried a second (internal) swing tracker - tkAH / tkAL, the rm* / hnt* helpers, the qHi / qLo queues and the iCe / iFl
# levels. Nothing the function returns (trend, leg start, leg extreme, events, leg start time) reads any of it: it was dead code
# (checked by tools/ea/pinedead.py: every removed line defines only values the outputs never read). Removed.
s = open(dst).read()
L = s.split('\n')
a = [i for i, l in enumerate(L) if l.startswith('f_tfPack(bool on) =>')][0]
b = [i for i in range(a, len(L)) if L[i] == '    [trOut, loOut, lxOut, ecOut, lgOut]'][0]
body = L[a:b + 1]
drop = set()
def rng(first, last):
    i = next(k for k, l in enumerate(body) if l.startswith(first))
    j = next(k for k in range(i, len(body)) if body[k].startswith(last))
    drop.update(range(i, j + 1))
rng('        var SwingTracker tkAH', '        var SwingTracker tkAL')
rng('        var float iCe  = na', '        var float iFl  = na')
rng('        var bool  hntH   = true', '            rmHiLo  := low')
rng('        int _hPot0 = tkAH.potentialBar', '            rmHiB := bar_index')
rng('        var int   iAnc = na', '                iFlB := na')
k = max(drop)
if body[k + 1] == '' : pass
body = [l for i, l in enumerate(body) if i not in drop]
# a blank line left inside the function body at the end
while body[-2] == '': del body[-2]
L[a:b + 1] = body
s = '\n'.join(L)
s = s.replace('table.cell(stTbl, 0, 0, "STRATEGY v15.0"', 'table.cell(stTbl, 0, 0, "STRATEGY v15.1"')
assert 'tkAH' not in s and 'iCe' not in s
open(dst, 'w').write(s)
print('dead code removed from f_tfPack:', len(drop), 'lines')

# ---------------------------------------------------------------- v15.1 size: the same orders written once (long / short in one call)
s = open(dst).read()
def rp(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('size step: expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)
rp('''            if stDir == 1
                strategy.entry(stPendId, strategy.long, qty = _qm, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg("buy", 1, stEnt, stSl, stTgt, _qm, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", 1, close, stSl, stTgt, _qm, stPendId))
            else
                strategy.entry(stPendId, strategy.short, qty = _qm, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg("sell", -1, stEnt, stSl, stTgt, _qm, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", -1, close, stSl, stTgt, _qm, stPendId))
''', '''            strategy.entry(stPendId, stDir == 1 ? strategy.long : strategy.short, qty = _qm, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg(stDir == 1 ? "buy" : "sell", stDir, stEnt, stSl, stTgt, _qm, stPendId))
            strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", stDir, close, stSl, stTgt, _qm, stPendId))
''')
rp('''                if stDir == 1
                    strategy.entry(_pId, strategy.long, qty = _q1, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg("buy", 1, stEnt, stSl, _tp1, _q1, _pId))
                    strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", 1, close, stSl, _tp1, _q1, _pId))
                else
                    strategy.entry(_pId, strategy.short, qty = _q1, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg("sell", -1, stEnt, stSl, _tp1, _q1, _pId))
                    strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", -1, close, stSl, _tp1, _q1, _pId))
''', '''                strategy.entry(_pId, stDir == 1 ? strategy.long : strategy.short, qty = _q1, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg(stDir == 1 ? "buy" : "sell", stDir, stEnt, stSl, _tp1, _q1, _pId))
                strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", stDir, close, stSl, _tp1, _q1, _pId))
''')
# the zones: 'touched' = state 1 or 2
rp('(z.st == 1 or z.st == 2)', 'z.st % 3 > 0')
rp('(zLn.st == 1 or zLn.st == 2)', 'zLn.st % 3 > 0')
open(dst, 'w').write(s)

# ---------------------------------------------------------------- v15.1 size: texts written once
s = open(dst).read()
# the timeframe name of a zone
rp('''string stZnTf2 = stZnTf1 == "" ? "" : f_znUp(stZnTf1)
''', '''string stZnTf2 = stZnTf1 == "" ? "" : f_znUp(stZnTf1)
f_znTf(int tf) =>
    f_tfName(tf == 0 ? stHtfTf : tf == 1 ? stZnTf1 : stZnTf2)
''')
rp('f_tfName(z.tf == 0 ? stHtfTf : z.tf == 1 ? stZnTf1 : stZnTf2)', 'f_znTf(z.tf)')
rp('f_tfName(_z.tf == 0 ? stHtfTf : _z.tf == 1 ? stZnTf1 : stZnTf2)', 'f_znTf(_z.tf)')
rp('f_tfName(zLast.tf == 0 ? stHtfTf : zLast.tf == 1 ? stZnTf1 : stZnTf2)', 'f_znTf(zLast.tf)')
rp('''        color c  = z.d == 1 ? (not na(zLast) and z.id == zLast.id ? #006400 : color.green) : (not na(zLast) and z.id == zLast.id ? #800000 : color.red)''',
   '''        bool  lz = not na(zLast) and z.id == zLast.id
        color c  = z.d == 1 ? (lz ? #006400 : color.green) : (lz ? #800000 : color.red)''')
# the next US release (table)
rp('''            if not na(e1) and e1 + stAuPost * 60000 > timenow and (na(_bT) or e1 < _bT)
                _bT := e1
                _bN := "NFP"
            if not na(e2) and e2 + stAuPost * 60000 > timenow and (na(_bT) or e2 < _bT)
                _bT := e2
                _bN := "Jobless claims"
            if not na(e3) and e3 + stAuPost * 60000 > timenow and (na(_bT) or e3 < _bT)
                _bT := e3
                _bN := "ISM Manufacturing"
            if not na(e4) and e4 + stAuPost * 60000 > timenow and (na(_bT) or e4 < _bT)
                _bT := e4
                _bN := "ISM Services"
''', '''            for [q, e] in array.from(e1, e2, e3, e4)
                if not na(e) and e + stAuPost * 60000 > timenow and (na(_bT) or e < _bT)
                    _bT := e
                    _bN := array.get(array.from("NFP", "Jobless claims", "ISM Manufacturing", "ISM Services"), q)
''')
# what blocks new trades now: one text for the audit label and the table
rp('''    _audS := "SKIP - " + (not stOn ? "trading off" : stDDHit ? "drawdown stop" : stHolNow ? "US holiday" : stNwNow ? "news window" : stPreNow ? "news soon - no new trades" : stWkBlock ? "weekend" : stDayHalt ? "daily limit" : stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : stLdHalt ? "loss pause (days)" : stLdAltH ? "loss pause (every other day)" : stEqBlock ? "waiting for the higher timeframe equilibrium" : "blocked")''',
   '''    _audS := "SKIP - " + f_blk()''')
rp('''bool stGo   = stOn and not stSeqHalt''', '''// what blocks new trades now ("" = nothing) - the audit label and the table
f_blk() =>
    not stOn ? "trading off" : stDDHit ? "drawdown stop" : stHolNow ? "US holiday" : stNwNow ? "news window" : stPreNow ? "news soon - no new trades" : stWkBlock ? "weekend" : stDayHalt ? "daily limit" : stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : stLdHalt ? "loss pause (days)" : stLdAltH ? "loss pause (every other day)" : stEqBlock ? "waiting for the higher timeframe equilibrium" : ""
bool stGo   = stOn and not stSeqHalt''')
L = s.split('\n')
k = [i for i, l in enumerate(L) if l.startswith('    f_stCell(39, "BLOCKED NOW",')]
assert len(k) == 1
m = re.match(r'^(    f_stCell\(39, "BLOCKED NOW",\s+)(.*), (\(stDDHit or .*)\)$', L[k[0]])
assert m, L[k[0]][:200]
L[k[0]] = m.group(1) + 'f_blk() == "" ? "-" : f_blk(), ' + m.group(3) + ')'
s = '\n'.join(L)
# the skip texts of the RSI / EMA filters
rp('''f_xRsOk(int d, float v, string md, float lv) =>
    str.startswith(md, "Pullback") ? (d == 1 ? v < lv : v > 100 - lv) : (d == 1 ? v > lv : v < 100 - lv)
''', '''f_xRsOk(int d, float v, string md, float lv) =>
    str.startswith(md, "Pullback") ? (d == 1 ? v < lv : v > 100 - lv) : (d == 1 ? v > lv : v < 100 - lv)
f_xRsT(int d, int n, string tf, float v, string md, float lv) =>
    "RSI(" + str.tostring(n) + ") " + f_xTfTxt(tf) + " = " + str.tostring(v, "#.#") + ", a " + (d == 1 ? "buy" : "sell") + " needs " + (str.startswith(md, "Pullback") == (d == 1) ? "below " : "above ") + str.tostring(d == 1 ? lv : 100 - lv, "#.#")
f_xEmT(int d, bool two, int fast, int n, string tf, float sl) =>
    (two ? "EMA " + str.tostring(fast) : "price " + f_mt(close)) + (d == 1 ? " not above" : " not below") + " the EMA " + str.tostring(n) + " " + f_xTfTxt(tf) + " (" + f_mt(sl) + ")"
''')
rp('''                _xs := "RSI(" + str.tostring(stRsLLen) + ") " + f_xTfTxt(stRsLTfS) + " = " + str.tostring(stRsLv, "#.#") + ", a " + (_d == 1 ? "buy" : "sell") + " needs " + (str.startswith(stRsLMode, "Pullback") == (_d == 1) ? "below " : "above ") + str.tostring(_d == 1 ? stRsLLvl : 100 - stRsLLvl, "#.#")''',
   '''                _xs := f_xRsT(_d, stRsLLen, stRsLTfS, stRsLv, stRsLMode, stRsLLvl)''')
rp('''                _xs := "RSI(" + str.tostring(stRsHLen) + ") " + f_xTfTxt(stRsHTfS) + " = " + str.tostring(stRsHv, "#.#") + ", a " + (_d == 1 ? "buy" : "sell") + " needs " + (str.startswith(stRsHMode, "Pullback") == (_d == 1) ? "below " : "above ") + str.tostring(_d == 1 ? stRsHLvl : 100 - stRsHLvl, "#.#")''',
   '''                _xs := f_xRsT(_d, stRsHLen, stRsHTfS, stRsHv, stRsHMode, stRsHLvl)''')
rp('''                _xs := (_emL2 ? "EMA " + str.tostring(stEmLFast) : "price " + f_mt(close)) + (_d == 1 ? " not above" : " not below") + " the EMA " + str.tostring(stEmLLen) + " " + f_xTfTxt(stEmLTfS) + " (" + f_mt(stEmLs) + ")"''',
   '''                _xs := f_xEmT(_d, _emL2, stEmLFast, stEmLLen, stEmLTfS, stEmLs)''')
rp('''                _xs := (_emH2 ? "EMA " + str.tostring(stEmHFast) : "price " + f_mt(close)) + (_d == 1 ? " not above" : " not below") + " the EMA " + str.tostring(stEmHLen) + " " + f_xTfTxt(stEmHTfS) + " (" + f_mt(stEmHs) + ")"''',
   '''                _xs := f_xEmT(_d, _emH2, stEmHFast, stEmHLen, stEmHTfS, stEmHs)''')
open(dst, 'w').write(s)

# ---------------------------------------------------------------- v15.1 size: the chart engine's ceiling / floor written once
# (the same steps in the same order: adopt + IDM for the ceiling then the floor, then the break / sweep of the ceiling then the
# floor; checked bar by bar against the file before this step with tools/ea/pinerun.py)
rp('''    if not na(phP)
        bool _cSwept = false
        bool _cEq    = false
        if not na(ceilS)
            _cSwept := not na(ceilS.swpP)
            _cEq    := phP == ceilS.price
        bool adoptC  = trendDir == 0 ? (phP >= allHi and not _cSwept and not _cEq) : na(ceilS)
        if adoptC
            ceilS.drop()
            ceilS := mkSLine(phP, phB, trendDir == -1 ? 2 : 0, drawOk)
            ceilS.armIdm()

    if not na(plP)
        bool _fSwept = false
        bool _fEq    = false
        if not na(florS)
            _fSwept := not na(florS.swpP)
            _fEq    := plP == florS.price
        bool adoptF  = trendDir == 0 ? (plP <= allLo and not _fSwept and not _fEq) : na(florS)
        if adoptF
            florS.drop()
            florS := mkSLine(plP, plB, trendDir == 1 ? 3 : 1, drawOk)
            florS.armIdm()

    if not na(ceilS) and not ceilS.idmHit and not na(ceilS.idmP) and low < ceilS.idmP
        ceilS.idmHit := true
    if not na(florS) and not florS.idmHit and not na(florS.idmP) and high > florS.idmP
        florS.idmHit := true

    if not na(ceilS) and bar_index > ceilS.born
        if close > ceilS.price and (trendDir == -1 or not altMode or ceilS.idmHit or na(ceilS.idmP))
            bool isCho = trendDir == -1
            evChoUp := isCho
            evBosUp := not isCho
            int srcC = ceilS.x1
            ceilS.freeze()
            [rpC, rbC] = f_retExt(srcC, false, true)
            if not na(rpC)
                florS.drop()
                florS := mkSLine(rpC, rbC, 3, drawOk)
                florS.armIdm()
            if not isCho and ceilS.idmHit and not na(rpC) and drawOk and f_xNear(rbC)
                f_addLb(mainLb, mainCnt, label.new(rbC, na, "#", yloc = yloc.belowbar, style = label.style_none, textcolor = color.gray, size = size.small))
            trendDir := 1
            ceilS := na
        else
            if high > ceilS.price
                if na(ceilS.swpP) or high > ceilS.swpP
                    ceilS.swpP := high
                    ceilS.swpB := bar_index
                    ceilS.swpT := false
                if altMode and not ceilS.idmHit and not na(ceilS.idmP) and close > ceilS.price and not na(ceilS.swpP)
                    float mpC = ceilS.swpP
                    int   mbC = ceilS.swpB
                    int   mdC = ceilS.sid
                    ceilS.drop()
                    ceilS := mkSLine(mpC, mbC, mdC, drawOk)
                    ceilS.armIdm()
            if not na(ceilS.swpP) and na(ceilS.refP)
                [refPc, refBc] = f_retExt(ceilS.x1, false, false)
                ceilS.refP := refPc
            if not na(ceilS.swpB) and ceilS.swpB == bar_index and trendDir == 1 and not na(ceilS.refP) and low < ceilS.refP
                ceilS.swpT := true
            if trendDir == 1 and not na(ceilS.swpP) and not na(ceilS.refP) and low < ceilS.refP and (not ceilS.swpT or f_swpConf(mnHiB, ceilS.swpB))
                float spC = ceilS.swpP
                int   sbC = ceilS.x1
                if not na(spC)
                    int sdC = ceilS.sid
                    ceilS.drop()
                    ceilS := mkSLine(spC, sbC, sdC, drawOk)
                    ceilS.armIdm()

    if not na(florS) and bar_index > florS.born
        if close < florS.price and (trendDir == 1 or not altMode or florS.idmHit or na(florS.idmP))
            bool isCho = trendDir == 1
            evChoDn := isCho
            evBosDn := not isCho
            int srcF = florS.x1
            florS.freeze()
            [rpF, rbF] = f_retExt(srcF, true, true)
            if not na(rpF)
                ceilS.drop()
                ceilS := mkSLine(rpF, rbF, 2, drawOk)
                ceilS.armIdm()
            if not isCho and florS.idmHit and not na(rpF) and drawOk and f_xNear(rbF)
                f_addLb(mainLb, mainCnt, label.new(rbF, na, "#", yloc = yloc.abovebar, style = label.style_none, textcolor = color.gray, size = size.small))
            trendDir := -1
            florS := na
        else
            if low < florS.price
                if na(florS.swpP) or low < florS.swpP
                    florS.swpP := low
                    florS.swpB := bar_index
                    florS.swpT := false
                if altMode and not florS.idmHit and not na(florS.idmP) and close < florS.price and not na(florS.swpP)
                    float mpF = florS.swpP
                    int   mbF = florS.swpB
                    int   mdF = florS.sid
                    florS.drop()
                    florS := mkSLine(mpF, mbF, mdF, drawOk)
                    florS.armIdm()
            if not na(florS.swpP) and na(florS.refP)
                [refPf, refBf] = f_retExt(florS.x1, true, false)
                florS.refP := refPf
            if not na(florS.swpB) and florS.swpB == bar_index and trendDir == -1 and not na(florS.refP) and high > florS.refP
                florS.swpT := true
            if trendDir == -1 and not na(florS.swpP) and not na(florS.refP) and high > florS.refP and (not florS.swpT or f_swpConf(mnLoB, florS.swpB))
                float spF = florS.swpP
                int   sbF = florS.x1
                if not na(spF)
                    int sdF = florS.sid
                    florS.drop()
                    florS := mkSLine(spF, sbF, sdF, drawOk)
                    florS.armIdm()
''', '''    // the ceiling (_k = 0, u = 1) and the floor (_k = 1, u = -1): a new pivot becomes the level, the IDM taken
    for _k = 0 to 1
        int   _u = 1 - 2 * _k
        SLine _s = _k == 0 ? ceilS : florS
        float _p = _k == 0 ? phP : plP
        if not na(_p)
            bool _sw = false
            bool _eq = false
            if not na(_s)
                _sw := not na(_s.swpP)
                _eq := _p == _s.price
            if trendDir == 0 ? ((_p - (_k == 0 ? allHi : allLo)) * _u >= 0 and not _sw and not _eq) : na(_s)
                _s.drop()
                _s := mkSLine(_p, _k == 0 ? phB : plB, (trendDir == -_u ? 2 : 0) + _k, drawOk)
                _s.armIdm()
        if not na(_s) and not _s.idmHit and not na(_s.idmP) and ((_k == 0 ? low : high) - _s.idmP) * _u < 0
            _s.idmHit := true
        if _k == 0
            ceilS := _s
        else
            florS := _s

    // a close beyond the level = CHOCH / BOS; else its sweep and re-level
    for _k = 0 to 1
        int   _u = 1 - 2 * _k
        SLine _s = _k == 0 ? ceilS : florS
        if not na(_s) and bar_index > _s.born
            if (close - _s.price) * _u > 0 and (trendDir == -_u or not altMode or _s.idmHit or na(_s.idmP))
                bool isCho = trendDir == -_u
                if _k == 0
                    evChoUp := isCho
                    evBosUp := not isCho
                else
                    evChoDn := isCho
                    evBosDn := not isCho
                int src = _s.x1
                _s.freeze()
                [rp, rb] = f_retExt(src, _k == 1, true)
                SLine _o = _k == 0 ? florS : ceilS
                if not na(rp)
                    _o.drop()
                    _o := mkSLine(rp, rb, 3 - _k, drawOk)
                    _o.armIdm()
                if not isCho and _s.idmHit and not na(rp) and drawOk and f_xNear(rb)
                    f_addLb(mainLb, mainCnt, label.new(rb, na, "#", yloc = _k == 0 ? yloc.belowbar : yloc.abovebar, style = label.style_none, textcolor = color.gray, size = size.small))
                trendDir := _u
                _s := na
                if _k == 0
                    florS := _o
                else
                    ceilS := _o
            else
                float _x = _k == 0 ? high : low
                float _y = _k == 0 ? low : high
                if (_x - _s.price) * _u > 0
                    if na(_s.swpP) or (_x - _s.swpP) * _u > 0
                        _s.swpP := _x
                        _s.swpB := bar_index
                        _s.swpT := false
                    if altMode and not _s.idmHit and not na(_s.idmP) and (close - _s.price) * _u > 0 and not na(_s.swpP)
                        float mp = _s.swpP
                        int   mb = _s.swpB
                        int   md = _s.sid
                        _s.drop()
                        _s := mkSLine(mp, mb, md, drawOk)
                        _s.armIdm()
                if not na(_s.swpP) and na(_s.refP)
                    [refP, refB] = f_retExt(_s.x1, _k == 1, false)
                    _s.refP := refP
                if not na(_s.swpB) and _s.swpB == bar_index and trendDir == _u and not na(_s.refP) and (_y - _s.refP) * _u < 0
                    _s.swpT := true
                if trendDir == _u and not na(_s.swpP) and not na(_s.refP) and (_y - _s.refP) * _u < 0 and (not _s.swpT or f_swpConf(_k == 0 ? mnHiB : mnLoB, _s.swpB))
                    float sp = _s.swpP
                    int   sb = _s.x1
                    if not na(sp)
                        int sd = _s.sid
                        _s.drop()
                        _s := mkSLine(sp, sb, sd, drawOk)
                        _s.armIdm()
        if _k == 0
            ceilS := _s
        else
            florS := _s
''')
open(dst, 'w').write(s)

# ---------------------------------------------------------------- v15.1 size: small ones (same results)
# the cancel of the waiting order: f_stCancel reads the order itself (it was always called with stOrdLive, stPendId)
rp('''f_stCancel(bool live, string id) =>
    bool _do = live and id != ""
    if _do
        strategy.cancel(id)
        strategy.cancel(id + " exit")
        // v9.0 e: the early-profit part of the same setup
        if stPpSent
            strategy.cancel(id + "p")
            strategy.cancel(id + "p exit")
    _do
''', '''f_stCancel() =>
    bool _do = stOrdLive and stPendId != ""
    if _do
        strategy.cancel(stPendId)
        strategy.cancel(stPendId + " exit")
        // v9.0 e: the early-profit part of the same setup
        if stPpSent
            strategy.cancel(stPendId + "p")
            strategy.cancel(stPendId + "p exit")
    _do
''')
s, _n = re.subn(r'\n( +)if f_stCancel\(stOrdLive, stPendId\)\n\1    stCnlSent := true\n', lambda m: '\n%sstCnlSent := f_stCancel() or stCnlSent\n' % m.group(1), s)
assert _n == 12, _n
assert 'f_stCancel(stOrdLive' not in s
# the loss-recovery modes by their names
rp('''bool stSeqPlus = stSeqMode == "Rule A+ (only when total P&L is below 0: that loss + amount)" or stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)" or stSeqMode == "Rule C+ (only when total P&L is below 0: that loss)"''',
   '''bool stSeqPlus = str.contains(stSeqMode, "+ (")''')
rp('''bool stSplitM = stSeqMode == "Rule A split (A, the base grows with the profit - section 7)" or stSeqMode == "Rule B split (B, the base grows with the profit - section 7)" or stSeqMode == "Rule C split (C, the base grows with the profit - section 7)"''',
   '''bool stSplitM = str.contains(stSeqMode, " split (")''')
rp('''if stSeqMode == "Rule A - recover losses + base profit" or stSeqMode == "Rule A+ (only when total P&L is below 0: that loss + amount)" or stSeqMode == "Rule A split (A, the base grows with the profit - section 7)"''',
   '''if str.startswith(stSeqMode, "Rule A")''')
rp('''else if stSeqMode == "Rule B - double the losses" or stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)" or stSeqMode == "Rule B split (B, the base grows with the profit - section 7)"''',
   '''else if str.startswith(stSeqMode, "Rule B")''')
rp('''else if stSeqMode == "Rule C - carry the losses" or stSeqMode == "Rule C+ (only when total P&L is below 0: that loss)" or stSeqMode == "Rule C split (C, the base grows with the profit - section 7)"''',
   '''else if str.startswith(stSeqMode, "Rule C")''')
L = s.split('\n')
k = [i for i, l in enumerate(L) if l.startswith('    string _sqM = stSeqMode == "Rule A - recover losses + base profit" ? ')]
assert len(k) == 1
L[k[0]] = '''    string _sqM = ""
    if stSeqMode != "Off"
        _sqM := str.substring(stSeqMode, 5, stSplitM ? 12 : stSeqPlus ? 7 : 6) + " - " + (str.startswith(stSeqMode, "Rule B") ? "2 x " : "") + (stSeqPlus ? "total below 0" : "loss since the high") + (str.startswith(stSeqMode, "Rule A") ? " + " + str.tostring(stSeqAdd) : "") + (stSplitM ? ", base from the profit steps" : "")'''
s = '\n'.join(L)
# a with-HTF signal closes the visits: the zones and the CHOCH* line in one loop
rp('''    for z in zA
        if z.d == d and z.st != 0
            z.st := z.st == 1 ? 2 : z.st
            z.vs := z.vs == 0 ? kind : z.vs
    if zLn.d == d and zLn.st != 0
        zLn.st := zLn.st == 1 ? 2 : zLn.st
        zLn.vs := zLn.vs == 0 ? kind : zLn.vs
''', '''    for z in array.concat(array.copy(zA), array.from(zLn))
        if z.d == d and z.st != 0
            z.st := z.st == 1 ? 2 : z.st
            z.vs := z.vs == 0 ? kind : z.vs
''')
# the liquidity pools: highs then lows (each pool on its own, so the order does not matter)
rp('''if stLqOn
    if not na(stSwH)
        array.push(stLqH, stSwH)
        if array.size(stLqH) > 60
            array.shift(stLqH)
    if not na(stSwL)
        array.push(stLqL, stSwL)
        if array.size(stLqL) > 60
            array.shift(stLqL)
    if array.size(stLqH) > 0
        for _i = array.size(stLqH) - 1 to 0
            if array.get(stLqH, _i) <= high
                array.remove(stLqH, _i)
    if array.size(stLqL) > 0
        for _i = array.size(stLqL) - 1 to 0
            if array.get(stLqL, _i) >= low
                array.remove(stLqL, _i)
''', '''if stLqOn
    for _k = 0 to 1
        array<float> _a = _k == 0 ? stLqH : stLqL
        float _v = _k == 0 ? stSwH : stSwL
        if not na(_v)
            array.push(_a, _v)
            if array.size(_a) > 60
                array.shift(_a)
        if array.size(_a) > 0
            for _i = array.size(_a) - 1 to 0
                if _k == 0 ? array.get(_a, _i) <= high : array.get(_a, _i) >= low
                    array.remove(_a, _i)
''')
open(dst, 'w').write(s)

# ---------------------------------------------------------------- v15.1 size: SwingTracker defaults, the two parts of an order in one loop
rp('''    int   count
    float refLevel
    bool  swept
''', '''    int   count = 0
    float refLevel
    bool  swept = false
''')
s, _n = re.subn(r'SwingTracker\.new\((true|false),\s+na, na, 0, na, false\)', r'SwingTracker.new(\1)', s)
assert _n == 6, _n
rp('''            float _qm = _q - _q1
            strategy.entry(stPendId, stDir == 1 ? strategy.long : strategy.short, qty = _qm, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg(stDir == 1 ? "buy" : "sell", stDir, stEnt, stSl, stTgt, _qm, stPendId))
            strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", stDir, close, stSl, stTgt, _qm, stPendId))
            if _q1 > 0
                // the early target is pushed out to cover its costs, like the main target; never beyond the main target
                float _tp1 = stDir == 1 ? stEnt + _r * stPpR + (stCmTgt and not stPxOff and _stPvA > 0 ? stCmU * (stPpR + 1.0) / _stPvA : 0.0) : stEnt - _r * stPpR - (stCmTgt and not stPxOff and _stPvA > 0 ? stCmU * (stPpR + 1.0) / _stPvA : 0.0)
                _tp1 := stDir == 1 ? math.min(_tp1, stTgt) : math.max(_tp1, stTgt)
                string _pId = stPendId + "p"
                strategy.entry(_pId, stDir == 1 ? strategy.long : strategy.short, qty = _q1, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg(stDir == 1 ? "buy" : "sell", stDir, stEnt, stSl, _tp1, _q1, _pId))
                strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", stDir, close, stSl, _tp1, _q1, _pId))
                stPpSent  := true
''', '''            // the early target is pushed out to cover its costs, like the main target; never beyond the main target
            float _c1  = stCmTgt and not stPxOff and _stPvA > 0 ? stCmU * (stPpR + 1.0) / _stPvA : 0.0
            float _tp1 = stDir == 1 ? math.min(stEnt + _r * stPpR + _c1, stTgt) : math.max(stEnt - _r * stPpR - _c1, stTgt)
            // the main part, then the early part (if any): its entry and its bracket
            for [_j, _qq] in array.from(_q - _q1, _q1)
                if _qq > 0
                    string _id = stPendId + (_j == 0 ? "" : "p")
                    float  _tp = _j == 0 ? stTgt : _tp1
                    strategy.entry(_id, stDir == 1 ? strategy.long : strategy.short, qty = _qq, limit = stRule == 3 ? na : stEnt, alert_message = f_stMsg(stDir == 1 ? "buy" : "sell", stDir, stEnt, stSl, _tp, _qq, _id))
                    strategy.exit(_id + " exit", _id, stop = stSl, limit = _tp, alert_message = f_stMsg("close", stDir, close, stSl, _tp, _qq, _id))
            if _q1 > 0
                stPpSent  := true
''')
open(dst, 'w').write(s)

# ---------------------------------------------------------------- the 'no RSI / EMA filters' file (third argument): the complete text
# without the 4 RSI / EMA filters of section 4 (the same cut as v15.0, pine150lite.py)
assert all(ord(c) < 128 for c in s), 'not ASCII'
if len(sys.argv) > 3:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pine150lite
    t = pine150lite.strip(s)
    for w in ('f_xRsT', 'f_xEmT'):
        assert w not in t, 'lite: %s left' % w
    k = t.index('  -  v15.1  -  ')
    t = t[:k] + '  -  v15.1 (no RSI / EMA filters)  -  ' + t[k + len('  -  v15.1  -  '):]
    open(sys.argv[3], 'w').write(t)
    print('written', sys.argv[3])
