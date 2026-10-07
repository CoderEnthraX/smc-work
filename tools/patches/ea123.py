# MT5 EA v12.2 -> v12.3: safe catch-up after a gap (the computer slept, the connection dropped, or a restart a few
#   candles ago). Up to v12.2 every missed candle was handled as if it were live: entries for old candles were sent at
#   today's price, and a trade opened during the catch-up was invisible to the next missed candles, so a buy and a sell
#   could open together. Now (always on, no setting):
#   - the missed candles are read WITHOUT opening trades;
#   - a waiting entry whose price was reached in a missed candle (or earlier in the candle forming now) is dropped -
#     TradingView would have filled it then, the EA cannot copy that, so there is no late entry; a rule 3 market entry of
#     a missed candle is dropped the same way; a real broker fill (pending mode) is kept;
#   - exits (force close, news, weekend) and stop moves the core asked for are done at once, after the catch-up;
#   - live: after a gap it waits (up to a minute) while MT5 downloads the missed candles;
#   - an old slip fixed: after a restart that kept a waiting setup, the setup number was not read back (went back to 0).
# Also (asked after the first v12.3): 'Signal audit' ON drew nothing on the chart (the EA only wrote the journal) - now the
#   audit labels are drawn like TradingView's (group 44 at the very END: label size, how many to keep).
#   The EA core (//==CORE-BEGIN== .. //==CORE-END==) is unchanged - only the MT5 part.
R = "/home/user/smc-work/"
s = open(R + "SMC_Structure_EA_v12.2.mq5").read()
assert "CatchUp" not in s and "DropReached" not in s


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:160])
    return s.replace(old, new)


# ---- version strings
s = rep(s, "//| SMC Structure EA v12.2 (+ hedge) - MetaTrader 5 Expert Advisor     |", "//| SMC Structure EA v12.3 (+ hedge) - MetaTrader 5 Expert Advisor     |")
s = rep(s, '//| The TradingView strategy "SMC Structure Strategy" v12.2, same      |', '//| The TradingView strategy "SMC Structure Strategy" v12.2, same      |')
s = rep(s, '#property version     "12.20"', '#property version     "12.30"')
s = rep(s, '#property description "SMC Structure EA v12.2 - the TradingView strategy v12.2 rules in MetaTrader 5, plus a hedge mode."',
        '#property description "SMC Structure EA v12.3 - the TradingView strategy v12.2 rules in MetaTrader 5, plus a hedge mode."')
s = rep(s, '   Print("SMC EA v12.2 ready: ", n,', '   Print("SMC EA v12.3 ready: ", n,')
s = rep(s, '   Row("SMC STRATEGY  (EA v12.2)", "value", clrWhite);', '   Row("SMC STRATEGY  (EA v12.3)", "value", clrWhite);')

# ---- prototypes (the catch-up comes before ProcessBar and SaveState in the file)
s = rep(s, "void ExecuteAll();\nbool TryInit();\n", "void ExecuteAll();\nbool TryInit();\nvoid ProcessBar(MqlRates &r, bool dry, datetime tEnd);\nvoid SaveState(datetime barTime);\n")

# ---- the catch-up (MT5 part, after ExecuteAll)
old = "void DeleteOurPending()\n"
s = rep(s, old,
        "// v12.3: after a gap - the computer slept, the connection dropped, or the EA was off for a few candles - the missed\n"
        "// candles are read WITHOUT opening trades. A waiting entry whose price was reached while the EA was offline is dropped:\n"
        "// TradingView would have filled it then, the EA cannot copy that, so there is no late entry at another price. A market\n"
        "// entry (rule 3) of a missed candle is dropped the same way. A real fill by the broker (pending mode) is kept.\n"
        "bool FilledReal(int dir, int seq, int piece)\n"
        "{\n"
        "   string cmt = CmtOf(dir, seq, piece);\n"
        "   if (PosWithComment(cmt)) return true;\n"
        "   if (!HistorySelect(TimeCurrent() - 10 * 86400, TimeCurrent() + 86400)) return false;\n"
        "   for (int i = HistoryDealsTotal() - 1; i >= 0; i--)\n"
        "   {\n"
        "      ulong dk = HistoryDealGetTicket(i);\n"
        "      if (dk == 0 || !OurDeal(dk)) continue;\n"
        "      if (HistoryDealGetInteger(dk, DEAL_ENTRY) == DEAL_ENTRY_IN && HistoryDealGetString(dk, DEAL_COMMENT) == cmt) return true;\n"
        "   }\n"
        "   return false;\n"
        "}\n"
        "int DropReached(double hi, double lo, datetime when)\n"
        "{\n"
        "   int d = 0;\n"
        "   for (int k = 0; k < g_nSides; k++)\n"
        "   {\n"
        "      if (g_side[k].dir == 0) continue;\n"
        "      bool hit = false, hitMkt = false;\n"
        "      double hitPx = 0;\n"
        "      for (int p = 0; p < 2; p++)\n"
        "      {\n"
        "         int i = k * 2 + p;\n"
        "         if (!g_vb[i].on || g_vb[i].seq != g_side[k].seq) continue;\n"
        "         bool reached = g_vb[i].mkt || (g_vb[i].dir == 1 && lo <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && hi >= NormUp(g_vb[i].ent));\n"
        "         if (reached && !FilledReal(g_vb[i].dir, g_vb[i].seq, p)) { hit = true; hitMkt = g_vb[i].mkt; hitPx = g_vb[i].ent; }\n"
        "      }\n"
        "      if (!hit) continue;\n"
        '      Print("SMC EA: setup ", TradeId(g_side[k].dir, g_side[k].seq, 0), " dropped - its entry ", hitMkt ? "(market, rule 3)" : DoubleToString(hitPx, g_digits),\n'
        '            " was reached while the EA was offline (candle ", TimeToString(when), "), no late entry");\n'
        "      g_audT = when;   // the candle where it was reached (for the audit)\n"
        '      g_side[k].Cancel("CANCELLED - entry reached while the EA was offline");\n'
        "      d++;\n"
        "   }\n"
        "   return d;\n"
        "}\n"
        "void CatchUp(MqlRates &rr[], int i0, int n, datetime t0, bool live)\n"
        "{\n"
        "   int m = 0, d = 0;\n"
        "   g_dealFlag = true;   // the broker may have filled or closed trades meanwhile - read the deals\n"
        "   for (int i = i0; i < n; i++)\n"
        "   {\n"
        "      if (live && (rr[i].time <= g_lastBar || rr[i].time >= t0)) continue;\n"
        "      d += DropReached(rr[i].high, rr[i].low, rr[i].time);   // the orders that were waiting during this candle\n"
        "      ProcessBar(rr[i], false, i + 1 < n ? rr[i + 1].time : t0);\n"
        "      if (live) { g_lastBar = rr[i].time; SaveState(g_lastBar); }\n"
        "      m++;\n"
        "   }\n"
        "   if (m == 0) return;\n"
        "   // the candle forming now: the part of it before this tick was offline too (nothing to check at its very first price)\n"
        "   double fh = iHigh(g_sym, g_tf, 0), fl = iLow(g_sym, g_tf, 0);\n"
        "   if (TimeCurrent() > t0 || fh > fl) d += DropReached(fh, fl, t0);\n"
        "   ExecuteAll();   // exits and stop moves the core asked for, and the setups that are still waiting\n"
        "   if (live) SaveState(g_lastBar);   // the orders just sent\n"
        '   Print("SMC EA: ", m, " candle(s) missed (computer asleep, no connection or a restart) - read without opening trades", d > 0 ? ", " + IntegerToString(d) + " waiting entry(ies) dropped" : "");\n'
        "}\n" + old)

# ---- a gap while the EA runs (sleep / no connection): wait (up to a minute) while MT5 downloads the missed candles
s = rep(s, """   if (t0 > g_curOpen)
   {
      CalTick();
      MqlRates rr[];
      int n = CopyRates(g_sym, g_tf, g_lastBar + 1, t0 - 1, rr);
""", """   if (t0 > g_curOpen)
   {
      // v12.3: after a gap (sleep / no connection) MT5 may still be downloading the missed candles - wait for them (up to a minute)
      if (!g_tester && t0 - g_lastBar > 2 * PeriodSeconds(g_tf) && !SeriesInfoInteger(g_sym, g_tf, SERIES_SYNCHRONIZED) && TimeCurrent() - t0 < 60) return;
      CalTick();
      MqlRates rr[];
      int n = CopyRates(g_sym, g_tf, g_lastBar + 1, t0 - 1, rr);
""")

# ---- a gap while the EA runs (sleep / no connection)
s = rep(s, """      if (n < 0) return;   // history not ready yet - try on the next tick
      for (int i = 0; i < n; i++)
      {
         if (rr[i].time <= g_lastBar || rr[i].time >= t0) continue;
         ProcessBar(rr[i], false, i + 1 < n ? rr[i + 1].time : t0);
         g_lastBar = rr[i].time;
         ExecuteAll();
         SaveState(g_lastBar);
      }
""", """      if (n < 0) return;   // history not ready yet - try on the next tick
      int miss = 0;
      for (int i = 0; i < n; i++) if (rr[i].time > g_lastBar && rr[i].time < t0) miss++;
      if (miss >= 2) CatchUp(rr, 0, n, t0, true);   // v12.3: a gap - the missed candles are read without opening trades
      else
         for (int i = 0; i < n; i++)
         {
            if (rr[i].time <= g_lastBar || rr[i].time >= t0) continue;
            ProcessBar(rr[i], false, i + 1 < n ? rr[i + 1].time : t0);
            g_lastBar = rr[i].time;
            ExecuteAll();
            SaveState(g_lastBar);
         }
""")

# ---- an old slip found by the v12.3 checks: after a restart that kept a waiting setup, the setup number (L12, S7 ...) was
#      not read back (only when no setup was kept), so it went back to 0 and new trades got numbers used before the restart
s = rep(s, """      g_side[k].dir = (int)GvGet(GvSide(k, "dir"), 0);      g_side[k].rule = (int)GvGet(GvSide(k, "rule"), 0);
""", """      g_side[k].dir = (int)GvGet(GvSide(k, "dir"), 0);      g_side[k].rule = (int)GvGet(GvSide(k, "rule"), 0);
      g_side[k].seq = (int)GvGet(GvSide(k, "seq"), 0);      // v12.3: the setup number goes on (it went back to 0 before)
""")

# ---- a restart a few candles ago (the waiting setup kept by 'After a restart, keep a waiting setup ...')
s = rep(s, """   for (int i = lastDry + 1; i < n; i++)
   {
      ProcessBar(rr[i], false, i + 1 < n ? rr[i + 1].time : t0);
      ExecuteAll();
   }
""", """   CatchUp(rr, lastDry + 1, n, t0, false);   // v12.3: the candles missed while the EA was off - read without opening trades
""")

# ---- signal audit LABELS on the chart (the user turned 'Signal audit' ON and saw no labels: up to v12.2 the EA only wrote
#      the audit to the Experts journal). Now, like TradingView: a label at every traded-on CHOCH / BOS, under the candle for
#      a buy signal, over it for a sell signal, coloured by what happened (blue armed, green filled, orange cancelled /
#      skipped, grey SKIP, red refused); hover = every step with its time. Display only - it changes no trade. MT5 shows at
#      most 63 characters of an object's text, so a long story is shortened on the chart and is complete in the tooltip.
s = rep(s, "input bool     InAudit     = false;   // Signal audit - write what happened to every signal in the Experts journal\n",
        "input bool     InAudit     = false;   // Signal audit - a label on the chart for every signal (what happened to it) + the Experts journal\n")
old = """enum ETblRows
"""
s = rep(s, old, """enum EAudSz
{
   AS_SMALL = 0,      // Small
   AS_NORMAL = 1,     // Normal
   AS_LARGE = 2,      // Large
   AS_HUGE = 3        // Huge
};
""" + old)
old = "input double   InSpAdd     = 1.0;     //   - each new step is split into this many more parts\n"
s = rep(s, old, old +
        'input group "44. Signal audit labels on the chart (v12.3)"\n'
        "input EAudSz   InAudSz     = AS_LARGE; // Audit label size (the labels show when 'Signal audit' in group 20 is ON)\n"
        "input int      InAudMax    = 200;     //   - how many audit labels to keep on the chart (0 = none, the journal only)\n")
old = 'string          g_P = "";           // prefix of this EA\'s global variables and chart objects\n'
s = rep(s, old, old +
        'string          g_AP = "";          // v12.3: prefix of the signal audit labels (they stay when the EA restarts)\n'
        "string          g_audCur[2];        // v12.3: the audit label of each side's setup (armed, waiting or filled)\n"
        "int             g_audSeq[2];        // v12.3: its setup number\n"
        "datetime        g_audT = 0;         // v12.3: the candle being read, its high and low (where a signal's label goes)\n"
        "double          g_audH = 0, g_audL = 0;\n")
old = "void BkNote(int side, string msg)\n{\n   g_note[side] = msg;\n   if (InAudit && !g_dry) Print("
s = rep(s, old, """// v12.3: the signal audit labels on the chart (group 20 'Signal audit' + group 44)
string AudTm(datetime t) { return TimeToString(t, TIME_DATE | TIME_MINUTES); }
int    AudSize()        { return InAudSz == AS_SMALL ? 7 : (InAudSz == AS_NORMAL ? 9 : (InAudSz == AS_HUGE ? 14 : 11)); }
bool   AudOn()          { return InAudit && InAudMax > 0 && !g_dry && (!g_tester || g_visual); }
color  AudCol(string st)   // readable on a dark and on a light chart
{
   long bg = ChartGetInteger(0, CHART_COLOR_BACKGROUND);
   bool dark = (bg & 0xFF) * 299 + ((bg >> 8) & 0xFF) * 587 + ((bg >> 16) & 0xFF) * 114 < 128000;
   if (StringFind(st, "REFUSED") >= 0) return dark ? clrTomato : clrRed;
   if (StringFind(st, "FILLED") >= 0) return dark ? clrLime : clrGreen;
   if (StringFind(st, "CANCELLED") >= 0 || StringFind(st, "SKIPPED") >= 0) return dark ? clrOrange : clrDarkOrange;
   if (StringFind(st, "ARMED") >= 0) return dark ? clrDodgerBlue : clrMediumBlue;
   return dark ? clrSilver : clrDimGray;   // SKIP
}
// the tooltip holds the whole story: line 1 = the signal and the higher timeframe, then one line per step (time, 2 spaces, what)
// the chart text (63 characters at most in MT5): signal | step > step > ..., shortened when too long
void AudShow(string nm, string tip)
{
   string ln[];
   int n = StringSplit(tip, '\\n', ln);
   if (n < 2) return;
   string sg = ln[0], chain = "", last = "";
   int h = StringFind(ln[0], "  HTF");
   if (h > 0) sg = StringSubstr(ln[0], 0, h);
   for (int i = 1; i < n; i++)
   {
      int q = StringFind(ln[i], "  ");
      last = q >= 0 ? StringSubstr(ln[i], q + 2) : ln[i];
      chain = chain + (i > 1 ? " > " : "") + last;
   }
   string v = ln[0] + " | " + chain;
   if (StringLen(v) > 63) v = sg + " | " + chain;
   if (StringLen(v) > 63) v = sg + " | " + last;
   if (StringLen(v) > 63) v = StringSubstr(v, 0, 60) + "...";
   ObjectSetString(0, nm, OBJPROP_TEXT, v);
   ObjectSetString(0, nm, OBJPROP_TOOLTIP, tip);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, AudCol(last));
}
// keep the newest InAudMax labels (the name ends with the candle time)
void AudTrim()
{
   int n = ObjectsTotal(0, 0, OBJ_TEXT), k = 0, L = StringLen(g_AP);
   long tt[];
   ArrayResize(tt, n);
   for (int i = 0; i < n; i++)
   {
      string nm = ObjectName(0, i, 0, OBJ_TEXT);
      if (StringFind(nm, g_AP) == 0) { tt[k] = StringToInteger(StringSubstr(nm, L + 2)); k++; }
   }
   if (k <= InAudMax) return;
   ArrayResize(tt, k);
   ArraySort(tt);
   long cut = tt[k - InAudMax];
   for (int i = n - 1; i >= 0; i--)
   {
      string nm = ObjectName(0, i, 0, OBJ_TEXT);
      if (StringFind(nm, g_AP) == 0 && StringToInteger(StringSubstr(nm, L + 2)) < cut) ObjectDelete(0, nm);
   }
}
// a signal: "CHOCH up: L12 R1 ARMED" or "BOS dn: SKIP - outside session hours" - a new label at the signal candle
void AudNew(int side, string msg)
{
   int p = StringFind(msg, ": ");
   if (p < 0) return;
   string sg = StringSubstr(msg, 0, p), st = StringSubstr(msg, p + 2);
   bool up = StringFind(sg, " up") >= 0;
   if (S.dirMode == 3 && (side == 0) != up) return;   // hedge: the long side labels the buy signals, the short side the sell signals
   string nm = g_AP + IntegerToString(side) + "_" + IntegerToString((long)g_audT);
   double px = up ? g_audL : g_audH;
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_TEXT, 0, g_audT, px);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
   }
   else ObjectMove(0, nm, 0, g_audT, px);
   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, up ? ANCHOR_LEFT_UPPER : ANCHOR_LEFT_LOWER);
   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, AudSize());
   ObjectSetString(0, nm, OBJPROP_FONT, "Arial Bold");
   AudShow(nm, sg + "  HTF " + (!g_htfUse ? "off" : (g_T15 == 1 ? "up" : (g_T15 == -1 ? "dn" : "-"))) + "\\n" + AudTm(g_audT) + "  " + st);
   if (StringFind(st, "ARMED") >= 0) { g_audCur[side] = nm; g_audSeq[side] = g_side[side].seq; }
   AudTrim();
}
// what happened next to the side's setup: FILLED, CANCELLED - ..., REFUSED ...
void AudEnd(int side, string st, datetime t)
{
   string nm = g_audCur[side];
   if (nm == "" || ObjectFind(0, nm) < 0) return;
   AudShow(nm, ObjectGetString(0, nm, OBJPROP_TOOLTIP) + "\\n" + AudTm(t) + "  " + st);
}
// the broker side (book entry i): only for the setup the label belongs to
void AudRef(int i, string st) { if (AudOn() && g_vb[i].seq == g_audSeq[i / 2]) AudEnd(i / 2, st, TimeCurrent()); }
""" + old)
old = """, TimeToString(UtcToSrv(g_t), TIME_DATE | TIME_MINUTES), " ", msg);
}
"""
s = rep(s, old, """, TimeToString(g_audT, TIME_DATE | TIME_MINUTES), " ", msg);
   if (!AudOn()) return;
   if (StringFind(msg, "CHOCH ") == 0 || StringFind(msg, "BOS ") == 0) AudNew(side, msg);
   else AudEnd(side, msg, g_audT);
}
""")
# the candle being read (for the label's place)
s = rep(s, """   g_dry = dry;
   PushBarTime(r.time);
""", """   g_dry = dry;
   g_audT = r.time; g_audH = r.high; g_audL = r.low;   // v12.3: where a signal's audit label goes
   PushBarTime(r.time);
""")
# the broker refused / skipped an entry
s = rep(s, """      Log("Entry " + id + " skipped: the price is already past its stop or target (TradingView would open and close it at once)");
      g_vb[i].on = false;
""", """      Log("Entry " + id + " skipped: the price is already past its stop or target (TradingView would open and close it at once)");
      AudRef(i, "SKIPPED - the price was already past the stop or target");
      g_vb[i].on = false;
""")
s = rep(s, """   Log("Entry " + id + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription());
""", """   Log("Entry " + id + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription());
   AudRef(i, "REFUSED BY THE BROKER - " + g_trade.ResultRetcodeDescription());
""")
s = rep(s, """         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker 5 times - setup dropped"); g_refused++; g_vb[i].on = false; continue; }
""", """         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker 5 times - setup dropped"); AudRef(i, "REFUSED BY THE BROKER (5 times)"); g_refused++; g_vb[i].on = false; continue; }
""")
s = rep(s, """         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription()); g_refused++; g_vb[i].on = false; }
""", """         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription()); AudRef(i, "REFUSED BY THE BROKER - " + g_trade.ResultRetcodeDescription()); g_refused++; g_vb[i].on = false; }
""")
# after a restart that kept a waiting setup: its label goes on
old = """      double mb = GvGet(GvSide(k, "mb"), -1);
      g_side[k].mktBar = mb < 0 ? NAI : BarOfTime((datetime)mb);
"""
s = rep(s, old, old + """      // v12.3: the audit label of the kept setup (named by its signal candle) goes on
      if (g_side[k].dir != 0 && g_side[k].armBar != NAI) { g_audCur[k] = g_AP + IntegerToString(k) + "_" + IntegerToString((long)TimeOfBar(g_side[k].armBar)); g_audSeq[k] = g_side[k].seq; }
""")
# start: the label prefix; the labels are removed with the EA (or when the audit is off), kept over a restart
old = """   g_P = "SMC" + IntegerToString(InMagic) + "_" + g_sym + "_";
"""
s = rep(s, old, old + """   g_AP = "SMCA" + IntegerToString(InMagic) + "_" + g_sym + "_";   // v12.3: the audit labels
   for (int k = 0; k < 2; k++) { g_audCur[k] = ""; g_audSeq[k] = 0; }
   if (!InAudit || InAudMax <= 0) ObjectsDeleteAll(0, g_AP);
""")
s = rep(s, """   ObjectsDeleteAll(0, g_P);
   Comment("");
""", """   ObjectsDeleteAll(0, g_P);
   if (reason == REASON_REMOVE || reason == REASON_ACCOUNT || reason == REASON_CHARTCHANGE) ObjectsDeleteAll(0, g_AP);   // v12.3: the audit labels
   Comment("");
""")
s = rep(s, '   if (InSp1 < 0 || InSp2 < 0', '   if (InAudMax < 0) return "Audit labels (group 44): how many to keep must be 0 or more";\n   if (InSp1 < 0 || InSp2 < 0')

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.3.mq5", "w").write(s)
print("EA v12.3 written:", len(s.split("\n")), "lines")
