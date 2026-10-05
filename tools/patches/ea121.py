# MT5 EA v12.0 -> v12.1 (everything OFF by default):
#   1. HARD CAP: a 4th choice for 'when the cap is reached' - start again from the base risk (forget the losses)
#   2. group 42 at the END of the inputs: loss recovery starts again from the base risk when the losses carried reach a mark
#   ('no new trades before news' is already in the EA - group 41)
#   core (between //==CORE-BEGIN== and //==CORE-END==) + adapter
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_EA_v12.0.mq5").read()
assert "InLmOn" not in s and "CAP_BASE" not in s and "cntLm" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


# ---- version strings (the notes file stays the v12.0 one - no v12.1 notes were asked for)
s = rep(s, "//| SMC Structure EA v12.0 (+ hedge) - MetaTrader 5 Expert Advisor     |", "//| SMC Structure EA v12.1 (+ hedge) - MetaTrader 5 Expert Advisor     |")
s = rep(s, '//| The TradingView strategy "SMC Structure Strategy" v12.0, same      |', '//| The TradingView strategy "SMC Structure Strategy" v12.1, same      |')
s = rep(s, '#property version     "12.00"', '#property version     "12.10"')
s = rep(s, '#property description "SMC Structure EA v12.0 - the TradingView strategy v12.0 rules in MetaTrader 5, plus a hedge mode."',
        '#property description "SMC Structure EA v12.1 - the TradingView strategy v12.1 rules in MetaTrader 5, plus a hedge mode."')
s = rep(s, "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.0)",
        "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.1)")
s = rep(s, '   Print("SMC EA v12.0 ready: ", n,', '   Print("SMC EA v12.1 ready: ", n,')
s = rep(s, '   Row("SMC STRATEGY  (EA v12.0)", "value", clrWhite);', '   Row("SMC STRATEGY  (EA v12.1)", "value", clrWhite);')

# ---- 1. the 4th cap choice (at the end of the list)
s = rep(s, "   CAP_PERM = 2       // Stop permanently\n};", "   CAP_PERM = 2,      // Stop permanently\n   CAP_BASE = 3       // Start again from the base risk (forget the losses)\n};")

# ---- 2. inputs (group 42 at the very end)
old = "input bool     InR3Fb      = false;   //   - if the close is too far: fall back to RULE 1 / 2\n"
s = rep(s, old, old +
        'input group "42. Loss recovery - start again from the base (v12.1)"\n'
        "input bool     InLmOn      = false;   // Start again from the base risk when the losses carried reach\n"
        "input double   InLmAmt     = 300.0;   //   - losses carried, in account currency\n")

# ---- core settings
s = rep(s, "   bool   r3On, r3BrkOn, r3Fb; // v12.0: rule 3, 'only if the close is near the broken level', 'too far: fall back to rule 1 / 2'\n",
        "   bool   r3On, r3BrkOn, r3Fb; // v12.0: rule 3, 'only if the close is near the broken level', 'too far: fall back to rule 1 / 2'\n"
        "   bool   lmOn;                // v12.1: group 42 - start again from the base when the losses carried reach lmAmt\n"
        "   double lmAmt;\n")
s = rep(s, "r3On = false; r3BrkOn = false; r3Fb = false; r3Brk = 0; }", "r3On = false; r3BrkOn = false; r3Fb = false; r3Brk = 0; lmOn = false; lmAmt = 0; }")

# ---- money: the counter
s = rep(s, "   int    cntSeqCap, dayTrades, lsRun, cntLs, ldRun, cntLd, prevDom;\n",
        "   int    cntSeqCap, dayTrades, lsRun, cntLs, ldRun, cntLd, prevDom;\n"
        "   int    cntLm;     // v12.1: times the losses carried reached the group 42 mark\n")
s = rep(s, "      cntSeqCap = 0; dayTrades = 0; lsRun = 0; cntLs = 0; ldRun = 0; cntLd = 0; prevDom = -1;\n",
        "      cntSeqCap = 0; dayTrades = 0; lsRun = 0; cntLs = 0; ldRun = 0; cntLd = 0; prevDom = -1;\n"
        "      cntLm = 0;\n")

# ---- 2. the loss mark, right after the closed trades are counted
s = rep(s, """      flPnl  += sqSum;
      flPeak  = Mx(flPeak, flPnl);
      if (Car() <= 0.005 && S.capAct != 2) { seqHalt = false; seqCapOn = false; }
""", """      flPnl  += sqSum;
      flPeak  = Mx(flPeak, flPnl);
      // v12.1: group 42 - the losses carried reached the mark: they are forgotten, the next trade risks the base again
      if (S.lmOn && S.seqMode != 0 && Car() >= S.lmAmt - 0.005) { seqLoss = 0; seqTot = 0; cntLm++; }
      if (Car() <= 0.005 && S.capAct != 2) { seqHalt = false; seqCapOn = false; }
""")

# ---- 1. the cap: start again from the base risk
s = rep(s, """         if (!seqCapOn) { cntSeqCap++; seqCapOn = true; }
         riskNow = S.seqMax;
         if (S.capAct != 0) seqHalt = true;
""", """         if (!seqCapOn) { cntSeqCap++; seqCapOn = true; }
         riskNow = S.seqMax;
         if (S.capAct == 3)
         {  // v12.1: the losses carried are forgotten and the next trade risks the base again (never above the cap)
            if (car > 0.005) { seqLoss = 0; seqTot = 0; seqCapOn = false; }
            riskNow = Mn(S.risk, S.seqMax);
         }
         else if (S.capAct != 0) seqHalt = true;
""")

# ---- adapter: settings, checks, table
s = rep(s, "   S.r3On = InR3On; S.r3BrkOn = InR3BrkOn; S.r3Brk = InR3Brk; S.r3Fb = InR3Fb;\n",
        "   S.r3On = InR3On; S.r3BrkOn = InR3BrkOn; S.r3Brk = InR3Brk; S.r3Fb = InR3Fb;\n"
        "   S.lmOn = InLmOn; S.lmAmt = InLmAmt;\n")
s = rep(s, '   if (InR3Brk < 0) return "Rule 3 (group 39): the distance from the broken level must be 0 or more";\n',
        '   if (InR3Brk < 0) return "Rule 3 (group 39): the distance from the broken level must be 0 or more";\n'
        '   if (InLmAmt < 0.01) return "Loss mark (group 42): the losses carried must be 0.01 or more";\n')
cap_old = 'MonTxt(I2(g_money[0].cntSeqCap) + (g_money[0].seqHalt ? "  HALTED" : ""), I2(g_money[1].cntSeqCap) + (g_money[1].seqHalt ? "  HALTED" : ""))'
cap_new = 'MonTxt(I2(g_money[0].cntSeqCap) + CapTxt() + (g_money[0].seqHalt ? "  HALTED" : ""), I2(g_money[1].cntSeqCap) + CapTxt() + (g_money[1].seqHalt ? "  HALTED" : ""))'
s = rep(s, cap_old, cap_new, 2)
s = rep(s, "   if (S.split > 1.0) m = m + \"  |  split over \" + DoubleToString(S.split, 1) + \" trades\";\n",
        "   if (S.split > 1.0) m = m + \"  |  split over \" + DoubleToString(S.split, 1) + \" trades\";\n"
        "   if (S.lmOn) m = m + \"  |  back to the base at \" + Mo(S.lmAmt) + \" carried\";\n")
s = rep(s, '   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", R3Txt(), S.r3On ? clrAqua : clrGray);\n',
        '   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", R3Txt(), S.r3On ? clrAqua : clrGray);\n'
        '   Row("LOSS MARK - BACK TO THE BASE (group 42)", LmTxt(), S.lmOn && S.seqMode != 0 ? clrAqua : clrGray);\n')
old = "// v12.0: rule 3 - entries at the close of the signal candle (group 39)\n"
s = rep(s, old,
        "// v12.1: the hard cap row, and group 42 (the loss mark)\n"
        "string CapTxt() { return S.capAct == 3 ? \" x back to the base\" : \"\"; }\n"
        "string LmTxt()\n"
        "{\n"
        '   if (!S.lmOn) return "off";\n'
        '   if (S.seqMode == 0) return "on - but loss recovery is Off";\n'
        '   return "at " + Mo(S.lmAmt) + ":  " + MonTxt(I2(g_money[0].cntLm) + " x back to the base", I2(g_money[1].cntLm) + " x back to the base");\n'
        "}\n" + old)

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.1.mq5", "w").write(s)
print("EA v12.1 written:", len(s.split("\n")), "lines")
