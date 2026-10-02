# v10.0 -> v10.1 : "loss recovery counts from" removed (every trade on the chart counts again), new Rule A+ / B+ / C+
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v10.0.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


A, B, C = "Rule A - recover losses + base profit", "Rule B - double the losses", "Rule C - carry the losses"
AP = "Rule A+ (only when total P&L is below 0: that loss + amount)"
BP = "Rule B+ (only when total P&L is below 0: 2 x that loss)"
CP = "Rule C+ (only when total P&L is below 0: that loss)"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v10.0  -  ")
s = rep(s, l2, l2.replace("v10.0  -  ", "v10.1  -  ", 1).replace(
    ", loss recovery counts from the moment the strategy goes live (or a date, or the whole history)  -  ASCII only",
    ", v10.1: every trade on the chart counts for loss recovery again, Rule A+ / B+ / C+ recover only the loss of the total P&L below zero  -  ASCII only"))

# ---- the recovery setting: three more choices (the existing ones unchanged, so saved settings still match), new tooltip
old = s[s.index('stSeqMode = input.string("Off", "Loss-recovery sizing"'):]
old = old[:old.index("\n")]
new = ('stSeqMode = input.string("Off", "Loss-recovery sizing", options = ["Off", "' + A + '", "' + B + '", "' + C + '", "' + AP + '", "' + BP + '", "' + CP + '"], group = gRsk, tooltip = "'
       "OFF = every trade risks the base amount. Nothing recovers anything.\\n\\n"
       "Every rule uses the Net P&L of each closed trade after commission, as the List of Trades shows it; trades that close on the same candle are added together first.\\n\\n"
       "RULE A / B / C - THE LOSS SINCE THE HIGH POINT: a loss adds, a profit takes off, never below zero. Profit beyond what is owed is NOT saved, "
       "so the loss is counted from the highest point the account has reached.\\n\\n"
       "RULE A+ / B+ / C+ - THE TOTAL BELOW ZERO: the loss is how far the total Net P&L of all closed trades (the Cumulative P&L of the List of Trades) is below zero. "
       "While the total is above zero every trade is the BASE risk - profit already made is a cushion.\\n\\n"
       "A and A+: next risk = the loss + the Rule A amount.\\nB and B+: next risk = 2 x the loss.\\nC and C+: next risk = the loss.\\n"
       "ALL: never less than the BASE risk, and the BASE risk again when the loss is 0.\\n\\n"
       "Example: the account reached +665.66, then fell to -494.55. Rule C risks 1,160.20 (the drop from the high), Rule C+ risks 494.55 (below zero). "
       "Later at +243.84: Rule C still risks 421.81, Rule C+ is back to the base 50.\\n\\n"
       "'Stop for the rest of the day' (below) clears the loss the next morning - for A+ / B+ / C+ the total starts again from zero. "
       "The size is still rounded to your lot step and cut by Max leverage. "
       "READ THE WARNING IN THE NOTES FILE BEFORE USING ANY OF THEM. They grow the position after losses, which is the fastest known way to empty an account. "
       "The hard cap below exists for exactly that reason - do not remove it.\")")
s = rep(s, old, new)

# ---- remove "loss recovery counts from" (the last two settings)
i = s.index("\n// v10.0 - appended after the last setting, so every setting saved on your chart keeps its place (shown in group 21)\n")
j = s.index("\n", s.index("stSeqFromT = input.time(", i)) + 1
assert s[j] == "\n"
s = s[:i + 1] + s[j + 1:]
i = s.index("// v10.0: the first live candle (na while the chart is still going through its history)\n")
j = s.index("// v9.0 state: risk factor of the armed setup", i)
s = s[:i] + s[j:]
assert "stSeqFrom" not in s.replace("stSeqFromT", "X") or True

# ---- the total of every closed trade (A+ / B+ / C+) and the loss the chosen rule works with
s = rep(s, "var float stSeqLoss = 0.0\n", """var float stSeqLoss = 0.0
// v10.1: the total Net P&L of every closed trade, for Rule A+ / B+ / C+
var float stSeqTot = 0.0
bool stSeqPlus = stSeqMode == \"""" + AP + """\" or stSeqMode == \"""" + BP + """\" or stSeqMode == \"""" + CP + """\"
// the loss the chosen rule works with: A / B / C the loss since the high point, A+ / B+ / C+ the total below zero
f_stCar() =>
    stSeqPlus ? math.max(0.0, -stSeqTot) : stSeqLoss
""")

# ---- every closed trade counts again
s = rep(s, """        if f_stSeqCounts(strategy.closedtrades.exit_time(_ix))
            _sqSum += _pf
""", """        _sqSum += _pf
""")
s = rep(s, """    float _debt = stSeqLoss - _sqSum
    stSeqLoss := _debt < 0.005 ? 0.0 : _debt
    if stSeqLoss <= 0 and stSeqCapAct != "Stop permanently\"""", """    float _debt = stSeqLoss - _sqSum
    stSeqLoss := _debt < 0.005 ? 0.0 : _debt
    stSeqTot  += _sqSum
    if f_stCar() <= 0.005 and stSeqCapAct != "Stop permanently\"""")

# ---- the day reset of "Stop for the rest of the day" also starts the total again
s = rep(s, """if stNewDay and stSeqHalt and stSeqCapAct == "Stop for the rest of the day"
    stSeqHalt  := false
    stSeqLoss  := 0.0
""", """if stNewDay and stSeqHalt and stSeqCapAct == "Stop for the rest of the day"
    stSeqHalt  := false
    stSeqLoss  := 0.0
    stSeqTot   := 0.0
""")

# ---- the six rules
s = rep(s, """if stSeqMode == "Rule A - recover losses + base profit"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, stSeqLoss + stSeqAdd) : stRisk
else if stSeqMode == "Rule B - double the losses"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, 2.0 * stSeqLoss) : stRisk
else if stSeqMode == "Rule C - carry the losses"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, stSeqLoss) : stRisk
""", """// v10.1: A+ / B+ / C+ work the same way with the loss of the total below zero
float stSeqCar = f_stCar()
if stSeqMode == \"""" + A + """\" or stSeqMode == \"""" + AP + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar + stSeqAdd) : stRisk
else if stSeqMode == \"""" + B + """\" or stSeqMode == \"""" + BP + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, 2.0 * stSeqCar) : stRisk
else if stSeqMode == \"""" + C + """\" or stSeqMode == \"""" + CP + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar) : stRisk
""")

# ---- table
old = s[s.index('    string _sqM = stSeqMode =='):]
old = old[:old.index('    f_stCell(stTbl, 24, "Losses carried"')]
new = ('    string _sqM = stSeqMode == "' + A + '" ? ("A - loss since the high + " + str.tostring(stSeqAdd)) : stSeqMode == "' + B + '" ? "B - 2 x loss since the high" : '
       'stSeqMode == "' + C + '" ? "C - loss since the high" : stSeqMode == "' + AP + '" ? ("A+ - total below 0 + " + str.tostring(stSeqAdd)) : '
       'stSeqMode == "' + BP + '" ? "B+ - 2 x total below 0" : "C+ - total below 0"\n'
       '    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : _sqM, stSeqMode == "Off" ? color.gray : color.orange)\n')
s = s.replace(old, new)
s = rep(s, """    f_stCell(stTbl, 24, "Losses carried",             stSeqMode == "Off" ? "off" : str.tostring(math.round(stSeqLoss * 100) / 100), stSeqLoss > 0 ? color.red : color""",
        """    f_stCell(stTbl, 24, "Losses carried",             stSeqMode == "Off" ? "off" : str.tostring(math.round(f_stCar() * 100) / 100), f_stCar() > 0 ? color.red : color""")

assert "stLiveT" not in s and "f_stSeqCounts" not in s and "stSeqFrom" not in s
open(R + "SMC_Structure_Strategy_v10.1.txt", "w").write(s)
print("ok", len(s.split("\n")))
