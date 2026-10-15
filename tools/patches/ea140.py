# EA v14.0 = EA v13.1 + (all OFF by default, old behaviour unchanged):
#   section 1: a 4th unit choice 'Separate unit for each setting' - then the stop buffer (section 5), skip closer /
#     further (section 4, one unit for both), the rule 3 distance (section 3) and the spread for sizing (section 11) each
#     have their OWN unit (price / pips / %) and box, at the end of their section; the old boxes are not used then
#   section 4: the LEG SIZE filter - the leg = from the broken level (the pivot the signal candle closed beyond) to the
#     CHOCH* level; skip the setup if it is shorter / longer than (own unit, any section 1 unit)
#   section 4: the BIG SIGNAL CANDLE filter - skip the setup if the CHOCH / BOS candle (high - low) is bigger than
#     (own unit)
# usage: python3 ea140.py SMC_Structure_EA_v13.1.mq5 SMC_Structure_EA_v14.0.mq5
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


def box(t):
    return '//| ' + t.ljust(66) + ' |'


# ---- header (version on line 2)
rep('//| SMC Structure EA v13.1 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v13.1, same      |\n',
    '//| SMC Structure EA v14.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v14.0, same      |\n')
rep('//| Owner: Punit. Read SMC_Structure_v13.1_NOTES.txt (what is new).   |',
    box('Owner: Punit. v14.0: own unit per distance, leg size, big candle.'))
rep('#property version     "13.10"', '#property version     "14.00"')
rep('#property description "SMC Structure EA v13.1 - the TradingView strategy v13.1 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v14.0 - the TradingView strategy v14.0 rules in MetaTrader 5, plus a hedge mode."')

# ---- choice lists
rep('''   BU_PCT = 2         // % of price
};''', '''   BU_PCT = 2,        // % of price
   BU_SEP = 3         // Separate unit for each setting (its own unit + box, sections 3, 4, 5, 11)
};
enum EUnit            // v14.0: the unit of ONE distance (the % is of the price named in the setting)
{
   UN_PRICE = 0,      // Price
   UN_PIPS = 1,       // Pips (auto per market)
   UN_PCT = 2         // % of price
};''')

# ---- settings text
rep('''// unit). Every price DISTANCE below (stop buffer, skip closer / further, rule 3 distance, spread for sizing) is read in
// the unit chosen in section 1: price, pips, or % of price.
''', '''// unit). Every price DISTANCE below (stop buffer, skip closer / further, rule 3 distance, spread for sizing) is read in
// the unit chosen in section 1: price, pips, or % of price.
// v14.0: section 1 'Separate unit for each setting' = each of those distances has its OWN unit and box instead (at the
// END of sections 3, 4, 5 and 11; skip closer / further share one unit); the old boxes are then not used. The new leg
// size and big candle filters (end of section 4) always have their own unit.
''')

# ---- the new settings: at the END of sections 3, 4, 5, 11
rep('input int      InExpBars   = 0;       // Cancel an unfilled order after N bars (0 = never)\n',
    '''input int      InExpBars   = 0;       // Cancel an unfilled order after N bars (0 = never)
input EUnit    InR3U       = UN_PRICE; // RULE 3 near the broken level - unit (used when section 1 = Separate unit for each setting)
input double   InR3V       = 3.0;     //   - the most the close may be beyond the broken level (% = of the close)
''')
rep('input int      InEmHFast   = 50;      //   - FAST EMA length (2-EMA rule only)\n',
    '''input int      InEmHFast   = 50;      //   - FAST EMA length (2-EMA rule only)
input EUnit    InSkU       = UN_PRICE; // Skip closer / further - unit for both (used when section 1 = Separate unit for each setting)
input double   InSkMin     = 0.0;     //   - skip the setup if the stop is CLOSER than this (% = of the entry; 0 = off)
input double   InSkMax     = 0.0;     //   - skip the setup if the stop is FURTHER than this (% = of the entry; 0 = off)
input EUnit    InLzU       = UN_PRICE; // Leg size (from the broken level to the CHOCH* level) - unit (any section 1 unit)
input double   InLzMin     = 0.0;     //   - skip the setup if the leg is SHORTER than this (% = of the CHOCH* level; 0 = off)
input double   InLzMax     = 0.0;     //   - skip the setup if the leg is LONGER than this (0 = off)
input EUnit    InBcU       = UN_PRICE; // Big signal candle - unit (any section 1 unit)
input double   InBcMax     = 0.0;     //   - skip the setup if the CHOCH / BOS candle (high - low) is BIGGER than this (% = of its close; 0 = off)
''')
rep('input ETrMode  InTrMode    = TR_LEVEL; //   - the stop follows\n',
    '''input ETrMode  InTrMode    = TR_LEVEL; //   - the stop follows
input EUnit    InBfU       = UN_PRICE; // Stop buffer - unit (used when section 1 = Separate unit for each setting)
input double   InBfV       = 0.0;     //   - stop buffer beyond the CHOCH* level (% = of the CHOCH* level)
''')
rep('input double   InSprd      = 0.0;     // Broker spread for SIZING (unit: section 1; 0 = not modelled)\n',
    '''input double   InSprd      = 0.0;     // Broker spread for SIZING (unit: section 1; 0 = not modelled)
input EUnit    InSpdU      = UN_PRICE; // Spread for sizing - unit (used when section 1 = Separate unit for each setting)
input double   InSpdV      = 0.0;     //   - broker spread for SIZING (% = of the price; 0 = not modelled)
''')

# ---- core: the settings
rep('''   double rsLvl[2];
   // broker facts, set by the adapter''', '''   double rsLvl[2];
   int    uBf, uSk, uR3, uSp;          // v14.0: the unit (0 price, 1 pips, 2 %) of the stop buffer, skip closer / further, rule 3
                                       // distance and spread - all = buMode, or their own with section 1 'Separate unit' (buMode 3)
   int    lzU, bcU;                    // v14.0 section 4: leg size (broken level to the CHOCH* level), big signal candle - units
   double lzMin, lzMax, bcMax;         //   and limits (0 = off)
   // broker facts, set by the adapter''')
rep('''            mnPct = 0; tdAtr = 0; fstOn = false; ydOn = false; tdOn = false; legMin = 0;
''', '''            mnPct = 0; tdAtr = 0; fstOn = false; ydOn = false; tdOn = false; legMin = 0;
            uBf = 0; uSk = 0; uR3 = 0; uSp = 0; lzU = 0; bcU = 0; lzMin = 0; lzMax = 0; bcMax = 0;
''')
rep('''      seqPlus = seqMode >= 4 && seqMode <= 6;
   }''', '''      seqPlus = seqMode >= 4 && seqMode <= 6;
      if (buMode != 3) { uBf = buMode; uSk = buMode; uR3 = buMode; uSp = buMode; }   // v14.0: one unit for all (as before)
   }''')

# ---- core: the unit helpers
rep('''double BufAt(double lv)
{
   if (S.buMode == 1) return RoundTick(S.slBuf * S.pipSz);
   if (S.buMode == 2) return RoundTick(lv * S.slBuf / 100.0);
   return S.slBuf;
}
// v11.2: a section 4 limit (skip the setup if the stop is closer / further than) in price: pips, or % of the entry price
double LimAt(double v, double ent) { return S.buMode == 1 ? v * S.pipSz : (S.buMode == 2 ? ent * v / 100.0 : v); }
// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is
double SprdAt(double px) { return S.buMode == 1 ? S.sprd * S.pipSz : (S.buMode == 2 ? Mx(px, 0.0) * S.sprd / 100.0 : S.sprd); }''',
    '''// (v14.0: in the unit of the stop buffer - section 1, or its own with 'Separate unit for each setting')
double BufAt(double lv)
{
   if (S.uBf == 1) return RoundTick(S.slBuf * S.pipSz);
   if (S.uBf == 2) return RoundTick(lv * S.slBuf / 100.0);
   return S.slBuf;
}
// v11.2 / v14.0: a distance v in the unit u (0 price, 1 pips, 2 % of ref) in price - the skip closer / further limits (% of
// the entry), the rule 3 distance (% of the close), the leg size (% of the CHOCH* level), the big candle (% of its close)
double LimAt(int u, double v, double ref) { return u == 1 ? v * S.pipSz : (u == 2 ? ref * v / 100.0 : v); }
// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is
double SprdAt(double px) { return S.uSp == 1 ? S.sprd * S.pipSz : (S.uSp == 2 ? Mx(px, 0.0) * S.sprd / 100.0 : S.sprd); }
// v14.0: a price as text with the decimals of the price step (gold 0.01 -> 2, EURUSD 0.00001 -> 5)
string TkS(double v)
{
   int dg = 0;
   double t = S.tick;
   while (dg < 8 && t > 0 && MathAbs(t - MathRound(t)) > 1e-7) { t *= 10.0; dg++; }
   return DoubleToString(v, dg);
}''')
rep('bool   r3Far = S.r3On && S.r3BrkOn && (IsNa(r3B) || r3B > LimAt(S.r3Brk, g_c));',
    'bool   r3Far = S.r3On && S.r3BrkOn && (IsNa(r3B) || r3B > LimAt(S.uR3, S.r3Brk, g_c));')
rep('bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;',
    'bool dOk   = (S.minStop <= 0 || r >= LimAt(S.uSk, S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.uSk, S.maxStop, ent)) && lotOk;')

# ---- core: the leg size and big candle filters (XSkip, before the first setup of the day)
rep('   int    cntX[9];                    // v13.1: skipped by: 0 first of day, 1 yesterday, 2 move candles, 3 today, 4 / 5 RSI, 6 / 7 EMA, 8 min stop %',
    '   int    cntX[12];                   // v13.1: skipped by: 0 first of day, 1 yesterday, 2 move candles, 3 today, 4 / 5 RSI, 6 / 7 EMA, 8 min stop %\n'
    '                                      // v14.0: 9 leg shorter, 10 leg longer, 11 big signal candle')
rep('      for (int j = 0; j < 9; j++) cntX[j] = 0;', '      for (int j = 0; j < 12; j++) cntX[j] = 0;')
rep('''   // setup of the day is checked LAST, so a setup that another filter skips is never the day's first.
   string XSkip(int d)
   {''', '''   // setup of the day is checked LAST, so a setup that another filter skips is never the day's first.
   // v14.0: piv = the broken level (the pivot the signal candle closed beyond), opl = the CHOCH* level
   string XSkip(int d, double piv, double opl)
   {''')
rep('''      if (S.fstOn)
      {
         long dy = FloorDivL(SessLoc(g_t + S.cs), 86400);''', '''      // v14.0: the leg from the broken level to the CHOCH* level (not the candle's close); no broken level = not measured
      if ((S.lzMin > 0 || S.lzMax > 0) && !IsNa(piv))
      {
         double lg = d * (piv - opl);
         double a = LimAt(S.lzU, S.lzMin, opl), b = LimAt(S.lzU, S.lzMax, opl);
         if (S.lzMin > 0 && lg < a - S.tick / 2)
         {
            cntX[9]++;
            return "leg " + TkS(lg) + " (broken level " + TkS(piv) + " to the CHOCH* level " + TkS(opl) + ") shorter than " + TkS(a);
         }
         if (S.lzMax > 0 && lg > b + S.tick / 2)
         {
            cntX[10]++;
            return "leg " + TkS(lg) + " (broken level " + TkS(piv) + " to the CHOCH* level " + TkS(opl) + ") longer than " + TkS(b);
         }
      }
      // v14.0: the size of the signal candle itself (high - low)
      if (S.bcMax > 0)
      {
         double bc = LimAt(S.bcU, S.bcMax, g_c);
         if (g_h - g_l > bc + S.tick / 2)
         {
            cntX[11]++;
            return "big signal candle " + TkS(g_h - g_l) + " (most " + TkS(bc) + ")";
         }
      }
      if (S.fstOn)
      {
         long dy = FloorDivL(SessLoc(g_t + S.cs), 86400);''')
rep('            if (use && !IsNa(opl)) xs = XSkip(d);', '            if (use && !IsNa(opl)) xs = XSkip(d, piv, opl);')

# ---- adapter: the inputs into the core
rep('''   S.emOn[1] = InEmHOn; S.emTf[1] = TffSec(InEmHTf); S.emMode[1] = (int)InEmHMode; S.emLen[1] = InEmHLen; S.emFast[1] = InEmHFast;
''', '''   S.emOn[1] = InEmHOn; S.emTf[1] = TffSec(InEmHTf); S.emMode[1] = (int)InEmHMode; S.emLen[1] = InEmHLen; S.emFast[1] = InEmHFast;
   // v14.0: section 1 'Separate unit for each setting' - each distance its own unit and box (end of sections 3, 4, 5, 11);
   // otherwise Derive() gives all four the section 1 unit and the old boxes stay as they are
   if (InBuMode == BU_SEP)
   {
      S.uBf = (int)InBfU; S.slBuf = InBfV; S.uSk = (int)InSkU; S.minStop = InSkMin; S.maxStop = InSkMax;
      S.uR3 = (int)InR3U; S.r3Brk = InR3V; S.uSp = (int)InSpdU; S.sprd = InSpdV;
   }
   S.lzU = (int)InLzU; S.lzMin = InLzMin; S.lzMax = InLzMax; S.bcU = (int)InBcU; S.bcMax = InBcMax;   // v14.0 section 4
''')
rep('''   if ((InEmLOn && InEmLMode == EM_CROSS && InEmLFast >= InEmLLen) || (InEmHOn && InEmHMode == EM_CROSS && InEmHFast >= InEmHLen)) return "EMA filter (section 4): the FAST EMA length must be smaller than the slow one";
''', '''   if ((InEmLOn && InEmLMode == EM_CROSS && InEmLFast >= InEmLLen) || (InEmHOn && InEmHMode == EM_CROSS && InEmHFast >= InEmHLen)) return "EMA filter (section 4): the FAST EMA length must be smaller than the slow one";
   // v14.0
   if (InBfV < 0 || InSkMin < 0 || InSkMax < 0 || InR3V < 0 || InSpdV < 0) return "The separate unit boxes (sections 3, 4, 5, 11) cannot be negative";
   if (InBuMode == BU_SEP && ((InBfU == UN_PCT && InBfV > 10) || (InSpdU == UN_PCT && InSpdV > 10))) return "Stop buffer (section 5) or spread (section 11) in % of price: at most 10";
   if (InLzMin < 0 || InLzMax < 0 || InBcMax < 0) return "Leg size / big signal candle (section 4) cannot be negative";
   if (InLzMin > 0 && InLzMax > 0 && InLzMax < InLzMin) return "Leg size (section 4): 'LONGER than' must be bigger than 'SHORTER than'";
''')

# ---- table
rep('   if (what >= 20 && what <= 28) return g_side[k].cntX[what - 20];   // v13.1',
    '   if (what >= 20 && what <= 31) return g_side[k].cntX[what - 20];   // v13.1 / v14.0')
rep('''// v12.0: rule 3 - entries at the close of the signal candle (section 3)
string R3Txt()
{
   if (!S.r3On) return "off - rules 1 / 2";
   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");''', '''// v14.0: the unit of one distance as text
string UnitTxt(int u) { return u == 1 ? " pips" : (u == 2 ? " %" : ""); }
// v12.0: rule 3 - entries at the close of the signal candle (section 3)
string R3Txt()
{
   if (!S.r3On) return "off - rules 1 / 2";
   string u = UnitTxt(S.uR3);''')
rep('''// v11.2 / v13.0: the unit (section 1), the stop buffer (section 5), the skip limits (section 4) and the spread, in price
string BufTxt()
{
   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");
   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID);
   string t = S.buMode == 1 ? Num(S.slBuf) + " pips x " + Num(S.pipSz) + " = " + Px(BufAt(0)) :
              (S.buMode == 2 ? Num(S.slBuf) + "% of the level = " + Px(BufAt(bid)) + " now" : "price " + Num(S.slBuf));
   if (S.sprd > 0) t = t + "  |  spread for sizing " + Px(SprdAt(bid));
   if (S.minStop > 0 || S.maxStop > 0)
      t = t + "  |  skip closer " + (S.minStop > 0 ? Num(S.minStop) + u : "off") + " / further " + (S.maxStop > 0 ? Num(S.maxStop) + u : "off");
   return t;
}''', '''// v11.2 / v13.0: the unit (section 1), the stop buffer (section 5), the skip limits (section 4) and the spread, in price
string BufTxt()
{
   string u = UnitTxt(S.uSk);
   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID);
   string t = S.uBf == 1 ? Num(S.slBuf) + " pips x " + Num(S.pipSz) + " = " + Px(BufAt(0)) :
              (S.uBf == 2 ? Num(S.slBuf) + "% of the level = " + Px(BufAt(bid)) + " now" : "price " + Num(S.slBuf));
   if (S.buMode == 3) t = "separate units  |  buffer " + t;   // v14.0
   if (S.sprd > 0) t = t + "  |  spread for sizing " + Px(SprdAt(bid));
   if (S.minStop > 0 || S.maxStop > 0)
      t = t + "  |  skip closer " + (S.minStop > 0 ? Num(S.minStop) + u : "off") + " / further " + (S.maxStop > 0 ? Num(S.maxStop) + u : "off");
   return t;
}''')
rep('''   if (S.mnPct > 0) t = t + ", stop < " + Num(S.mnPct) + "% " + CntTxt(28);
   return t == "" ? "off" : StringSubstr(t, 2);''', '''   if (S.mnPct > 0) t = t + ", stop < " + Num(S.mnPct) + "% " + CntTxt(28);
   if (S.lzMin > 0) t = t + ", leg < " + Num(S.lzMin) + UnitTxt(S.lzU) + " " + CntTxt(29);   // v14.0
   if (S.lzMax > 0) t = t + ", leg > " + Num(S.lzMax) + UnitTxt(S.lzU) + " " + CntTxt(30);
   if (S.bcMax > 0) t = t + ", candle > " + Num(S.bcMax) + UnitTxt(S.bcU) + " " + CntTxt(31);
   return t == "" ? "off" : StringSubstr(t, 2);''')
rep('bool XAny() { return S.fstOn || S.ydOn || S.legMin > 0 || S.tdOn || S.rsOn[0] || S.rsOn[1] || S.emOn[0] || S.emOn[1] || S.mnPct > 0; }',
    'bool XAny() { return S.fstOn || S.ydOn || S.legMin > 0 || S.tdOn || S.rsOn[0] || S.rsOn[1] || S.emOn[0] || S.emOn[1] || S.mnPct > 0 ||\n'
    '                     S.lzMin > 0 || S.lzMax > 0 || S.bcMax > 0; }')
rep('Row("  - skipped: section 4 filters (v13.1)", XTxt(), XAny() ? clrOrange : clrGray);',
    'Row("  - skipped: section 4 filters (v13.1 / v14.0)", XTxt(), XAny() ? clrOrange : clrGray);')

# ---- MT5 part: never a second entry for the same setup (bug found by the v14.0 restart test - old, since v11.1)
# After a restart or a settings change (both reload the EA) INSIDE a candle, the setup comes back from the state saved at the
# last candle close; in touch mode its entry may already have been filled in this candle (the core sees a fill only at the
# candle close), so the touch sent the same entry again. On a 15m chart that window is up to 15 minutes.
rep('''void SendMarket(int i)
{
   int    dir = g_vb[i].dir;
''', '''// v14.0: did this setup (order comment cmt) already get a fill at or after 'since' - an open position, or an IN deal?
bool FilledSince(string cmt, datetime since)
{
   if (since <= 0) since = TimeCurrent() - PeriodSeconds(g_tf);
   for (int p = PositionsTotal() - 1; p >= 0; p--)
   {
      ulong tk = PositionGetTicket(p);
      if (tk == 0) continue;
      if (PositionGetString(POSITION_SYMBOL) == g_sym && PositionGetInteger(POSITION_MAGIC) == InMagic && PositionGetString(POSITION_COMMENT) == cmt &&
          (datetime)PositionGetInteger(POSITION_TIME) >= since) return true;
   }
   if (!HistorySelect(since, TimeCurrent() + 86400)) return false;
   for (int d = HistoryDealsTotal() - 1; d >= 0; d--)
   {
      ulong dk = HistoryDealGetTicket(d);
      if (dk == 0 || !OurDeal(dk)) continue;
      if (HistoryDealGetInteger(dk, DEAL_ENTRY) == DEAL_ENTRY_IN && HistoryDealGetString(dk, DEAL_COMMENT) == cmt) return true;
   }
   return false;
}
void SendMarket(int i)
{
   int    dir = g_vb[i].dir;
   // v14.0: never a second entry for the same setup. (1) Only while the core still has this setup waiting - after a restart the
   // order kept here comes back from the saved state, and the core may since have seen it filled (it then ends the setup).
   // (2) After a restart or a settings change inside a candle the setup comes back from the state saved at the last candle
   // close, but its entry may already have been filled in this candle (the core sees that fill only at the close).
   int sk = i / 2;
   if (g_side[sk].dir == 0 || g_side[sk].seq != g_vb[i].seq) { g_vb[i].on = false; return; }
   if (FilledSince(CmtOf(dir, g_vb[i].seq, i % 2), g_curOpen))
   {
      Log("Entry " + TradeId(dir, g_vb[i].seq, i % 2) + " not sent again: it was already filled in this candle (the EA was reloaded)");
      g_vb[i].on = false;
      return;
   }
''')
rep('   Print("SMC EA v12.3 ready: ", n,', '   Print("SMC EA v14.0 ready: ", n,')

assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)
