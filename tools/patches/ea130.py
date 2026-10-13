# EA v13.0 = EA v12.3 + the settings in 13 sections (same names; ea130_inputs.txt) + ONE stop buffer box read in the
# section 1 unit (InBuPips / InBuPct gone) + the spread for sizing read in that unit too + hedge + shared money option
# 'a trade opened while the other side chases the loss risks only the base' (InHgBase, OFF) + faster drawing (the table
# sends a property to the chart only when it changes; lines / texts set their fixed look once, at creation) + every
# 'group N' in the messages and the table -> 'section N'.
# usage: python3 ea130.py SMC_Structure_EA_v12.3.mq5 SMC_Structure_EA_v13.0.mq5
import sys, os, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
HERE = os.path.dirname(os.path.abspath(__file__))


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


# ---- header (version on line 2)
rep('//| SMC Structure EA v12.3 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v12.2, same      |\n',
    '//| SMC Structure EA v13.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v13.0, same      |\n')
rep('//| Owner: Punit. Read SMC_Structure_EA_v12.0_NOTES.txt first.          |',
    '//| Owner: Punit. Read SMC_Structure_v13.0_NOTES.txt (settings map).  |')
rep('#property version     "12.30"', '#property version     "13.00"')
rep('#property description "SMC Structure EA v12.3 - the TradingView strategy v12.2 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v13.0 - the TradingView strategy v13.0 rules in MetaTrader 5, plus a hedge mode."')

# ---- choice lists
for x in 'ABC':
    rep('// Rule %s split (%s, the base grows with the profit - group 43)' % (x, x), '// Rule %s split (%s, the base grows with the profit - section 7)' % (x, x))
rep('BU_PRICE = 0,      // Price (as now)', 'BU_PRICE = 0,      // Price')

# ---- the settings block
a = s.index('//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.2)')
e = s.index('\n', s.index('input int      InAudMax'))
old_names = set(re.findall(r'^input\s+\w+\s+(\w+)\s*=', s[a:e], re.M))
blk = open(os.path.join(HERE, 'ea130_inputs.txt')).read().rstrip('\n')
new_names = set(re.findall(r'^input\s+\w+\s+(\w+)\s*=', blk, re.M))
if old_names - new_names != {'InBuPips', 'InBuPct'} or new_names - old_names != {'InHgBase'}:
    raise SystemExit('input names: gone %s, new %s' % (old_names - new_names, new_names - old_names))
s = s[:a] + blk + s[e:]

# ---- core: settings structure
rep('   double buPips, buPct, pipSz;\n', '   double pipSz;\n')
rep('   int    dirMode, hedgeMoney;\n',
    '   int    dirMode, hedgeMoney;\n'
    '   bool   hgBase;              // v13.0: hedge + shared money - a trade opened while the other side chases the loss risks the base\n')
rep('buMode = 0; buPips = 0; buPct = 0; pipSz = 0;', 'buMode = 0; pipSz = 0; hgBase = false;')

# ---- core: the stop buffer and the spread in the section 1 unit
rep('// v11.2: the stop buffer beyond the level lv, in price (pips x pip, or % of the level, rounded to the price step; else the group 20 buffer)\n',
    '// v11.2 / v13.0: the stop buffer beyond the level lv, in price - the ONE stop buffer box (slBuf, section 5) read in the\n'
    '// section 1 unit: pips x pip, or % of the level (both rounded to the price step), or the price as it is\n')
rep('   if (S.buMode == 1) return RoundTick(S.buPips * S.pipSz);\n   if (S.buMode == 2) return RoundTick(lv * S.buPct / 100.0);\n',
    '   if (S.buMode == 1) return RoundTick(S.slBuf * S.pipSz);\n   if (S.buMode == 2) return RoundTick(lv * S.slBuf / 100.0);\n')
rep('// v11.2: a group 24 limit (skip the setup if the stop is closer / further than) in price: pips, or % of the entry price\n'
    'double LimAt(double v, double ent) { return S.buMode == 1 ? v * S.pipSz : (S.buMode == 2 ? ent * v / 100.0 : v); }\n',
    '// v11.2: a section 4 limit (skip the setup if the stop is closer / further than) in price: pips, or % of the entry price\n'
    'double LimAt(double v, double ent) { return S.buMode == 1 ? v * S.pipSz : (S.buMode == 2 ? ent * v / 100.0 : v); }\n'
    '// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is\n'
    'double SprdAt(double px) { return S.buMode == 1 ? S.sprd * S.pipSz : (S.buMode == 2 ? Mx(px, 0.0) * S.sprd / 100.0 : S.sprd); }\n')
rep('   return c + (S.sprd > 0 ? S.sprd * S.uv : 0.0);', '   return c + (S.sprd > 0 ? SprdAt(ent) * S.uv : 0.0);')

# ---- core: one side - who chases the carried loss (hedge + shared money)
rep('   bool   ordLive, lastCapQ, placed, ppSent;\n',
    '   bool   ordLive, lastCapQ, placed, ppSent;\n'
    '   bool   chaseOrd, chasePos, hbSeen;   // v13.0: the waiting order / an open trade was sized to win back the carried loss\n')
rep('   int    cntR3, cntR3Far, cntR3Fb;   // v12.0\n',
    '   int    cntR3, cntR3Far, cntR3Fb;   // v12.0\n'
    '   int    cntHgB;                     // v13.0: setups sized at the base because the other side was chasing the loss\n')
rep('      ordLive = false; lastCapQ = false; placed = false; ppSent = false;\n',
    '      ordLive = false; lastCapQ = false; placed = false; ppSent = false;\n'
    '      chaseOrd = false; chasePos = false; hbSeen = false;\n')
rep('      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0;\n', '      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0; cntHgB = 0;\n')
rep('   void   Cancel(string why) { Note(why); CancelSent(); cntCanc++; dir = 0; }\n',
    '   void   Cancel(string why) { Note(why); CancelSent(); cntCanc++; dir = 0; }\n'
    '   bool   Chasing()          { return (ordLive && chaseOrd) || chasePos; }   // v13.0: this side is winning back the carried loss\n')
rep('      if (g_io[k].nFill == 0) return;\n      openSl  = IsNa(lastSl) ? sl : lastSl;\n',
    '      if (g_io[k].nFill == 0) return;\n'
    '      if (chaseOrd) chasePos = true;   // v13.0: the order that chased the carried loss is now an open trade\n'
    '      openSl  = IsNa(lastSl) ? sl : lastSl;\n')
rep('               seq++;\n               ppSent  = false;\n',
    '               seq++;\n               ppSent  = false;\n               hbSeen  = false;\n')
rep('         Qty(ent, r, g_money[mi].riskNow * addRk, pos, q, qCap);\n',
    '         // v13.0 (section 3): hedge + shared money - while the OTHER side chases the carried loss (its waiting order or an\n'
    '         // open trade was sized for it), this side risks only the base; the first side to chase keeps it\n'
    '         double rk = g_money[mi].riskNow;\n'
    '         bool   hb = S.hgBase && S.dirMode == 3 && S.hedgeMoney == 1 && S.seqMode != 0 && S.flMode != 1 && SideChasing(1 - k) &&\n'
    '                     rk > g_money[mi].basNow + 0.005;\n'
    '         if (hb) rk = g_money[mi].basNow;\n'
    '         Qty(ent, r, rk * addRk, pos, q, qCap);\n')
rep('            placed  = true;\n            entLock = ent;\n',
    '            placed  = true;\n'
    '            chaseOrd = !hb && g_money[mi].riskNow > g_money[mi].basNow + 0.005;   // v13.0\n'
    '            if (hb && !hbSeen) { hbSeen = true; cntHgB++; Note(Id() + " at the BASE risk - the other side is chasing the loss"); }\n'
    '            entLock = ent;\n')
rep('// ---------- one strategy side: Both / Longs only / Shorts only, or one half of the hedge ----------\n',
    'bool SideChasing(int k);   // v13.0: is side k winning back the carried loss? (defined after the sides)\n'
    '// ---------- one strategy side: Both / Longs only / Shorts only, or one half of the hedge ----------\n')
rep('CSide g_side[2];\n', 'CSide g_side[2];\nbool SideChasing(int k) { return g_side[k].Chasing(); }\n')
rep('   if (!g_dry)\n      for (int k = 0; k < g_nSides; k++) g_side[k].Decide();\n',
    '   if (!g_dry)\n'
    '      for (int k = 0; k < g_nSides; k++) if (g_io[k].nPos == 0) g_side[k].chasePos = false;   // v13.0: no open trade - none chases\n'
    '   if (!g_dry)\n      for (int k = 0; k < g_nSides; k++) g_side[k].Decide();\n')

# ---- restarts: the 'who chases the loss' flags are saved with the waiting setup (and the open-trade flag always)
rep('      GvSet(GvSide(k, "pt"), g_side[k].planTgt);\n',
    '      GvSet(GvSide(k, "pt"), g_side[k].planTgt);\n'
    '      GvSet(GvSide(k, "co"), g_side[k].chaseOrd ? 1 : 0); GvSet(GvSide(k, "cp"), g_side[k].chasePos ? 1 : 0); GvSet(GvSide(k, "hs"), g_side[k].hbSeen ? 1 : 0);   // v13.0\n')
rep('      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n',
    '      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);\n'
    '      g_side[k].chaseOrd = GvGet(GvSide(k, "co"), 0) > 0.5; g_side[k].chasePos = GvGet(GvSide(k, "cp"), 0) > 0.5;   // v13.0\n'
    '      g_side[k].hbSeen = GvGet(GvSide(k, "hs"), 0) > 0.5;\n')
rep('      if (!g_tester) for (int k = 0; k < g_nSides; k++) g_side[k].seq = (int)GvGet(GvSide(k, "seq"), 0);\n',
    '      if (!g_tester)\n'
    '         for (int k = 0; k < g_nSides; k++)\n'
    '         {\n'
    '            g_side[k].seq = (int)GvGet(GvSide(k, "seq"), 0);\n'
    '            g_side[k].chasePos = GvGet(GvSide(k, "cp"), 0) > 0.5;   // v13.0: an open trade that chases the loss still does\n'
    '         }\n')

# ---- settings from the inputs
rep('S.dirMode = (int)InDirMode; S.hedgeMoney = (int)InHedgeMoney;', 'S.dirMode = (int)InDirMode; S.hedgeMoney = (int)InHedgeMoney; S.hgBase = InHgBase;')
rep('   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n',
    '   S.buMode = (int)InBuMode; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();\n')
rep('   if (InSlBuf < 0) return "Stop buffer cannot be negative";\n',
    '   if (InSlBuf < 0 || (InBuMode == BU_PCT && InSlBuf > 10)) return "Stop buffer (section 5): 0 or more; in % of price at most 10";\n')
rep('InSprd < 0) return "Commission / spread values cannot be negative";\n',
    'InSprd < 0) return "Commission / spread values (section 11) cannot be negative";\n'
    '   if (InBuMode == BU_PCT && InSprd > 10) return "Spread for sizing (section 11): in % of price at most 10";\n')
rep('return "Safety values out of range";', 'return "Skip closer / further (section 4), expiry bars (section 3) or daily limits / drawdown (section 8) out of range";')
rep('return "A group 34 value is out of range";', 'return "Stacked BOS risk, liquidity target, partial profit, premium / discount or losses in a row: a value is out of range";')
rep('   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";\n',
    '   if (InBuPip < 0) return "Pip size (section 1) must be 0 or more";\n')
rep('"Rule 3 (group 39): ', '"Rule 3 (section 3): ')
rep('"Loss mark (group 42): ', '"Loss mark (section 7): ')
rep('"Audit labels (group 44): ', '"Audit labels (section 13): ')
rep('"Profit steps (group 43): ', '"Profit steps (section 7): ')

# ---- bugs found in the review (v12.3 and older): settings that were not checked
rep('   if (StringLen(InCmt) < 1 || StringLen(InCmt) > 16 || StringFind(InCmt, " ") >= 0) return "Order comment: 1 - 16 characters, no spaces";\n',
    '   if (StringLen(InCmt) < 1 || StringLen(InCmt) > 16 || StringFind(InCmt, " ") >= 0) return "Order comment: 1 - 16 characters, no spaces";\n'
    '   // v13.0: a window time that cannot be read was ignored without a word (the window never blocked anything)\n'
    '   if (InNw1On && !WinOk(InNw1)) return "Window 1 time (section 10) must look like 1725-1835 (HHMM-HHMM, 00:00 - 23:59, start and end different)";\n'
    '   if (InNw2On && !WinOk(InNw2)) return "Window 2 time (section 10) must look like 1725-1835 (HHMM-HHMM, 00:00 - 23:59, start and end different)";\n'
    '   if (InNw3On && !WinOk(InNw3)) return "Window 3 time (section 10) must look like 1725-1835 (HHMM-HHMM, 00:00 - 23:59, start and end different)";\n'
    '   // v13.0: a negative slippage became an unlimited one (it is sent to the broker as an unsigned number)\n'
    '   if (InSlip < 0 || InSlip > 100000) return "Max slippage (section 12) must be 0 - 100000 points";\n'
    '   if (InMagic < 0) return "Magic number (section 12) must be 0 or more";\n'
    '   if (InResume < 0 || InDrawMax < 0 || InHtfMarks < 0) return "Restart bars (section 12) and marks to keep (section 13) must be 0 or more";\n')
rep('// group 28: "3, 12-14 28" -> day-of-month flags\n',
    '// v13.0: a window time "HHMM-HHMM" that can be read: 9 characters, hours 00 - 23, minutes 00 - 59, start and end different\n'
    'bool WinOk(string s)\n'
    '{\n'
    '   if (StringLen(s) != 9 || StringGetCharacter(s, 4) != \'-\') return false;\n'
    '   int a = Hm(s, 0), b = Hm(s, 5);\n'
    '   if (a < 0 || b < 0 || a == b) return false;\n'
    '   return StringToInteger(StringSubstr(s, 0, 2)) <= 23 && StringToInteger(StringSubstr(s, 2, 2)) <= 59 && StringToInteger(StringSubstr(s, 5, 2)) <= 23 && StringToInteger(StringSubstr(s, 7, 2)) <= 59;\n'
    '}\n'
    '// group 28: "3, 12-14 28" -> day-of-month flags\n')

# ---- messages
rep('"broker clock rule (group 40)"', '"broker clock rule (section 12)"', 3)
rep('"ON but no news list on (group 41 calendar / group 29)"', '"ON but no news list on (calendar / automatic US news, section 10)"')
rep("Check 'Broker server time' in group 40 - session hours depend on it.", "Check 'Broker server time' in section 12 - session hours depend on it.")
rep('(group 41 calendar or group 29 automatic US news) - it does nothing', '(calendar or automatic US news, section 10) - it does nothing')
rep('Hedge mode, partial profit (34 e) and BOS signals need a HEDGING account', 'Hedge mode, partial profit (section 5) and BOS signals need a HEDGING account')
rep('   if (InPreOn && !(InCalOn || InAuOn)) Print(',
    '   if (InHgBase && !(InDirMode == DIR_HEDGE && InHedgeMoney == HM_SHARED)) Print("SMC EA: \'risks only the base\' (section 3) works only in Hedge mode with shared money - it does nothing now");\n'
    '   if (InPreOn && !(InCalOn || InAuOn)) Print(')

# ---- the table
rep('Row("SMC STRATEGY  (EA v12.3)", "value", clrWhite);', 'Row("SMC STRATEGY  (EA v13.0)", "value", clrWhite);')
rep('"ACCOUNT FLOOR (group 35)"', '"ACCOUNT FLOOR (section 8)"', 2)
rep('"PAUSE AFTER LOSSES (group 36)"', '"PAUSE AFTER LOSSES (section 8)"', 2)
rep('"HTF EQUILIBRIUM FIRST (group 37)"', '"HTF EQUILIBRIUM FIRST (section 4)"', 2)
rep('Row("Stop buffer (group 38)", BufTxt(), clrAqua);', 'Row("Unit + stop buffer (sections 1, 5)", BufTxt(), clrAqua);')
rep('Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);', 'Row("UNIT + STOP BUFFER (sections 1, 5)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);')
rep('"RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)"', '"RULE 3 - ENTRY AT THE SIGNAL CLOSE (section 3)"')
rep('"LOSS MARK - BACK TO THE BASE (group 42)"', '"LOSS MARK - BACK TO THE BASE (section 7)"')
rep('"PROFIT STEPS - A / B / C split (group 43)"', '"PROFIT STEPS - A / B / C split (section 7)"')
rep('"Calendar news (group 41) - next"', '"Calendar news (section 10) - next"')
rep('Row("Trade direction (group 33)", dm, S.dirMode == 0 ? clrGray : clrAqua);',
    'if (S.dirMode == 3 && S.hedgeMoney == 1 && S.hgBase) dm = dm + "  |  2nd trade at the base: " + CntTxt(16);\n'
    '   Row("Trade direction (section 3)", dm, S.dirMode == 0 ? clrGray : clrAqua);')
rep('Row("v9.0 ideas switched ON (group 34)", IdeasTxt(), IdeasTxt() == "none" ? clrGray : clrAqua);',
    'Row("Extra options switched ON", IdeasTxt(), IdeasTxt() == "none" ? clrGray : clrAqua);')
rep('   string t = (string)(S.bkOn ? "a " : "") + (S.hfOn ? "b " : "") + (S.trOn ? "c " : "") + (S.lqOn ? "d " : "") + (S.ppOn ? "e " : "") + (S.pdOn ? "f " : "") + (S.lsOn ? "g " : "");\n'
    '   return t == "" ? "none" : t;\n',
    '   string t = (string)(S.bkOn ? ", stacked BOS risk" : "") + (S.hfOn ? ", HTF filter" : "") + (S.trOn ? ", trailing stop" : "") + (S.lqOn ? ", liquidity target" : "") +\n'
    '              (S.ppOn ? ", partial profit" : "") + (S.pdOn ? ", premium / discount" : "") + (S.lsOn ? ", day pause" : "");\n'
    '   return t == "" ? "none" : StringSubstr(t, 2);\n')
rep('   if (what == 15) return g_side[k].cntR3Fb;\n', '   if (what == 15) return g_side[k].cntR3Fb;\n   if (what == 16) return g_side[k].cntHgB;\n')
rep('// v12.0: rule 3 - entries at the close of the signal candle (group 39)', '// v12.0: rule 3 - entries at the close of the signal candle (section 3)')
rep('// v11.2: the stop buffer in use, in price\n'
    'string BufTxt()\n'
    '{\n'
    '   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");\n'
    '   string t = S.buMode == 1 ? Num(S.buPips) + " pips x " + Num(S.pipSz) + " = " + Px(BufAt(0)) :\n'
    '              (S.buMode == 2 ? Num(S.buPct) + "% of the level = " + Px(BufAt(SymbolInfoDouble(g_sym, SYMBOL_BID))) + " now" : "price " + Num(S.slBuf));\n',
    '// v11.2 / v13.0: the unit (section 1), the stop buffer (section 5), the skip limits (section 4) and the spread, in price\n'
    'string BufTxt()\n'
    '{\n'
    '   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");\n'
    '   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID);\n'
    '   string t = S.buMode == 1 ? Num(S.slBuf) + " pips x " + Num(S.pipSz) + " = " + Px(BufAt(0)) :\n'
    '              (S.buMode == 2 ? Num(S.slBuf) + "% of the level = " + Px(BufAt(bid)) + " now" : "price " + Num(S.slBuf));\n'
    '   if (S.sprd > 0) t = t + "  |  spread for sizing " + Px(SprdAt(bid));\n')

# ---- faster drawing: lines / texts set their fixed look once (each name always keeps the same look)
rep('      ObjectCreate(0, nm, OBJ_TREND, 0, t1, p, t2, p);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_BACK, true);\n'
    '   }\n'
    '   else\n'
    '   {\n'
    '      ObjectMove(0, nm, 0, t1, p);\n'
    '      ObjectMove(0, nm, 1, t2, p);\n'
    '   }\n'
    '   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_STYLE, style);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_WIDTH, width);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, ray);\n',
    '      ObjectCreate(0, nm, OBJ_TREND, 0, t1, p, t2, p);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_BACK, true);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_STYLE, style);   // v13.0: the fixed look is set once\n'
    '      ObjectSetInteger(0, nm, OBJPROP_WIDTH, width);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, ray);\n'
    '   }\n'
    '   else\n'
    '   {\n'
    '      ObjectMove(0, nm, 0, t1, p);\n'
    '      ObjectMove(0, nm, 1, t2, p);\n'
    '   }\n'
    '   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);\n')
rep('      ObjectCreate(0, nm, OBJ_TEXT, 0, t, p);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);\n'
    '   }\n'
    '   else ObjectMove(0, nm, 0, t, p);\n'
    '   ObjectSetString(0, nm, OBJPROP_TEXT, txt);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 8);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anchor);\n',
    '      ObjectCreate(0, nm, OBJ_TEXT, 0, t, p);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);\n'
    '      ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 8);   // v13.0: the fixed look is set once\n'
    '      ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anchor);\n'
    '   }\n'
    '   else ObjectMove(0, nm, 0, t, p);\n'
    '   ObjectSetString(0, nm, OBJPROP_TEXT, txt);\n'
    '   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);\n')

# ---- faster table: every cell remembers what it shows; a property goes to the chart only when it changes
a = s.index('void TblLabel(string nm, int x, int y, string txt, color c, int fs, int anchor)')
b = s.index('void TblDelete()')
s = s[:a] + '''// v13.0: every table object remembers what it shows - a property is sent to the chart only when it changes
// (slot = the object's place: 0 / 1 the two boxes, 2 + 2 x row the left cell, 3 + 2 x row the right cell)
struct TblMem { int x, y, w, h, anchor, fs; color c, c2; string txt; bool ok; };
TblMem g_tm[];
void TblForget() { for (int i = 0; i < ArraySize(g_tm); i++) g_tm[i].ok = false; }
bool TblSlot(int slot, string nm)
{
   if (slot >= ArraySize(g_tm))
   {
      int n0 = ArraySize(g_tm);
      ArrayResize(g_tm, slot + 32);
      for (int i = n0; i < ArraySize(g_tm); i++) g_tm[i].ok = false;
   }
   if (ObjectFind(0, nm) < 0) g_tm[slot].ok = false;   // new, or deleted by hand: everything is sent again
   return g_tm[slot].ok;
}
void TblLabel(int slot, string nm, int x, int y, string txt, color c, int fs, int anchor)
{
   bool ok = TblSlot(slot, nm);
   if (!ok && ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);
      ObjectSetString(0, nm, OBJPROP_FONT, "Consolas");
   }
   if (!ok || g_tm[slot].x != x) ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x);
   if (!ok || g_tm[slot].y != y) ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   if (!ok || g_tm[slot].anchor != anchor) ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anchor);
   if (!ok || g_tm[slot].fs != fs) ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, fs);
   if (!ok || g_tm[slot].c != c) ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   if (!ok || g_tm[slot].txt != txt) ObjectSetString(0, nm, OBJPROP_TEXT, txt);
   g_tm[slot].x = x; g_tm[slot].y = y; g_tm[slot].anchor = anchor; g_tm[slot].fs = fs; g_tm[slot].c = c; g_tm[slot].txt = txt; g_tm[slot].ok = true;
}
void TblBox(int slot, string nm, int x, int y, int w, int h, color bg, color border)
{
   bool ok = TblSlot(slot, nm);
   if (!ok && ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);
      ObjectSetInteger(0, nm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   }
   if (!ok || g_tm[slot].x != x) ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x);
   if (!ok || g_tm[slot].y != y) ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   if (!ok || g_tm[slot].w != w) ObjectSetInteger(0, nm, OBJPROP_XSIZE, w);
   if (!ok || g_tm[slot].h != h) ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   if (!ok || g_tm[slot].c != bg) ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg);
   if (!ok || g_tm[slot].c2 != border) ObjectSetInteger(0, nm, OBJPROP_COLOR, border);
   g_tm[slot].x = x; g_tm[slot].y = y; g_tm[slot].w = w; g_tm[slot].h = h; g_tm[slot].c = bg; g_tm[slot].c2 = border; g_tm[slot].ok = true;
}
''' + s[b:]
rep('   for (int i = 0; i < g_tblShown; i++) { ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i)); }\n   g_tblShown = 0;\n',
    '   for (int i = 0; i < g_tblShown; i++) { ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i)); }\n   g_tblShown = 0;\n   TblForget();\n')
rep('   TblBox(g_P + "tb", x0, y0, W, H, C\'16,18,26\', C\'80,80,90\');\n   TblBox(g_P + "th", ',
    '   TblBox(0, g_P + "tb", x0, y0, W, H, C\'16,18,26\', C\'80,80,90\');\n   TblBox(1, g_P + "th", ')
rep('      TblLabel(g_P + "tl" + I2(i), ', '      TblLabel(2 + 2 * i, g_P + "tl" + I2(i), ')
rep('      TblLabel(g_P + "tv" + I2(i), ', '      TblLabel(3 + 2 * i, g_P + "tv" + I2(i), ')
rep('   for (int i = g_rN; i < g_tblShown; i++) { ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i)); }\n',
    '   for (int i = g_rN; i < g_tblShown; i++)\n'
    '   {\n'
    '      ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i));\n'
    '      if (3 + 2 * i < ArraySize(g_tm)) { g_tm[2 + 2 * i].ok = false; g_tm[3 + 2 * i].ok = false; }\n'
    '   }\n')

for ch in s:
    if ord(ch) > 126 or (ord(ch) < 32 and ch not in '\n\t'): raise SystemExit('not ASCII: %r' % ch)
open(dst, 'w').write(s)
print('written', dst, len(s.split('\n')), 'lines')
