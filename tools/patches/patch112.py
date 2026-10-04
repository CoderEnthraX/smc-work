# v11.1 -> v11.2 : stop buffer unit - price (as before), pips (automatic per market) or % of price
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v11.1.txt").read()
assert "stBuMode" not in s and "f_stBuf" not in s and "stPipSz" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


PIP = "Pips (auto per market)"
PCT = "% of price"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v11.1  -  ")
s = rep(s, l2, l2.replace("v11.1  -  ", "v11.2  -  ", 1).replace(
    "  -  ASCII only", ", v11.2: stop buffer in price, pips (automatic per market) or % of price  -  ASCII only"))

# ---- the new settings, at the END of the list (group 38)
old = """stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg", """
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    'gBu = "38. Stop buffer unit - price, pips or % (v11.2)"\n'
    'stBuMode = input.string("Price (as now)", "Stop buffer unit", options = ["Price (as now)", "' + PIP + '", "' + PCT + '"], group = gBu, tooltip = '
    '"PRICE (default): exactly as before - the stop buffer of group 20 and the group 24 limits (skip the setup if the stop is CLOSER / FURTHER than) are in price.\\n\\n'
    'PIPS: the buffer below is in pips, and the strategy knows the pip of the market on the chart: gold 0.10, silver 0.01, Bitcoin 1, Ethereum 0.10, '
    'forex 0.0001 (JPY pairs 0.01), anything else 10 x the smallest price step. 10 pips on gold = 1.00, on EURUSD = 0.0010. The group 24 limits are read as pips too.\\n\\n'
    '% OF PRICE: the buffer is this % of the CHOCH* level the stop sits beyond, worked out again for every setup - 0.02% of gold at 4,000 = 0.80, '
    'of EURUSD at 1.10 = 0.00022. The group 24 limits are read as % of the entry price.\\n\\n'
    'The buffer is rounded to the smallest price step. The group 20 stop buffer is not used in the pips and % modes. The structure trailing stop (group 34 c) '
    'uses the same buffer. The table shows the buffer in price.")\n'
    'stBuPips = input.float(10.0, "  - stop buffer in pips", minval = 0.0, step = 0.1, group = gBu, tooltip = '
    '"Used only when the unit is Pips. 10 (default) = 1.00 on gold, 0.10 on silver, 10 on Bitcoin, 0.0010 on EURUSD, 0.10 on USDJPY.")\n'
    'stBuPct  = input.float(0.02, "  - stop buffer in % of price", minval = 0.0, maxval = 10.0, step = 0.001, group = gBu, tooltip = '
    '"Used only when the unit is % of price. 0.02 (default) = 0.02% of the level: 0.80 on gold at 4,000, 20 on Bitcoin at 100,000, 0.00022 on EURUSD at 1.10.")\n'
    'stBuPip  = input.float(0.0, "  - pip size (0 = automatic)", minval = 0.0, step = 0.00000001, group = gBu, tooltip = '
    '"0 (default) = automatic from the ticker (the table shows the pip it uses). Type a number only if your broker counts pips differently, e.g. 0.01 for gold.")\n'
) + s[j:]

# ---- the pip of this market and the buffer, after the market type (stCls)
old = "var int    stCls = "
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    "// v11.2: the pip of this market (stop buffer unit 'Pips') - gold 0.10, silver 0.01, Bitcoin 1, Ethereum 0.10, forex 0.0001 (JPY 0.01), else 10 x the price step\n"
    'var bool  _isBtc    = _bc == "BTC" or (_bc == "" and str.startswith(_tk, "BTC"))\n'
    'var bool  _isEth    = _bc == "ETH" or (_bc == "" and str.startswith(_tk, "ETH"))\n'
    'var float stPipAuto = stCls == 2 ? 0.1 : stCls == 3 ? 0.01 : stCls == 4 and _isBtc ? 1.0 : stCls == 4 and _isEth ? 0.1 : stCls == 1 ? (syminfo.currency == "JPY" ? 0.01 : 0.0001) : 10 * syminfo.mintick\n'
    "var float stPipSz   = stBuPip > 0 ? stBuPip : stPipAuto\n"
    'var bool  stBuPipM  = stBuMode == "' + PIP + '"\n'
    'var bool  stBuPctM  = stBuMode == "' + PCT + '"\n'
    "// v11.2: the stop buffer beyond the level _lv, in price (pips x pip, or % of the level, rounded to the price step; else the group 20 buffer)\n"
    "f_stBuf(float _lv) =>\n"
    "    stBuPipM ? math.round_to_mintick(stBuPips * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stBuPct / 100.0) : stSlBuf\n"
) + s[j:]

# ---- the three places that put the buffer beyond a level
s = rep(s, "float _l2 = _t.dir == 1 ? _lv - stSlBuf : _lv + stSlBuf", "float _l2 = _t.dir == 1 ? _lv - f_stBuf(_lv) : _lv + f_stBuf(_lv)")
s = rep(s, "stSl := stDir == 1 ? _live - stSlBuf : _live + stSlBuf", "stSl := stDir == 1 ? _live - f_stBuf(_live) : _live + f_stBuf(_live)")
s = rep(s, "stSl   := _d == 1 ? _opl - stSlBuf : _opl + stSlBuf", "stSl   := _d == 1 ? _opl - f_stBuf(_opl) : _opl + f_stBuf(_opl)")

# ---- the group 24 limits in the same unit
s = rep(s, "    bool _dOk = (stMinStop <= 0 or _r >= stMinStop) and (stMaxStop <= 0 or _r <= stMaxStop) and _lotOk\n",
        "    // v11.2: the group 24 limits in the unit of group 38 (pips, or % of the entry price)\n"
        "    float _mnS = stBuPipM ? stMinStop * stPipSz : stBuPctM ? stEnt * stMinStop / 100.0 : stMinStop\n"
        "    float _mxS = stBuPipM ? stMaxStop * stPipSz : stBuPctM ? stEnt * stMaxStop / 100.0 : stMaxStop\n"
        "    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk\n")

# ---- one more table row: the buffer in use
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 47, ", "stTbl := table.new(f_stPos(stStatPos), 2, 48, ")
old = '    f_stCell(stTbl, 46, "HTF EQUILIBRIUM FIRST (group 37)", _eqT, '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    "    // v11.2: the stop buffer in use, in price\n"
    '    string _buU = stBuPipM ? " pips" : stBuPctM ? " %" : ""\n'
    '    string _buT = stBuPipM ? (str.tostring(stBuPips) + " pips x " + str.tostring(stPipSz) + " = " + str.tostring(f_stBuf(close), format.mintick)) : stBuPctM ? (str.tostring(stBuPct) + "% of the level = " + str.tostring(f_stBuf(close), format.mintick) + " now") : ("price " + str.tostring(stSlBuf))\n'
    '    if stMinStop > 0 or stMaxStop > 0\n'
    '        _buT := _buT + "  |  skip closer " + (stMinStop > 0 ? str.tostring(stMinStop) + _buU : "off") + " / further " + (stMaxStop > 0 ? str.tostring(stMaxStop) + _buU : "off")\n'
    '    f_stCell(stTbl, 47, "STOP BUFFER (group 38)", _buT, stBuPipM or stBuPctM ? color.aqua : color.gray)\n'
) + s[j:]

assert all(ord(ch) < 128 for ch in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v11.2.txt", "w").write(s)
print("v11.2 written:", len(s.split("\n")), "lines")
