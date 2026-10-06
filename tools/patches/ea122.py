# MT5 EA v12.1 -> v12.2 (everything OFF by default):
#   - the v12.1 profit mark is removed: v12.2 starts from the EA v12.1 as it was before the profit mark (commit ec60510)
#   - 'Loss-recovery sizing' gets 3 choices at the end (SEQ_AS / SEQ_BS / SEQ_CS = 7 / 8 / 9): Rule A / B / C with the base
#     risk from the profit steps of group 43 (at the very END of the inputs); same rule as the TradingView strategy v12.2
import subprocess
R = "/home/user/smc-work/"
s = subprocess.run(["git", "-C", R, "show", "ec60510:SMC_Structure_EA_v12.1.mq5"], capture_output=True, text=True, check=True).stdout
assert "InPmOn" not in s and "InSp1" not in s and "SEQ_CS" not in s and "StepBase" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


# ---- version strings (the notes file stays the v12.0 one - no notes were asked for)
s = rep(s, "//| SMC Structure EA v12.1 (+ hedge) - MetaTrader 5 Expert Advisor     |", "//| SMC Structure EA v12.2 (+ hedge) - MetaTrader 5 Expert Advisor     |")
s = rep(s, '//| The TradingView strategy "SMC Structure Strategy" v12.1, same      |', '//| The TradingView strategy "SMC Structure Strategy" v12.2, same      |')
s = rep(s, '#property version     "12.10"', '#property version     "12.20"')
s = rep(s, '#property description "SMC Structure EA v12.1 - the TradingView strategy v12.1 rules in MetaTrader 5, plus a hedge mode."',
        '#property description "SMC Structure EA v12.2 - the TradingView strategy v12.2 rules in MetaTrader 5, plus a hedge mode."')
s = rep(s, "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.1)",
        "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.2)")
s = rep(s, '   Print("SMC EA v12.1 ready: ", n,', '   Print("SMC EA v12.2 ready: ", n,')
s = rep(s, '   Row("SMC STRATEGY  (EA v12.1)", "value", clrWhite);', '   Row("SMC STRATEGY  (EA v12.2)", "value", clrWhite);')

# ---- the 3 new rules at the end of the list
s = rep(s, "   SEQ_CP = 6         // Rule C+ (only when total P&L is below 0: that loss)\n};",
        "   SEQ_CP = 6,        // Rule C+ (only when total P&L is below 0: that loss)\n"
        "   SEQ_AS = 7,        // Rule A split (A, the base grows with the profit - group 43)\n"
        "   SEQ_BS = 8,        // Rule B split (B, the base grows with the profit - group 43)\n"
        "   SEQ_CS = 9         // Rule C split (C, the base grows with the profit - group 43)\n};")
s = rep(s, "      seqPlus = seqMode >= 4;\n", "      seqPlus = seqMode >= 4 && seqMode <= 6;\n")

# ---- inputs (group 43 at the very end)
old = "input double   InLmAmt     = 300.0;   //   - losses carried, in account currency\n"
s = rep(s, old, old +
        'input group "43. Rule A / B / C split - the base risk grows with the profit (v12.2)"\n'
        "input double   InSp1       = 200.0;   // Step 1 - total profit of at least\n"
        "input double   InSpN1      = 3.0;     //   - split it into this many parts\n"
        "input double   InSp2       = 500.0;   // Step 2 - total profit of at least\n"
        "input double   InSpN2      = 5.0;     //   - split it into this many parts\n"
        "input double   InSp3       = 1000.0;  // Step 3 - total profit of at least\n"
        "input double   InSpN3      = 8.0;     //   - split it into this many parts\n"
        "input double   InSpInc     = 500.0;   // Then a new step every this much more profit  (0 = no more steps)\n"
        "input double   InSpAdd     = 1.0;     //   - each new step is split into this many more parts\n")

# ---- core settings
s = rep(s, "   double lmAmt;\n", "   double lmAmt;\n"
        "   double sp1, spN1, sp2, spN2, sp3, spN3, spInc, spAdd;   // v12.2: group 43 - the profit steps of Rule A / B / C split\n")
s = rep(s, "lmOn = false; lmAmt = 0; }", "lmOn = false; lmAmt = 0; sp1 = 0; spN1 = 1; sp2 = 0; spN2 = 1; sp3 = 0; spN3 = 1; spInc = 0; spAdd = 0; }")

# ---- the step base (core), before the money class
old = "// ---------- money: loss recovery, floor, daily limits, pause (one per side, or one shared) ----------\n"
s = rep(s, old,
        "// v12.2: Rule A / B / C split - the base risk from the profit steps of group 43: the step reached / its parts (0 = no step)\n"
        "double StepBase(double pf)\n"
        "{\n"
        "   double a = 0, n = 1;\n"
        "   if (S.sp1 > 0 && pf >= S.sp1 - 0.005 && S.sp1 > a) { a = S.sp1; n = S.spN1; }\n"
        "   if (S.sp2 > 0 && pf >= S.sp2 - 0.005 && S.sp2 > a) { a = S.sp2; n = S.spN2; }\n"
        "   if (S.sp3 > 0 && pf >= S.sp3 - 0.005 && S.sp3 > a)\n"
        "   {\n"
        "      a = S.sp3;\n"
        "      n = S.spN3;\n"
        "      if (S.spInc > 0)\n"
        "      {\n"
        "         double k = MathFloor((pf - S.sp3 + 0.005) / S.spInc);\n"
        "         a = S.sp3 + k * S.spInc;\n"
        "         n = S.spN3 + k * S.spAdd;\n"
        "      }\n"
        "   }\n"
        "   return a > 0 ? a / n : 0.0;\n"
        "}\n" + old)

# ---- money: the base in use (for the table) and the risk
s = rep(s, "   int    cntLm;     // v12.1: times the losses carried reached the group 42 mark\n",
        "   int    cntLm;     // v12.1: times the losses carried reached the group 42 mark\n"
        "   double basNow;    // v12.2: the base risk in use (the profit step with Rule A / B / C split)\n")
s = rep(s, "      cntLm = 0;\n", "      cntLm = 0; basNow = 0;\n")
s = rep(s, """      else if (S.seqMode == 3 || S.seqMode == 6) riskNow = car > 0.005 ? Mx(S.risk, car / S.split) : S.risk;
""", """      else if (S.seqMode == 3 || S.seqMode == 6) riskNow = car > 0.005 ? Mx(S.risk, car / S.split) : S.risk;
      // v12.2: Rule A / B / C split - the base grows in steps with the total profit (never below the base risk, never above the cap)
      basNow = S.seqMode >= 7 ? Mx(S.risk, Mn(StepBase(flPnl), S.seqMax)) : S.risk;
      if (S.seqMode == 7) riskNow = car > 0.005 ? Mx(basNow, (car + S.seqAdd) / S.split) : basNow;
      else if (S.seqMode == 8) riskNow = car > 0.005 ? Mx(basNow, 2.0 * car / S.split) : basNow;
      else if (S.seqMode == 9) riskNow = car > 0.005 ? Mx(basNow, car / S.split) : basNow;
""")
s = rep(s, "            riskNow = Mn(S.risk, S.seqMax);\n", "            riskNow = Mn(basNow, S.seqMax);\n")

# ---- adapter: settings, checks, table
s = rep(s, "   S.lmOn = InLmOn; S.lmAmt = InLmAmt;\n",
        "   S.lmOn = InLmOn; S.lmAmt = InLmAmt;\n"
        "   S.sp1 = InSp1; S.spN1 = InSpN1; S.sp2 = InSp2; S.spN2 = InSpN2; S.sp3 = InSp3; S.spN3 = InSpN3; S.spInc = InSpInc; S.spAdd = InSpAdd;\n")
s = rep(s, '   if (InLmAmt < 0.01) return "Loss mark (group 42): the losses carried must be 0.01 or more";\n',
        '   if (InLmAmt < 0.01) return "Loss mark (group 42): the losses carried must be 0.01 or more";\n'
        '   if (InSp1 < 0 || InSp2 < 0 || InSp3 < 0 || InSpInc < 0 || InSpAdd < 0 || InSpN1 < 1 || InSpN2 < 1 || InSpN3 < 1) return "Profit steps (group 43): amounts 0 or more, parts 1 or more";\n')
s = rep(s, '''              (S.seqMode == 4 ? "A+ - total below 0 + " + Mo(S.seqAdd) : (S.seqMode == 5 ? "B+ - 2 x total below 0" : "C+ - total below 0"))));''',
        '''              (S.seqMode == 4 ? "A+ - total below 0 + " + Mo(S.seqAdd) : (S.seqMode == 5 ? "B+ - 2 x total below 0" : (S.seqMode == 6 ? "C+ - total below 0" :
              (S.seqMode == 7 ? "A split - loss since the high + " + Mo(S.seqAdd) + ", base from the profit steps" : (S.seqMode == 8 ? "B split - 2 x loss since the high, base from the profit steps" :
              "C split - loss since the high, base from the profit steps")))))));''')
s = rep(s, '   Row("LOSS MARK - BACK TO THE BASE (group 42)", LmTxt(), S.lmOn && S.seqMode != 0 ? clrAqua : clrGray);\n',
        '   Row("LOSS MARK - BACK TO THE BASE (group 42)", LmTxt(), S.lmOn && S.seqMode != 0 ? clrAqua : clrGray);\n'
        '   Row("PROFIT STEPS - A / B / C split (group 43)", SpTxt(), S.seqMode >= 7 ? clrAqua : clrGray);\n')
old = "// v12.1: the hard cap row, and group 42 (the loss mark)\n"
s = rep(s, old,
        "// v12.2: group 43 - the profit and the base risk of Rule A / B / C split\n"
        "string SpTxt()\n"
        "{\n"
        '   if (S.seqMode < 7) return "off";\n'
        '   return MonTxt("profit " + Mo(g_money[0].flPnl) + "  ->  base " + Mo(g_money[0].basNow), "profit " + Mo(g_money[1].flPnl) + "  ->  base " + Mo(g_money[1].basNow));\n'
        "}\n" + old)

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.2.mq5", "w").write(s)
print("EA v12.2 written:", len(s.split("\n")), "lines")
