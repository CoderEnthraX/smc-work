# v10.1 -> v10.2 : "loss recovery counts from" back, with "The whole chart history" as the default
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v10.1.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


WH, LV, DT = "The whole chart history", "When the strategy goes live (automatic)", "A date I choose"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v10.1  -  ")
s = rep(s, l2, l2.replace("v10.1  -  ", "v10.2  -  ", 1).replace(
    "  -  ASCII only",
    ", v10.2: loss recovery counts from the whole chart history (default), the moment the strategy goes live, or a date  -  ASCII only"))

# ---- the setting, after the last one (shown in group 21) - the same place as in v10.0
TF = ("Which closed trades count for loss recovery (Rule A / B / C and A+ / B+ / C+) - the loss the rule works with and the hard cap.\\n\\n"
      "THE WHOLE CHART HISTORY (default): every closed trade on the chart. Use it to see a rule in the backtest.\\n\\n"
      "WHEN THE STRATEGY GOES LIVE (automatic): only trades that OPEN from the first live candle on - the moment you create the alert, or open the chart. "
      "A trade still open from the replayed past never reached your broker, so it does not count either. "
      "The past candles are ignored, so the strategy starts live with no loss carried, at the base risk, and not stopped by a cap the backtest reached. "
      "For A+ / B+ / C+ the total starts from zero at that moment, so the cushion is only the profit made live. Nothing to type. "
      "The backtest shows every trade at the base risk. Changing any setting, or creating the alert again, starts from zero again.\\n\\n"
      "A DATE I CHOOSE: only trades that open on or after the date below - for example the day you went live, a new month, or to test a rule from a date.")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stBosCnl = input.bool(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v10.2 - appended after the last setting, so every setting saved on your chart keeps its place (shown in group 21)",
    'stSeqFrom = input.string("' + WH + '", "  - loss recovery counts from", options = ["' + WH + '", "' + LV + '", "' + DT + '"], group = gRsk, tooltip = "' + TF + '")',
    'stSeqFromT = input.time(timestamp("01 Jan 2026 00:00 +0000"), "  - the date (only for \'' + DT + '\')", group = gRsk)',
]
s = "\n".join(lines)

# ---- the first live candle, and which trades count
s = rep(s, "var int    stCntBosCnl = 0\n", """var int    stCntBosCnl = 0
// v10.2: the first live candle (na while the chart is still going through its history)
var int    stLiveT = na
if na(stLiveT) and barstate.isrealtime
    stLiveT := time
// v10.2: does a trade that OPENED at et count for loss recovery?
f_stSeqCounts(int xt) =>
    stSeqFrom == \"""" + WH + """\" ? true : stSeqFrom == \"""" + DT + """\" ? xt >= stSeqFromT : not na(stLiveT) and xt >= stLiveT
""")
s = rep(s, "        _sqSum += _pf\n", """        if f_stSeqCounts(strategy.closedtrades.entry_time(_ix))
            _sqSum += _pf
""")

# ---- the recovery tooltip mentions the new setting
s = rep(s, "The size is still rounded to your lot step and cut by Max leverage. READ THE WARNING",
        "Which trades count: 'loss recovery counts from' (default: the whole chart history). The size is still rounded to your lot step and cut by Max leverage. READ THE WARNING")

# ---- table row 23 shows where it counts from
s = rep(s, """    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : _sqM, stSeqMode == "Off" ? color.gray : color.orange)""",
        """    string _sqF = stSeqFrom == \"""" + WH + """\" ? "whole history" : stSeqFrom == \"""" + DT + """\" ? ("from " + str.format_time(stSeqFromT, "dd MMM yyyy", stTz)) : na(stLiveT) ? "from live (not live yet)" : ("from live " + str.format_time(stLiveT, "dd MMM HH:mm", stTz))
    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : (_sqM + "  |  " + _sqF), stSeqMode == "Off" ? color.gray : color.orange)""")

open(R + "SMC_Structure_Strategy_v10.2.txt", "w").write(s)
print("ok", len(s.split("\n")))
