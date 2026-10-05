# MT5 EA v11.2 -> v12.0 : RULE 3 - enter at the close of the signal candle, optionally only when the close is at most N
#   beyond the broken level (group 39 at the END of the inputs, everything OFF by default)
#   core (between //==CORE-BEGIN== and //==CORE-END==) + adapter; the test harness / fake MT5 get the same BkPlace(..., mkt)
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_EA_v11.2.mq5").read()
assert "InR3On" not in s and "mktBar" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


# ---- version strings
s = rep(s, "//| SMC Structure EA v11.2 (+ hedge) - MetaTrader 5 Expert Advisor     |", "//| SMC Structure EA v12.0 (+ hedge) - MetaTrader 5 Expert Advisor     |")
s = rep(s, '//| The TradingView strategy "SMC Structure Strategy" v11.2, same      |', '//| The TradingView strategy "SMC Structure Strategy" v12.0, same      |')
s = rep(s, "//| Owner: Punit. Read SMC_Structure_EA_v11.2_NOTES.txt first.          |", "//| Owner: Punit. Read SMC_Structure_EA_v12.0_NOTES.txt first.          |")
s = rep(s, '#property version     "11.20"', '#property version     "12.00"')
s = rep(s, '#property description "SMC Structure EA v11.2 - the TradingView strategy v11.2 rules in MetaTrader 5, plus a hedge mode."',
        '#property description "SMC Structure EA v12.0 - the TradingView strategy v12.0 rules in MetaTrader 5, plus a hedge mode."')
s = rep(s, "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v11.2)",
        "//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.0)")
s = rep(s, '   Print("SMC EA v11.2 ready: ", n,', '   Print("SMC EA v12.0 ready: ", n,')
s = rep(s, '   Row("SMC STRATEGY  (EA v11.2)", "value", clrWhite);', '   Row("SMC STRATEGY  (EA v12.0)", "value", clrWhite);')


# ---- inputs (group 39 at the very end)
old = "input double   InBuPip     = 0.0;     //   - pip size (0 = automatic)\n"
s = rep(s, old, old +
        'input group "39. RULE 3 - enter at the close of the signal candle (v12.0)"\n'
        "input bool     InR3On      = false;   // RULE 3 - enter at the close of the signal candle\n"
        "input bool     InR3BrkOn   = false;   //   - RULE 3: only if the close is near the broken level\n"
        "input double   InR3Brk     = 3.0;     //   - the most the close may be beyond the broken level\n")

# ---- core settings
s = rep(s, "   int    buMode;\n   double buPips, buPct, pipSz;\n",
        "   int    buMode;\n   double buPips, buPct, pipSz;\n"
        "   bool   r3On, r3BrkOn;       // v12.0: rule 3, and 'only if the close is near the broken level'\n"
        "   double r3Brk;\n")
s = rep(s, "buMode = 0; buPips = 0; buPct = 0; pipSz = 0; }", "buMode = 0; buPips = 0; buPct = 0; pipSz = 0; r3On = false; r3BrkOn = false; r3Brk = 0; }")

# ---- broker action: market flag
s = rep(s, "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q);",
        "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt);")

# ---- the side: state + counters
s = rep(s, "   int    dir, rule, armBar, seq;\n", "   int    dir, rule, armBar, seq, mktBar;\n")
s = rep(s, "   int    cntArm, cntFill, cntCanc, cntSkip, cntR1, cntR2, cntDir, cntHf, cntPd, cntBosCnl, cntExp, cntCap, cntMoves;\n",
        "   int    cntArm, cntFill, cntCanc, cntSkip, cntR1, cntR2, cntDir, cntHf, cntPd, cntBosCnl, cntExp, cntCap, cntMoves;\n"
        "   int    cntR3, cntR3Far;   // v12.0\n")
s = rep(s, "      dir = 0; rule = 0; armBar = NAI; seq = 0;\n", "      dir = 0; rule = 0; armBar = NAI; seq = 0; mktBar = NAI;\n")
s = rep(s, "cntBosCnl = 0; cntExp = 0; cntCap = 0; cntMoves = 0;\n      ntrk = 0;\n",
        "cntBosCnl = 0; cntExp = 0; cntCap = 0; cntMoves = 0;\n      cntR3 = 0; cntR3Far = 0;\n      ntrk = 0;\n")
s = rep(s, "      if (rule == 2) cntR2++; else cntR1++;\n", "      if (rule == 3) cntR3++; else if (rule == 2) cntR2++; else cntR1++;\n")

# ---- one chance for a rule 3 entry; the live stop is for rule 1 only
old = "      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with\n      if (dir != 0 && rule != 2 && !(S.once && placed))\n"
s = rep(s, old,
        "      // v12.0: a rule 3 entry at the signal close has ONE chance - sent on the signal candle (or the next one when an\n"
        "      // opposite trade had to close first), filled at the next open; never sent again at a later price\n"
        "      if (dir != 0 && rule == 3 && ((mktBar != NAI && EN.bi > mktBar) || (armBar != NAI && EN.bi > armBar + 1))) Cancel(\"CANCELLED - the entry at the signal close did not fill\");\n"
        "      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with\n      if (dir != 0 && rule != 2 && rule != 3 && !(S.once && placed))\n")

# ---- arming
old = "            if ((S.autoM && !use) || (!S.autoM && S.agn && !agst && S.r1) || (!S.autoM && !S.agn && !agree && S.r1 && S.hfEff)) cntHf++;\n"
s = rep(s, old,
        "            bool hfSkip = (S.autoM && !use) || (!S.autoM && S.agn && !agst && S.r1) || (!S.autoM && !S.agn && !agree && S.r1 && S.hfEff);\n"
        "            // v12.0: rule 3 - enter at the close of this candle (rules 1 / 2 not used; the higher-timeframe filters still apply,\n"
        "            // no agreement needed - like rule 1). Optionally only when the close is near the broken level (the pivot).\n"
        "            double r3B   = IsNa(piv) ? NAD : d * (g_c - piv);\n"
        "            bool   r3Far = S.r3On && S.r3BrkOn && (IsNa(r3B) || r3B > LimAt(S.r3Brk, g_c));\n"
        "            bool   useM  = S.autoM ? (g_autoDir != 0 && d == g_autoDir) : (S.agn ? agst : (agree || !S.hfEff));\n"
        "            if (S.r3On)\n"
        "            {\n"
        "               hfSkip = !r3Far && !useM;\n"
        "               use    = !r3Far && useM;\n"
        "               if (r3Far) cntR3Far++;\n"
        "            }\n"
        "            if (hfSkip) cntHf++;\n")
s = rep(s, "               rule    = (agree && S.r2 && !S.agn) ? 2 : 1;\n",
        "               rule    = S.r3On ? 3 : ((agree && S.r2 && !S.agn) ? 2 : 1);\n"
        "               mktBar  = NAI;\n")
s = rep(s, '               Note(sg + ": " + Id() + (rule == 2 ? " R2" : " R1") + " ARMED");\n',
        '               Note(sg + ": " + Id() + (rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED")));\n')
s = rep(s, '            else if (!use) Note(sg + ": SKIP - " + (S.autoM ? "auto mode side / rule" : (S.agn ? "not against the higher timeframe" : (agree ? "no broken pivot" : "higher timeframe filter"))));\n',
        '            else if (S.r3On && r3Far) Note(sg + ": SKIP - RULE 3: " + (IsNa(r3B) ? (string)"no broken level" : "close " + DoubleToString(r3B, 2) + " beyond the broken level"));\n'
        '            else if (!use) Note(sg + ": SKIP - " + (S.autoM ? "auto mode side / rule" : (S.agn ? "not against the higher timeframe" : (agree && !S.r3On ? "no broken pivot" : "higher timeframe filter"))));\n')

# ---- the entry: the close for rule 3
s = rep(s, "         ent = (S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb));\n",
        "         ent = rule == 3 ? g_c : ((S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb)));\n")
s = rep(s, "               BkPlace(k, seq, 0, dir, ent, sl, tgt, q - q1);\n", "               BkPlace(k, seq, 0, dir, ent, sl, tgt, q - q1, rule == 3);\n")
s = rep(s, "                  BkPlace(k, seq, 1, dir, ent, sl, tp1, q1);\n", "                  BkPlace(k, seq, 1, dir, ent, sl, tp1, q1, rule == 3);\n")
s = rep(s, "               ordLive  = true;\n               lastCapQ = qCap;\n",
        "               ordLive  = true;\n"
        "               if (rule == 3 && mktBar == NAI) mktBar = EN.bi;\n"
        "               lastCapQ = qCap;\n")

# ---- adapter: the virtual order gets the market flag
s = rep(s, "   long   ticket;\n   int    fails;\n};\nVOrd     g_vb[4];", "   long   ticket;\n   int    fails;\n   bool   mkt;     // v12.0: a rule 3 entry - a market order at once\n};\nVOrd     g_vb[4];")
s = rep(s, "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q)\n{",
        "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt)\n{")
s = rep(s, "   g_vb[i].lots = NormLots(q);\n", "   g_vb[i].lots = NormLots(q);\n   g_vb[i].mkt  = mkt;\n")
s = rep(s, "      if (g_vb[i].on && ((g_vb[i].dir == 1 && bid <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && bid >= NormUp(g_vb[i].ent)))) SendMarket(i);\n",
        "      if (g_vb[i].on && (g_vb[i].mkt || (g_vb[i].dir == 1 && bid <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && bid >= NormUp(g_vb[i].ent)))) SendMarket(i);\n")
old = "      int    dir = g_vb[i].dir;\n      double px  = dir == 1 ? NormDn(g_vb[i].ent) : NormUp(g_vb[i].ent);\n"
s = rep(s, old,
        "      if (g_vb[i].mkt)\n"
        "      {   // v12.0: a rule 3 entry is a market order at once (no pending order)\n"
        "         if (exists) { if (!g_trade.OrderDelete(tk)) continue; g_vb[i].ticket = 0; }\n"
        "         if (PosWithComment(CmtOf(g_vb[i].dir, g_vb[i].seq, i % 2))) { g_vb[i].on = false; continue; }\n"
        "         SendMarket(i);\n"
        "         continue;\n"
        "      }\n" + old)
# restarts: keep the flags
s = rep(s, '      GvSet(v + "sl", g_vb[i].sl); GvSet(v + "tg", g_vb[i].tgt); GvSet(v + "lot", g_vb[i].lots); GvSet(v + "tk", (double)g_vb[i].ticket);\n',
        '      GvSet(v + "sl", g_vb[i].sl); GvSet(v + "tg", g_vb[i].tgt); GvSet(v + "lot", g_vb[i].lots); GvSet(v + "tk", (double)g_vb[i].ticket);\n'
        '      GvSet(v + "mk", g_vb[i].mkt ? 1 : 0);\n')
s = rep(s, "      g_vb[i].ticket = (long)GvGet(v + \"tk\", 0); g_vb[i].fails = 0;\n",
        "      g_vb[i].ticket = (long)GvGet(v + \"tk\", 0); g_vb[i].fails = 0; g_vb[i].mkt = GvGet(v + \"mk\", 0) > 0.5;\n")
s = rep(s, '      GvSet(GvSide(k, "pt"), g_side[k].planTgt);\n',
        '      GvSet(GvSide(k, "pt"), g_side[k].planTgt);\n'
        '      GvSet(GvSide(k, "mb"), g_side[k].mktBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].mktBar));\n')
s = rep(s, '      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n',
        '      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n'
        '      double mb = GvGet(GvSide(k, "mb"), -1);\n'
        '      g_side[k].mktBar = mb < 0 ? NAI : BarOfTime((datetime)mb);\n')

# ---- adapter: settings, checks, table
s = rep(s, "   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n",
        "   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n"
        "   S.r3On = InR3On; S.r3BrkOn = InR3BrkOn; S.r3Brk = InR3Brk;\n")
s = rep(s, '   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";\n',
        '   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";\n'
        '   if (InR3Brk < 0) return "Rule 3 (group 39): the distance from the broken level must be 0 or more";\n')
s = rep(s, "   if (what == 11) return g_side[k].cntCap;\n",
        "   if (what == 11) return g_side[k].cntCap;\n"
        "   if (what == 13) return g_side[k].cntR3;\n"
        "   if (what == 14) return g_side[k].cntR3Far;\n")
s = rep(s, '   Row("  - by ENTRY RULE 2 (broken pivot)", CntTxt(5), clrLime);\n',
        '   Row("  - by ENTRY RULE 2 (broken pivot)", CntTxt(5), clrLime);\n'
        '   if (S.r3On) Row("  - by ENTRY RULE 3 (signal close)", CntTxt(13), clrLime);\n')
s = rep(s, '   Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);\n   Row("Entries  |  magic",',
        '   Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);\n'
        '   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", R3Txt(), S.r3On ? clrAqua : clrGray);\n'
        '   Row("Entries  |  magic",')
old = "// v11.2: the stop buffer in use, in price\n"
s = rep(s, old,
        "// v12.0: rule 3 - entries at the close of the signal candle (group 39)\n"
        "string R3Txt()\n"
        "{\n"
        '   if (!S.r3On) return "off - rules 1 / 2";\n'
        '   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");\n'
        '   string t = "on  -  " + CntTxt(13) + " entered at the close";\n'
        '   if (S.r3BrkOn) t = t + "  |  close within " + Num(S.r3Brk) + u + " of the break: " + CntTxt(14) + " skipped";\n'
        "   return t;\n"
        "}\n" + old)

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.0.mq5", "w").write(s)
print("EA v12.0 written:", len(s.split("\n")), "lines")
