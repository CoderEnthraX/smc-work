# v12.1 -> v12.2 (everything OFF by default):
#   - the v12.1 profit mark is removed: v12.2 starts from v12.1 as it was before the profit mark (commit ec60510)
#   - 'Loss-recovery sizing' gets 3 choices at the end: Rule A split / Rule B split / Rule C split = Rule A / B / C, but the
#     base risk grows in steps with the total profit (group 43): the step reached / its parts (option 2 - the step amount,
#     not the actual profit), never below the base risk, never above the hard cap; the next risk = the bigger of that base
#     and what Rule A / B / C asks for
import subprocess
R = "/home/user/smc-work/"
s = subprocess.run(["git", "-C", R, "show", "ec60510:SMC_Structure_Strategy_v12.1.txt"], capture_output=True, text=True, check=True).stdout
assert "stPmOn" not in s and "stSp1" not in s and "stSplitM" not in s and "f_stStep" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


AS = "Rule A split (A, the base grows with the profit - group 43)"
BS = "Rule B split (B, the base grows with the profit - group 43)"
CS = "Rule C split (C, the base grows with the profit - group 43)"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v12.1  -  ") and l2.endswith("  -  ASCII only")
s = rep(s, l2, l2.replace("v12.1  -  ", "v12.2  -  ", 1)[:-len("  -  ASCII only")] +
        ", v12.2: Rule A / B / C split - the base risk grows in steps with the profit  -  ASCII only")

# ---- the 3 new choices at the end of 'Loss-recovery sizing' + the tooltip
old = '"Rule C+ (only when total P&L is below 0: that loss)"], group = gRsk'
s = rep(s, old, '"Rule C+ (only when total P&L is below 0: that loss)", "' + AS + '", "' + BS + '", "' + CS + '"], group = gRsk')
s = rep(s, 'The hard cap below exists for exactly that reason - do not remove it.")',
        'The hard cap below exists for exactly that reason - do not remove it.\\n\\n'
        'RULE A SPLIT / B SPLIT / C SPLIT (v12.2): exactly Rule A / B / C, but once the total profit (the Net P&L of the counted closed trades) '
        'reaches a step of group 43, the BASE risk becomes that step divided into its parts: 200 / 3 = 66.67, 500 / 5 = 100, 1,000 / 8 = 125, then every '
        '500 more one more part (1,500 / 9 = 166.67, 2,000 / 10 = 200 ...). The next risk is the bigger of that base and what Rule A / B / C asks for. '
        'Below the first step - or in a loss - the base is your base risk, as before. The step base is never above the hard cap.")')

# ---- group 43 at the END of the settings
old = 'stLmAmt = input.float(300.0, "  - losses carried, in account currency", '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    'gSp = "43. Rule A / B / C split - the base risk grows with the profit (v12.2)"\n'
    'stSp1   = input.float(200.0, "Step 1 - total profit of at least", minval = 0.0, group = gSp, tooltip = '
    '"Used only by Rule A split / B split / C split (group 21). 0 = this step is off.\\n\\n'
    'The total profit = the Net P&L of the closed trades that loss recovery counts (\'loss recovery counts from\', group 21). Once it reaches a step, '
    'the base risk is the STEP amount divided into the parts below - not the actual profit, so a loss never makes the next base bigger.\\n\\n'
    'Defaults: 200 / 3 = 66.67, 500 / 5 = 100, 1,000 / 8 = 125, then every 500 more: one more part - 1,500 / 9 = 166.67, 2,000 / 10 = 200, '
    '2,500 / 11 = 227.27, 3,000 / 12 = 250, 3,500 / 13 = 269.23, 4,000 / 14 = 285.71, 5,000 / 16 = 312.50. The base keeps growing, but more and more '
    'slowly (it never reaches 500), so each trade risks a smaller share of the profit as the profit grows.\\n\\n'
    'Example (Rule C split, split 3): profit 1,040 -> base 125. That trade loses 125 -> profit 915 -> step 500 -> base 100; Rule C asks 125 / 3 = 41.67 '
    '-> the next trade risks 100.")\n'
    'stSpN1  = input.float(3.0, "  - split it into this many parts", minval = 1.0, step = 1.0, group = gSp)\n'
    'stSp2   = input.float(500.0, "Step 2 - total profit of at least", minval = 0.0, group = gSp)\n'
    'stSpN2  = input.float(5.0, "  - split it into this many parts", minval = 1.0, step = 1.0, group = gSp)\n'
    'stSp3   = input.float(1000.0, "Step 3 - total profit of at least", minval = 0.0, group = gSp)\n'
    'stSpN3  = input.float(8.0, "  - split it into this many parts", minval = 1.0, step = 1.0, group = gSp)\n'
    'stSpInc = input.float(500.0, "Then a new step every this much more profit  (0 = no more steps)", minval = 0.0, group = gSp, tooltip = '
    '"After step 3: every this much more profit is a new step (1,500, 2,000, 2,500 ... with the defaults), each split into the parts of the step '
    'before plus the number below.")\n'
    'stSpAdd = input.float(1.0, "  - each new step is split into this many more parts", minval = 0.0, step = 1.0, group = gSp)\n'
) + s[j:]

# ---- the split modes + the step base
s = rep(s, "f_stCar() =>\n    stSeqPlus ? math.max(0.0, -stSeqTot) : stSeqLoss\n",
        "f_stCar() =>\n    stSeqPlus ? math.max(0.0, -stSeqTot) : stSeqLoss\n"
        "// v12.2: Rule A / B / C split - the base risk from the profit steps of group 43 (the step reached / its parts; 0 = no step)\n"
        'bool stSplitM = stSeqMode == "' + AS + '" or stSeqMode == "' + BS + '" or stSeqMode == "' + CS + '"\n'
        "f_stStep(float _pf) =>\n"
        "    float _a = 0.0\n"
        "    float _n = 1.0\n"
        "    if stSp1 > 0 and _pf >= stSp1 - 0.005 and stSp1 > _a\n"
        "        _a := stSp1\n"
        "        _n := stSpN1\n"
        "    if stSp2 > 0 and _pf >= stSp2 - 0.005 and stSp2 > _a\n"
        "        _a := stSp2\n"
        "        _n := stSpN2\n"
        "    if stSp3 > 0 and _pf >= stSp3 - 0.005 and stSp3 > _a\n"
        "        _a := stSp3\n"
        "        _n := stSpN3\n"
        "        if stSpInc > 0\n"
        "            int _k = int(math.floor((_pf - stSp3 + 0.005) / stSpInc))\n"
        "            _a := stSp3 + _k * stSpInc\n"
        "            _n := stSpN3 + _k * stSpAdd\n"
        "    _a > 0 ? _a / _n : 0.0\n")

# ---- the risk: the split rules use the step base instead of the base risk
s = rep(s, """float stSeqCar = f_stCar()
if stSeqMode == "Rule A - recover losses + base profit" or stSeqMode == "Rule A+ (only when total P&L is below 0: that loss + amount)"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, (stSeqCar + stSeqAdd) / stSeqSplit) : stRisk
else if stSeqMode == "Rule B - double the losses" or stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, 2.0 * stSeqCar / stSeqSplit) : stRisk
else if stSeqMode == "Rule C - carry the losses" or stSeqMode == "Rule C+ (only when total P&L is below 0: that loss)"
    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar / stSeqSplit) : stRisk
""", """float stSeqCar = f_stCar()
// v12.2: Rule A / B / C split - the base grows in steps with the total profit (never below the base risk, never above the cap)
float stBaseNow = stSplitM ? math.max(stRisk, math.min(f_stStep(stFlPnl), stSeqMax)) : stRisk
if stSeqMode == "Rule A - recover losses + base profit" or stSeqMode == "Rule A+ (only when total P&L is below 0: that loss + amount)" or stSeqMode == \"""" + AS + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stBaseNow, (stSeqCar + stSeqAdd) / stSeqSplit) : stBaseNow
else if stSeqMode == "Rule B - double the losses" or stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)" or stSeqMode == \"""" + BS + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stBaseNow, 2.0 * stSeqCar / stSeqSplit) : stBaseNow
else if stSeqMode == "Rule C - carry the losses" or stSeqMode == "Rule C+ (only when total P&L is below 0: that loss)" or stSeqMode == \"""" + CS + """\"
    stRiskNow := stSeqCar > 0.005 ? math.max(stBaseNow, stSeqCar / stSeqSplit) : stBaseNow
""")
s = rep(s, "        stRiskNow := math.min(stRisk, stSeqMax)\n", "        stRiskNow := math.min(stBaseNow, stSeqMax)\n")

# ---- the table: the recovery row names the split rules + a new row for the steps
s = rep(s, '''stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)" ? "B+ - 2 x total below 0" : "C+ - total below 0"''',
        '''stSeqMode == "Rule B+ (only when total P&L is below 0: 2 x that loss)" ? "B+ - 2 x total below 0" : stSeqMode == "Rule C+ (only when total P&L is below 0: that loss)" ? "C+ - total below 0" : '''
        '''stSeqMode == "''' + AS + '''" ? ("A split - loss since the high + " + str.tostring(stSeqAdd) + ", base from the profit steps") : '''
        '''stSeqMode == "''' + BS + '''" ? "B split - 2 x loss since the high, base from the profit steps" : "C split - loss since the high, base from the profit steps"''')
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 51, ", "stTbl := table.new(f_stPos(stStatPos), 2, 52, ")
old = '    f_stCell(stTbl, 50, "LOSS MARK - BACK TO THE BASE (group 42)", _lmT, '
i = s.index(old)
j = s.index("\n", i) + 1
s = s[:j] + (
    "    // v12.2: group 43 - the profit steps of Rule A / B / C split\n"
    '    string _spT = not stSplitM ? "off" : "profit " + str.tostring(math.round(stFlPnl * 100) / 100) + "  ->  base " + str.tostring(math.round(stBaseNow * 100) / 100)\n'
    '    f_stCell(stTbl, 51, "PROFIT STEPS - A / B / C split (group 43)", _spT, stSplitM ? color.aqua : color.gray)\n'
) + s[j:]

assert all(ord(ch) < 128 for ch in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v12.2.txt", "w").write(s)
print("v12.2 written:", len(s.split("\n")), "lines")
