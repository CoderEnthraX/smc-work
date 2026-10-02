# v9.1 -> v10.0 : Rule C, every rule never below the base risk, loss recovery counts from the moment the strategy goes live
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v9.1.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v9.1  -  ")
s = rep(s, l2, l2.replace("v9.1  -  ", "v10.0  -  ", 1).replace(
    "  -  ASCII only",
    ", v10.0: loss recovery Rule A / B / C never below the base risk, Rule C = carry the losses, loss recovery counts from the moment the strategy goes live (or a date, or the whole history)  -  ASCII only"))

# ---- the recovery setting: Rule C added (existing choices unchanged, so saved settings still match), new tooltip
old = s[s.index('stSeqMode = input.string("Off", "Loss-recovery sizing"'):]
old = old[:old.index("\n")]
new = ('stSeqMode = input.string("Off", "Loss-recovery sizing", options = ["Off", "Rule A - recover losses + base profit", "Rule B - double the losses", "Rule C - carry the losses"], group = gRsk, tooltip = "'
       "OFF = every trade risks the base amount. Nothing recovers anything.\\n\\n"
       "LOSSES CARRIED (all three rules): every closed trade adds its real loss or takes off its real profit - its Net P&L after commission, as the List of Trades shows it. "
       "Trades that close on the same candle are added together first. Never below zero. They carry over into the next days. "
       "Which trades count: see 'loss recovery counts from' (default: from the moment the strategy goes live).\\n\\n"
       "RULE A: next risk = losses carried + the Rule A amount.\\n"
       "RULE B: next risk = 2 x losses carried.\\n"
       "RULE C: next risk = losses carried.\\n"
       "ALL THREE: never less than the BASE risk, and back to the BASE risk as soon as the losses carried are paid off (profit beyond that is not saved).\\n\\n"
       "Example, base 50 and Rule A amount 50, results -50, -30, -30, +20:\\n"
       "  Rule A risks 50, 100, 130, 160, 140\\n"
       "  Rule B risks 50, 100, 160, 220, 180\\n"
       "  Rule C risks 50, 50, 80, 110, 90\\n\\n"
       "The size is still rounded to your lot step and cut by Max leverage, so the real risk can differ a little. "
       "READ THE WARNING IN THE NOTES FILE BEFORE USING ANY OF THEM. They grow the position after losses, which is the fastest known way to empty an account. "
       "The hard cap below exists for exactly that reason - do not remove it.\")")
s = rep(s, old, new)

# ---- the new settings, after the last one (shown in group 21)
TF = ("Which closed trades count for Rule A, B and C (the losses carried and the hard cap).\\n\\n"
      "WHEN THE STRATEGY GOES LIVE (default): only trades that close from the first live candle on - the moment you create the alert, or open the chart. "
      "The past candles on the chart are ignored, so the strategy always starts live with 0 carried and not stopped. Nothing to type. "
      "The backtest therefore shows every trade at the base risk. Changing any setting, or creating the alert again, starts from 0 again.\\n\\n"
      "A DATE I CHOOSE: only trades that close on or after the date below.\\n\\n"
      "THE WHOLE CHART HISTORY: every trade on the chart (v9.1). Use it to see a rule in the backtest. "
      "Careful live: if the cap was reached anywhere in the history, the strategy is already stopped when you create the alert.")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stBosCnl = input.bool(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v10.0 - appended after the last setting, so every setting saved on your chart keeps its place (shown in group 21)",
    'stSeqFrom = input.string("When the strategy goes live (automatic)", "  - loss recovery counts from", options = ["When the strategy goes live (automatic)", "A date I choose", "The whole chart history"], group = gRsk, tooltip = "' + TF + '")',
    'stSeqFromT = input.time(timestamp("01 Jan 2026 00:00 +0000"), "  - the date (only for \'A date I choose\')", group = gRsk)',
]
s = "\n".join(lines)

# ---- the moment the strategy went live, and which trades count
s = rep(s, "var int    stCntBosCnl = 0\n", """var int    stCntBosCnl = 0
// v10.0: the first live candle (na while the chart is still going through its history)
var int    stLiveT = na
if na(stLiveT) and barstate.isrealtime
    stLiveT := time
// v10.0: does a trade that closed at xt count for the loss recovery (Rule A / B / C)?
f_stSeqCounts(int xt) =>
    stSeqFrom == "The whole chart history" ? true : stSeqFrom == "A date I choose" ? xt >= stSeqFromT : not na(stLiveT) and xt >= stLiveT
""")

# ---- the losses carried: only the trades that count, the ones closing on the same candle added together
s = rep(s, """        float _debt = stSeqLoss - _pf
        stSeqLoss := _debt < 0.005 ? 0.0 : _debt
    if stSeqLoss <= 0 and stSeqCapAct != "Stop permanently\"""", """        if f_stSeqCounts(strategy.closedtrades.exit_time(_ix))
            _sqSum += _pf
    // v10.0: the trades that closed on this candle are added together, then the losses carried are updated once
    float _debt = stSeqLoss - _sqSum
    stSeqLoss := _debt < 0.005 ? 0.0 : _debt
    if stSeqLoss <= 0 and stSeqCapAct != "Stop permanently\"""")
s = rep(s, """    int _nCl = strategy.closedtrades - stClosed
""", """    int _nCl = strategy.closedtrades - stClosed
    float _sqSum = 0.0
""")

# ---- the three rules, never below the base risk
s = rep(s, """if stSeqMode == "Rule A - recover losses + base profit"
    // v9.1: losses carried + the Rule A amount - nothing divided by R
    stRiskNow := stSeqLoss > 0 ? stSeqLoss + stSeqAdd : stRisk
else if stSeqMode == "Rule B - double the losses"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, 2.0 * stSeqLoss) : stRisk
""", """// v10.0: A = losses carried + the Rule A amount, B = 2 x losses carried, C = losses carried - never less than the base risk
if stSeqMode == "Rule A - recover losses + base profit"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, stSeqLoss + stSeqAdd) : stRisk
else if stSeqMode == "Rule B - double the losses"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, 2.0 * stSeqLoss) : stRisk
else if stSeqMode == "Rule C - carry the losses"
    stRiskNow := stSeqLoss > 0 ? math.max(stRisk, stSeqLoss) : stRisk
""")

# ---- table
old23 = s[s.index('    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B)"'):]
old23 = old23[:old23.index("\n")]
new23 = ('    string _sqM = stSeqMode == "Rule A - recover losses + base profit" ? ("A - losses + " + str.tostring(stSeqAdd)) : stSeqMode == "Rule B - double the losses" ? "B - 2 x losses" : "C - losses"\n'
         '    string _sqF = stSeqFrom == "The whole chart history" ? "whole history" : stSeqFrom == "A date I choose" ? ("from " + str.format_time(stSeqFromT, "dd MMM yyyy", stTz)) : na(stLiveT) ? "from live (not live yet)" : ("from live " + str.format_time(stLiveT, "dd MMM HH:mm", stTz))\n'
         '    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C)",  stSeqMode == "Off" ? "off" : (_sqM + "  |  " + _sqF), stSeqMode == "Off" ? color.gray : color.orange)')
s = rep(s, old23, new23)

open(R + "SMC_Structure_Strategy_v10.0.txt", "w").write(s)
print("ok", len(s.split("\n")))
