# v12.0 -> v12.1 (everything OFF by default):
#   1. HARD CAP: a 4th choice for 'when the cap is reached' - 'Start again from the base risk (forget the losses)'
#   2. group 41: no NEW trades in the hours before the group 29 US releases (the MT5 EA's group 41 rule, without its calendar)
#   3. group 42: loss recovery starts again from the base risk when the losses carried reach a mark
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v12.0.txt").read()
assert "stPreOn" not in s and "stLmOn" not in s and "stAuN1" not in s and "stCntLm" not in s and "stPreNow" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


RST = "Start again from the base risk (forget the losses)"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v12.0  -  ") and l2.endswith("  -  ASCII only")
s = rep(s, l2, l2.replace("v12.0  -  ", "v12.1  -  ", 1)[:-len("  -  ASCII only")] +
        ", v12.1: hard cap 'start again from the base risk', a loss mark that starts again from the base, no new trades in the hours before the US releases  -  ASCII only")

# ---- 1. the 4th cap choice (at the end of the list) + its tooltip
s = rep(s, 'options = ["Clamp to the cap and carry on", "Stop for the rest of the day", "Stop permanently"], group = gRsk',
        'options = ["Clamp to the cap and carry on", "Stop for the rest of the day", "Stop permanently", "' + RST + '"], group = gRsk')
s = rep(s, "CLAMP: take the cap as the risk and keep going. The sequence can no longer recover everything, but it keeps trading.\")",
        "CLAMP: take the cap as the risk and keep going. The sequence can no longer recover everything, but it keeps trading.\\n\\n"
        "START AGAIN FROM THE BASE RISK (v12.1): the losses carried are forgotten and the next trade risks the BASE again - trading carries on. "
        "For A+ / B+ / C+ the total starts again from zero. Example with a cap of 200, Rule C, split 1, every trade losing: 50, 50, 100, 200, "
        "then 400 would be above 200 -> 50 again.\")")

# ---- 2 + 3. the new settings at the END of the list (groups 41 and 42)
old = 'stR3Fb    = input.bool(false, "  - if the close is too far: fall back to RULE 1 / 2", '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    'gPre = "41. No new trades before news (v12.1)"\n'
    'stPreOn  = input.bool(false, "No NEW trades in the hours before news (group 29 US releases)", group = gPre, tooltip = '
    '"OFF (default): nothing changes.\\n\\n'
    'ON: in the hours before each release that group 29 works out (NFP, weekly jobless claims, ISM Manufacturing / Services - the ones ticked there), '
    'no NEW trade is opened: signals are skipped and a waiting order is cancelled. Open trades run on - your news window (group 25 \'When a window starts\', '
    'and the minutes before / after of group 29) still closes them as before. The same rule as the MT5 EA\'s group 41 (the EA can also use the MT5 economic '
    'calendar; TradingView has no calendar, so CPI / FOMC are not known here).\\n\\n'
    'Needs group 29 \'Automatic US news windows\' ON and the news master switch ON.\\n\\n'
    'Example with 1 hour: jobless claims every Thursday 08:30 New York = 18:00 IST in US summer time. No new trades from 17:00 IST; '
    'the news window then blocks 17:50 - 18:20 and closes open trades at 17:50.")\n'
    'stPreHrs = input.float(1.0, "  - hours before the release (e.g. 1, 2 or 0.5)", minval = 0.1, maxval = 24.0, step = 0.5, group = gPre, tooltip = '
    '"1 (default) = no new trades in the last hour before the release. 0.5 = 30 minutes, 2 = two hours. From 0.1 to 24.")\n'
    'gLm = "42. Loss recovery - start again from the base (v12.1)"\n'
    'stLmOn  = input.bool(false, "Start again from the base risk when the losses carried reach", group = gLm, tooltip = '
    '"Works with any loss-recovery rule (A, B, C, A+, B+, C+ - group 21).\\n\\n'
    'OFF (default): nothing changes.\\n\\n'
    'ON: when a trade closes and the losses carried (the \'Losses carried\' row of the table) reach the amount below or more, they are forgotten and the next '
    'trade risks the BASE again. Trading carries on. For A+ / B+ / C+ the total starts again from zero.\\n\\n'
    'Example with 300, Rule C, split 3, base 50, losing trades: carried 50, 100, 150, 200 (next risk 67), 267 (next risk 89), 356 -> reached 300 -> the next '
    'trade risks 50 again.\\n\\n'
    'The hard cap (group 21) still works as before.")\n'
    'stLmAmt = input.float(300.0, "  - losses carried, in account currency", minval = 0.01, group = gLm, tooltip = '
    '"300 (default). In account currency (USD), the same number as the \'Losses carried\' row of the table.")\n'
) + s[j:]

# ---- state
s = rep(s, "var bool  stSeqHalt = false\n", "var bool  stSeqHalt = false\n"
        "var int   stCntLm = 0        // v12.1: group 42 - times the losses carried reached the mark and were forgotten\n")

# ---- 2. tomorrow's releases + the 'no new trades before news' test
s = rep(s, "var string stHolT0 = \"\"\n", "var string stHolT0 = \"\"\n"
        "// v12.1: tomorrow's releases as well, for 'no new trades before news' (a block that reaches back across midnight New York)\n"
        "var int    stAuN1  = na\nvar int    stAuN2  = na\nvar int    stAuN3  = na\nvar int    stAuN4  = na\n")
s = rep(s, """            stAuT3 := a3
            stAuT4 := a4
""", """            stAuT3 := a3
            stAuT4 := a4
        if stAuOn and stPreOn
            [b1, b2, b3, b4] = f_auDay(hy, hm, hd)
            stAuN1 := b1
            stAuN2 := b2
            stAuN3 := b3
            stAuN4 := b4
""")
s = rep(s, "bool stHolNow = _auUse and not stHolTrade and ",
        "// v12.1: group 41 - the next bar touches [release - hours, release): no NEW trades (the MT5 EA's PreHit)\n"
        "int stPreMs = math.round(stPreHrs * 3600) * 1000\n"
        "f_preHit(int t) =>\n"
        "    not na(t) and time_close < t and time_close + _lenMs > t - stPreMs\n"
        "bool stPreNow = _auUse and stAuOn and stPreOn and (f_preHit(stAuT1) or f_preHit(stAuT2) or f_preHit(stAuT3) or f_preHit(stAuT4) or "
        "f_preHit(stAuN1) or f_preHit(stAuN2) or f_preHit(stAuN3) or f_preHit(stAuN4))\n"
        "bool stHolNow = _auUse and not stHolTrade and ")
s = rep(s, "bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt and not stLdHalt and not stEqBlock\n",
        "bool stGo   = stOn and not stSeqHalt and not stDayHalt and not stDDHit and not stWkBlock and not stNwNow and not stPtHalt and not stLdHalt and not stEqBlock and not stPreNow\n")
s = rep(s, '_audS := "SKIP - " + (not stOn ? "trading off" : stDDHit ? "drawdown stop" : stHolNow ? "US holiday" : stNwNow ? "news window" : stWkBlock',
        '_audS := "SKIP - " + (not stOn ? "trading off" : stDDHit ? "drawdown stop" : stHolNow ? "US holiday" : stNwNow ? "news window" : stPreNow ? "news soon - no new trades" : stWkBlock')
s = rep(s, 'f_stCell(stTbl, 39, "BLOCKED NOW",                stDDHit ? "drawdown" : stHolNow ? "US holiday" : stNwNow ? "news window" : stWkBlock',
        'f_stCell(stTbl, 39, "BLOCKED NOW",                stDDHit ? "drawdown" : stHolNow ? "US holiday" : stNwNow ? "news window" : stPreNow ? "news soon - no new trades" : stWkBlock')
s = rep(s, "(stDDHit or stNwNow or stWkBlock or stDayHalt or stSeqHalt or stLdHalt) ? color.red",
        "(stDDHit or stNwNow or stPreNow or stWkBlock or stDayHalt or stSeqHalt or stLdHalt) ? color.red")

# ---- 3. the loss mark, right after the closed trades are counted
s = rep(s, """    stFlPnl   += _sqSum
    stFlPeak  := math.max(stFlPeak, stFlPnl)
    if f_stCar() <= 0.005 and stSeqCapAct != "Stop permanently"
""", """    stFlPnl   += _sqSum
    stFlPeak  := math.max(stFlPeak, stFlPnl)
    // v12.1: group 42 - the losses carried reached the mark: they are forgotten, the next trade risks the base again
    if stLmOn and stSeqMode != "Off" and f_stCar() >= stLmAmt - 0.005
        stSeqLoss := 0.0
        stSeqTot  := 0.0
        stCntLm   += 1
    if f_stCar() <= 0.005 and stSeqCapAct != "Stop permanently"
""")

# ---- 1. the cap: start again from the base risk
s = rep(s, """    stRiskNow := stSeqMax
    if stSeqCapAct != "Clamp to the cap and carry on"
        stSeqHalt := true
""", """    stRiskNow := stSeqMax
    if stSeqCapAct == \"""" + RST + """\"
        // v12.1: the losses carried are forgotten and the next trade risks the base again (never above the cap)
        if stSeqCar > 0.005
            stSeqLoss  := 0.0
            stSeqTot   := 0.0
            stSeqCapOn := false
        stRiskNow := math.min(stRisk, stSeqMax)
    else if stSeqCapAct != "Clamp to the cap and carry on"
        stSeqHalt := true
""")

# ---- the table: the cap row + two new rows
s = rep(s, 'f_stCell(stTbl, 26, "Risk cap hit / HALT",        stSeqMode == "Off" ? "off" : (str.tostring(stCntSeqCap) + (stSeqHalt ? "  HALTED" : ""))',
        'f_stCell(stTbl, 26, "Risk cap hit / HALT",        stSeqMode == "Off" ? "off" : (str.tostring(stCntSeqCap) + (stSeqCapAct == "' + RST + '" ? " x back to the base" : "") + (stSeqHalt ? "  HALTED" : ""))')
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 49, ", "stTbl := table.new(f_stPos(stStatPos), 2, 51, ")
old = '    f_stCell(stTbl, 48, "RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", _r3T, '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    "    // v12.1: group 41 (no new trades before news) and group 42 (the loss mark)\n"
    '    string _preT = not stPreOn ? "off" : not stNewsOn ? "on - but the news master is OFF" : not stAuOn ? "on - but group 29 is OFF (no releases)" : '
    '(stPreNow ? "NOW - no new trades  |  " : "") + str.tostring(stPreHrs) + " h before the group 29 releases"\n'
    '    f_stCell(stTbl, 49, "NO NEW TRADES BEFORE NEWS (group 41)", _preT, not stPreOn ? color.gray : stPreNow ? color.red : color.aqua)\n'
    '    string _lmT = not stLmOn ? "off" : stSeqMode == "Off" ? "on - but loss recovery is Off" : "at " + str.tostring(stLmAmt) + ":  " + str.tostring(stCntLm) + " x back to the base"\n'
    '    f_stCell(stTbl, 50, "LOSS MARK - BACK TO THE BASE (group 42)", _lmT, stLmOn and stSeqMode != "Off" ? color.aqua : color.gray)\n'
) + s[j:]

assert all(ord(ch) < 128 for ch in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v12.1.txt", "w").write(s)
print("v12.1 written:", len(s.split("\n")), "lines")
