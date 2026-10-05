# MT5 EA v11.2 -> v12.0 : RULE 3 / RULE 4 - enter at the close of the signal candle (group 39 at the END of the inputs)
#   core (between //==CORE-BEGIN== and //==CORE-END==) + adapter; the test harness / fake MT5 get the same BkPlace(..., mkt)
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_EA_v11.2.mq5").read()
assert "InCcMode" not in s and "mktBar" not in s


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

# ---- enums + inputs (group 39 at the very end)
s = rep(s, "enum EBuMode\n{\n", "enum ECcMode\n{\n"
        "   CC_OFF = 0,        // Off (rules 1 / 2 as now)\n"
        "   CC_R3 = 1,         // RULE 3 - always enter at the close\n"
        "   CC_R4 = 2          // RULE 4 - enter at the close only if the stop distance is within the limits\n"
        "};\n"
        "enum ECcFar\n{\n"
        "   CF_SKIP = 0,       // Skip the setup\n"
        "   CF_BACK = 1        // Fall back to RULE 1 / 2 (wait for the pullback)\n"
        "};\n"
        "enum EBuMode\n{\n")
old = "input double   InBuPip     = 0.0;     //   - pip size (0 = automatic)\n"
s = rep(s, old, old +
        'input group "39. Entry at the close of the signal candle - rules 3 / 4 (v12.0)"\n'
        "input ECcMode  InCcMode    = CC_OFF;  // Entry at the close of the signal candle\n"
        "input double   InCcMax     = 30.0;    //   - RULE 4: skip if the stop is FURTHER than (0 = off)\n"
        "input double   InCcMin     = 3.0;     //   - RULE 4: skip if the stop is CLOSER than (0 = off)\n"
        "input ECcFar   InCcFar     = CF_SKIP; //   - RULE 4: when the stop is too far\n")

# ---- core settings
s = rep(s, "   int    buMode;\n   double buPips, buPct, pipSz;\n",
        "   int    buMode;\n   double buPips, buPct, pipSz;\n"
        "   int    ccMode;              // v12.0: 0 off, 1 rule 3, 2 rule 4\n"
        "   double ccMax, ccMin;\n"
        "   bool   ccFb;\n")
s = rep(s, "buMode = 0; buPips = 0; buPct = 0; pipSz = 0; }", "buMode = 0; buPips = 0; buPct = 0; pipSz = 0; ccMode = 0; ccMax = 0; ccMin = 0; ccFb = false; }")
old = "double LimAt(double v, double ent) { return S.buMode == 1 ? v * S.pipSz : (S.buMode == 2 ? ent * v / 100.0 : v); }\n"
s = rep(s, old, old +
        "// v12.0: the rule 4 limits (group 39), in the unit of group 38 like group 24\n"
        "bool CcOk(double r, double ent) { return (S.ccMin <= 0 || r >= LimAt(S.ccMin, ent)) && (S.ccMax <= 0 || r <= LimAt(S.ccMax, ent)); }\n")

# ---- broker action: market flag
s = rep(s, "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q);",
        "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt);")

# ---- the side: state + counters
s = rep(s, "   int    dir, rule, armBar, seq;\n", "   int    dir, rule, armBar, seq, mktBar;\n")
s = rep(s, "   bool   ordLive, lastCapQ, placed, ppSent;\n", "   bool   ordLive, lastCapQ, placed, ppSent, ccLim;\n")
s = rep(s, "   int    cntArm, cntFill, cntCanc, cntSkip, cntR1, cntR2, cntDir, cntHf, cntPd, cntBosCnl, cntExp, cntCap, cntMoves;\n",
        "   int    cntArm, cntFill, cntCanc, cntSkip, cntR1, cntR2, cntDir, cntHf, cntPd, cntBosCnl, cntExp, cntCap, cntMoves;\n"
        "   int    cntR3, cntCcFar, cntCcNear, cntCcFb;   // v12.0\n")
s = rep(s, "      dir = 0; rule = 0; armBar = NAI; seq = 0;\n", "      dir = 0; rule = 0; armBar = NAI; seq = 0; mktBar = NAI; ccLim = false;\n")
s = rep(s, "cntBosCnl = 0; cntExp = 0; cntCap = 0; cntMoves = 0;\n      ntrk = 0;\n",
        "cntBosCnl = 0; cntExp = 0; cntCap = 0; cntMoves = 0;\n      cntR3 = 0; cntCcFar = 0; cntCcNear = 0; cntCcFb = 0;\n      ntrk = 0;\n")
s = rep(s, "      if (rule == 2) cntR2++; else cntR1++;\n", "      if (rule == 3) cntR3++; else if (rule == 2) cntR2++; else cntR1++;\n")

# ---- one chance for a rule 3 / 4 entry; the live stop is for rule 1 only
old = "      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with\n      if (dir != 0 && rule != 2 && !(S.once && placed))\n"
s = rep(s, old,
        "      // v12.0: a rule 3 / 4 entry at the signal close has ONE chance - sent on the signal candle (or the next one when an\n"
        "      // opposite trade had to close first), filled at the next open; never sent again at a later price\n"
        "      if (dir != 0 && rule == 3 && ((mktBar != NAI && EN.bi > mktBar) || (armBar != NAI && EN.bi > armBar + 1))) Cancel(\"CANCELLED - the entry at the signal close did not fill\");\n"
        "      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with\n      if (dir != 0 && rule != 2 && rule != 3 && !(S.once && placed))\n")

# ---- arming
old = "            if ((S.autoM && !use) || (!S.autoM && S.agn && !agst && S.r1) || (!S.autoM && !S.agn && !agree && S.r1 && S.hfEff)) cntHf++;\n"
s = rep(s, old,
        "            bool hfSkip = (S.autoM && !use) || (!S.autoM && S.agn && !agst && S.r1) || (!S.autoM && !S.agn && !agree && S.r1 && S.hfEff);\n"
        "            // v12.0: rules 3 / 4 - enter at the close of this candle (rules 1 / 2 not used, a rule 4 setup may fall back to them;\n"
        "            // the higher-timeframe filters still apply, no agreement needed - like rule 1)\n"
        "            bool   ccOn  = S.ccMode != 0, ccR4 = S.ccMode == 2;\n"
        "            double ccSl  = IsNa(opl) ? NAD : (d == 1 ? opl - BufAt(opl) : opl + BufAt(opl));\n"
        "            double ccR   = IsNa(ccSl) ? NAD : d * (g_c - ccSl);\n"
        "            bool   ccFar  = ccR4 && !IsNa(ccR) && S.ccMax > 0 && ccR > LimAt(S.ccMax, g_c);\n"
        "            bool   ccNear = ccR4 && !IsNa(ccR) && S.ccMin > 0 && ccR < LimAt(S.ccMin, g_c);\n"
        "            bool   ccMkt  = ccOn && !ccFar && !ccNear;\n"
        "            bool   ccBack = ccOn && ccFar && !ccNear && S.ccFb;\n"
        "            bool   useM   = S.autoM ? (g_autoDir != 0 && d == g_autoDir) : (S.agn ? agst : (agree || !S.hfEff));\n"
        "            if (ccOn)\n"
        "            {\n"
        "               hfSkip = ccMkt ? !useM : (ccBack ? hfSkip : false);\n"
        "               use    = ccMkt ? useM : (ccBack ? use : false);\n"
        "               if (ccNear) cntCcNear++;\n"
        "               else if (ccFar && !ccBack) cntCcFar++;\n"
        "               else if (ccBack && use && !IsNa(opl)) cntCcFb++;\n"
        "            }\n"
        "            if (hfSkip) cntHf++;\n")
s = rep(s, "               rule    = (agree && S.r2 && !S.agn) ? 2 : 1;\n",
        "               rule    = (ccOn && ccMkt) ? 3 : ((agree && S.r2 && !S.agn) ? 2 : 1);\n"
        "               ccLim   = ccBack;\n"
        "               mktBar  = NAI;\n")
s = rep(s, '               Note(sg + ": " + Id() + (rule == 2 ? " R2" : " R1") + " ARMED");\n',
        '               Note(sg + ": " + Id() + (rule == 3 ? (string)(ccR4 ? " R4" : " R3") + " ARMED - entry at the close" : (string)(rule == 2 ? " R2" : " R1") + " ARMED") + (ccBack ? (string)" (rule 4 fell back: stop " + DoubleToString(ccR, 2) + " too far at the close)" : (string)""));\n')
s = rep(s, '            else if (!use) Note(sg + ": SKIP - " + (S.autoM ? "auto mode side / rule" : (S.agn ? "not against the higher timeframe" : (agree ? "no broken pivot" : "higher timeframe filter"))));\n',
        '            else if (ccOn && ccNear) Note(sg + ": SKIP - RULE 4: stop too close (" + DoubleToString(ccR, 2) + ")");\n'
        '            else if (ccOn && ccFar && !ccBack) Note(sg + ": SKIP - RULE 4: stop too far (" + DoubleToString(ccR, 2) + ")");\n'
        '            else if (!use) Note(sg + ": SKIP - " + (S.autoM ? "auto mode side / rule" : (S.agn ? "not against the higher timeframe" : (agree && !(ccOn && ccMkt) ? "no broken pivot" : "higher timeframe filter"))));\n')

# ---- the entry: the close for rule 3 / 4
s = rep(s, "         ent = (S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb));\n",
        "         ent = rule == 3 ? g_c : ((S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb)));\n")
s = rep(s, "         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;\n",
        "         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;\n"
        "         if (((rule == 3 && S.ccMode == 2) || ccLim) && !CcOk(r, ent)) dOk = false;   // v12.0: rule 4 limits\n")
s = rep(s, "               BkPlace(k, seq, 0, dir, ent, sl, tgt, q - q1);\n", "               BkPlace(k, seq, 0, dir, ent, sl, tgt, q - q1, rule == 3);\n")
s = rep(s, "                  BkPlace(k, seq, 1, dir, ent, sl, tp1, q1);\n", "                  BkPlace(k, seq, 1, dir, ent, sl, tp1, q1, rule == 3);\n")
s = rep(s, "               ordLive  = true;\n               lastCapQ = qCap;\n",
        "               ordLive  = true;\n"
        "               if (rule == 3 && mktBar == NAI) mktBar = EN.bi;\n"
        "               lastCapQ = qCap;\n")

# ---- adapter: the virtual order gets the market flag
s = rep(s, "   long   ticket;\n   int    fails;\n};\nVOrd     g_vb[4];", "   long   ticket;\n   int    fails;\n   bool   mkt;     // v12.0: a rule 3 / 4 entry - a market order at once\n};\nVOrd     g_vb[4];")
s = rep(s, "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q)\n{",
        "void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt)\n{")
s = rep(s, "   g_vb[i].lots = NormLots(q);\n", "   g_vb[i].lots = NormLots(q);\n   g_vb[i].mkt  = mkt;\n")
s = rep(s, "      if (g_vb[i].on && ((g_vb[i].dir == 1 && bid <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && bid >= NormUp(g_vb[i].ent)))) SendMarket(i);\n",
        "      if (g_vb[i].on && (g_vb[i].mkt || (g_vb[i].dir == 1 && bid <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && bid >= NormUp(g_vb[i].ent)))) SendMarket(i);\n")
old = "      int    dir = g_vb[i].dir;\n      double px  = dir == 1 ? NormDn(g_vb[i].ent) : NormUp(g_vb[i].ent);\n"
s = rep(s, old,
        "      if (g_vb[i].mkt)\n"
        "      {   // v12.0: a rule 3 / 4 entry is a market order at once (no pending order)\n"
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
        '      GvSet(GvSide(k, "mb"), g_side[k].mktBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].mktBar)); GvSet(GvSide(k, "cl"), g_side[k].ccLim ? 1 : 0);\n')
s = rep(s, '      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n',
        '      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n'
        '      double mb = GvGet(GvSide(k, "mb"), -1);\n'
        '      g_side[k].mktBar = mb < 0 ? NAI : BarOfTime((datetime)mb);   g_side[k].ccLim = GvGet(GvSide(k, "cl"), 0) > 0.5;\n')

# ---- adapter: settings, checks, table
s = rep(s, "   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n",
        "   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n"
        "   S.ccMode = (int)InCcMode; S.ccMax = InCcMax; S.ccMin = InCcMin; S.ccFb = InCcFar == CF_BACK;\n")
s = rep(s, '   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";\n',
        '   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";\n'
        '   if (InCcMax < 0 || InCcMin < 0 || (InCcMax > 0 && InCcMin > InCcMax)) return "Rule 4 limits (group 39): 0 or more, and the minimum not above the maximum";\n')
s = rep(s, "   if (what == 11) return g_side[k].cntCap;\n",
        "   if (what == 11) return g_side[k].cntCap;\n"
        "   if (what == 13) return g_side[k].cntR3;\n"
        "   if (what == 14) return g_side[k].cntCcFar;\n"
        "   if (what == 15) return g_side[k].cntCcNear;\n"
        "   if (what == 16) return g_side[k].cntCcFb;\n")
s = rep(s, '   Row("  - by ENTRY RULE 2 (broken pivot)", CntTxt(5), clrLime);\n',
        '   Row("  - by ENTRY RULE 2 (broken pivot)", CntTxt(5), clrLime);\n'
        '   if (S.ccMode != 0) Row("  - by ENTRY RULE 3 / 4 (signal close)", CntTxt(13), clrLime);\n')
s = rep(s, '   Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);\n   Row("Entries  |  magic",',
        '   Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);\n'
        '   Row("ENTRY AT THE SIGNAL CLOSE (group 39)", CcTxt(), S.ccMode != 0 ? clrAqua : clrGray);\n'
        '   Row("Entries  |  magic",')
old = "// v11.2: the stop buffer in use, in price\n"
s = rep(s, old,
        "// v12.0: entries at the close of the signal candle (group 39)\n"
        "string CcTxt()\n"
        "{\n"
        '   if (S.ccMode == 0) return "off - rules 1 / 2";\n'
        '   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");\n'
        '   string t = (S.ccMode == 2 ? "RULE 4 (" + (S.ccMin > 0 ? Num(S.ccMin) : "0") + " - " + (S.ccMax > 0 ? Num(S.ccMax) : "no max") + u + ")" : "RULE 3") + "  -  " + CntTxt(13) + " entered";\n'
        '   if (S.ccMode == 2) t = t + "  |  skipped: too far " + CntTxt(14) + " / too close " + CntTxt(15) + (S.ccFb ? "  |  fell back " + CntTxt(16) : "");\n'
        "   return t;\n"
        "}\n" + old)

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.0.mq5", "w").write(s)
print("EA v12.0 written:", len(s.split("\n")), "lines")
