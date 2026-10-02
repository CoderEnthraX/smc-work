# v8.4 -> v9.0 : the seven "ideas to make it more profitable", every one a switch that is OFF by default
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v8.4.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v8.4  -  ")
n2 = l2.replace("v8.4  -  ", "v9.0  -  ", 1).replace(
    "  -  ASCII only",
    ", v9.0 ideas as switches that are all OFF by default (smaller risk for stacked BOS trades, higher-timeframe filter, structure trailing stop, target at the next liquidity, partial profit, premium / discount filter, pause after losses in a row)  -  ASCII only")
s = rep(s, l2, n2)

# ---- swings confirmed on this candle, captured for the strategy part
s = rep(s, "if not onClose or barstate.isconfirmed\n",
        "// v9.0: the swing high / low confirmed on this candle (structure trailing stop, liquidity targets)\n"
        "float stSwH = na\nfloat stSwL = na\n\n"
        "if not onClose or barstate.isconfirmed\n")
s = rep(s, "    [plP, plB] = loT.update(_swpL)\n", "    [plP, plB] = loT.update(_swpL)\n    stSwH := phP\n    stSwL := plP\n")

# ---- the new settings, after the last one
T = {}
T["a"] = ("OFF (default): a stacked BOS trade risks the same as any trade.\\n\\n"
          "ON: every trade ADDED by a same-side BOS (group 31 stacking - 'Take trades on' must include BOS) risks only this percentage of the normal risk. "
          "The first trade of a move keeps the full risk. It limits the damage when a stack of trades reverses together.")
T["b"] = ("OFF (default): rule 1 takes the signals where the higher timeframe does NOT agree, exactly as before.\\n\\n"
          "ON: a signal is taken ONLY when the higher timeframe trend (group 20 'Higher timeframe for RULE 2') points the same way. "
          "With rule 2 ON the agreeing signals use rule 2 as before - so this is the same as rule 2 only. "
          "With rule 2 OFF and rule 1 ON, the agreeing signals use RULE 1 (pullback %) - rule 1 in the direction of the higher timeframe only.")
T["c"] = ("OFF (default): the stop stays where it was placed (group 32 can still move it).\\n\\n"
          "ON: at every candle close the stop of each open trade follows the structure, never backwards:\\n"
          "CHOCH* LEVEL (slower): behind the protected low of an up-trend (the high of a down-trend) - the level whose break would be the opposite CHOCH. It moves after every BOS.\\n"
          "EVERY NEW SWING (faster): behind every new swing low (swing high for a sell) the structure confirms.\\n\\n"
          "The stop is placed the group 20 stop buffer beyond the level. The moved stop is sent like a group 32 move: the broker closes the trade when it is hit. "
          "Works together with group 32 - the stop is always the tighter of the two.")
T["d"] = ("OFF (default): the target is the R multiple of group 20.\\n\\n"
          "ON: the target is the nearest swing high (swing low for a sell) that the price has NOT traded through yet - where the stops of other traders sit - "
          "but only one at least this many R away from the entry. When there is none, the normal R target is used. "
          "The target follows new swings until the order fills, then it stays fixed.")
T["e"] = ("OFF (default): one trade per setup.\\n\\n"
          "ON: every setup is sent as TWO trades at the same price and stop - a smaller part with an early target (this R, pushed out to cover its costs like the main target), "
          "and the rest with the normal target. Each part has its own order id and its own TheConnector tag (the part ends in _), so ANY bridge can do it: "
          "no partial-close command is needed. With 'then move the rest to break-even' ON, the rest moves its stop to break-even once the early part hits its target.\\n\\n"
          "The size is split on the broker's lot step (group 21). If a part would be below one lot step or below the minimum lot, the setup is sent as one trade. "
          "Group 31 'Max trades open' counts each part.")
T["f"] = ("OFF (default): the entry can be anywhere in the leg.\\n\\n"
          "ON: a buy is placed only at a DISCOUNT - at or below this line of the leg, measured down from its high (50 = the middle). A sell only at a PREMIUM - at or above it, measured up from its low. "
          "The leg is the same one rule 1 uses. A setup whose entry is on the wrong side is cancelled.\\n\\n"
          "IMPORTANT: a rule 1 pullback smaller than this line is ALWAYS on the wrong side, so every rule 1 setup would be cancelled. "
          "Use a rule 1 pullback (group 20) equal to or bigger than this line - for example 50 and 50.")
T["g"] = ("OFF (default): no pause.\\n\\n"
          "ON: after this many losing trades in a row (after costs), no new trade is opened for the rest of the day (session timezone). "
          "Open trades are not touched. A winning trade starts the count again, and so does a new day. "
          "With partial profit (e) only the main part of each setup is counted.")
new_inputs = [
    "",
    "// v9.0 - appended after the last setting, so every setting saved on your chart keeps its place. EVERY switch below is OFF by",
    "// default: with all of them OFF, v9.0 trades exactly like v8.4.",
    'gV9 = "34. v9.0 ideas - each one OFF by default"',
    'stBkOn  = input.bool(false, "a. Smaller risk for stacked BOS trades", group = gV9, tooltip = "' + T["a"] + '")',
    'stBkPct = input.float(50.0, "  - risk of each stacked BOS trade, % of the normal risk", minval = 1.0, maxval = 100.0, step = 5.0, group = gV9)',
    'stHfOn  = input.bool(false, "b. Higher-timeframe filter - take a signal only in the higher timeframe direction", group = gV9, tooltip = "' + T["b"] + '")',
    'stTrOn  = input.bool(false, "c. Structure trailing stop", group = gV9, tooltip = "' + T["c"] + '")',
    'stTrMode = input.string("Behind the CHOCH* level (slower)", "  - the stop follows", options = ["Behind the CHOCH* level (slower)", "Behind every new swing (faster)"], group = gV9)',
    'stLqOn  = input.bool(false, "d. Target at the next liquidity (the nearest untaken swing high / low)", group = gV9, tooltip = "' + T["d"] + '")',
    'stLqMin = input.float(1.5, "  - only a swing at least this far from the entry, in R", minval = 0.1, maxval = 50.0, step = 0.1, group = gV9)',
    'stPpOn  = input.bool(false, "e. Partial profit - a smaller part of every setup takes profit early", group = gV9, tooltip = "' + T["e"] + '")',
    'stPpPct = input.float(50.0, "  - size of the early part, % of the setup", minval = 1.0, maxval = 99.0, step = 5.0, group = gV9)',
    'stPpR   = input.float(1.0, "  - early target, in R", minval = 0.1, maxval = 50.0, step = 0.1, group = gV9)',
    'stPpBe  = input.bool(true, "  - then move the rest to break-even", group = gV9)',
    'stPdOn  = input.bool(false, "f. Premium / discount filter - buy only at a discount, sell only at a premium", group = gV9, tooltip = "' + T["f"] + '")',
    'stPdPct = input.float(50.0, "  - the line, % of the leg (50 = the middle)", minval = 1.0, maxval = 99.0, step = 5.0, group = gV9)',
    'stLsOn  = input.bool(false, "g. Pause for the rest of the day after losses in a row", group = gV9, tooltip = "' + T["g"] + '")',
    'stLsN   = input.int(3, "  - losses in a row", minval = 1, maxval = 50, group = gV9)',
]
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stDirMode = input.string(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = new_inputs
s = "\n".join(lines)
for k, v in T.items():
    assert '"' not in v.replace('\\"', ""), k

# ---- b: the higher timeframe is also needed for the filter
s = rep(s, "bool   _u15    = stOn and stR2On and stHtfOk", "bool   _u15    = stOn and (stR2On or stHfOn) and stHtfOk")

# ---- state
s = rep(s, "var int    stCntDir = 0\n", """var int    stCntDir = 0
// v9.0 state: risk factor of the armed setup (a), counters (b, f, g), losses in a row (g), partial profit (e)
var float  stAddRk  = 1.0
var int    stCntHf  = 0
var int    stCntPd  = 0
var int    stCntLs  = 0
var int    stLsRun  = 0
var bool   stPpSent = false
var bool   stPpCnl  = false
var float  stLastTp1 = na
// d: swing highs / lows the price has not traded through yet (liquidity)
var array<float> stLqH = array.new_float()
var array<float> stLqL = array.new_float()
""")

# ---- cancel both parts of a partial-profit setup
s = rep(s, """f_stCancel(bool live, string id) =>
    bool _do = live and id != ""
    if _do
        strategy.cancel(id)
        strategy.cancel(id + " exit")
    _do
""", """f_stCancel(bool live, string id) =>
    bool _do = live and id != ""
    if _do
        strategy.cancel(id)
        strategy.cancel(id + " exit")
        // v9.0 e: the early-profit part of the same setup
        if stPpSent
            strategy.cancel(id + "p")
            strategy.cancel(id + "p exit")
    _do

// v9.0 e: did this order fill (still open, or already closed)?
f_stFilled(string id) =>
    bool _f = false
    if id != ""
        int _n = strategy.opentrades
        if _n > 0
            for _k = 0 to _n - 1
                if strategy.opentrades.entry_id(_k) == id
                    _f := true
                    break
        int _c = strategy.closedtrades
        if not _f and _c > 0
            for _k = _c - 1 to math.max(0, _c - 20)
                if strategy.closedtrades.entry_id(_k) == id
                    _f := true
                    break
    _f

// v9.0 d: the nearest untaken swing high (dir 1) / swing low (dir -1) at or beyond lim
f_stLq(int dir, float lim) =>
    float _b = na
    array<float> _a = dir == 1 ? stLqH : stLqL
    int _n = array.size(_a)
    if _n > 0 and not na(lim)
        for _i = 0 to _n - 1
            float _v = array.get(_a, _i)
            if (dir == 1 ? _v >= lim : _v <= lim) and (na(_b) or (dir == 1 ? _v < _b : _v > _b))
                _b := _v
    _b
""")

# ---- g: the count starts again every day
s = rep(s, """if stNewDay
    stDayTrades := 0
    stDayPnl    := 0.0
    stDayHalt   := false
""", """if stNewDay
    stDayTrades := 0
    stDayPnl    := 0.0
    stDayHalt   := false
    stLsRun     := 0
""")

# ---- StTrade: two new fields
s = rep(s, """    int    fix
    string why
""", """    int    fix
    string why
    int    part = 0
    bool   pp   = false
""")
s = rep(s, "bool stMvOn   = stMvStepOn or stMvBeOn\n",
        "bool stMvOn   = stMvStepOn or stMvBeOn\n// v9.0: any stop that can move (group 32, trailing stop, break-even after the early profit)\nbool stMgOn   = stMvOn or stTrOn or (stPpOn and stPpBe)\n")

# ---- fills: one record per trade entered on this candle (two with partial profit), a part that did not fill is cancelled
s = rep(s, """    if _eOpen and not na(stOpenSl) and not na(stOpenTgt)
        float _r0 = math.abs(_eP - stOpenSl)
        // break-even = entry + the round-turn costs of this size, so a break-even exit nets zero
        float _cst = _stPvA > 0 ? (stCmU + (_eQ > 0 ? f_stCmF() / _eQ : 0.0)) / _stPvA : 0.0
        array.push(stTrk, StTrade.new(_eId, _eDir, _eP, _r0, _eDir == 1 ? _eP + _cst : _eP - _cst, stOpenSl, stOpenTgt, _eQ, 0, bar_index, false, -1, ""))
""", """    if _eOpen and not na(stOpenSl) and not na(stOpenTgt)
        // v9.0: every trade entered on this candle gets its record - with partial profit (e) a setup is two trades
        for _k = strategy.opentrades - 1 to 0
            if strategy.opentrades.entry_bar_index(_k) != stEntNow
                break
            string _kId = strategy.opentrades.entry_id(_k)
            if na(f_stTrk(_kId))
                float _kP  = strategy.opentrades.entry_price(_k)
                float _kQ  = math.abs(strategy.opentrades.size(_k))
                int   _kD  = strategy.opentrades.size(_k) > 0 ? 1 : -1
                bool  _kPp = stPpSent and _kId == stPendId + "p"
                float _r0 = math.abs(_kP - stOpenSl)
                // break-even = entry + the round-turn costs of this size, so a break-even exit nets zero
                float _cst = _stPvA > 0 ? (stCmU + (_kQ > 0 ? f_stCmF() / _kQ : 0.0)) / _stPvA : 0.0
                array.push(stTrk, StTrade.new(_kId, _kD, _kP, _r0, _kD == 1 ? _kP + _cst : _kP - _cst, stOpenSl, _kPp and not na(stLastTp1) ? stLastTp1 : stOpenTgt, _kQ, 0, bar_index, false, -1, "", _kPp ? 1 : 0, false))
    // v9.0 e: the two parts of a setup fill together; a part still waiting is cancelled, so it can never fill on its own later
    if stPpSent and stPendId != ""
        if not f_stFilled(stPendId)
            strategy.cancel(stPendId)
            strategy.cancel(stPendId + " exit")
            stPpCnl := true
        if not f_stFilled(stPendId + "p")
            strategy.cancel(stPendId + "p")
            strategy.cancel(stPendId + "p exit")
            stPpCnl := true
    stPpSent := false
""")

# ---- closed trades: moved-stop count for every kind of moved stop, early-profit part hit, losses in a row
s = rep(s, "            StTrade _mvT = stMvOn ? f_stTrk(strategy.closedtrades.entry_id(_ix)) : na\n",
        "            StTrade _mvT = stMgOn ? f_stTrk(strategy.closedtrades.entry_id(_ix)) : na\n")
s = rep(s, """        stDayPnl  := stDayPnl + _pf
""", """        stDayPnl  := stDayPnl + _pf
        // v9.0 e: the early-profit part closed in profit by its own order - the rest of the setup goes to break-even (below)
        string _cId = strategy.closedtrades.entry_id(_ix)
        if stPpOn and str.endswith(_cId, "p") and str.endswith(_xid, " exit") and _pf > 0
            StTrade _mn = f_stTrk(str.substring(_cId, 0, str.length(_cId) - 1))
            if not na(_mn)
                _mn.pp := true
""")
s = rep(s, """    stClosed := strategy.closedtrades
""", """    // v9.0 g: losing trades in a row, oldest first (the early-profit part of a setup is not counted)
    for _i = stClosed to strategy.closedtrades - 1
        string _gId = strategy.closedtrades.entry_id(_i)
        if not (str.endswith(_gId, "p") and map.contains(stCodeOf, _gId))
            float _gR = math.abs(nz(strategy.closedtrades.commission(_i)))
            float _gE = math.abs(nz(strategy.closedtrades.size(_i))) * f_stCmU(nz(strategy.closedtrades.entry_price(_i), close)) + f_stCmF()
            float _gP = strategy.closedtrades.profit(_i) - (_gR > 0 ? 0.0 : _gE)
            stLsRun := _gP < 0 ? stLsRun + 1 : 0
    stClosed := strategy.closedtrades
""")

# ---- the stop of every managed trade: group 32 steps, trailing (c), break-even after the early profit (e)
old_mv = s[s.index("            else if stMvOn and stMvKMax >= 1 and _t.r > 0\n"):s.index("\nfloat stRiskNow = stRisk\n")]
assert old_mv.count("strategy.exit(") == 1
new_mv = """            else
                float _ns = _t.sl
                if stMvOn and stMvKMax >= 1 and _t.r > 0
                    int _k = _t.step
                    if stMvStepOn
                        // how many whole R the trade has reached - on its entry candle only the close is known to be after the fill
                        float _ref = bar_index == _t.bar ? close : (_t.dir == 1 ? high : low)
                        int   _got = math.floor((_t.dir == 1 ? _ref - _t.ent : _t.ent - _ref) / _t.r)
                        _k := math.max(_t.step, math.min(_got, stMvKMax))
                    else if _t.step == 0 and (_t.dir == 1 ? close >= _t.ent + _t.r : close <= _t.ent - _t.r)
                        _k := 1
                    // the new stop must lie below the level just reached (above it for a sell) - with costs bigger than 1R,
                    // break-even is above 1R and the move waits for a later step
                    float _c = _k == 1 ? _t.be : (_t.dir == 1 ? math.max(_t.be, _t.ent + (_k - 1) * _t.r) : math.min(_t.be, _t.ent - (_k - 1) * _t.r))
                    if _k > _t.step and (_t.dir == 1 ? _c < _t.ent + _k * _t.r : _c > _t.ent - _k * _t.r)
                        _ns := _t.dir == 1 ? math.max(_ns, _c) : math.min(_ns, _c)
                        _t.step := _k
                // v9.0 c: structure trailing stop - behind the CHOCH* level or behind every new swing, never backwards
                if stTrOn and bar_index > _t.bar
                    float _lv = na
                    if stTrMode == "Behind every new swing (faster)"
                        _lv := _t.dir == 1 ? stSwL : stSwH
                    else if _t.dir == 1 and trendDir == 1 and not na(florS)
                        _lv := florS.price
                    else if _t.dir == -1 and trendDir == -1 and not na(ceilS)
                        _lv := ceilS.price
                    if not na(_lv)
                        float _l2 = _t.dir == 1 ? _lv - stSlBuf : _lv + stSlBuf
                        if _t.dir == 1 ? _l2 < close : _l2 > close
                            _ns := _t.dir == 1 ? math.max(_ns, _l2) : math.min(_ns, _l2)
                // v9.0 e: the early-profit part of this setup hit its target - the rest goes to break-even
                if _t.pp and stPpBe
                    _ns := _t.dir == 1 ? math.max(_ns, _t.be) : math.min(_ns, _t.be)
                if _ns != _t.sl
                    _t.sl := _ns
                    _t.mv := true
                    strategy.exit(_t.id + " exit", _t.id, stop = _ns, limit = _t.tgt, alert_message = f_stMsg("close", _t.dir, close, _ns, _t.tgt, _t.q, _t.id))
                    stCntMoves += 1
                    if _t.id == strategy.opentrades.entry_id(strategy.opentrades - 1)
                        stOpenSl := _ns
"""
s = s.replace(old_mv, new_mv.rstrip("\n"))

# ---- d: keep the liquidity pools (after the stop moves, before any target is worked out)
s = rep(s, "\nfloat stRiskNow = stRisk\n", """
// v9.0 d: new swings join the pools; a swing the price has traded through is taken - it is no longer a target
if stLqOn
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

float stRiskNow = stRisk
""")

# ---- g: the pause
s = rep(s, "if stMaxTrades > 0 and stDayTrades >= stMaxTrades\n    stDayHalt := true\n", """if stMaxTrades > 0 and stDayTrades >= stMaxTrades
    stDayHalt := true
// v9.0 g: losses in a row - no new trade for the rest of the day
if stLsOn and stLsRun >= stLsN and not stDayHalt
    stDayHalt := true
    stCntLs += 1
""")

# ---- e: a part cancelled at the fill -> the brackets of the open trades are sent again at the end of the candle
s = rep(s, "bool   stCnlSent = false\n", """bool   stCnlSent = false
if stPpCnl
    stCnlSent := true
    stPpCnl   := false
""")

# ---- b: arming
s = rep(s, "        bool _use   = _agree ? (stR2On and not na(_piv)) : stR1On\n",
        "        // v9.0 b: with the higher-timeframe filter a signal against it is skipped; with rule 2 OFF an agreeing signal uses rule 1\n"
        "        bool _use   = _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfOn)\n"
        "        if not _agree and stR1On and stHfOn\n"
        "            stCntHf += 1\n")
s = rep(s, """        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : "SKIP - HTF not agreeing (rule 2 only)") : na(_opl) ? "SKIP - no stop level" : ((_agree ? "R2" : "R1") + " ARMED")""",
        """        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : stHfOn and stR1On ? "SKIP - against the higher timeframe (filter)" : "SKIP - HTF not agreeing (rule 2 only)") : na(_opl) ? "SKIP - no stop level" : ((_agree and stR2On ? "R2" : "R1") + " ARMED")""")
s = rep(s, "            map.put(stCodeOf, stPendId, f_stCode(time))\n", """            map.put(stCodeOf, stPendId, f_stCode(time))
            // v9.0 e: the early-profit part - its own tag: the same code with its last character replaced by _
            if stPpOn
                map.put(stCodeOf, stPendId + "p", str.substring(f_stCode(time), 0, 3) + "_")
            stPpSent := false
            // v9.0 a: a trade added by a same-side BOS risks less
            stAddRk  := _addB and stBkOn ? stBkPct / 100.0 : 1.0
""")
s = rep(s, "            stRule := _agree ? 2 : 1\n", "            stRule := _agree and stR2On ? 2 : 1\n")
s = rep(s, "            stFix  := _agree ? _piv : na\n", "            stFix  := _agree and stR2On ? _piv : na\n")

# ---- d: target
s = rep(s, "        stTgt := stDir == 1 ? stEnt + _r * stRR + stCmPx : stEnt - _r * stRR - stCmPx\n", """        stTgt := stDir == 1 ? stEnt + _r * stRR + stCmPx : stEnt - _r * stRR - stCmPx
        // v9.0 d: the nearest untaken swing at least stLqMin R away; none = the normal R target
        if stLqOn
            float _lq = f_stLq(stDir, stDir == 1 ? stEnt + stLqMin * _r : stEnt - stLqMin * _r)
            if not na(_lq)
                stTgt := _lq
""")

# ---- a + f + e: sizing, the filter, the two parts
s = rep(s, "    [_q, _qCap] = f_stQty(stEnt, _r, stRiskNow)\n", "    [_q, _qCap] = f_stQty(stEnt, _r, stRiskNow * stAddRk)\n")
s = rep(s, "    bool _dOk = (stMinStop <= 0 or _r >= stMinStop) and (stMaxStop <= 0 or _r <= stMaxStop) and _lotOk\n",
        """    bool _dOk = (stMinStop <= 0 or _r >= stMinStop) and (stMaxStop <= 0 or _r <= stMaxStop) and _lotOk
    // v9.0 f: premium / discount - a buy at or below the line of the leg, a sell at or above it
    float _pdL  = stPdOn ? f_retLvl(trendDir, mAnch, mOrig, stPdPct) : na
    bool  _pdOk = not stPdOn or (not na(_pdL) and (stDir == 1 ? stEnt <= _pdL + syminfo.mintick / 2 : stEnt >= _pdL - syminfo.mintick / 2))
""")
s = rep(s, "    bool _place = _sane and _dOk and _q /", "    bool _place = _sane and _dOk and _pdOk and _q /")
old_send = """            if stDir == 1
                strategy.entry(stPendId, strategy.long, qty = _q, limit = stEnt, alert_message = f_stMsg("buy", 1, stEnt, stSl, stTgt, _q, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", 1, close, stSl, stTgt, _q, stPendId))
            else
                strategy.entry(stPendId, strategy.short, qty = _q, limit = stEnt, alert_message = f_stMsg("sell", -1, stEnt, stSl, stTgt, _q, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", -1, close, stSl, stTgt, _q, stPendId))
            stOrdLive := true
"""
new_send = """            // v9.0 e: partial profit - the early part is split off on the lot step; too small a part = one trade as before
            float _q1 = 0.0
            if stPpOn
                float _stp = stLotStep > 0 and stCmLots > 0 ? stLotStep * stCmLots : 0.0
                _q1 := _stp > 0 ? math.round(_q * stPpPct / 100.0 / _stp) * _stp : _q * stPpPct / 100.0
                float _lt1 = stWhQty == "Raw units  (exactly what Pine sizes)" or stCmLots <= 0 ? 1.0 : stCmLots
                bool  _tiny = _q1 / _lt1 < 0.00000001 or (_q - _q1) / _lt1 < 0.00000001 or (stWhMinLot > 0 and stCmLots > 0 and (_q1 / stCmLots < stWhMinLot - 1e-9 or (_q - _q1) / stCmLots < stWhMinLot - 1e-9))
                if _tiny or _q1 >= _q
                    _q1 := 0.0
            float _qm = _q - _q1
            if stDir == 1
                strategy.entry(stPendId, strategy.long, qty = _qm, limit = stEnt, alert_message = f_stMsg("buy", 1, stEnt, stSl, stTgt, _qm, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", 1, close, stSl, stTgt, _qm, stPendId))
            else
                strategy.entry(stPendId, strategy.short, qty = _qm, limit = stEnt, alert_message = f_stMsg("sell", -1, stEnt, stSl, stTgt, _qm, stPendId))
                strategy.exit(stPendId + " exit", stPendId, stop = stSl, limit = stTgt, alert_message = f_stMsg("close", -1, close, stSl, stTgt, _qm, stPendId))
            if _q1 > 0
                // the early target is pushed out to cover its costs, like the main target; never beyond the main target
                float _tp1 = stDir == 1 ? stEnt + _r * stPpR + (stCmTgt and _stPvA > 0 ? stCmU * (stPpR + 1.0) / _stPvA : 0.0) : stEnt - _r * stPpR - (stCmTgt and _stPvA > 0 ? stCmU * (stPpR + 1.0) / _stPvA : 0.0)
                _tp1 := stDir == 1 ? math.min(_tp1, stTgt) : math.max(_tp1, stTgt)
                string _pId = stPendId + "p"
                if stDir == 1
                    strategy.entry(_pId, strategy.long, qty = _q1, limit = stEnt, alert_message = f_stMsg("buy", 1, stEnt, stSl, _tp1, _q1, _pId))
                    strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", 1, close, stSl, _tp1, _q1, _pId))
                else
                    strategy.entry(_pId, strategy.short, qty = _q1, limit = stEnt, alert_message = f_stMsg("sell", -1, stEnt, stSl, _tp1, _q1, _pId))
                    strategy.exit(_pId + " exit", _pId, stop = stSl, limit = _tp1, alert_message = f_stMsg("close", -1, close, stSl, _tp1, _q1, _pId))
                stPpSent  := true
                stLastTp1 := _tp1
            else if stPpSent
                // the setup is one trade again (the size shrank) - the early part that was waiting goes
                strategy.cancel(stPendId + "p")
                strategy.cancel(stPendId + "p exit")
                stCnlSent := true
                stPpSent  := false
            stOrdLive := true
"""
s = rep(s, old_send, new_send)
s = rep(s, """    else if not _sane or not _dOk or _q /""", """    else if not _sane or not _dOk or not _pdOk or _q /""")
s = rep(s, """        f_audEnd(not _sane ? "CANCELLED - entry beyond the stop" : not _lotOk""",
        """        f_audEnd(not _sane ? "CANCELLED - entry beyond the stop" : not _pdOk ? (stDir == 1 ? "CANCELLED - buy in the premium (filter f)" : "CANCELLED - sell in the discount (filter f)") : not _lotOk""")
s = rep(s, """        if not _dOk
            stCntSkip += 1
""", """        if not _dOk
            stCntSkip += 1
        if not _pdOk
            stCntPd += 1
""")

# ---- table
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 41,", "stTbl := table.new(f_stPos(stStatPos), 2, 43,")
s = rep(s, """    f_stCell(stTbl, 13, "Exit - moved stop (BE / step)", not stMvOn ? "off" : (str.tostring(stCntMvx) + "  (" + str.tostring(stCntMoves) + " moves, " + (stMvStepOn ? "step stop" : "break-even only") + ")"), not stMvOn ? color.gray : color.aqua)""",
        """    f_stCell(stTbl, 13, "Exit - moved stop (BE / step / trail)", not stMgOn ? "off" : (str.tostring(stCntMvx) + "  (" + str.tostring(stCntMoves) + " moves" + (stMvStepOn ? ", step stop" : stMvBeOn ? ", break-even only" : "") + (stTrOn ? ", trailing" : "") + (stPpOn and stPpBe ? ", BE after early profit" : "") + ")"), not stMgOn ? color.gray : color.aqua)""")
i = s.index("    f_stCell(stTbl, 40, \"Trade direction (group 33)\"")
j = s.index("\n", i)
s = s[:j + 1] + """    string _v9 = (stBkOn ? "a " : "") + (stHfOn ? "b " : "") + (stTrOn ? "c " : "") + (stLqOn ? "d " : "") + (stPpOn ? "e " : "") + (stPdOn ? "f " : "") + (stLsOn ? "g " : "")
    f_stCell(stTbl, 41, "v9.0 ideas switched ON (group 34)", _v9 == "" ? "none" : _v9, _v9 == "" ? color.gray : color.aqua)
    f_stCell(stTbl, 42, "  - skipped: HTF filter / premium-discount / paused days", str.tostring(stCntHf) + " / " + str.tostring(stCntPd) + " / " + str.tostring(stCntLs), stCntHf + stCntPd + stCntLs > 0 ? color.orange : color.gray)
""" + s[j + 1:]

# ---- b: the audit header and the table show the higher timeframe when the filter uses it
s = rep(s, """ + "  HTF " + (not stR2On ? "off" : not stHtfOk""", """ + "  HTF " + (not stR2On and not stHfOn ? "off" : not stHtfOk""")
s = rep(s, """    f_stCell(stTbl, 22, "RULE 2 higher timeframe",    stR2On ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", stR2On and stHtfOk ? color.aqua : color.gray)""",
        """    f_stCell(stTbl, 22, "RULE 2 / filter higher timeframe", stR2On or stHfOn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfOn) and stHtfOk ? color.aqua : color.gray)""")

open(R + "SMC_Structure_Strategy_v9.0.txt", "w").write(s)
print("ok", len(s.split("\n")))
