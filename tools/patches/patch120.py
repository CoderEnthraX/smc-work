# v11.2 -> v12.0 : RULE 3 - enter at the close of the signal candle (group 39, everything OFF by default)
#   + optional: only when the close is at most N beyond the broken level (default 3, OFF)
#   The 'skip if the stop is CLOSER / FURTHER than' limits are the existing group 24 settings (0 = off): they already
#   apply to every entry rule, rule 3 included.
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v11.2.txt").read()
assert "stR3On" not in s and "stCntR3" not in s and "stMktBar" not in s and "f_stR3Lim" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v11.2  -  ")
s = rep(s, l2, l2.replace("v11.2  -  ", "v12.0  -  ", 1).replace(
    "  -  ASCII only", ", v12.0: rule 3 enters at the close of the signal candle, optionally only when the close is at most N beyond the broken level  -  ASCII only"))

# ---- the new settings, at the END of the list (group 39)
old = 'stBuPip  = input.float(0.0, "  - pip size (0 = automatic)", '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    'gCc = "39. RULE 3 - enter at the close of the signal candle (v12.0)"\n'
    'stR3On    = input.bool(false, "RULE 3 - enter at the close of the signal candle", group = gCc, tooltip = '
    '"OFF (default): rules 1 and 2 as before - the strategy waits for the pullback.\\n\\n'
    'ON: the moment a candle CLOSES and confirms the signal (your CHOCH; a BOS too if you trade BOS), the strategy enters - a market order that fills at the '
    'open of the next candle, which is practically the close. It does not matter where the candle closes. No pullback; rules 1 and 2 are not used. '
    'Stop = the CHOCH* level + your stop buffer, as always; target = your R multiple from the entry; the size comes from your risk and that distance.\\n\\n'
    'Group 24 \'Skip the setup if the stop is CLOSER / FURTHER than\' (0 = off) works for rule 3 too, like for rules 1 and 2.\\n\\n'
    'Everything else is unchanged: entry hours, news windows, weekend, loss pause, loss recovery, the higher-timeframe filters (b, favourable / against / auto). '
    'Rule 3 does NOT need the higher timeframe to agree (like rule 1). A signal outside the entry hours or while trading is blocked opens nothing - there is no '
    'late entry. With close and reverse ON, a signal that reverses an open trade enters one candle later, after the old trade is closed.")\n'
    'stR3BrkOn = input.bool(false, "  - RULE 3: only if the close is near the broken level", group = gCc, tooltip = '
    '"OFF (default): rule 3 enters wherever the signal candle closes.\\n\\n'
    'ON: rule 3 enters only when the close is at most the distance set in the next setting (default 3) beyond the level the candle broke (the broken high of a bullish CHOCH, the broken low '
    'of a bearish one). A candle that closes far beyond it is skipped.\\n\\n'
    'Example with 3: the broken high is 4,100.00. Close 4,102.50 = 2.50 beyond: enters. Close 4,108.00 = 8.00 beyond: skipped.")\n'
    'stR3Brk   = input.float(3.0, "  - the most the close may be beyond the broken level", minval = 0.0, step = 0.00000001, group = gCc, tooltip = '
    '"Used only with the switch above ON. In the unit of group 38 like group 24: Price = dollars on gold (3 = 3.00); Pips (3 pips = 0.30 on gold); '
    '% of the price. 3 (default).")\n'
) + s[j:]

# ---- helper after the stop buffer function (v11.2)
old = "    stBuPipM ? math.round_to_mintick(stBuPips * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stBuPct / 100.0) : stSlBuf\n"
s = rep(s, old, old + (
    "// v12.0: the rule 3 'near the broken level' distance in price (the unit of group 38: price, pips, or % of the close)\n"
    "f_stR3Lim(float _v, float _px) =>\n"
    "    stBuPipM ? _v * stPipSz : stBuPctM ? _px * _v / 100.0 : _v\n"))

# ---- state + counters
s = rep(s, "var int stCntR2   = 0\n", "var int stCntR2   = 0\n"
        "var int stCntR3   = 0       // v12.0: trades entered at the close of the signal candle (rule 3)\n"
        "var int stCntR3Far = 0      // v12.0: rule 3 signals skipped - the close too far beyond the broken level\n"
        "var int stMktBar  = na      // v12.0: the bar a rule 3 market entry was sent on\n")

# ---- fill counters
s = rep(s, "    if stRule == 2\n        stCntR2 += 1\n    else\n        stCntR1 += 1\n",
        "    if stRule == 3\n        stCntR3 += 1\n    else if stRule == 2\n        stCntR2 += 1\n    else\n        stCntR1 += 1\n")

# ---- a rule 3 entry has one chance; the live-stop update is for rule 1 only
old = "// RULE 1 follows the live level (Continuous mode). RULE 2 keeps the stop it was armed with: its entry is the\n"
s = rep(s, old, (
    "// v12.0: a rule 3 entry at the signal close has ONE chance - it is sent on the signal candle (or on the next one when an\n"
    "// opposite trade had to close first) and fills at the next open. It is never sent again at a later price.\n"
    "if stDir != 0 and stRule == 3 and ((not na(stMktBar) and bar_index > stMktBar) or (not na(stArmBar) and bar_index > stArmBar + 1))\n"
    '    f_audEnd("CANCELLED - the entry at the signal close did not fill", stAudCancC)\n'
    "    if f_stCancel(stOrdLive, stPendId)\n"
    "        stCnlSent := true\n"
    "    stOrdLive := false\n"
    "    stCntCanc += 1\n"
    "    stDir := 0\n\n") + old)
s = rep(s, "if stDir != 0 and stRule != 2 and not (stOnce and stPlaced)\n", "if stDir != 0 and stRule != 2 and stRule != 3 and not (stOnce and stPlaced)\n")

# ---- arming: rule 3
old = ("        if (stAutoM and not _use) or (not stAutoM and stAgn and not _agst and stR1On) or (not stAutoM and not stAgn and not _agree and stR1On and stHfEff)\n"
       "            stCntHf += 1\n")
s = rep(s, old, (
    "        bool _hfSkip = (stAutoM and not _use) or (not stAutoM and stAgn and not _agst and stR1On) or (not stAutoM and not stAgn and not _agree and stR1On and stHfEff)\n"
    "        // v12.0: RULE 3 - enter at the close of this candle. Rules 1 / 2 are not used; the higher-timeframe filters still are\n"
    "        // (like rule 1: no agreement needed). Optionally only when the close is near the broken level.\n"
    "        float _r3B   = na(_piv) ? na : _d * (close - _piv)\n"
    "        bool  _r3Far = stR3On and stR3BrkOn and (na(_r3B) or _r3B > f_stR3Lim(stR3Brk, close))\n"
    "        bool  _useM  = stAutoM ? (stAutoDir != 0 and _d == stAutoDir) : stAgn ? _agst : (_agree or not stHfEff)\n"
    "        if stR3On\n"
    "            _hfSkip := not _r3Far and not _useM\n"
    "            _use    := not _r3Far and _useM\n"
    "        if _hfSkip\n"
    "            stCntHf += 1\n"))
old = '        if _use and not na(_opl)\n            if stDir != 0\n                stCntCanc += 1\n                f_audEnd("CANCELLED - new signal", stAudCancC)\n'
s = rep(s, old, (
    "        if stR3On\n"
    "            if _r3Far\n"
    '                _audS := "SKIP - RULE 3: " + (na(_r3B) ? "no broken level" : "close " + str.tostring(_r3B, format.mintick) + " beyond the broken level")\n'
    "                stCntR3Far += 1\n"
    "            else\n"
    '                _audS := not _useM ? (stAutoM ? "SKIP - auto mode: other side now" : stAgn ? "SKIP - not against the higher timeframe (against mode)" : stFav ? "SKIP - against the higher timeframe (favourable mode)" : "SKIP - against the higher timeframe (filter)") : na(_opl) ? "SKIP - no stop level" : "R3 ARMED - entry at the close"\n') + old)
s = rep(s, "            stRule := _agree and stR2On and not stAgn ? 2 : 1\n",
        "            stRule := stR3On ? 3 : (_agree and stR2On and not stAgn ? 2 : 1)\n"
        "            stMktBar := na\n")
s = rep(s, "            stFix  := _agree and stR2On and not stAgn ? _piv : na\n",
        "            stFix  := stRule == 2 ? _piv : na\n")

# ---- the entry: the close for rule 3
s = rep(s, "    stEnt := stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : f_retLvl(trendDir, mAnch, mOrig, stPbPct))\n",
        "    stEnt := stRule == 3 ? close : stOnce and stPlaced and not na(stEntLock) ? stEntLock : (stRule == 2 ? stFix : f_retLvl(trendDir, mAnch, mOrig, stPbPct))\n")

# ---- market orders for rule 3 (limit = na)
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
    "    // v12.0: rule 3 - entries at the close of the signal candle (group 39)\n"
    '    string _r3U = stBuPipM ? " pips" : stBuPctM ? " %" : ""\n'
    '    string _r3T = not stR3On ? "off - rules 1 / 2" : "on  -  " + str.tostring(stCntR3) + " entered at the close" + (stR3BrkOn ? "  |  close within " + str.tostring(stR3Brk) + _r3U + " of the break: " + str.tostring(stCntR3Far) + " skipped" : "")\n'
    '    f_stCell(stTbl, 48, "RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", _r3T, stR3On ? color.aqua : color.gray)\n'
) + s[j:]

assert all(ord(ch) < 128 for ch in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v12.0.txt", "w").write(s)
print("v12.0 written:", len(s.split("\n")), "lines")
