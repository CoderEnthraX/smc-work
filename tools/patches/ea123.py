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
        '      g_side[k].Cancel("CANCELLED - the entry was reached while the EA was offline");\n'
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

assert all(ord(ch) < 128 for ch in s) and "\t" not in s
open(R + "SMC_Structure_EA_v12.3.mq5", "w").write(s)
print("EA v12.3 written:", len(s.split("\n")), "lines")
