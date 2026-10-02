# v10.2 -> v10.3 : "split the loss over this many trades" - whatever the recovery rule asks for is divided by it
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v10.2.txt").read()


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
assert l2.startswith("// SMC Structure Strategy  -  v10.2  -  ")
s = rep(s, l2, l2.replace("v10.2  -  ", "v10.3  -  ", 1).replace(
    "  -  ASCII only",
    ", v10.3: split the loss over this many trades (the rule's amount divided, never below the base risk)  -  ASCII only"))

# ---- the setting, after the last one (shown in group 21)
TS = ("1 (default) = as before: the next trade risks everything the loss-recovery rule asks for.\\n\\n"
      "ABOVE 1: what the rule asks for is divided by this number - never less than your BASE risk. It works for all six rules:\\n"
      "A and A+: (loss + Rule A amount) / this number\\nB and B+: 2 x loss / this number\\nC and C+: loss / this number\\n\\n"
      "SET IT TO YOUR RISK:REWARD. With a 1:3 target and 3 here, one full take-profit win pays back: C / C+ the whole loss, "
      "A / A+ the loss + the Rule A amount, B / B+ 2 x the loss. A trade that closes early (time flat, news, weekend, opposite signal) pays back only part, "
      "and the rest carries on to the next trade.\\n\\n"
      "Example - C+, base risk 50, 1:3 target, 3 here: four losses in a row (risks 50, 50, 50, 50) = -200. The fifth trade risks 200 / 3 = 66.67. "
      "A full TP win pays 200, the total is back to 0, and the next trade is the base 50 again. With 1 here the same trades risk 50, 50, 100, 200 and then 400.\\n\\n"
      "A losing streak still makes the risk grow - by a third per loss with 3, instead of doubling with 1. "
      "The hard cap is checked after the split, so keep the cap small (a few % of the account).")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stSeqFromT = input.time(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v10.3 - appended after the last setting, so every setting saved on your chart keeps its place (shown in group 21)",
    'stSeqSplit = input.float(1.0, "  - split the loss over this many trades", minval = 1.0, maxval = 20.0, step = 0.5, group = gRsk, tooltip = "' + TS + '")',
]
s = "\n".join(lines)

# ---- the six rules: the amount divided by the split
s = rep(s, """// v10.1: A+ / B+ / C+ work the same way with the loss of the total below zero
float stSeqCar = f_stCar()
""", """// v10.1: A+ / B+ / C+ work the same way with the loss of the total below zero
// v10.3: what the rule asks for is divided by 'split the loss over this many trades' (1 = as before), never below the base
float stSeqCar = f_stCar()
""")
s = rep(s, "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar + stSeqAdd) : stRisk\n",
        "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, (stSeqCar + stSeqAdd) / stSeqSplit) : stRisk\n")
s = rep(s, "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, 2.0 * stSeqCar) : stRisk\n",
        "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, 2.0 * stSeqCar / stSeqSplit) : stRisk\n")
s = rep(s, "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar) : stRisk\n",
        "    stRiskNow := stSeqCar > 0.005 ? math.max(stRisk, stSeqCar / stSeqSplit) : stRisk\n")

# ---- the recovery tooltip and the cap tooltip mention the split
s = rep(s, "Which trades count: 'loss recovery counts from' (default: the whole chart history).",
        "'Split the loss over this many trades' (the last setting of this group) divides what the rule asks for - with 3 and a 1:3 target, one full TP win pays back the whole loss. "
        "Which trades count: 'loss recovery counts from' (default: the whole chart history).")
s = rep(s, "The cap is reached when the NEXT risk would be bigger than the hard cap - for example 470 carried + 50 = 520 with a cap of 500.",
        "The cap is reached when the NEXT risk would be bigger than the hard cap - for example 470 carried + 50 = 520 with a cap of 500. "
        "With 'split the loss over this many trades' above 1, the risk after the split is what is checked.")

# ---- table row 23 shows the split
s = rep(s, """    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : (_sqM + "  |  " + _sqF), stSeqMode == "Off" ? color.gray : color.orange)""",
        """    string _sqS = stSeqSplit > 1.0 ? ("  |  split over " + str.tostring(stSeqSplit) + " trades") : ""
    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : (_sqM + _sqS + "  |  " + _sqF), stSeqMode == "Off" ? color.gray : color.orange)""")

assert all(ord(c) < 128 for c in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v10.3.txt", "w").write(s)
print("ok", len(s.split("\n")))
