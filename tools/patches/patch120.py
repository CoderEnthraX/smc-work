# v11.2 -> v12.0 : RULE 3 / RULE 4 - enter at the close of the signal candle (group 39, OFF by default)
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v11.2.txt").read()
assert "stCcMode" not in s and "stCntR3" not in s and "stMktBar" not in s and "f_stCcLim" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


OFF = "Off (rules 1 / 2 as now)"
R3 = "RULE 3 - always enter at the close"
R4 = "RULE 4 - enter at the close only if the stop distance is within the limits"
SKIP = "Skip the setup"
FB = "Fall back to RULE 1 / 2 (wait for the pullback)"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v11.2  -  ")
s = rep(s, l2, l2.replace("v11.2  -  ", "v12.0  -  ", 1).replace(
    "  -  ASCII only", ", v12.0: rule 3 enters at the close of the signal candle, rule 4 the same only when the entry-to-stop distance is within your limits (skip, or fall back to rule 1 / 2)  -  ASCII only"))

# ---- the new settings, at the END of the list (group 39)
old = 'stBuPip  = input.float(0.0, "  - pip size (0 = automatic)", '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    'gCc = "39. Entry at the close of the signal candle - rules 3 / 4 (v12.0)"\n'
    'stCcMode = input.string("' + OFF + '", "Entry at the close of the signal candle", options = ["' + OFF + '", "' + R3 + '", "' + R4 + '"], group = gCc, tooltip = '
    '"OFF (default): rules 1 and 2 as before - the strategy waits for the pullback.\\n\\n'
    'RULE 3: the moment a candle CLOSES and confirms the signal (your CHOCH; a BOS too if you trade BOS), the strategy enters - a market order that fills at the '
    'open of the next candle, which is practically the close. No pullback. Rules 1 and 2 are not used. Stop = the CHOCH* level + your stop buffer, as always; '
    'target = your R multiple from the entry; the size comes from your risk and that distance.\\n\\n'
    'RULE 4: the same, but first the distance from the close to the stop is checked against the two limits below. A huge signal candle means a far stop: '
    'the setup is skipped (or falls back to rule 1 / 2, see below).\\n\\n'
    'Example: stop 4,089.00. The candle closes at 4,101.00: distance 12.00, inside 3 - 30, enters. A huge candle closes at 4,125.00: distance 36.00 - more than 30, skipped.\\n\\n'
    'Everything else is unchanged: entry hours, news windows, weekend, loss pause, loss recovery, the higher-timeframe filters (b, favourable / against / auto), '
    'group 24. Rule 3 / 4 do NOT need the higher timeframe to agree (like rule 1). A signal outside the entry hours or while trading is blocked opens nothing - '
    'there is no late entry. With close and reverse ON, a signal that reverses an open trade enters one candle later, after the old trade is closed.")\n'
    'stCcMax = input.float(30.0, "  - RULE 4: skip if the stop is FURTHER than  (0 = off)", minval = 0.0, step = 0.00000001, group = gCc, tooltip = '
    '"RULE 4 only. The largest entry-to-stop distance a trade may have, in the unit of group 38 (Price = dollars on gold; pips; or % of the entry price). '
    '30 (default) = 30.00 on gold. 0 = no upper limit.")\n'
    'stCcMin = input.float(3.0, "  - RULE 4: skip if the stop is CLOSER than  (0 = off)", minval = 0.0, step = 0.00000001, group = gCc, tooltip = '
    '"RULE 4 only. The smallest entry-to-stop distance a trade may have, same unit. 3 (default) = 3.00 on gold - a very tight stop is mostly noise. A setup '
    'with a stop this close is always skipped (a pullback entry would be even closer). 0 = no lower limit.")\n'
    'stCcFar = input.string("' + SKIP + '", "  - RULE 4: when the stop is too far", options = ["' + SKIP + '", "' + FB + '"], group = gCc, tooltip = '
    '"RULE 4 only.\\n\\nSKIP THE SETUP (default): a signal candle with a stop further than the limit opens nothing.\\n\\n'
    'FALL BACK TO RULE 1 / 2: the setup is armed the normal way instead - a limit order at the pullback (rule 1) or the broken pivot (rule 2), with your rule 1 / 2 '
    'switches and the higher-timeframe rule of rule 2. That pullback entry must keep the same rule 4 limits: if its stop is further than the limit (or closer '
    'than the minimum) it is cancelled too.")\n'
) + s[j:]

# ---- helpers after the stop buffer function (v11.2)
old = "    stBuPipM ? math.round_to_mintick(stBuPips * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stBuPct / 100.0) : stSlBuf\n"
s = rep(s, old, old + (
    "// v12.0: rules 3 / 4 (group 39) - a rule 4 limit in price (the unit of group 38: price, pips, or % of the entry price), and the check\n"
    'var bool stCcOn = stCcMode != "' + OFF + '"\n'
    'var bool stCcR4 = stCcMode == "' + R4 + '"\n'
    'var bool stCcFb = stCcFar == "' + FB + '"\n'
    "f_stCcLim(float _v, float _ent) =>\n"
    "    stBuPipM ? _v * stPipSz : stBuPctM ? _ent * _v / 100.0 : _v\n"
    "f_stCcOk(float _r, float _ent) =>\n"
    "    (stCcMin <= 0 or _r >= f_stCcLim(stCcMin, _ent)) and (stCcMax <= 0 or _r <= f_stCcLim(stCcMax, _ent))\n"))

# ---- state + counters
s = rep(s, "var int stCntR2   = 0\n", "var int stCntR2   = 0\n"
        "var int stCntR3   = 0       // v12.0: trades entered at the close of the signal candle (rule 3 / 4)\n"
        "var int stCntCcFar  = 0     // v12.0: rule 4 - signals skipped, stop too far\n"
        "var int stCntCcNear = 0     // v12.0: rule 4 - signals skipped, stop too close\n"
        "var int stCntCcFb   = 0     // v12.0: rule 4 - setups that fell back to rule 1 / 2\n"
        "var bool stCcLim  = false   // v12.0: a rule 4 setup that fell back - its pullback entry keeps the rule 4 limits\n"
        "var int  stMktBar = na      // v12.0: the bar a rule 3 / 4 market entry was sent on\n")

# ---- fill counters
s = rep(s, "    if stRule == 2\n        stCntR2 += 1\n    else\n        stCntR1 += 1\n",
        "    if stRule == 3\n        stCntR3 += 1\n    else if stRule == 2\n        stCntR2 += 1\n    else\n        stCntR1 += 1\n")

# ---- a rule 3 / 4 entry has one chance; the live-stop update is for rule 1 only
old = "// RULE 1 follows the live level (Continuous mode). RULE 2 keeps the stop it was armed with: its entry is the\n"
s = rep(s, old, (
    "// v12.0: a rule 3 / 4 entry at the signal close has ONE chance - it is sent on the signal candle (or on the next one when an\n"
    "// opposite trade had to close first) and fills at the next open. It is never sent again at a later price.\n"
    "if stDir != 0 and stRule == 3 and ((not na(stMktBar) and bar_index > stMktBar) or (not na(stArmBar) and bar_index > stArmBar + 1))\n"
    '    f_audEnd("CANCELLED - the entry at the signal close did not fill", stAudCancC)\n'
    "    if f_stCancel(stOrdLive, stPendId)\n"
    "        stCnlSent := true\n"
    "    stOrdLive := false\n"
    "    stCntCanc += 1\n"
    "    stDir := 0\n\n") + old)
s = rep(s, "if stDir != 0 and stRule != 2 and not (stOnce and stPlaced)\n", "if stDir != 0 and stRule != 2 and stRule != 3 and not (stOnce and stPlaced)\n")

# ---- arming: rules 3 / 4
old = ("        if (stAutoM and not _use) or (not stAutoM and stAgn and not _agst and stR1On) or (not stAutoM and not stAgn and not _agree and stR1On and stHfEff)\n"
       "            stCntHf += 1\n")
s = rep(s, old, (
    "        bool _hfSkip = (stAutoM and not _use) or (not stAutoM and stAgn and not _agst and stR1On) or (not stAutoM and not stAgn and not _agree and stR1On and stHfEff)\n"
    "        // v12.0: rules 3 / 4 - enter at the close of this candle. Rules 1 / 2 are not used (a rule 4 setup may fall back to them);\n"
    "        // the higher-timeframe filters still are (like rule 1: no agreement needed)\n"
    "        float _ccSl   = na(_opl) ? na : (_d == 1 ? _opl - f_stBuf(_opl) : _opl + f_stBuf(_opl))\n"
    "        float _ccR    = na(_ccSl) ? na : _d * (close - _ccSl)\n"
    "        bool  _ccFar  = stCcR4 and not na(_ccR) and stCcMax > 0 and _ccR > f_stCcLim(stCcMax, close)\n"
    "        bool  _ccNear = stCcR4 and not na(_ccR) and stCcMin > 0 and _ccR < f_stCcLim(stCcMin, close)\n"
    "        bool  _ccMkt  = stCcOn and not _ccFar and not _ccNear\n"
    "        bool  _ccBack = stCcOn and _ccFar and not _ccNear and stCcFb\n"
    "        bool  _useM   = stAutoM ? (stAutoDir != 0 and _d == stAutoDir) : stAgn ? _agst : (_agree or not stHfEff)\n"
    "        if stCcOn\n"
    "            _hfSkip := _ccMkt ? not _useM : _ccBack ? _hfSkip : false\n"
    "            _use    := _ccMkt ? _useM : _ccBack ? _use : false\n"
    "        if _hfSkip\n"
    "            stCntHf += 1\n"))
old = '        if _use and not na(_opl)\n            if stDir != 0\n                stCntCanc += 1\n                f_audEnd("CANCELLED - new signal", stAudCancC)\n'
s = rep(s, old, (
    "        if stCcOn\n"
    "            string _ccD = na(_ccR) ? \"\" : str.tostring(_ccR, format.mintick)\n"
    "            if _ccMkt\n"
    '                _audS := not _useM ? (stAutoM ? "SKIP - auto mode: other side now" : stAgn ? "SKIP - not against the higher timeframe (against mode)" : stFav ? "SKIP - against the higher timeframe (favourable mode)" : "SKIP - against the higher timeframe (filter)") : na(_opl) ? "SKIP - no stop level" : (stCcR4 ? "R4" : "R3") + " ARMED - entry at the close, stop " + _ccD\n'
    "            else if _ccNear\n"
    '                _audS := "SKIP - RULE 4: stop too close (" + _ccD + ")"\n'
    "                stCntCcNear += 1\n"
    "            else if not _ccBack\n"
    '                _audS := "SKIP - RULE 4: stop too far (" + _ccD + ")"\n'
    "                stCntCcFar += 1\n"
    "            else\n"
    '                _audS := _audS + "\\n(RULE 4 fell back: stop " + _ccD + " too far at the close)"\n'
    "                if _use and not na(_opl)\n"
    "                    stCntCcFb += 1\n") + old)
s = rep(s, "            stRule := _agree and stR2On and not stAgn ? 2 : 1\n",
        "            stRule := stCcOn and _ccMkt ? 3 : (_agree and stR2On and not stAgn ? 2 : 1)\n"
        "            stCcLim  := _ccBack\n"
        "            stMktBar := na\n")
s = rep(s, "            stFix  := _agree and stR2On and not stAgn ? _piv : na\n",
        "            stFix  := stRule == 2 ? _piv : na\n")

# ---- the entry: the close for rule 3 / 4
s = rep(s, "    stEnt := stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : f_retLvl(trendDir, mAnch, mOrig, stPbPct))\n",
        "    stEnt := stRule == 3 ? close : stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : f_retLvl(trendDir, mAnch, mOrig, stPbPct))\n")

# ---- the rule 4 limits at the order (the market entry, and a pullback entry that fell back)
s = rep(s, "    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk\n",
        "    // v12.0: the rule 4 limits - for the entry at the close, and for a pullback entry a rule 4 setup fell back to\n"
        "    bool _ccOk = not ((stRule == 3 and stCcR4) or stCcLim) or f_stCcOk(_r, stEnt)\n"
        "    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk and _ccOk\n")

# ---- market orders for rule 3 / 4 (limit = na)
for a in ('strategy.entry(stPendId, strategy.long, qty = _qm, limit = stEnt,', 'strategy.entry(stPendId, strategy.short, qty = _qm, limit = stEnt,',
          'strategy.entry(_pId, strategy.long, qty = _q1, limit = stEnt,', 'strategy.entry(_pId, strategy.short, qty = _q1, limit = stEnt,'):
    s = rep(s, a, a.replace("limit = stEnt,", "limit = stRule == 3 ? na : stEnt,"))
s = rep(s, "            stOrdLive := true\n            stLastCapQ := _qCap\n",
        "            stOrdLive := true\n"
        "            if stRule == 3 and na(stMktBar)\n"
        "                stMktBar := bar_index\n"
        "            stLastCapQ := _qCap\n")

# ---- one more table row
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 48, ", "stTbl := table.new(f_stPos(stStatPos), 2, 49, ")
old = '    f_stCell(stTbl, 47, "STOP BUFFER (group 38)", _buT, '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    "    // v12.0: entries at the close of the signal candle (group 39)\n"
    '    string _ccU = stBuPipM ? " pips" : stBuPctM ? " %" : ""\n'
    '    string _ccT = not stCcOn ? "off - rules 1 / 2" : (stCcR4 ? "RULE 4 (" + (stCcMin > 0 ? str.tostring(stCcMin) : "0") + " - " + (stCcMax > 0 ? str.tostring(stCcMax) : "no max") + _ccU + ")" : "RULE 3") + "  -  " + str.tostring(stCntR3) + " entered at the close"\n'
    "    if stCcR4\n"
    '        _ccT := _ccT + "  |  skipped: too far " + str.tostring(stCntCcFar) + " / too close " + str.tostring(stCntCcNear) + (stCcFb ? "  |  fell back " + str.tostring(stCntCcFb) : "")\n'
    '    f_stCell(stTbl, 48, "ENTRY AT THE SIGNAL CLOSE (group 39)", _ccT, stCcOn ? color.aqua : color.gray)\n'
) + s[j:]

assert all(ord(ch) < 128 for ch in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v12.0.txt", "w").write(s)
print("v12.0 written:", len(s.split("\n")), "lines")
