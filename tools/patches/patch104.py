# v10.3 -> v10.4 : account floor with profit lock (risk = % of the cushion above the floor)
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v10.3.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


FO = "Off"
FS = "On - size every trade from the cushion (risk grows with profit)"
FC = "On - only cap the risk (base / loss recovery, never above the cushion %)"

# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v10.3  -  ")
s = rep(s, l2, l2.replace("v10.3  -  ", "v10.4  -  ", 1).replace(
    "  -  ASCII only",
    ", v10.4: account floor with profit lock (risk = % of the cushion above the floor)  -  ASCII only"))

# ---- the settings, after the last one (shown in their own group 35, at the end of the panel)
TM = ("OFF (default): no floor - exactly as v10.3.\\n\\n"
      "THE FLOOR: the account may never fall more than 'the most the account may lose' below where it starts (the same start as 'loss recovery counts from' in group 21), "
      "and every new profit high raises the floor by 'lock' % of that high - that part of the profit is kept.\\n\\n"
      "CUSHION = your P&L since the start minus the floor. Each trade risks 'risk per trade' % of the cushion. A loss takes only that share, "
      "so the cushion shrinks but never reaches zero: the account cannot fall through the floor - except for slippage beyond the stop, price gaps and the minimum lot. "
      "The size is rounded to your lot step as usual (never more than 'never let rounding raise the risk by more than' % above), which still keeps every trade far below the cushion. "
      "When the cushion is too small for one lot step, no trade is placed.\\n\\n"
      "SIZE EVERY TRADE FROM THE CUSHION: risk = % of the cushion. It grows when you are in profit and shrinks after losses. "
      "Loss recovery (A / B / C, A+ / B+ / C+) and its hard cap are not used - set loss recovery to Off.\\n\\n"
      "ONLY CAP THE RISK: the base risk and loss recovery work as before, but a trade never risks more than % of the cushion.\\n\\n"
      "Example (the defaults): the most to lose 2,000, lock 50%, risk 2.5%. Floor -2,000, cushion 2,000, first risk 50. After 10 losses in a row about 447 is lost, after 20 about 795 - never 2,000. "
      "At a profit high of +4,000 the floor is 0 (break-even locked); at +6,000 it is +1,000 (1,000 of profit kept).\\n\\n"
      "Going live: set 'loss recovery counts from' (group 21) to 'When the strategy goes live (automatic)', so the floor starts from your live account and not from the backtest.")
TA = ("In account currency. The floor starts this far below the P&L at the start. "
      "With 'loss recovery counts from' = the whole chart history the start is the first trade of the backtest; "
      "with 'When the strategy goes live' it is your first live candle; with a date it is that date.")
TL = ("0 = the floor never moves up. 50 (default) = the floor rises by half of every new profit high: with 2,000 to lose it is at -1,000 at +2,000, "
      "at 0 at +4,000 (break-even locked) and at +1,000 at +6,000. 100 = the floor follows every high, always 'the most to lose' below it.")
TP = ("2.5 (default) = each trade risks 2.5% of the cushion - 50 at the start with 2,000 to lose. "
      "Set it to your BASE risk / the most to lose x 100, so the first trade risks your base. "
      "Keep 'the most to lose' at least 40 x your base risk: on gold the smallest step (0.01 lot = 1 oz) is already 20-25 of risk in 2026, "
      "so with a small cushion many setups round to 0 and are skipped. In the tests 500 / 10% ended a year in profit about half as often as 2,000 / 2.5%.")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stSeqSplit = input.float(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v10.4 - appended after the last setting, so every setting saved on your chart keeps its place (shown in group 35)",
    'gFl = "35. Account floor + profit lock"',
    'stFlMode = input.string("' + FO + '", "Account floor - never lose more than the amount below, and keep part of every new high", options = ["' + FO + '", "' + FS + '", "' + FC + '"], group = gFl, tooltip = "' + TM + '")',
    'stFlAmt  = input.float(2000.0, "  - the most the account may lose (below the start)", minval = 0.01, group = gFl, tooltip = "' + TA + '")',
    'stFlLock = input.float(50.0, "  - lock this % of every new profit high", minval = 0.0, maxval = 100.0, step = 5.0, group = gFl, tooltip = "' + TL + '")',
    'stFlPct  = input.float(2.5, "  - risk per trade, % of the cushion above the floor", minval = 0.5, maxval = 50.0, step = 0.5, group = gFl, tooltip = "' + TP + '")',
]
s = "\n".join(lines)

# ---- state: the P&L the floor follows and its highest point
s = rep(s, "// v10.1: the total Net P&L of every closed trade, for Rule A+ / B+ / C+\nvar float stSeqTot = 0.0\n",
        """// v10.1: the total Net P&L of every closed trade, for Rule A+ / B+ / C+
var float stSeqTot = 0.0
// v10.4: account floor - the P&L of the counted closed trades and its highest point (never reset)
var float stFlPnl  = 0.0
var float stFlPeak = 0.0
""")
s = rep(s, "    stSeqTot  += _sqSum\n", """    stSeqTot  += _sqSum
    stFlPnl   += _sqSum
    stFlPeak  := math.max(stFlPeak, stFlPnl)
""")

# ---- the floor after the loss-recovery rules and the hard cap
s = rep(s, "if stSeqMode != \"Off\" and stRiskNow > stSeqMax\n",
        "if stSeqMode != \"Off\" and stFlMode != \"" + FS + "\" and stRiskNow > stSeqMax\n")
i = s.index("if stSeqMode != \"Off\" and stFlMode != ")
j = s.index("    stSeqCapOn := false\n", i) + len("    stSeqCapOn := false\n")
s = s[:j] + """// v10.4: account floor - the floor is the most you may lose below the start, raised by a share of every new high;
// each trade risks a % of the cushion above it, so a loss can never take the whole cushion
float stFlFloor = -stFlAmt + stFlLock / 100.0 * stFlPeak
float stFlCush  = math.max(0.0, stFlPnl - stFlFloor)
float stFlRisk  = stFlPct / 100.0 * stFlCush
if stFlMode == \"""" + FS + """\"
    stRiskNow := stFlRisk
else if stFlMode == \"""" + FC + """\"
    stRiskNow := math.min(stRiskNow, stFlRisk)
""" + s[j:]

# ---- table: one more row
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 44,", "stTbl := table.new(f_stPos(stStatPos), 2, 45,")
s = rep(s, """    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : (_sqM + _sqS + "  |  " + _sqF), stSeqMode == "Off" ? color.gray : color.orange)""",
        """    f_stCell(stTbl, 23, "LOSS RECOVERY (A / B / C, A+ / B+ / C+)", stSeqMode == "Off" ? "off" : stFlMode == \"""" + FS + """\" ? "not used - the account floor sizes every trade" : (_sqM + _sqS + "  |  " + _sqF), stSeqMode == "Off" or stFlMode == \"""" + FS + """\" ? color.gray : color.orange)""")
last = s.index('    f_stCell(stTbl, 43, "Cancelled - new BOS before the fill"')
eol = s.index("\n", last) + 1
s = s[:eol] + """    // v10.4: the account floor - where it is, the cushion above it and the risk it allows
    string _flT = stFlMode == \"""" + FO + """\" ? "off" : (stFlCush <= 0.005 ? "AT THE FLOOR - no risk left  |  " : "") + "P&L " + str.tostring(math.round(stFlPnl * 100) / 100) + "  |  floor " + str.tostring(math.round(stFlFloor * 100) / 100) + "  |  cushion " + str.tostring(math.round(stFlCush * 100) / 100) + "  |  risk " + str.tostring(math.round(stFlRisk * 100) / 100) + (stFlMode == \"""" + FC + """\" ? " (cap)" : "")
    f_stCell(stTbl, 44, "ACCOUNT FLOOR (group 35)", _flT, stFlMode == \"""" + FO + """\" ? color.gray : stFlCush < 0.25 * stFlAmt ? color.red : color.aqua)
""" + s[eol:]

assert all(ord(c) < 128 for c in s) and "\t" not in s and "strategy.close_all(" not in s
open(R + "SMC_Structure_Strategy_v10.4.txt", "w").write(s)
print("ok", len(s.split("\n")))
