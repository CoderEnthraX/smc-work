# v10.4 -> v11.0 : (1) pause for D days after N losses in a row, (2) 'higher timeframe favourable' modes of
# 'Take trades on', (3) higher timeframe equilibrium first. All optional, all OFF by default.
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v10.4.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


FAV = " - higher timeframe favourable"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v10.4  -  ")
s = rep(s, l2, l2.replace("v10.4  -  ", "v11.0  -  ", 1).replace(
    "  -  ASCII only",
    ", v11.0: pause for days after losses in a row, higher-timeframe-favourable modes, higher timeframe equilibrium first  -  ASCII only"))

# ---- feature 2: three more choices for 'Take trades on' (the old ones unchanged, so saved settings still match)
s = rep(s, 'stSigSrc = input.string("CHOCH only", "Take trades on", options = ["CHOCH only", "BOS only", "CHOCH and BOS"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n',
        'stSigSrc = input.string("CHOCH only", "Take trades on", options = ["CHOCH only", "BOS only", "CHOCH and BOS", "CHOCH only' + FAV + '", "BOS only' + FAV + '", "CHOCH and BOS' + FAV + '"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n'
        "HIGHER TIMEFRAME FAVOURABLE (v11.0, the last three choices): the same signals, but ONLY in the direction of the higher timeframe "
        "(the one set below - Auto: 1m chart -> 15m, 5m -> 1h, 15m -> 4h, 1h -> 1D, 4h -> 1W, 1D -> 1M). Higher timeframe bullish: only buys. Bearish: only sells. "
        "Not clear yet: no trades. Entry: rule 1 only = the pullback %, rule 2 on = the broken pivot. A waiting order is cancelled when the higher timeframe flips "
        "against it; an open trade keeps running to its stop or target.\\n\\n")

# ---- the new settings, after the last one (shown in their own groups 36 and 37, at the end of the panel)
T_LD = ("OFF (default): no pause.\\n\\nON: after this many LOSING trades IN A ROW, no new trade for the rest of that day plus the number of days below. "
        "A loss is any trade with Net P&L below 0 after costs (as the List of Trades shows it); a winning trade starts the count again at 0; a trade at exactly 0 changes nothing. "
        "The early-profit part of a setup (group 34 e) is not counted.\\n\\n"
        "A trade still open when the limit is reached keeps running to its stop or target; a waiting order is cancelled. "
        "After the pause trading starts again by itself and the count starts again at 0; trades that close during the pause are not counted.\\n\\n"
        "Only the trades that 'loss recovery counts from' (group 21) counts are counted - with 'When the strategy goes live' the replayed backtest cannot start your alert paused.")
T_LDN = "Example: 3 = the 3rd losing trade in a row starts the pause."
T_LDD = ("The days after the rest of that day. Gold, forex, silver and indices: only Monday to Friday count. Crypto (or 'Trade 24/7' on): every day counts. "
         "A day starts at 00:00 in the session timezone (group 20).\\n\\n"
         "Example, 2 days, gold: 3rd loss on Monday 14:00 -> no trades for the rest of Monday, Tuesday and Wednesday -> trading again on Thursday. "
         "3rd loss on Thursday -> Friday and Monday are the 2 days -> trading again on Tuesday.")
T_EQ = ("OFF (default): the chart trades by itself, as before.\\n\\n"
        "ON: every CHOCH or BOS on the HIGHER timeframe (the one set in group 20 - Auto: 1m chart -> 15m, 5m -> 1h, 15m -> 4h, 1h -> 1D, 4h -> 1W, 1D -> 1M) "
        "starts a new higher-timeframe leg and CLOSES the gate: no trades, buys or sells, until the price has pulled back to the equilibrium % below of that leg - "
        "a touch is enough (a wick counts), deeper is fine. Then the gate stays OPEN and the chart trades by 'Take trades on', rule 1 and rule 2, until the next "
        "higher-timeframe CHOCH or BOS closes it again. If the leg runs further before the pullback, the level moves with it.\\n\\n"
        "A waiting order is cancelled when the gate closes; an open trade keeps running. The higher-timeframe CHOCH / BOS counts once its candle has closed, "
        "so the backtest and live are the same.\\n\\n"
        "Example, 50%: the 15m breaks up and its leg runs from 3,950 to 4,050 -> the level is 4,000. No 1m trades until the price touches 4,000, then the 1m "
        "trades normally until the next 15m CHOCH or BOS.\\n\\n"
        "Together with a 'higher timeframe favourable' mode: only trades with the higher timeframe, and only after its pullback. "
        "The higher timeframe must be ABOVE the chart, or the gate never opens.")
T_EQP = ("50 (default) = the middle of the higher-timeframe leg. 61.8 or 70.5 = a deeper pullback first. Measured from the end of the leg back towards its start.")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stFlPct  = input.float(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v11.0 - appended after the last setting, so every setting saved on your chart keeps its place (shown in groups 36 and 37)",
    'gLd = "36. Pause for days after losses in a row"',
    'stLdOn  = input.bool(false, "Pause for some days after losses in a row", group = gLd, tooltip = "' + T_LD + '")',
    'stLdN   = input.int(3, "  - losses in a row", minval = 1, maxval = 50, group = gLd, tooltip = "' + T_LDN + '")',
    'stLdD   = input.int(2, "  - days to pause (after the rest of that day)", minval = 1, maxval = 60, group = gLd, tooltip = "' + T_LDD + '")',
    'gEq = "37. Higher timeframe equilibrium first"',
    'stEqOn  = input.bool(false, "Trade only after the higher timeframe pulled back to its equilibrium", group = gEq, tooltip = "' + T_EQ + '")',
    'stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg", minval = 1.0, maxval = 99.0, step = 0.5, group = gEq, tooltip = "' + T_EQP + '")',
]
s = "\n".join(lines)

# ---- the higher timeframe is needed for rule 2, filter b, the favourable modes and the equilibrium gate
s = rep(s, "bool   _u15    = stOn and (stR2On or stHfOn) and stHtfOk\n",
        """// v11.0: a 'higher timeframe favourable' mode works like filter b (group 34); the equilibrium gate needs the higher timeframe too
bool   stFav   = str.contains(stSigSrc, "favourable")
bool   stHfEff = stHfOn or stFav
bool   _u15    = stOn and (stR2On or stHfEff or stEqOn) and stHtfOk
""")

# ---- the higher-timeframe pack also returns its leg: where it started, how far it has run, and how many legs so far
s = rep(s, """f_tfPack(bool on) =>
    int trOut = 0
    int evOut = 0
    int inOut = 0
    int nnOut = 0
""", """f_tfPack(bool on) =>
    int trOut = 0
    int evOut = 0
    int inOut = 0
    int nnOut = 0
    float loOut = na
    float lxOut = na
    int   ecOut = 0
""")
s = rep(s, """        trOut := tTrend
        if mEvt
            evOut := tTrend == 1 ? 1 : 2
""", """        trOut := tTrend
        if mEvt
            evOut := tTrend == 1 ? 1 : 2
        // v11.0: the leg the higher timeframe is in - its start, its extreme so far, and the number of CHOCH / BOS so far
        var int tEvN = 0
        if mEvt
            tEvN += 1
        ecOut := tEvN
        if tTrend == 1
            lxOut := tRunHi
            loOut := na(tFlor) ? tRunLo : tFlor
        else if tTrend == -1
            lxOut := tRunLo
            loOut := na(tCeil) ? tRunHi : tCeil
""")
s = rep(s, "    [trOut, evOut, inOut, nnOut]\n", "    [trOut, evOut, inOut, nnOut, loOut, lxOut, ecOut]\n")
s = rep(s, """f_tfTrC(bool on) =>
    [_tA, _tB, _tC, _tD] = f_tfPack(on)
    _tA[1]
int stT15 = nz(request.security(syminfo.tickerid, _u15 ? stHtfTf : timeframe.period, f_tfTrC(_u15), lookahead = barmerge.lookahead_on), 0)
""", """f_tfTrC(bool on) =>
    [_tA, _tB, _tC, _tD, _tO, _tX, _tE] = f_tfPack(on)
    [_tA[1], _tO[1], _tX[1], _tE[1]]
// v11.0: one request brings the trend and the leg of the last CLOSED higher-timeframe candle
[_htT, _htO, _htX, _htE] = request.security(syminfo.tickerid, _u15 ? stHtfTf : timeframe.period, f_tfTrC(_u15), lookahead = barmerge.lookahead_on)
int   stT15 = nz(_htT, 0)
float stHtO = _htO
float stHtX = _htX
int   stHtE = nz(_htE, 0)
""")

# ---- state for the pause and the gate, and the day the pause ends
s = rep(s, "var int    stCntBosCnl = 0\n", """var int    stCntBosCnl = 0
// v11.0: feature 1 - losses in a row for the pause of days, the time the pause ends, pauses so far
var int    stLdRun   = 0
var int    stLdUntil = na
var int    stCntLd   = 0
// v11.0: feature 3 - the higher timeframe equilibrium gate
var bool   stEqOpen  = false
""")
s = rep(s, """f_stSeqCounts(int xt) =>
    stSeqFrom == "The whole chart history" ? true : stSeqFrom == "A date I choose" ? xt >= stSeqFromT : not na(stLiveT) and xt >= stLiveT
""", """f_stSeqCounts(int xt) =>
    stSeqFrom == "The whole chart history" ? true : stSeqFrom == "A date I choose" ? xt >= stSeqFromT : not na(stLiveT) and xt >= stLiveT
// v11.0: feature 1 - when a pause that starts at time t ends: the rest of that day plus d days (Monday to Friday, or every
// day for crypto / 24-7), at 00:00 in the session timezone. Each day is checked at its midday, so clock changes cannot shift it.
f_ldUntil(int t, int d, bool allDays) =>
    int _d0 = timestamp(stTz, year(t, stTz), month(t, stTz), dayofmonth(t, stTz), 0, 0)
    int _n  = 0
    int _k  = 0
    while _n < d and _k < 500
        _k += 1
        int _w = dayofweek(_d0 + _k * 86400000 + 43200000, stTz)
        if allDays or (_w != dayofweek.saturday and _w != dayofweek.sunday)
            _n += 1
    int _c = _d0 + (_k + 1) * 86400000 + 43200000
    timestamp(stTz, year(_c, stTz), month(_c, stTz), dayofmonth(_c, stTz), 0, 0)
""")

# ---- feature 1: count the losses in a row where the closed trades are counted (oldest first)
s = rep(s, """            float _gP = strategy.closedtrades.profit(_i) - (_gR > 0 ? 0.0 : _gE)
            stLsRun := _gP < 0 ? stLsRun + 1 : 0
""", """            float _gP = strategy.closedtrades.profit(_i) - (_gR > 0 ? 0.0 : _gE)
            stLsRun := _gP < 0 ? stLsRun + 1 : 0
            // v11.0: feature 1 - only the counted trades, nothing that closes during a pause; a win starts again at 0
            int _gX = strategy.closedtrades.exit_time(_i)
            if stLdOn and f_stSeqCounts(strategy.closedtrades.entry_time(_i)) and not (not na(stLdUntil) and _gX < stLdUntil)
                stLdRun := _gP < 0 ? stLdRun + 1 : _gP > 0 ? 0 : stLdRun
                if stLdRun >= stLdN
                    stLdUntil := f_ldUntil(_gX, stLdD, stCls == 4 or stWk247)
                    stLdRun   := 0
                    stCntLd   += 1
""")

# ---- features 1 and 3 stop new trades through the same gate as every other block
s = rep(s, "bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt\n",
        """// v11.0: feature 1 - paused for days after losses in a row (set where the closed trades are counted)
bool stLdHalt = stLdOn and not na(stLdUntil) and time < stLdUntil
// v11.0: feature 3 - a new higher-timeframe CHOCH / BOS closes the gate; it opens when the price touches the equilibrium
// of that leg (a wick is enough) and stays open until the next one
if bar_index > 0 and stHtE != stHtE[1]
    stEqOpen := false
float stEqLvl = f_retLvl(stT15, stHtX, stHtO, stEqPct)
if stEqOn and not stEqOpen and not na(stEqLvl) and ((stT15 == 1 and low <= stEqLvl) or (stT15 == -1 and high >= stEqLvl))
    stEqOpen := true
bool stEqBlock = stEqOn and not stEqOpen
bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt and not stLdHalt and not stEqBlock
""")

# ---- feature 2: a waiting order is cancelled when the higher timeframe flips against it
old = """if stDir != 0 and (not stGo or (trendDir != 0 and trendDir != stDir))
    f_audEnd(not stGo ? "CANCELLED - blocked" : "CANCELLED - trend flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
"""
s = rep(s, old, old + """// v11.0: feature 2 - in a 'higher timeframe favourable' mode a waiting order is cancelled when the higher timeframe no
// longer agrees with it (an open trade keeps running)
if stFav and stDir != 0 and stT15 != stDir
    f_audEnd("CANCELLED - higher timeframe flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
""")

# ---- feature 2: the signal types of the new modes, and the favourable modes skip a signal against the higher timeframe
s = rep(s, 'bool stUseCho = stSigSrc != "BOS only"\nbool stUseBos = stSigSrc != "CHOCH only"\n',
        'bool stUseCho = not str.startswith(stSigSrc, "BOS only")\nbool stUseBos = not str.startswith(stSigSrc, "CHOCH only")\n')
s = rep(s, "        bool _use   = _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfOn)\n        if not _agree and stR1On and stHfOn\n",
        "        bool _use   = _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfEff)\n        if not _agree and stR1On and stHfEff\n")
s = rep(s, '_agree ? "SKIP - no broken pivot" : stHfOn and stR1On ? "SKIP - against the higher timeframe (filter)" : "SKIP - HTF not agreeing (rule 2 only)"',
        '_agree ? "SKIP - no broken pivot" : stHfEff and stR1On ? (stFav ? "SKIP - against the higher timeframe (favourable mode)" : "SKIP - against the higher timeframe (filter)") : "SKIP - HTF not agreeing (rule 2 only)"')
s = rep(s, '"  HTF " + (not stR2On and not stHfOn ? "off"', '"  HTF " + (not stR2On and not stHfEff and not stEqOn ? "off"')

# ---- why a signal was skipped / what blocks now
s = rep(s, 'stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : "blocked")',
        'stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : stLdHalt ? "loss pause (days)" : stEqBlock ? "waiting for the higher timeframe equilibrium" : "blocked")')
s = rep(s, '''stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : not stOn ? "disabled" : "-", (stDDHit or stNwNow or stWkBlock or stDayHalt or stSeqHalt) ? color.red''',
        '''stSeqHalt ? "risk cap" : stPtHalt ? "profit target" : stLdHalt ? "loss pause (days)" : stEqBlock ? "HTF equilibrium not reached" : not stOn ? "disabled" : "-", (stDDHit or stNwNow or stWkBlock or stDayHalt or stSeqHalt or stLdHalt) ? color.red : stEqBlock ? color.orange''')

# ---- table: two more rows, the favourable mode in row 21, and the higher timeframe row
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 45,", "stTbl := table.new(f_stPos(stStatPos), 2, 47,")
s = rep(s, '''    f_stCell(stTbl, 21, "ENTRY rules in use (1 / 2)", stR1On and stR2On ? "1 + 2 (dynamic)" : stR1On ? "1 only (pullback %)" : stR2On ? "2 only (HTF must agree)" : "NONE - both off", stR1On or stR2On ? color.aqua : color.red)''',
        '''    f_stCell(stTbl, 21, "ENTRY rules in use (1 / 2)", (stR1On and stR2On ? "1 + 2 (dynamic)" : stR1On ? "1 only (pullback %)" : stR2On ? "2 only (HTF must agree)" : "NONE - both off") + (stFav ? "  |  HTF favourable only" : ""), stR1On or stR2On ? color.aqua : color.red)''')
s = rep(s, '''    f_stCell(stTbl, 22, "RULE 2 / filter higher timeframe", stR2On or stHfOn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfOn) and stHtfOk ? color.aqua : color.gray)''',
        '''    f_stCell(stTbl, 22, "RULE 2 / filter higher timeframe", stR2On or stHfEff or stEqOn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfEff or stEqOn) and stHtfOk ? color.aqua : color.gray)''')
last = s.index('    f_stCell(stTbl, 44, "ACCOUNT FLOOR (group 35)"')
eol = s.index("\n", last) + 1
s = s[:eol] + """    // v11.0: feature 1 - the pause after losses in a row, feature 3 - the higher timeframe equilibrium gate
    string _ldT = not stLdOn ? "off" : (stLdHalt ? ("PAUSED until " + str.format_time(stLdUntil, "EEE dd MMM HH:mm", stTz)) : (str.tostring(stLdRun) + " of " + str.tostring(stLdN) + " losses in a row")) + "  |  pauses so far " + str.tostring(stCntLd)
    f_stCell(stTbl, 45, "PAUSE AFTER LOSSES (group 36)", _ldT, not stLdOn ? color.gray : stLdHalt ? color.red : color.aqua)
    string _eqT = not stEqOn ? "off" : not stHtfOk ? "higher timeframe not above the chart - no trades" : stEqOpen ? ("OPEN - pulled back to " + str.tostring(stEqPct) + "%") : na(stEqLvl) ? "WAITING - no higher timeframe leg yet" : ("WAITING - needs " + str.tostring(stEqLvl, format.mintick))
    f_stCell(stTbl, 46, "HTF EQUILIBRIUM FIRST (group 37)", _eqT, not stEqOn ? color.gray : stEqOpen ? color.lime : color.orange)
""" + s[eol:]

assert all(ord(c) < 128 for c in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v11.0.txt", "w").write(s)
print("ok", len(s.split("\n")))
