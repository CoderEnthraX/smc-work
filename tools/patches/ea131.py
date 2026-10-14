# EA v13.1 = EA v13.0 + new setup filters at the END of section 4 (all OFF by default):
#   minimum stop as % of the price (any unit), skip the first setup of the day, yesterday's high / low, the CHOCH / BOS move
#   must take at least N candles, only with today's move (x the average daily range of the last 14 days), an RSI filter and
#   an EMA filter for a LOWER and for a HIGHER timeframe (each: timeframe, length(s), rule).
# usage: python3 ea131.py SMC_Structure_EA_v13.0.mq5 SMC_Structure_EA_v13.1.mq5
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


# ---- header (version on line 2)
rep('//| SMC Structure EA v13.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v13.0, same      |\n',
    '//| SMC Structure EA v13.1 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v13.1, same      |\n')
rep('//| Owner: Punit. Read SMC_Structure_v13.0_NOTES.txt (settings map).  |',
    '//| Owner: Punit. Read SMC_Structure_v13.1_NOTES.txt (what is new).   |')
rep('#property version     "13.00"', '#property version     "13.10"')
rep('#property description "SMC Structure EA v13.0 - the TradingView strategy v13.0 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v13.1 - the TradingView strategy v13.1 rules in MetaTrader 5, plus a hedge mode."')

# ---- choice lists
rep('''enum ECalToday
{
   CT_OFF = 0,        // Off
   CT_HIGH = 1,       // High impact
   CT_HIGHMED = 2     // High and medium impact
};
''', '''enum ECalToday
{
   CT_OFF = 0,        // Off
   CT_HIGH = 1,       // High impact
   CT_HIGHMED = 2     // High and medium impact
};
enum ETfF             // v13.1: the timeframe of an RSI / EMA filter (section 4); not above the chart = the chart's own candles
{
   TFF_M1 = 0,        // 1 minute
   TFF_M5 = 1,        // 5 minutes
   TFF_M15 = 2,       // 15 minutes
   TFF_H1 = 3,        // 1 hour
   TFF_H4 = 4,        // 4 hours
   TFF_D1 = 5,        // 1 day
   TFF_W1 = 6,        // 1 week
   TFF_MN1 = 7        // 1 month
};
enum ERsMode
{
   RS_PULL = 0,       // Pullback: buy when RSI is BELOW the level, sell when ABOVE 100 minus it
   RS_MOM = 1         // Momentum: buy when RSI is ABOVE the level, sell when BELOW 100 minus it
};
enum EEmMode
{
   EM_PRICE = 0,      // Price above the EMA for buys, below it for sells
   EM_CROSS = 1       // Fast EMA above the slow EMA for buys, below it for sells
};
''')

# ---- the new settings: at the END of section 4
rep('input double   InEqPct     = 50.0;    //   - the equilibrium, % pullback of the higher timeframe leg\n',
    '''input double   InEqPct     = 50.0;    //   - the equilibrium, % pullback of the higher timeframe leg
input double   InMnPct     = 0.0;     // Skip the setup if the stop is closer than this % of the price (any unit; 0 = off)
input bool     InFstOn     = false;   // Skip the first setup of the day (the day of the session timezone, section 9)
input bool     InYdOn      = false;   // No buy below yesterday's low, no sell above yesterday's high (the day ends 17:00 New York)
input int      InLegMin    = 0;       // Skip a CHOCH / BOS whose move took fewer than this many candles (0 = off)
input bool     InTdOn      = false;   // Trade only with today's move (buy above today's open, sell below it)
input double   InTdAtr     = 0.15;    //   - by at least this many x the average daily range of the last 14 days (0 = just past the open)
input bool     InRsLOn     = false;   // RSI filter - LOWER timeframe
input ETfF     InRsLTf     = TFF_M1;  //   - timeframe (not above the chart = the chart's own candles)
input int      InRsLLen    = 14;      //   - RSI length
input ERsMode  InRsLMode   = RS_PULL; //   - rule
input double   InRsLLvl    = 50.0;    //   - level (the buy side; the sell side uses 100 minus it)
input bool     InRsHOn     = false;   // RSI filter - HIGHER timeframe
input ETfF     InRsHTf     = TFF_H1;  //   - timeframe
input int      InRsHLen    = 2;       //   - RSI length
input ERsMode  InRsHMode   = RS_PULL; //   - rule
input double   InRsHLvl    = 50.0;    //   - level (the buy side; the sell side uses 100 minus it)
input bool     InEmLOn     = false;   // EMA filter - LOWER timeframe
input ETfF     InEmLTf     = TFF_M1;  //   - timeframe (not above the chart = the chart's own candles)
input EEmMode  InEmLMode   = EM_PRICE; //   - rule
input int      InEmLLen    = 200;     //   - EMA length (the SLOW one for the 2-EMA rule), e.g. 9, 20, 50, 100, 200
input int      InEmLFast   = 50;      //   - FAST EMA length (2-EMA rule only)
input bool     InEmHOn     = false;   // EMA filter - HIGHER timeframe
input ETfF     InEmHTf     = TFF_H1;  //   - timeframe
input EEmMode  InEmHMode   = EM_PRICE; //   - rule
input int      InEmHLen    = 200;     //   - EMA length (the SLOW one for the 2-EMA rule), e.g. 9, 20, 50, 100, 200
input int      InEmHFast   = 50;      //   - FAST EMA length (2-EMA rule only)
''')

# ---- core: settings structure
rep('   double r3Brk;\n   // broker facts, set by the adapter\n',
    '''   double r3Brk;
   double mnPct, tdAtr;                // v13.1 section 4: min stop % of the entry price; today's move x the average daily range
   bool   fstOn, ydOn, tdOn;           // v13.1: first setup of the day, yesterday's high / low, only with today's move
   int    legMin;                      // v13.1: the CHOCH / BOS move must take at least this many candles (0 = off)
   bool   rsOn[2], emOn[2];            // v13.1: RSI / EMA filters - [0] the LOWER, [1] the HIGHER timeframe one
   int    rsTf[2], rsLen[2], rsMode[2], emTf[2], emLen[2], emFast[2], emMode[2];   // timeframes in seconds (0 = the chart)
   double rsLvl[2];
   // broker facts, set by the adapter
''')
rep('spInc = 0; spAdd = 0; }\n',
    'spInc = 0; spAdd = 0;\n'
    '            mnPct = 0; tdAtr = 0; fstOn = false; ydOn = false; tdOn = false; legMin = 0;\n'
    '            for (int j = 0; j < 2; j++) { rsOn[j] = false; emOn[j] = false; rsTf[j] = 0; rsLen[j] = 14; rsMode[j] = 0; rsLvl[j] = 50; emTf[j] = 0; emLen[j] = 200; emFast[j] = 50; emMode[j] = 0; } }\n')

# ---- core: the trading day, the RSI / EMA filters (after the higher-timeframe engine)
rep('CHtf HT;\n', r'''CHtf HT;

// ---------- v13.1 (section 4): the New York trading day and the RSI / EMA filters ----------
// The day of a bar = the New York trading day of its OPEN: a new day starts at 17:00 New York (02:30 IST in US summer time,
// 03:30 IST in winter) - the gold daily close. Today's open / high / low, yesterday's high / low, and the average range
// (high - low) of the last 14 complete days.
long   g_dyKey = LNONE;
double g_dyO = NAD, g_dyH = NAD, g_dyL = NAD, g_ydH = NAD, g_ydL = NAD, g_dyAvg = 0;
double g_dyRng[14];
int    g_dyN = 0, g_dyI = 0;
long   DayNy(long t) { return FloorDivL(NyLoc(t) - 61200, 86400); }
void   DayReset()
{
   g_dyKey = LNONE; g_dyO = NAD; g_dyH = NAD; g_dyL = NAD; g_ydH = NAD; g_ydL = NAD; g_dyAvg = 0; g_dyN = 0; g_dyI = 0;
   for (int i = 0; i < 14; i++) g_dyRng[i] = 0;
}
void DayStep(long t, double o, double h, double l)
{
   long k = DayNy(t);
   if (k != g_dyKey)
   {
      if (g_dyKey != LNONE)
      {
         g_ydH = g_dyH; g_ydL = g_dyL;
         g_dyRng[g_dyI] = g_dyH - g_dyL;
         g_dyI = (g_dyI + 1) % 14;
         if (g_dyN < 14) g_dyN++;
         if (g_dyN >= 14) { double sm = 0; for (int j = 0; j < 14; j++) sm += g_dyRng[(g_dyI + j) % 14]; g_dyAvg = sm / 14.0; }   // oldest first
      }
      g_dyKey = k; g_dyO = o; g_dyH = h; g_dyL = l;
   }
   else { g_dyH = Mx(g_dyH, h); g_dyL = Mn(g_dyL, l); }
}
// one RSI or EMA on CLOSED candles of its timeframe. RSI = TradingView's ta.rsi (Wilder averages started with a simple
// average of the first 'len' changes); EMA starts at the first close. kind 1 RSI, 2 EMA (len2 > 0 = a second, fast EMA).
class CInd
{
public:
   int    kind, len, len2, tf, n;     // tf = seconds of its candles (0 = the chart's own candles)
   double prev, su, sd, au, ad, e1, e2, val, val2;
   bool   ok;
   CInd() { kind = 0; len = 14; len2 = 0; tf = 0; Reset(); }
   void Reset() { n = 0; prev = NAD; su = 0; sd = 0; au = NAD; ad = NAD; e1 = NAD; e2 = NAD; val = NAD; val2 = NAD; ok = false; }
   void Step(double c)
   {
      n++;
      if (kind == 1)
      {
         if (IsNa(prev)) { prev = c; return; }
         double u = Mx(c - prev, 0.0), d = Mx(prev - c, 0.0);
         prev = c;
         if (IsNa(au))
         {
            su += u; sd += d;
            if (n - 1 >= len) { au = su / len; ad = sd / len; }
         }
         else { au = (au * (len - 1) + u) / len; ad = (ad * (len - 1) + d) / len; }
         if (!IsNa(au)) { val = ad == 0 ? 100.0 : (au == 0 ? 0.0 : 100.0 - 100.0 / (1.0 + au / ad)); ok = true; }
      }
      else if (kind == 2)
      {
         e1 = IsNa(e1) ? c : e1 + 2.0 / (len + 1) * (c - e1);
         val = e1;
         if (len2 > 0) { e2 = IsNa(e2) ? c : e2 + 2.0 / (len2 + 1) * (c - e2); val2 = e2; }
         ok = true;
      }
   }
};
CInd g_ind[4];   // 0 RSI lower, 1 RSI higher, 2 EMA lower, 3 EMA higher timeframe
bool IndOn(int i)  { return i < 2 ? S.rsOn[i] : S.emOn[i - 2]; }
// on candles of a higher timeframe (fed by the MT5 part / the test, the candles that closed before the one holding the bar)
bool IndHtf(int i) { return IndOn(i) && g_ind[i].tf > 0; }
void IndCandle(int i, double c) { g_ind[i].Step(c); }
string TfTxt(int sec)
{
   if (sec <= 0) return "chart";
   if (sec < 3600) return IntegerToString(sec / 60) + "m";
   if (sec < 86400) return IntegerToString(sec / 3600) + "h";
   if (sec < 604800) return "1D";
   if (sec < 2592000) return "1W";
   return "1M";
}
''')

# ---- core: the side - first setup of the day + the counters of the new filters + the checks
rep('   int    cntHgB;                     // v13.0: setups sized at the base because the other side was chasing the loss\n',
    '   int    cntHgB;                     // v13.0: setups sized at the base because the other side was chasing the loss\n'
    '   long   fstDay;                     // v13.1: the day (session timezone) whose first setup was already skipped\n'
    '   int    cntX[9];                    // v13.1: skipped by: 0 first of day, 1 yesterday, 2 move candles, 3 today, 4 / 5 RSI, 6 / 7 EMA, 8 min stop %\n')
rep('      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0; cntHgB = 0;\n',
    '      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0; cntHgB = 0;\n'
    '      fstDay = LNONE;\n'
    '      for (int j = 0; j < 9; j++) cntX[j] = 0;\n')
rep('   bool   Chasing()          { return (ordLive && chaseOrd) || chasePos; }   // v13.0: this side is winning back the carried loss\n',
    r'''   bool   Chasing()          { return (ordLive && chaseOrd) || chasePos; }   // v13.0: this side is winning back the carried loss
   // v13.1 (section 4): "" = take this setup; otherwise why it is skipped (each filter counts its own skips). The first
   // setup of the day is checked LAST, so a setup that another filter skips is never the day's first.
   string XSkip(int d)
   {
      if (S.tdOn && g_dyAvg > 0 && !IsNa(g_dyO) && d * (g_c - g_dyO) < S.tdAtr * g_dyAvg)
      {
         cntX[3]++;
         return "against today's move (open " + DoubleToString(g_dyO, 2) + ", needs " + DoubleToString(S.tdAtr * g_dyAvg, 2) + (d == 1 ? " above it)" : " below it)");
      }
      if (S.ydOn && !IsNa(g_ydH) && (d == 1 ? g_c < g_ydL : g_c > g_ydH))
      {
         cntX[1]++;
         return d == 1 ? "below yesterday's low " + DoubleToString(g_ydL, 2) : "above yesterday's high " + DoubleToString(g_ydH, 2);
      }
      int lb = d == 1 ? EN.bi - EN.flr.x1 : EN.bi - EN.cel.x1;
      if (S.legMin > 0 && lb < S.legMin)
      {
         cntX[2]++;
         return "the move took " + IntegerToString(lb) + " candles (at least " + IntegerToString(S.legMin) + ")";
      }
      for (int k = 0; k < 2; k++)
         if (S.rsOn[k] && g_ind[k].ok)
         {
            double v = g_ind[k].val, a = S.rsLvl[k], b = 100.0 - S.rsLvl[k];
            bool okR = S.rsMode[k] == 0 ? (d == 1 ? v < a : v > b) : (d == 1 ? v > a : v < b);
            if (!okR)
            {
               cntX[4 + k]++;
               return "RSI(" + IntegerToString(S.rsLen[k]) + ") " + TfTxt(g_ind[k].tf) + " = " + DoubleToString(v, 1) + ", a " + (d == 1 ? "buy" : "sell") +
                      " needs " + ((S.rsMode[k] == 0) == (d == 1) ? "below " : "above ") + DoubleToString(d == 1 ? a : b, 1);
            }
         }
      for (int k = 0; k < 2; k++)
         if (S.emOn[k] && g_ind[2 + k].ok)
         {
            double sl2 = g_ind[2 + k].val, fs = S.emMode[k] == 1 ? g_ind[2 + k].val2 : g_c;
            if (!(d == 1 ? fs > sl2 : fs < sl2))
            {
               cntX[6 + k]++;
               return (S.emMode[k] == 1 ? "EMA " + IntegerToString(S.emFast[k]) : "price " + DoubleToString(g_c, 2)) + (d == 1 ? " not above" : " not below") +
                      " the EMA " + IntegerToString(S.emLen[k]) + " " + TfTxt(g_ind[2 + k].tf) + " (" + DoubleToString(sl2, 2) + ")";
            }
         }
      if (S.fstOn)
      {
         long dy = FloorDivL(SessLoc(g_t + S.cs), 86400);
         if (fstDay != dy) { fstDay = dy; cntX[0]++; return "first setup of the day"; }
      }
      return "";
   }
''')
rep('''            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;
            if (use && !IsNa(opl))
            {
               if (dir != 0) cntCanc++;
''', '''            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;
            // v13.1 (section 4): the new setup filters (the first setup of the day is checked last)
            string xs = "";
            if (use && !IsNa(opl)) xs = XSkip(d);
            if (xs != "") use = false;
            if (use && !IsNa(opl))
            {
               if (dir != 0) cntCanc++;
''')
rep('            else if (r3Use && r3Far) Note(sg + ": SKIP - RULE 3: "',
    '            else if (xs != "") Note(sg + ": SKIP - " + xs);\n'
    '            else if (r3Use && r3Far) Note(sg + ": SKIP - RULE 3: "')
# the minimum stop as % of the entry price, at the placement (like the other stop-distance limits)
rep('''         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;
''', '''         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;
         bool mpOk  = S.mnPct <= 0 || r >= ent * S.mnPct / 100.0;   // v13.1 (section 4): the stop at least this % of the entry price
''')
rep('         if (sane && dOk && pdOk && qOk && r > 0 && (!S.once || !placed))\n',
    '         if (sane && dOk && mpOk && pdOk && qOk && r > 0 && (!S.once || !placed))\n')
rep('''         else if (!sane || !dOk || !pdOk || !qOk || r <= 0)
         {
            Note(!sane ? "CANCELLED - entry beyond the stop" : (!pdOk ? "CANCELLED - premium / discount filter" : (!lotOk ? "CANCELLED - below the minimum lot" : (!dOk ? "CANCELLED - stop too close / too far" : "CANCELLED - size is zero"))));
            CancelSent();
            if (!dOk) cntSkip++;
''', '''         else if (!sane || !dOk || !mpOk || !pdOk || !qOk || r <= 0)
         {
            Note(!sane ? "CANCELLED - entry beyond the stop" : (!pdOk ? "CANCELLED - premium / discount filter" : (!lotOk ? "CANCELLED - below the minimum lot" :
                 (!mpOk ? "CANCELLED - stop closer than " + DoubleToString(S.mnPct, 2) + "% of the price" : (!dOk ? "CANCELLED - stop too close / too far" : "CANCELLED - size is zero")))));
            CancelSent();
            if (!dOk || !mpOk) cntSkip++;
            if (!mpOk) cntX[8]++;
''')

# ---- core: setup and one bar
rep('''   g_calI = 0; g_calH0 = false; g_calH1 = false; g_preNow = false; g_holCal = false; g_auN1 = LNONE; g_auN2 = LNONE; g_auN3 = LNONE; g_auN4 = LNONE;
}
// one CLOSED chart bar.''', '''   g_calI = 0; g_calH0 = false; g_calH1 = false; g_preNow = false; g_holCal = false; g_auN1 = LNONE; g_auN2 = LNONE; g_auN3 = LNONE; g_auN4 = LNONE;
   // v13.1: the trading day and the RSI / EMA filters (a timeframe not above the chart = the chart's own candles)
   DayReset();
   for (int i = 0; i < 4; i++) g_ind[i].Reset();
   for (int k = 0; k < 2; k++)
   {
      g_ind[k].kind = 1; g_ind[k].len = S.rsLen[k]; g_ind[k].len2 = 0; g_ind[k].tf = S.rsTf[k] > S.cs ? S.rsTf[k] : 0;
      g_ind[2 + k].kind = 2; g_ind[2 + k].len = S.emLen[k]; g_ind[2 + k].len2 = S.emMode[k] == 1 ? S.emFast[k] : 0; g_ind[2 + k].tf = S.emTf[k] > S.cs ? S.emTf[k] : 0;
   }
}
// one CLOSED chart bar.''')
rep('''   g_t = t; g_o = o; g_h = h; g_l = l; g_c = c; g_eq = eq;
   EN.Step(o, h, l, c);
''', '''   g_t = t; g_o = o; g_h = h; g_l = l; g_c = c; g_eq = eq;
   EN.Step(o, h, l, c);
   DayStep(t, o, h, l);                                                                 // v13.1: the trading day
   for (int i = 0; i < 4; i++) if (IndOn(i) && g_ind[i].tf == 0) g_ind[i].Step(c);    // v13.1: filters on the chart's candles
''')

# ---- MT5 part: settings, checks, the higher-timeframe candles of the filters, warm-up, restarts, table
rep('   S.sp1 = InSp1; S.spN1 = InSpN1; S.sp2 = InSp2; S.spN2 = InSpN2; S.sp3 = InSp3; S.spN3 = InSpN3; S.spInc = InSpInc; S.spAdd = InSpAdd;\n   S.cs = g_cs;\n',
    '''   S.sp1 = InSp1; S.spN1 = InSpN1; S.sp2 = InSp2; S.spN2 = InSpN2; S.sp3 = InSp3; S.spN3 = InSpN3; S.spInc = InSpInc; S.spAdd = InSpAdd;
   S.mnPct = InMnPct; S.fstOn = InFstOn; S.ydOn = InYdOn; S.legMin = InLegMin; S.tdOn = InTdOn; S.tdAtr = InTdAtr;   // v13.1
   S.rsOn[0] = InRsLOn; S.rsTf[0] = TffSec(InRsLTf); S.rsLen[0] = InRsLLen; S.rsMode[0] = (int)InRsLMode; S.rsLvl[0] = InRsLLvl;
   S.rsOn[1] = InRsHOn; S.rsTf[1] = TffSec(InRsHTf); S.rsLen[1] = InRsHLen; S.rsMode[1] = (int)InRsHMode; S.rsLvl[1] = InRsHLvl;
   S.emOn[0] = InEmLOn; S.emTf[0] = TffSec(InEmLTf); S.emMode[0] = (int)InEmLMode; S.emLen[0] = InEmLLen; S.emFast[0] = InEmLFast;
   S.emOn[1] = InEmHOn; S.emTf[1] = TffSec(InEmHTf); S.emMode[1] = (int)InEmHMode; S.emLen[1] = InEmHLen; S.emFast[1] = InEmHFast;
   S.cs = g_cs;
''')
rep('''//---------------------------------------------------------------- settings from the inputs
void FillSettings()
''', '''//---------------------------------------------------------------- v13.1: the timeframe of an RSI / EMA filter
int TffSec(ETfF f)   // MT5's own period lengths (1 month = 2,592,000 like PeriodSeconds)
{
   if (f == TFF_M5) return 300;
   if (f == TFF_M15) return 900;
   if (f == TFF_H1) return 3600;
   if (f == TFF_H4) return 14400;
   if (f == TFF_D1) return 86400;
   if (f == TFF_W1) return 604800;
   if (f == TFF_MN1) return 2592000;
   return 60;
}
ENUM_TIMEFRAMES TffPer(ETfF f)
{
   if (f == TFF_M5) return PERIOD_M5;
   if (f == TFF_M15) return PERIOD_M15;
   if (f == TFF_H1) return PERIOD_H1;
   if (f == TFF_H4) return PERIOD_H4;
   if (f == TFF_D1) return PERIOD_D1;
   if (f == TFF_W1) return PERIOD_W1;
   if (f == TFF_MN1) return PERIOD_MN1;
   return PERIOD_M1;
}

//---------------------------------------------------------------- settings from the inputs
void FillSettings()
''')
rep('   if (InResume < 0 || InDrawMax < 0 || InHtfMarks < 0) return "Restart bars (section 12) and marks to keep (section 13) must be 0 or more";\n   return "";\n',
    '''   if (InResume < 0 || InDrawMax < 0 || InHtfMarks < 0) return "Restart bars (section 12) and marks to keep (section 13) must be 0 or more";
   // v13.1 (section 4)
   if (InMnPct < 0 || InMnPct > 10) return "Minimum stop % of the price (section 4) must be 0 - 10";
   if (InLegMin < 0 || InLegMin > 10000) return "Candles of the CHOCH / BOS move (section 4) must be 0 - 10000";
   if (InTdAtr < 0 || InTdAtr > 5) return "Today's move (section 4) must be 0 - 5 x the average daily range";
   if (InRsLLen < 1 || InRsLLen > 100 || InRsHLen < 1 || InRsHLen > 100) return "RSI length (section 4) must be 1 - 100";
   if (InRsLLvl < 0 || InRsLLvl > 100 || InRsHLvl < 0 || InRsHLvl > 100) return "RSI level (section 4) must be 0 - 100";
   if (InEmLLen < 1 || InEmLLen > 500 || InEmHLen < 1 || InEmHLen > 500 || InEmLFast < 1 || InEmLFast > 500 || InEmHFast < 1 || InEmHFast > 500) return "EMA lengths (section 4) must be 1 - 500";
   if ((InEmLOn && InEmLMode == EM_CROSS && InEmLFast >= InEmLLen) || (InEmHOn && InEmHMode == EM_CROSS && InEmHFast >= InEmHLen)) return "EMA filter (section 4): the FAST EMA length must be smaller than the slow one";
   return "";
''')
# the filters' higher-timeframe candles (the same way as the higher-timeframe engine: closed candles before the bar's own)
rep('''// feed every higher-timeframe candle that closed before the candle holding this chart bar
bool FeedHtf(datetime barOpen)''', '''// v13.1: the RSI / EMA filters on a timeframe above the chart - their MT5 candles, fed like the higher timeframe below
bool            g_indUse[4];
ENUM_TIMEFRAMES g_indPer[4];
datetime        g_indFed[4];
void IndSetup()
{
   ETfF tf[4];
   tf[0] = InRsLTf; tf[1] = InRsHTf; tf[2] = InEmLTf; tf[3] = InEmHTf;
   for (int i = 0; i < 4; i++)
   {
      bool on = i < 2 ? S.rsOn[i] : S.emOn[i - 2];
      g_indUse[i] = on && TffSec(tf[i]) > g_cs;
      g_indPer[i] = TffPer(tf[i]);
      g_indFed[i] = 0;
   }
}
datetime IndOpenOf(int i, datetime t)
{
   int sh = iBarShift(g_sym, g_indPer[i], t, false);
   if (sh < 0) return 0;
   return iTime(g_sym, g_indPer[i], sh);
}
bool FeedInd(datetime barOpen)
{
   for (int i = 0; i < 4; i++)
   {
      if (!g_indUse[i]) continue;
      datetime hc = IndOpenOf(i, barOpen);
      if (hc == 0) return false;
      if (hc <= g_indFed[i] + 1) continue;
      MqlRates ir[];
      int n = CopyRates(g_sym, g_indPer[i], g_indFed[i] + 1, hc - 1, ir);
      if (n < 0) return false;
      for (int j = 0; j < n; j++)
         if (ir[j].time > g_indFed[i] && ir[j].time < hc) { IndCandle(i, ir[j].close); g_indFed[i] = ir[j].time; }
   }
   return true;
}
// v13.1: 'only with today's move' needs 14 complete days before the first live bar
int WarmBars() { int w = 17 * 1440 * 60 / g_cs; return InTdOn && w > InWarm ? w : InWarm; }

// feed every higher-timeframe candle that closed before the candle holding this chart bar
bool FeedHtf(datetime barOpen)''')
rep('''   FeedHtf(r.time);
   if (!dry) GatherIO(tEnd);
''', '''   FeedHtf(r.time);
   FeedInd(r.time);   // v13.1
   if (!dry) GatherIO(tEnd);
''')
rep('''   if (g_htfUse && !g_tester && !SeriesInfoInteger(g_sym, g_htf, SERIES_SYNCHRONIZED)) { iTime(g_sym, g_htf, 0); return false; }
   MqlRates rr[];
   int n = CopyRates(g_sym, g_tf, 1, InWarm, rr);
''', '''   if (g_htfUse && !g_tester && !SeriesInfoInteger(g_sym, g_htf, SERIES_SYNCHRONIZED)) { iTime(g_sym, g_htf, 0); return false; }
   for (int i = 0; i < 4; i++) if (g_indUse[i] && !g_tester && !SeriesInfoInteger(g_sym, g_indPer[i], SERIES_SYNCHRONIZED)) { iTime(g_sym, g_indPer[i], 0); return false; }
   MqlRates rr[];
   int n = CopyRates(g_sym, g_tf, 1, WarmBars(), rr);
''')
rep('''      if (g_htfFed == 0) g_htfFed = hc0 - 1;
   }
''', '''      if (g_htfFed == 0) g_htfFed = hc0 - 1;
   }
   // v13.1: the RSI / EMA filters above the chart - their candles before the first chart bar
   for (int i = 0; i < 4; i++)
   {
      g_indFed[i] = 0;
      if (!g_indUse[i]) continue;
      datetime ic0 = IndOpenOf(i, rr[0].time);
      if (ic0 == 0) return false;
      MqlRates ir[];
      int m = CopyRates(g_sym, g_indPer[i], ic0 - 1, 3000, ir);
      for (int j = 0; j < m; j++) if (ir[j].time < ic0) { IndCandle(i, ir[j].close); g_indFed[i] = ir[j].time; }
      if (g_indFed[i] == 0) g_indFed[i] = ic0 - 1;
   }
''')
rep('''   ReplayMoney(tLimit);
''', '''   ReplayMoney(tLimit);
   // v13.1: the day whose first setup was already skipped goes on after a restart
   if (!g_tester) for (int k = 0; k < g_nSides; k++) g_side[k].fstDay = (long)GvGet(GvSide(k, "fd"), (double)LNONE);
''')
rep('''      GvSet(GvSide(k, "mb"), g_side[k].mktBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].mktBar));
''', '''      GvSet(GvSide(k, "mb"), g_side[k].mktBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].mktBar));
      GvSet(GvSide(k, "fd"), (double)g_side[k].fstDay);   // v13.1
''')
rep('''   g_htfUse = S.htfOk;
   g_P = "SMC" + IntegerToString(InMagic) + "_" + g_sym + "_";''', '''   g_htfUse = S.htfOk;
   IndSetup();   // v13.1
   g_P = "SMC" + IntegerToString(InMagic) + "_" + g_sym + "_";''')
# table
rep('''   if (what == 16) return g_side[k].cntHgB;
''', '''   if (what == 16) return g_side[k].cntHgB;
   if (what >= 20 && what <= 28) return g_side[k].cntX[what - 20];   // v13.1
''')
rep('''string IdeasTxt()
''', '''// v13.1: the new section 4 filters - how many setups each one skipped, and what they read now
string XTxt()
{
   string t = "";
   if (S.fstOn) t = t + ", first of the day " + CntTxt(20);
   if (S.ydOn) t = t + ", yesterday's high / low " + CntTxt(21);
   if (S.legMin > 0) t = t + ", move < " + I2(S.legMin) + " candles " + CntTxt(22);
   if (S.tdOn) t = t + ", today's move " + CntTxt(23);
   if (S.rsOn[0]) t = t + ", RSI " + TfTxt(g_ind[0].tf) + " " + CntTxt(24);
   if (S.rsOn[1]) t = t + ", RSI " + TfTxt(g_ind[1].tf) + " " + CntTxt(25);
   if (S.emOn[0]) t = t + ", EMA " + TfTxt(g_ind[2].tf) + " " + CntTxt(26);
   if (S.emOn[1]) t = t + ", EMA " + TfTxt(g_ind[3].tf) + " " + CntTxt(27);
   if (S.mnPct > 0) t = t + ", stop < " + Num(S.mnPct) + "% " + CntTxt(28);
   return t == "" ? "off" : StringSubstr(t, 2);
}
string XNowTxt()
{
   string t = "";
   if (S.ydOn) t = t + "  |  yesterday " + (IsNa(g_ydH) ? "-" : Px(g_ydL) + " - " + Px(g_ydH));
   if (S.tdOn) t = t + "  |  today's open " + (IsNa(g_dyO) ? "-" : Px(g_dyO)) + ", average day " + (g_dyAvg > 0 ? Px(g_dyAvg) : "not ready");
   for (int k = 0; k < 2; k++)
      if (S.rsOn[k]) t = t + "  |  RSI(" + I2(S.rsLen[k]) + ") " + TfTxt(g_ind[k].tf) + " " + (g_ind[k].ok ? DoubleToString(g_ind[k].val, 1) : "-");
   for (int k = 0; k < 2; k++)
      if (S.emOn[k]) t = t + "  |  EMA " + (S.emMode[k] == 1 ? I2(S.emFast[k]) + " / " : "") + I2(S.emLen[k]) + " " + TfTxt(g_ind[2 + k].tf) + " " +
                     (g_ind[2 + k].ok ? (S.emMode[k] == 1 ? Px(g_ind[2 + k].val2) + " / " : "") + Px(g_ind[2 + k].val) : "-");
   return t == "" ? "off" : StringSubstr(t, 5);
}
bool XAny() { return S.fstOn || S.ydOn || S.legMin > 0 || S.tdOn || S.rsOn[0] || S.rsOn[1] || S.emOn[0] || S.emOn[1] || S.mnPct > 0; }
string IdeasTxt()
''')
rep('''   Row("Cancelled - new BOS before the fill", S.bosCnl ? CntTxt(9) : "off", S.bosCnl && CntSum(9) > 0 ? clrOrange : clrGray);
''', '''   Row("Cancelled - new BOS before the fill", S.bosCnl ? CntTxt(9) : "off", S.bosCnl && CntSum(9) > 0 ? clrOrange : clrGray);
   Row("  - skipped: section 4 filters (v13.1)", XTxt(), XAny() ? clrOrange : clrGray);
   Row("  - section 4 filters now", XNowTxt(), XAny() ? clrAqua : clrGray);
''')
rep('   Row("SMC STRATEGY  (EA v13.0)", "value", clrWhite);', '   Row("SMC STRATEGY  (EA v13.1)", "value", clrWhite);')

open(dst, 'w').write(s)
print('written', dst)
