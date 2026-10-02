# v9.0 -> v9.1 : a waiting order only fills on its own signal's leg (cancel on a new BOS), Rule A = losses carried +
# a Rule A amount (no division by R), "Stop permanently" as the default when the hard cap is reached
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_Strategy_v9.0.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:150])
    return s.replace(old, new)


# ---- line 2
l2 = s.split("\n")[1]
assert l2.startswith("// SMC Structure Strategy  -  v9.0  -  ")
s = rep(s, l2, l2.replace("v9.0  -  ", "v9.1  -  ", 1).replace(
    "  -  ASCII only",
    ", v9.1: a waiting order is cancelled when a new BOS prints before it fills (it never moves to the new leg), Rule A = losses carried + your Rule A amount, the hard cap stops trading until you raise it  -  ASCII only"))

# ---- Rule A tooltip (label and options unchanged, so saved settings still match)
old_tip = s[s.index('stSeqMode = input.string("Off", "Loss-recovery sizing"'):]
old_tip = old_tip[:old_tip.index("\n")]
new_tip = ('stSeqMode = input.string("Off", "Loss-recovery sizing", options = ["Off", "Rule A - recover losses + base profit", "Rule B - double the losses"], group = gRsk, tooltip = "'
           "OFF = every trade risks the base amount. Nothing recovers anything.\\n\\n"
           "LOSSES CARRIED: every closed trade adds its loss or takes off its profit - its Net P&L after commission, as the List of Trades shows it. "
           "Never below zero. They carry over into the next days.\\n\\n"
           "RULE A (v9.1): next risk = losses carried + the Rule A amount (the setting after 'when the cap is reached', 50 by default). Nothing is divided by R. "
           "With base 50 and amount 50: a full loss of 50 -> next risk 100. A news close at -30 -> carried 80 -> next 130. Another -30 -> 110 -> next 160. "
           "A close at +20 -> 90 -> next 140. A win bigger than what is carried -> carried 0 -> back to the base 50.\\n\\n"
           "RULE B: next risk = 2 x losses carried, never less than the base. 50 -> 100 -> 300 -> 900 -> 2700 -> 8100 when every loss is a full stop. "
           "An early exit (opposite signal, time flat) loses less, so the next step is smaller.\\n\\n"
           "A win pays off losses carried; the ladder goes back to the base only when they reach zero, and profit beyond that is not saved. "
           "The size is still rounded to your lot step and cut by Max leverage.\\n\\n"
           "READ THE WARNING IN THE NOTES FILE BEFORE USING EITHER. Both grow the position after losses, which is the fastest known way to empty an account. "
           "The hard cap below exists for exactly that reason - do not remove it.\")")
s = rep(s, old_tip, new_tip)

# ---- the cap: Stop permanently is the new default
old_cap = s[s.index('stSeqCapAct = input.string("Stop for the rest of the day"'):]
old_cap = old_cap[:old_cap.index("\n")]
new_cap = ('stSeqCapAct = input.string("Stop permanently", "  - when the cap is reached", options = ["Clamp to the cap and carry on", "Stop for the rest of the day", "Stop permanently"], group = gRsk, tooltip = "'
           "The cap is reached when the NEXT risk would be bigger than the hard cap - for example 470 carried + 50 = 520 with a cap of 500.\\n\\n"
           "STOP PERMANENTLY (default from v9.1): no new trade is opened - today, tomorrow and every day after. The losses carried are kept. "
           "Trading starts again only when you raise the cap: TradingView then works the whole backtest out again with the new cap, "
           "and you must delete the alert and create it again (an alert keeps the settings it was made with). Open trades keep their own stop and target.\\n\\n"
           "STOP FOR THE DAY: stop opening trades, then clear the carried losses and start fresh at the next trading day.\\n\\n"
           "CLAMP: take the cap as the risk and keep going. The sequence can no longer recover everything, but it keeps trading.\")")
s = rep(s, old_cap, new_cap)

# ---- the two new settings, after the last one (each shows in its own group)
TA = ("Only used by RULE A. The next trade risks the losses carried PLUS this amount.\\n\\n"
      "Example with base risk 50 and this amount 50: a loss of 50 -> the next trade risks 100. With this amount 10: it risks 60.\\n\\n"
      "The first trade of a sequence, and every trade while nothing is carried, risks the BASE risk (above).")
TB = ("ON (default from v9.1): a waiting order only fills on the leg of the signal that armed it. When a new BOS the same way prints before it fills, "
      "a new leg has started: the order is cancelled (audit label 'CANCELLED - new BOS before the fill'), it never moves onto the new leg.\\n"
      "  CHOCH only: every trade is a trade of its CHOCH leg - nothing opens until the next CHOCH.\\n"
      "  BOS only / CHOCH and BOS: the new BOS arms its own order, as before. If it cannot be traded (max trades open, outside the session), "
      "the old order is still cancelled, not moved.\\n\\n"
      "OFF: v9.0 behaviour. In 'Continuous' entry mode the waiting order follows the level, so after a BOS it moves to the pullback of the "
      "BOS leg, with its stop at the new CHOCH* level.")
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stLsN   = input.int(")]
assert len(ix) == 1
lines[ix[0] + 1:ix[0] + 1] = [
    "",
    "// v9.1 - appended after the last setting, so every setting saved on your chart keeps its place. Each one is shown in",
    "// its own group (21 and 24).",
    'stSeqAdd = input.float(50.0, "  - Rule A: amount added on top of the losses carried", minval = 0.0, step = 0.01, group = gRsk, tooltip = "' + TA + '")',
    'stBosCnl = input.bool(true, "Cancel a waiting order when a new BOS prints before it fills", group = gSaf, tooltip = "' + TB + '")',
]
s = "\n".join(lines)

# ---- counter
s = rep(s, "var int    stCntDir = 0\n", "var int    stCntDir = 0\n// v9.1: waiting orders cancelled because a new BOS printed before they filled\nvar int    stCntBosCnl = 0\n")

# ---- Rule A
s = rep(s, "    stRiskNow := stSeqLoss > 0 ? (stSeqLoss + stRisk) / math.max(stRR, 0.1) : stRisk\n",
        "    // v9.1: losses carried + the Rule A amount - nothing divided by R\n"
        "    stRiskNow := stSeqLoss > 0 ? stSeqLoss + stSeqAdd : stRisk\n")

# ---- cancel on a new BOS before the fill
s = rep(s, """if stDir != 0 and (not stGo or (trendDir != 0 and trendDir != stDir))
    f_audEnd(not stGo ? "CANCELLED - blocked" : "CANCELLED - trend flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0
""", """if stDir != 0 and (not stGo or (trendDir != 0 and trendDir != stDir))
    f_audEnd(not stGo ? "CANCELLED - blocked" : "CANCELLED - trend flipped", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stDir := 0

// v9.1: a waiting order only fills on the leg of the signal that armed it. A new BOS the same way before the fill starts a
// new leg: the order is cancelled and never moves onto it (in the BOS modes the new BOS then arms its own order below)
if stBosCnl and stDir != 0 and not na(stArmBar) and bar_index > stArmBar and ((stDir == 1 and evBosUp) or (stDir == -1 and evBosDn))
    f_audEnd("CANCELLED - new BOS before the fill", stAudCancC)
    if f_stCancel(stOrdLive, stPendId)
        stCnlSent := true
    stOrdLive := false
    stCntCanc += 1
    stCntBosCnl += 1
    stDir := 0
""")

# ---- table
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 43,", "stTbl := table.new(f_stPos(stStatPos), 2, 44,")
s = rep(s, """stSeqMode == "Rule A - recover losses + base profit" ? "A - recover + base" : "B - double the losses\"""",
        """stSeqMode == "Rule A - recover losses + base profit" ? ("A - losses + " + str.tostring(stSeqAdd)) : "B - double the losses\"""")
i = s.index('    f_stCell(stTbl, 42, "  - skipped: HTF filter')
j = s.index("\n", i)
s = s[:j + 1] + """    f_stCell(stTbl, 43, "Cancelled - new BOS before the fill", stBosCnl ? str.tostring(stCntBosCnl) : "off", stBosCnl ? (stCntBosCnl > 0 ? color.orange : color.gray) : color.gray)
""" + s[j + 1:]

open(R + "SMC_Structure_Strategy_v9.1.txt", "w").write(s)
print("ok", len(s.split("\n")))
