# v11.0 -> v11.1 : 'against the higher timeframe' modes of 'Take trades on' - the mirror of the favourable modes
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v11.0.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


FAV = " - higher timeframe favourable"
AGN = " - against the higher timeframe"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v11.0  -  ")
s = rep(s, l2, l2.replace("v11.0  -  ", "v11.1  -  ", 1).replace(
    "  -  ASCII only", ", v11.1: against-the-higher-timeframe modes  -  ASCII only"))

# ---- three more choices for 'Take trades on' (the old six unchanged, so saved settings still match)
s = rep(s, '"CHOCH and BOS' + FAV + '"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n',
        '"CHOCH and BOS' + FAV + '", "CHOCH only' + AGN + '", "BOS only' + AGN + '", "CHOCH and BOS' + AGN + '"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n'
        "AGAINST THE HIGHER TIMEFRAME (v11.1, the last three choices): the mirror of the favourable modes - the same signals, but ONLY AGAINST the higher timeframe. "
        "Higher timeframe bullish: only sells. Bearish: only buys. Not clear yet: no trades. Entry: always rule 1 (the pullback %) - rule 2 needs the higher timeframe "
        "to agree, so with rule 1 off these modes take no trades. A waiting order is cancelled when the higher timeframe turns to agree with it; an open trade keeps "
        "running to its stop or target. Filter b (group 34) is not used in these modes.\\n\\n")

# ---- the mode flag; the higher timeframe is needed for it too
s = rep(s, """bool   stFav   = str.contains(stSigSrc, "favourable")
bool   stHfEff = stHfOn or stFav
bool   _u15    = stOn and (stR2On or stHfEff or stEqOn) and stHtfOk
""", """bool   stFav   = str.contains(stSigSrc, "favourable")
// v11.1: the 'against the higher timeframe' modes - only signals the other way to the higher timeframe, entered by rule 1
bool   stAgn   = str.contains(stSigSrc, "against the higher timeframe")
bool   stHfEff = stHfOn or stFav
bool   _u15    = stOn and (stR2On or stHfEff or stEqOn or stAgn) and stHtfOk
""")

# ---- a waiting order is cancelled when the higher timeframe turns to agree with it
old = """if stFav and stDir != 0 and stT15 != stDir
    f_audEnd("CANCELLED - higher timeframe flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
"""
s = rep(s, old, old + """// v11.1: in an 'against the higher timeframe' mode a waiting order is cancelled when the higher timeframe is no longer
// the other way to it (an open trade keeps running)
if stAgn and stDir != 0 and stT15 != -stDir
    f_audEnd("CANCELLED - higher timeframe now agrees", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
""")

# ---- the entry decision: in an against mode only a signal the other way to the higher timeframe, by rule 1
s = rep(s, """        bool _use   = _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfEff)
        if not _agree and stR1On and stHfEff
            stCntHf += 1
        _audS := not _use ? (_agree ? "SKIP - no broken pivot" : stHfEff and stR1On ? (stFav ? "SKIP - against the higher timeframe (favourable mode)" : "SKIP - against the higher timeframe (filter)") : "SKIP - HTF not agreeing (rule 2 only)") :""",
        """        bool _agst  = (_d == 1 and stT15 == -1) or (_d == -1 and stT15 == 1)
        bool _use   = stAgn ? (_agst and stR1On) : _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfEff)
        if (stAgn and not _agst and stR1On) or (not stAgn and not _agree and stR1On and stHfEff)
            stCntHf += 1
        _audS := not _use ? (stAgn ? (not stR1On ? "SKIP - rule 1 is off (against mode)" : _agree ? "SKIP - with the higher timeframe (against mode)" : "SKIP - higher timeframe not clear (against mode)") : _agree ? "SKIP - no broken pivot" : stHfEff and stR1On ? (stFav ? "SKIP - against the higher timeframe (favourable mode)" : "SKIP - against the higher timeframe (filter)") : "SKIP - HTF not agreeing (rule 2 only)") :""")
s = rep(s, "            stRule := _agree and stR2On ? 2 : 1\n", "            stRule := _agree and stR2On and not stAgn ? 2 : 1\n")
s = rep(s, "            stFix  := _agree and stR2On ? _piv : na\n", "            stFix  := _agree and stR2On and not stAgn ? _piv : na\n")
s = rep(s, '((_agree and stR2On ? "R2" : "R1") + " ARMED")', '((_agree and stR2On and not stAgn ? "R2" : "R1") + " ARMED")')
s = rep(s, '"  HTF " + (not stR2On and not stHfEff and not stEqOn ? "off"', '"  HTF " + (not stR2On and not stHfEff and not stEqOn and not stAgn ? "off"')

# ---- table rows 21 and 22
s = rep(s, '''+ (stFav ? "  |  HTF favourable only" : ""), stR1On or stR2On ? color.aqua : color.red)''',
        '''+ (stFav ? "  |  HTF favourable only" : stAgn ? (stR1On ? "  |  against the HTF only (rule 1)" : "  |  against the HTF needs rule 1 - NO TRADES") : ""), (stR1On or stR2On) and not (stAgn and not stR1On) ? color.aqua : color.red)''')
s = rep(s, '''stR2On or stHfEff or stEqOn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfEff or stEqOn) and stHtfOk ? color.aqua''',
        '''stR2On or stHfEff or stEqOn or stAgn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfEff or stEqOn or stAgn) and stHtfOk ? color.aqua''')

assert all(ord(c) < 128 for c in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v11.1.txt", "w").write(s)
print("ok", len(s.split("\n")))
