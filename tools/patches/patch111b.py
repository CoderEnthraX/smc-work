# v11.1 part 2 : 'auto' modes of 'Take trades on' - against the higher timeframe until its equilibrium is touched, then with it
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v11.1.txt").read()
assert "stAutoM" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


AGN = " - against the higher timeframe"
AUT = " - auto: against HTF to equilibrium, then with HTF"

# ---- line 2
s = rep(s, ", v11.1: against-the-higher-timeframe modes  -  ASCII only", ", v11.1: against-the-higher-timeframe modes and auto modes  -  ASCII only")

# ---- three more choices for 'Take trades on' (the old nine unchanged)
s = rep(s, '"CHOCH and BOS' + AGN + '"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n',
        '"CHOCH and BOS' + AGN + '", "CHOCH only' + AUT + '", "BOS only' + AUT + '", "CHOCH and BOS' + AUT + '"], group = gStg, tooltip = "Which main-tier structure events are allowed to start a trade.\\n\\n'
        "AUTO (v11.1, the last three choices): every CHOCH or BOS on the higher timeframe starts a new leg. PART 1 - until the price touches the equilibrium of that leg "
        "(the % in group 37): only signals AGAINST the higher timeframe, entered by rule 1 - trading the pullback. PART 2 - from the touch on: only signals WITH the "
        "higher timeframe, entered like the favourable modes (rule 2 on = the broken pivot, else rule 1) - trading the move back. The next higher-timeframe CHOCH or BOS "
        "starts part 1 again. A waiting order on the wrong side after a switch is cancelled; an open trade keeps running. Higher timeframe not clear: no trades. "
        "The group 37 switch is not used in these modes - only its %.\\n\\n")
s = rep(s, 'stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg", minval = 1.0, maxval = 99.0, step = 0.5, group = gEq, tooltip = "50 (default) = the middle of the higher-timeframe leg.',
        'stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg", minval = 1.0, maxval = 99.0, step = 0.5, group = gEq, tooltip = "Also used by the AUTO modes of Take trades on (group 20), even with the switch above off. 50 (default) = the middle of the higher-timeframe leg.')

# ---- the mode flag; it needs the higher timeframe
s = rep(s, """bool   stAgn   = str.contains(stSigSrc, "against the higher timeframe")
""", """bool   stAgn   = str.contains(stSigSrc, "against the higher timeframe")
// v11.1: the 'auto' modes - against the higher timeframe until its equilibrium is touched, then with it
bool   stAutoM = str.contains(stSigSrc, "auto: against HTF")
""")
s = rep(s, "bool   _u15    = stOn and (stR2On or stHfEff or stEqOn or stAgn) and stHtfOk\n",
        "bool   _u15    = stOn and (stR2On or stHfEff or stEqOn or stAgn or stAutoM) and stHtfOk\n")

# ---- the equilibrium is followed for the auto modes too; the group 37 gate does not block them; the side allowed now
s = rep(s, """if stEqOn and not stEqOpen and not na(stEqLvl) and ((stT15 == 1 and low <= stEqLvl) or (stT15 == -1 and high >= stEqLvl))
    stEqOpen := true
bool stEqBlock = stEqOn and not stEqOpen
""", """if (stEqOn or stAutoM) and not stEqOpen and not na(stEqLvl) and ((stT15 == 1 and low <= stEqLvl) or (stT15 == -1 and high >= stEqLvl))
    stEqOpen := true
bool stEqBlock = stEqOn and not stAutoM and not stEqOpen
// v11.1: auto modes - the side that may trade now: against the higher timeframe before the touch, with it after (0 = none)
int  stAutoDir = stAutoM ? (stEqOpen ? stT15 : -stT15) : 0
""")

# ---- a waiting order on the wrong side after a switch is cancelled
old = """if stAgn and stDir != 0 and stT15 != -stDir
    f_audEnd("CANCELLED - higher timeframe now agrees", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
"""
s = rep(s, old, old + """// v11.1: in an 'auto' mode a waiting order is cancelled when the side it may trade changes (an open trade keeps running)
if stAutoM and stDir != 0 and stDir != stAutoDir
    f_audEnd("CANCELLED - auto mode switched side", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
""")

# ---- the entry decision
s = rep(s, """        bool _use   = stAgn ? (_agst and stR1On) : _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfEff)
        if (stAgn and not _agst and stR1On) or (not stAgn and not _agree and stR1On and stHfEff)
            stCntHf += 1
        _audS := not _use ? (stAgn ?""", """        bool _use   = stAutoM ? (stAutoDir != 0 and _d == stAutoDir and (stEqOpen ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : stR1On)) : stAgn ? (_agst and stR1On) : _agree ? ((stR2On and not na(_piv)) or (not stR2On and stR1On)) : (stR1On and not stHfEff)
        if (stAutoM and not _use) or (not stAutoM and stAgn and not _agst and stR1On) or (not stAutoM and not stAgn and not _agree and stR1On and stHfEff)
            stCntHf += 1
        _audS := not _use ? (stAutoM ? (stAutoDir == 0 ? "SKIP - higher timeframe not clear (auto mode)" : _d != stAutoDir ? (stEqOpen ? "SKIP - auto mode: with the higher timeframe only (equilibrium reached)" : "SKIP - auto mode: against the higher timeframe only (equilibrium not reached)") : stEqOpen ? "SKIP - no broken pivot" : "SKIP - rule 1 is off (auto mode, first part)") : stAgn ?""")
s = rep(s, '"  HTF " + (not stR2On and not stHfEff and not stEqOn and not stAgn ? "off"', '"  HTF " + (not stR2On and not stHfEff and not stEqOn and not stAgn and not stAutoM ? "off"')

# ---- table rows 21, 22 and 46
s = rep(s, '''stAgn ? (stR1On ? "  |  against the HTF only (rule 1)" : "  |  against the HTF needs rule 1 - NO TRADES") : ""), (stR1On or stR2On) and not (stAgn and not stR1On) ? color.aqua : color.red)''',
        '''stAgn ? (stR1On ? "  |  against the HTF only (rule 1)" : "  |  against the HTF needs rule 1 - NO TRADES") : stAutoM ? (stR1On ? "  |  auto: against the HTF, then with it" : "  |  auto: no trades before the equilibrium (rule 1 off)") : ""), (stR1On or stR2On) and not (stAgn and not stR1On) ? color.aqua : color.red)''')
s = rep(s, '''stR2On or stHfEff or stEqOn or stAgn ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfEff or stEqOn or stAgn) and stHtfOk''',
        '''stR2On or stHfEff or stEqOn or stAgn or stAutoM ? (stHtfOk ? f_tfName(stHtfTf) : "off (not above chart)") : "off (rule 2 off)", (stR2On or stHfEff or stEqOn or stAgn or stAutoM) and stHtfOk''')
s = rep(s, '''    string _eqT = not stEqOn ? "off" :''',
        '''    string _eqT = stAutoM ? (not stHtfOk ? "auto mode - higher timeframe not above the chart - no trades" : stAutoDir == 0 ? "AUTO - no higher timeframe leg yet" : stEqOpen ? ("AUTO part 2 - WITH the HTF (" + str.tostring(stEqPct) + "% reached)") : ("AUTO part 1 - AGAINST the HTF until " + (na(stEqLvl) ? "-" : str.tostring(stEqLvl, format.mintick)))) : not stEqOn ? "off" :''')
s = rep(s, '''f_stCell(stTbl, 46, "HTF EQUILIBRIUM FIRST (group 37)", _eqT, not stEqOn ? color.gray :''',
        '''f_stCell(stTbl, 46, "HTF EQUILIBRIUM FIRST (group 37)", _eqT, not stEqOn and not stAutoM ? color.gray :''')

assert all(ord(c) < 128 for c in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v11.1.txt", "w").write(s)
print("ok", len(s.split("\n")))
