# EA v15.1 = EA v15.0 +
#   1. zone boxes: ONE box per zone (a later signal stretches it, the text counts them: '1h OB x3'); EVERY zone that counted for the
#      signal is drawn (order blocks and FVGs, every timeframe); an FVG with 'far half' ON is drawn as its far half
#   2. section 13: 'show all zones' (every live zone the settings can use), fill visible % per timeframe (50 / 30 / 15), order block /
#      FVG colours (buy / sell), label colour of the two timeframes above; a border on the higher timeframe's zones only; the last
#      zone darker (MT5 boxes cannot be see-through: the colour is mixed with the chart background)
#   3. a new higher timeframe leg (CHOCH or BOS): the zones made BEFORE the leg started go (a zone whose 3rd candle holds the leg
#      start stays), the old leg's CHOCH* line goes; always on
#   4. a waiting setup is cancelled only when ALL the zones that allowed it are gone (broken by a close, or 3.)
#   5. section 2: 'only trade from the last zone' (the deepest order block of the biggest timeframe that has one, beyond the line),
#      'order block box reaches the swing low / high' (also used by the rules), 'order block type 2' (candle 1 of the FVG, one per
#      burst of FVGs), MSS (market structure shift) signals + their swing size + 'enter on the MSS confirmation' + its stop
#   6. section 8: after the pause, N losses in a row -> trade only every (skip + 1)-th trading day until a winning trade
#   7. section 9: the force-close hour on the 1-minute chart only (ON)
#   8. section 1: switch off every price-distance setting (all charts, also 1 minute) - for other markets
# usage: python3 ea151.py SMC_Structure_EA_v15.0.mq5 SMC_Structure_EA_v15.1.mq5
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:160]))
    s = s.replace(old, new)


def box(t):
    return '//| ' + t.ljust(66) + ' |'


# ---------------------------------------------------------------- header (version on line 2)
rep('//| SMC Structure EA v15.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v15.0, same      |\n',
    '//| SMC Structure EA v15.1 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v15.1, same      |\n')
rep(box('Owner: Punit. v15.0: order block zone modes, 1-minute-only rules.'),
    box('Owner: Punit. v15.1: zone boxes, last zone, OB 2, MSS, pauses.'))
rep('#property version     "15.00"', '#property version     "15.10"')
rep('#property description "SMC Structure EA v15.0 - the TradingView strategy v15.0 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v15.1 - the TradingView strategy v15.1 rules in MetaTrader 5, plus a hedge mode."')
rep('   Print("SMC EA v15.0 ready: ", n,', '   Print("SMC EA v15.1 ready: ", n,')

# ---------------------------------------------------------------- the MSS confirmation stop choice
rep('''enum EEmMode
{''', '''enum EMssSt           // v15.1: the stop of an entry on the MSS confirmation
{
   MS_FIRST = 0,      // First MSS low / high (the low / high the MSS started from)
   MS_NEW = 1         // Newest swing low / high (the low / high of the pullback)
};
enum EEmMode
{''')

# ---------------------------------------------------------------- inputs (new ones at the END of their section)
rep('''input double   InBuPip     = 0.0;     //   - pip size (0 = automatic: gold 0.10, silver 0.01, forex 0.0001, JPY 0.01)
''', '''input double   InBuPip     = 0.0;     //   - pip size (0 = automatic: gold 0.10, silver 0.01, forex 0.0001, JPY 0.01)
input bool     InPxOff     = false;   // Switch OFF every price-distance setting on every chart (other markets: forex, crypto, metals)
''')
rep('''input bool     InZnLine    = true;    //   - the higher timeframe's CHOCH* line (the leg start) counts as a zone
''', '''input bool     InZnLine    = true;    //   - the higher timeframe's CHOCH* line (the leg start) counts as a zone
input bool     InZnLast    = false;   //   - only trade from the LAST zone (the deepest order block of the biggest timeframe that has one)
input bool     InZnSw      = false;   //   - order block box reaches the swing low (buy) / high (sell) - the rules use the bigger box too
input bool     InZnOb2     = false;   //   - order block type 2: the FIRST candle of the FVG (one per burst of FVGs); OFF = the last opposite candle
input bool     InMssOn     = false;   //   - also trade a market structure shift (MSS) after a zone touch
input int      InMssN      = 2;       //   - MSS swing: candles on each side (1 - 10)
input bool     InMssCf     = false;   //   - MSS: enter on the confirmation (a pullback to the first FVG, then a new FVG + order block)
input EMssSt   InMssSt     = MS_FIRST; //   - MSS confirmation: the stop
''')
rep('''input int      InLdD       = 2;       //   - days to pause (after the rest of that day)
''', '''input int      InLdD       = 2;       //   - days to pause (after the rest of that day)
input int      InLdN2      = 0;       //   - after the pause: this many losses in a row start the every-other-day mode (0 = off)
input int      InLdSkip    = 1;       //   - that mode: days skipped between trading days (1 = every other day), until a winning trade
''')
rep('''input bool     InWk247     = false;   // Trade 24/7 - allow weekends (crypto)
''', '''input bool     InWk247     = false;   // Trade 24/7 - allow weekends (crypto)
input bool     InFl1m      = true;    // Force-close hour on the 1-minute chart only (above 1 minute: no force close)
''')
rep('''input bool     InZnBox     = true;    // Zone modes: draw the zone that was touched and gave the signal as a box (the last 50)
''', '''input bool     InZnBox     = true;    // Zone modes: draw every zone that gave a signal as a box (one box per zone, the newest 440)
input bool     InZnAll     = false;   // Zone modes: show ALL zones (every live zone the settings can use); OFF = only those that gave a signal
input int      InZnV0      = 50;      //   - fill visible %: zones of the higher timeframe (e.g. 15m)
input int      InZnV1      = 30;      //   - fill visible %: the timeframe above it (e.g. 1h)
input int      InZnV2      = 15;      //   - fill visible %: two above (e.g. 4h)
input color    InZnCObB    = clrGreen;  //   - order block colour, buy
input color    InZnCObS    = clrRed;    //   - order block colour, sell
input color    InZnCFvB    = clrTeal;   //   - FVG colour, buy
input color    InZnCFvS    = clrOrange; //   - FVG colour, sell
input color    InZnCLb     = clrWhite;  //   - label colour of the two timeframes above (the higher timeframe's label has the zone colour)
''')

# ---------------------------------------------------------------- settings in the core
rep('''   bool   obM, znBig, znOb, znFvg, znHalf, znTwo, znLine;   // v15.0 section 2: the order block zone modes and their settings
   double znPct;
''', '''   bool   obM, znBig, znOb, znFvg, znHalf, znTwo, znLine;   // v15.0 section 2: the order block zone modes and their settings
   double znPct;
   bool   pxOff, fl1m, flOn;           // v15.1: every price distance off (section 1); the force close on 1m only (section 9) and in use
   bool   znLast, znSw, znOb2, mssOn, mssCf;   // v15.1 section 2: last zone only, order block to the swing, order block type 2, MSS
   int    mssN, mssSt, ldN2, ldSkip;   //   MSS swing size, confirmation stop; section 8: losses after the pause, days skipped
''')
rep('''            znTwo = true; znLine = true; znPct = 50;
''', '''            znTwo = true; znLine = true; znPct = 50;
            pxOff = false; fl1m = false; flOn = true; znLast = false; znSw = false; znOb2 = false; mssOn = false; mssCf = false;
            mssN = 2; mssSt = 0; ldN2 = 0; ldSkip = 1;
''')
rep('''      // v15.0: section 4 - on charts above 1 minute these are not used (the switch ON); the big candle has its own box there
      x1m    = m1On && cs > 60;
''', '''      // v15.1: section 1 - every price distance off on every chart (other markets): stop buffer, skip closer / further, min stop %,
      // rule 3 distance (rule 3 itself works), leg size, big signal candle, spread for sizing, the target pushed out for the commission
      if (pxOff) { slBuf = 0; minStop = 0; maxStop = 0; mnPct = 0; lzMin = 0; lzMax = 0; r3BrkOn = false; bcMax = 0; bcMax2 = 0; sprd = 0; cmTgt = false; }
      flOn   = !(fl1m && cs > 60);    // v15.1: the force-close hour only on the 1-minute chart (and seconds charts)
      // v15.0: section 4 - on charts above 1 minute these are not used (the switch ON); the big candle has its own box there
      x1m    = m1On && cs > 60;
''')

# ---------------------------------------------------------------- the higher timeframe engine: the time of the leg start
rep('''   bool   brkNow, brkUp, brkCho;   // a CHOCH / BOS on this candle (drawing only)
   double brkP;
   int    brkB;
   CHtf() { Reset(); }''', '''   bool   brkNow, brkUp, brkCho;   // a CHOCH / BOS on this candle (drawing only)
   double brkP;
   int    brkB;
   long   tNow, tRunLoT, tRunHiT, legT;   // v15.1: open time (UTC) of the candle fed (set by the caller), of the running low / high, of the leg start
   CHtf() { Reset(); }''')
rep('''      brkNow = false; brkUp = false; brkCho = false; brkP = NAD; brkB = NAI;
   }''', '''      brkNow = false; brkUp = false; brkCho = false; brkP = NAD; brkB = NAI;
      tNow = 0; tRunLoT = 0; tRunHiT = 0; legT = LNONE;
   }''')
rep('''      tRunLo = IsNa(tRunLo) ? l : Mn(tRunLo, l);
      tRunHi = IsNa(tRunHi) ? h : Mx(tRunHi, h);
      double cfH = NAD, cfL = NAD;''', '''      if (IsNa(tRunLo) || l < tRunLo) { tRunLo = l; tRunLoT = tNow; }
      if (IsNa(tRunHi) || h > tRunHi) { tRunHi = h; tRunHiT = tNow; }
      double cfH = NAD, cfL = NAD;''')
rep('''         if (ad || (!IsNa(tCeil) && cfH == tCeil)) { tCeil = cfH; tCeilB = hb; tRunLo = l; }''',
    '''         if (ad || (!IsNa(tCeil) && cfH == tCeil)) { tCeil = cfH; tCeilB = hb; tRunLo = l; tRunLoT = tNow; }''')
rep('''         if (ad || (!IsNa(tFlor) && cfL == tFlor)) { tFlor = cfL; tFlorB = hb; tRunHi = h; }''',
    '''         if (ad || (!IsNa(tFlor) && cfL == tFlor)) { tFlor = cfL; tFlorB = hb; tRunHi = h; tRunHiT = tNow; }''')
rep('''      { brkNow = true; brkUp = true; brkCho = tTrend == -1; brkP = tCeil; brkB = tCeilB; tTrend = 1; tFlor = tRunLo; tFlorB = hb; tRunHi = h; tCeil = NAD; tCeilB = NAI; evN++; }''',
    '''      { brkNow = true; brkUp = true; brkCho = tTrend == -1; brkP = tCeil; brkB = tCeilB; tTrend = 1; tFlor = tRunLo; tFlorB = hb; legT = tRunLoT; tRunHi = h; tRunHiT = tNow; tCeil = NAD; tCeilB = NAI; evN++; }''')
rep('''      { brkNow = true; brkUp = false; brkCho = tTrend == 1; brkP = tFlor; brkB = tFlorB; tTrend = -1; tCeil = tRunHi; tCeilB = hb; tRunLo = l; tFlor = NAD; tFlorB = NAI; evN++; }''',
    '''      { brkNow = true; brkUp = false; brkCho = tTrend == 1; brkP = tFlor; brkB = tFlorB; tTrend = -1; tCeil = tRunHi; tCeilB = hb; legT = tRunHiT; tRunLo = l; tRunLoT = tNow; tFlor = NAD; tFlorB = NAI; evN++; }''')

# ---------------------------------------------------------------- shared state: the leg start time
rep('''int    g_T15 = 0, g_htE = 0, g_prevE = 0, g_autoDir = 0;
''', '''int    g_T15 = 0, g_htE = 0, g_prevE = 0, g_autoDir = 0;
long   g_htS = LNONE;   // v15.1: the open time (UTC) of the higher timeframe candle where its leg started
''')

# ---------------------------------------------------------------- the zone engine (v15.0 block replaced)
a = s.index('// ---------- v15.0: the order block zone modes (section 2) ----------')
b = s.index('double CmU(double ent)')
ZONE = r'''// ---------- v15.0 / v15.1: the order block zone modes (section 2) ----------
// Zones come from the CLOSED candles of the higher timeframe (j = 0) and the two timeframes above it (j = 1, 2). An FVG = candle 1
// and candle 3 do not overlap; its order block = the last opposite candle among the 3 candles before the move (candles 3, 4, 5
// back) - v15.1 type 2: candle 1 of the FVG, one per burst (an FVG whose candle 1 is one of the last FVG's 3 candles is the same
// burst); v15.1 'to the swing': the order block box reaches the lowest low (buy) / highest high (sell) from its candle to the 3rd FVG
// candle. A zone goes when a candle of ITS OWN timeframe closes beyond its far side, and (v15.1) when a new higher timeframe leg
// starts after it was made. At each chart bar a zone of the higher timeframe direction is 'in the zone' when it lies in the
// pullback zone of the higher timeframe leg (from the zone line % to the leg start = 100%; an order block may touch the line, an
// FVG's touch line must be beyond it); then the bar's low (high) reaching its touch line (order block: its near edge; FVG: its 50%
// line or its near edge) touches it. A with-HTF signal after a touch may trade; it 'closes the visit' (the visit's low / high
// stays); a later bar beyond that low / high took its liquidity: with 'second visit' ON the zone works again, OFF it stops. A new
// higher timeframe leg starts all touches again. The higher timeframe's CHOCH* line (the leg start) can work as a zone too.
// v15.1 MSS: a visit that gave an MSS gives no CHOCH / BOS trade, a visit that gave a signal gives no MSS (one trade per visit).
#define ZMAX 60
#define ZPER 10
struct ZRec
{
   int    id, tf, dir, kind, n, vs;  // kind 0 = order block, 1 = FVG, 2 = the CHOCH* line; n = the signals it counted for; vs = the signal
                                     // that closed this visit (0 none, 1 CHOCH / BOS, 2 MSS)
   double top, bot, ext;             // ext = the low (buy) / high (sell) of the current visit
   long   t0, te, tt, t1;            // t0 = the open time of the zone's candle, te = when it was made (the close of the 3rd FVG candle),
                                     // tt = its first touch, t1 = its last signal (UTC)
   bool   q, tch, frz, spent;        // q = in the leg's zone at this bar, tch = touched, frz = a signal closed the visit, spent = stopped
};
ZRec   g_zn[ZMAX];
ZRec   g_zl;                         // the higher timeframe's CHOCH* line as a zone
int    g_znN = 0, g_znId = 0, g_znLegE = -1;
double g_znCo[3][6], g_znCh[3][6], g_znCl[3][6], g_znCc[3][6];   // the last closed candles of each zone timeframe (0 = newest)
long   g_znCt[3][6];                                              // their open times (UTC)
int    g_znCn[3];
long   g_znObTm[3][2];                // the candle time of the last order block added per timeframe and side (not added twice)
long   g_znSeq[3], g_znFc[3][2];       // v15.1: candles fed per timeframe; the number of the last FVG's candle 1 per side (type 2)
// v15.1: the zones gone on THIS bar (broken by a close of their own timeframe, made before a new higher timeframe leg, the old leg's
// CHOCH* line) - a waiting setup whose zones are ALL gone is cancelled
#define ZDMAX 64
int    g_zdTf[ZDMAX], g_zdK[ZDMAX], g_zdD[ZDMAX];
double g_zdT[ZDMAX], g_zdB[ZDMAX];
long   g_zdT0[ZDMAX];
int    g_zdN = 0;
int    g_zc[ZMAX + 1];                 // v15.1: the zones that count for a signal (indexes into g_zn; -1 = the CHOCH* line)
int    g_zcN = 0;
int    g_lz = -1;                      // v15.1: the last zone now (index into g_zn, -1 = none), for the higher timeframe direction
// v15.1: the zone boxes of this bar (the adapter draws them): every zone that counted for a with-HTF signal, after the count
struct ZBox { int tf, kind, dir, n, leg; double top, bot; long t0, t1; bool last; };
ZBox   g_zb[ZMAX + 1];
int    g_zbN = 0;
void ZnClr(ZRec &z) { z.q = false; z.tch = false; z.frz = false; z.spent = false; z.ext = NAD; z.vs = 0; }
void ZnReset()
{
   g_znN = 0; g_znId = 0; g_znLegE = -1; g_zdN = 0; g_zcN = 0; g_lz = -1; g_zbN = 0;
   for (int j = 0; j < 3; j++)
   {
      g_znCn[j] = 0; g_znSeq[j] = 0;
      for (int k = 0; k < 6; k++) { g_znCo[j][k] = NAD; g_znCh[j][k] = NAD; g_znCl[j][k] = NAD; g_znCc[j][k] = NAD; g_znCt[j][k] = 0; }
      for (int a = 0; a < 2; a++) { g_znObTm[j][a] = -1; g_znFc[j][a] = -100; }
   }
   g_zl.id = -1; g_zl.tf = 9; g_zl.dir = 0; g_zl.kind = 2; g_zl.top = NAD; g_zl.bot = NAD; g_zl.n = 0; g_zl.t0 = 0; g_zl.te = 0; g_zl.tt = 0; g_zl.t1 = 0;
   ZnClr(g_zl);
}
void ZnDel(int i) { for (int k = i; k + 1 < g_znN; k++) g_zn[k] = g_zn[k + 1]; g_znN--; }
void ZnGone(int tf, int kind, int dir, double top, double bot, long t0)
{
   if (g_zdN >= ZDMAX) return;
   g_zdTf[g_zdN] = tf; g_zdK[g_zdN] = kind; g_zdD[g_zdN] = dir; g_zdT[g_zdN] = top; g_zdB[g_zdN] = bot; g_zdT0[g_zdN] = t0; g_zdN++;
}
bool ZnIsGone(int tf, int kind, int dir, double top, double bot, long t0)
{
   for (int i = 0; i < g_zdN; i++) if (g_zdTf[i] == tf && g_zdK[i] == kind && g_zdD[i] == dir && g_zdT[i] == top && g_zdB[i] == bot && g_zdT0[i] == t0) return true;
   return false;
}
// a new zone; the oldest of the same timeframe and side goes when there are already ZPER
void ZnAdd(int j, int dir, int kind, double top, double bot, long t0, long te)
{
   int same = 0, old = -1;
   for (int i = 0; i < g_znN; i++) if (g_zn[i].tf == j && g_zn[i].dir == dir) { same++; if (old < 0) old = i; }
   if (same >= ZPER) ZnDel(old);
   if (g_znN >= ZMAX) ZnDel(0);
   g_znId++;
   g_zn[g_znN].id = g_znId; g_zn[g_znN].tf = j; g_zn[g_znN].dir = dir; g_zn[g_znN].kind = kind; g_zn[g_znN].top = top; g_zn[g_znN].bot = bot;
   g_zn[g_znN].t0 = t0; g_zn[g_znN].te = te; g_zn[g_znN].tt = 0; g_zn[g_znN].t1 = 0; g_zn[g_znN].n = 0;
   ZnClr(g_zn[g_znN]);
   g_znN++;
}
// one CLOSED candle of zone timeframe j (t = its open, te = its close, UTC)
void ZnCandle(int j, long t, long te, double o, double h, double l, double c)
{
   if (!S.obM || j < 0 || j > 2) return;
   for (int i = g_znN - 1; i >= 0; i--)
      if (g_zn[i].tf == j && (g_zn[i].dir == 1 ? c < g_zn[i].bot : c > g_zn[i].top))
      {
         ZnGone(j, g_zn[i].kind, g_zn[i].dir, g_zn[i].top, g_zn[i].bot, g_zn[i].t0);
         ZnDel(i);
      }
   for (int k = 5; k > 0; k--) { g_znCo[j][k] = g_znCo[j][k - 1]; g_znCh[j][k] = g_znCh[j][k - 1]; g_znCl[j][k] = g_znCl[j][k - 1]; g_znCc[j][k] = g_znCc[j][k - 1]; g_znCt[j][k] = g_znCt[j][k - 1]; }
   g_znCo[j][0] = o; g_znCh[j][0] = h; g_znCl[j][0] = l; g_znCc[j][0] = c; g_znCt[j][0] = t;
   if (g_znCn[j] < 6) g_znCn[j]++;
   g_znSeq[j]++;
   if (g_znCn[j] < 3) return;
   for (int a = 0; a < 2; a++)
   {
      int d = a == 0 ? 1 : -1;
      if (!(d == 1 ? g_znCl[j][0] > g_znCh[j][2] : g_znCh[j][0] < g_znCl[j][2])) continue;
      long c1 = g_znSeq[j] - 2;                                      // the number of this FVG's candle 1
      bool burst = c1 >= g_znFc[j][a] && c1 <= g_znFc[j][a] + 2;      // it is one of the last FVG's 3 candles = the same burst
      g_znFc[j][a] = c1;
      if (S.znFvg)
      {
         if (d == 1) ZnAdd(j, 1, 1, g_znCl[j][0], g_znCh[j][2], g_znCt[j][2], te);
         else        ZnAdd(j, -1, 1, g_znCl[j][2], g_znCh[j][0], g_znCt[j][2], te);
      }
      if (!S.znOb) continue;
      int kb = -1;
      if (S.znOb2) { if (!burst) kb = 2; }
      else
         for (int k = 2; k <= 4 && k < g_znCn[j]; k++)
            if (d == 1 ? g_znCc[j][k] < g_znCo[j][k] : g_znCc[j][k] > g_znCo[j][k]) { kb = k; break; }
      if (kb < 0) continue;
      if (!S.znOb2 && g_znCt[j][kb] == g_znObTm[j][a]) continue;   // the same order block candle again
      double tp = g_znCh[j][kb], bt = g_znCl[j][kb];
      if (S.znSw) for (int k = 0; k < kb; k++) { if (d == 1) bt = Mn(bt, g_znCl[j][k]); else tp = Mx(tp, g_znCh[j][k]); }
      ZnAdd(j, d, 0, tp, bt, g_znCt[j][kb], te);
      g_znObTm[j][a] = g_znCt[j][kb];
   }
}
// the touch line of a zone: an order block's near edge; an FVG's 50% line (or its near edge with the far-half switch OFF)
double ZnTl(int i)
{
   if (g_zn[i].kind == 1 && S.znHalf) return (g_zn[i].top + g_zn[i].bot) / 2.0;
   return g_zn[i].dir == 1 ? g_zn[i].top : g_zn[i].bot;
}
// this bar against one zone: touch, the visit's low / high, its liquidity taken
void ZnStep(ZRec &z, double tl)
{
   int    d = z.dir;
   double x = d == 1 ? g_l : g_h;
   if (!z.tch)
   {
      if (z.q && (d == 1 ? x <= tl : x >= tl)) { z.tch = true; z.frz = false; z.ext = x; z.tt = g_t; z.vs = 0; }
      return;
   }
   if (z.spent) return;
   if (!z.frz) { z.ext = d == 1 ? Mn(z.ext, x) : Mx(z.ext, x); return; }
   if (d == 1 ? x < z.ext : x > z.ext)
   {
      if (S.znTwo) { z.frz = false; z.ext = x; z.vs = 0; }
      else z.spent = true;
   }
}
// v15.1: the last zone = among the order blocks of direction d in the leg's zone (not stopped): the biggest timeframe that has one,
// then the deepest (buy: the lowest bottom, sell: the highest top); -1 = none
int LastZn(int d)
{
   int best = -1;
   if (d == 0) return -1;
   for (int i = 0; i < g_znN; i++)
   {
      if (g_zn[i].dir != d || g_zn[i].kind != 0 || !g_zn[i].q || g_zn[i].spent) continue;
      if (best < 0 || g_zn[i].tf > g_zn[best].tf || (g_zn[i].tf == g_zn[best].tf && (d == 1 ? g_zn[i].bot < g_zn[best].bot : g_zn[i].top > g_zn[best].top))) best = i;
   }
   return best;
}
// every chart bar (after the higher timeframe values are set): which zones are in the leg's zone, touches, visits
void ZnBar()
{
   if (!S.obM) return;
   int d = g_T15;
   if (g_htE != g_znLegE)
   {
      // v15.1: a new higher timeframe leg - the zones made before the leg started go (made = the close of the 3rd FVG candle, so a
      // zone whose 3rd candle holds the leg start stays), and the old leg's CHOCH* line
      if (g_znLegE >= 0) ZnGone(9, 2, 0, 0.0, 0.0, (long)g_znLegE);
      if (g_htS != LNONE)
         for (int i = g_znN - 1; i >= 0; i--)
            if (g_zn[i].te <= g_htS) { ZnGone(g_zn[i].tf, g_zn[i].kind, g_zn[i].dir, g_zn[i].top, g_zn[i].bot, g_zn[i].t0); ZnDel(i); }
      g_znLegE = g_htE;
      for (int i = 0; i < g_znN; i++) ZnClr(g_zn[i]);
      ZnClr(g_zl);
      g_zl.n = 0;
   }
   double L = RetLvl(d, g_htX, g_htO, S.znPct), e = S.tick / 2;
   for (int i = 0; i < g_znN; i++)
   {
      g_zn[i].q = false;
      if (d == 0 || g_zn[i].dir != d || IsNa(L) || IsNa(g_htO)) continue;
      double tl = ZnTl(i);
      if (g_zn[i].kind == 0) g_zn[i].q = d == 1 ? (g_zn[i].bot <= L + e && g_zn[i].top >= g_htO - e) : (g_zn[i].top >= L - e && g_zn[i].bot <= g_htO + e);
      else                   g_zn[i].q = d == 1 ? (tl <= L + e && tl >= g_htO - e) : (tl >= L - e && tl <= g_htO + e);
      ZnStep(g_zn[i], tl);
   }
   g_zl.dir = d;
   g_zl.q = S.znLine && d != 0 && !IsNa(g_htO);
   if (g_zl.q) ZnStep(g_zl, g_htO);
   g_lz = LastZn(d);
}
// v15.1: the zones a signal in direction d may trade from (kind 1 = a chart CHOCH / BOS, 2 = an MSS), into g_zc: every touched zone
// (only the biggest timeframe's with 'biggest' ON, only the last zone with 'last zone' ON); a visit that gave an MSS does not count for
// a CHOCH / BOS, a visit that gave any signal does not count for an MSS; none = the CHOCH* line when it was touched
int ZnCount(int d, int kind)
{
   g_zcN = 0;
   int big = -1;
   if (S.znBig && !S.znLast) for (int i = 0; i < g_znN; i++) if (g_zn[i].dir == d && g_zn[i].q && !g_zn[i].spent) big = MxI(big, g_zn[i].tf);
   int lz = S.znLast ? LastZn(d) : -1;
   for (int i = 0; i < g_znN; i++)
   {
      if (g_zn[i].dir != d || !g_zn[i].tch || g_zn[i].spent) continue;
      if (kind == 1 ? g_zn[i].vs == 2 : g_zn[i].vs != 0) continue;
      if (S.znLast ? i != lz : (S.znBig && g_zn[i].tf != big)) continue;
      g_zc[g_zcN++] = i;
   }
   if (g_zcN == 0 && S.znLine && g_zl.dir == d && g_zl.tch && !g_zl.spent && (kind == 1 ? g_zl.vs != 2 : g_zl.vs == 0)) g_zc[g_zcN++] = -1;
   return g_zcN;
}
// the zone named in the notes: the first of the biggest timeframe (-1 = the CHOCH* line, -2 = none)
int ZnPick()
{
   int b = -2, bt = -1;
   for (int a = 0; a < g_zcN; a++) { int i = g_zc[a]; if (i < 0) return -1; if (g_zn[i].tf > bt) { bt = g_zn[i].tf; b = i; } }
   return b;
}
// a with-HTF signal (kind 1 a chart CHOCH / BOS, 2 an MSS) closes the visit of every touched zone of that side
void ZnFreeze(int d, int kind)
{
   for (int i = 0; i < g_znN; i++) if (g_zn[i].dir == d && g_zn[i].tch) { g_zn[i].frz = true; if (g_zn[i].vs == 0) g_zn[i].vs = kind; }
   if (g_zl.dir == d && g_zl.tch) { g_zl.frz = true; if (g_zl.vs == 0) g_zl.vs = kind; }
}
// v15.1: every zone that counted for a with-HTF signal gets it counted and goes to the boxes of this bar
void ZnMark(int d, int kind)
{
   ZnCount(d, kind);
   for (int a = 0; a < g_zcN && g_zbN <= ZMAX; a++)
   {
      int i = g_zc[a];
      if (i >= 0)
      {
         g_zn[i].n++; g_zn[i].t1 = g_t;
         g_zb[g_zbN].tf = g_zn[i].tf; g_zb[g_zbN].kind = g_zn[i].kind; g_zb[g_zbN].n = g_zn[i].n; g_zb[g_zbN].leg = 0;
         g_zb[g_zbN].top = g_zn[i].top; g_zb[g_zbN].bot = g_zn[i].bot; g_zb[g_zbN].t0 = g_zn[i].t0; g_zb[g_zbN].last = i == g_lz;
      }
      else
      {
         g_zl.n++; g_zl.t1 = g_t;
         g_zb[g_zbN].tf = 9; g_zb[g_zbN].kind = 2; g_zb[g_zbN].n = g_zl.n; g_zb[g_zbN].leg = g_znLegE;
         g_zb[g_zbN].top = g_htO; g_zb[g_zbN].bot = g_htO; g_zb[g_zbN].t0 = g_zl.tt; g_zb[g_zbN].last = false;
      }
      g_zb[g_zbN].dir = d; g_zb[g_zbN].t1 = g_t;
      g_zbN++;
   }
}
string ZnName(int tf) { return tf == 0 ? "HTF" : (tf == 1 ? "HTF+1" : (tf == 2 ? "HTF+2" : "CHOCH* line")); }

// ---------- v15.1: the market structure shift (MSS) on the chart (zone modes, section 2) ----------
// A swing high = a candle whose high is above the highs of the N candles on each side (N = 'MSS swing'); the newest one is kept until a
// close goes above it. An MSS up = that first close above it, WITH the higher timeframe, when the move from the lowest low since that
// swing (the MSS low) to this candle holds a chart FVG with its order block (the order block type of the zone settings: type 1 = an
// opposite candle among candle 1 and the 2 before it, type 2 = always), and a zone counts for it (ZnCount kind 2); never on a candle
// with a chart CHOCH / BOS signal (that one is used). Mirror for down.
double g_mo[6], g_mh[6], g_ml[6], g_mc[6];   // the last 6 chart candles (0 = this one)
int    g_mn = 0;
double g_msSw[2];                             // [0] the newest swing high not closed above, [1] the newest swing low not closed below
int    g_msSwB[2];
int    g_mfC1[2];                             // candle 1 bar of the newest chart FVG with its order block: [0] up, [1] down
#define MFMAX 64
int    g_mfB[2][MFMAX];                       // the recent chart FVGs with an order block: candle 1 bar and near edge (up: the 3rd candle's low)
double g_mfE[2][MFMAX];
int    g_mfN[2], g_mfI[2];
bool   g_mfNew[2];                            // one was completed on this bar
bool   g_msU = false, g_msD = false;          // an MSS on this bar
double g_msPiv = NAD, g_msLow = NAD;          // its broken swing, its low (buy) / high (sell)
int    g_msLowB = NAI;
void MsReset()
{
   g_mn = 0; g_msU = false; g_msD = false; g_msPiv = NAD; g_msLow = NAD; g_msLowB = NAI;
   for (int k = 0; k < 6; k++) { g_mo[k] = NAD; g_mh[k] = NAD; g_ml[k] = NAD; g_mc[k] = NAD; }
   for (int a = 0; a < 2; a++) { g_msSw[a] = NAD; g_msSwB[a] = NAI; g_mfC1[a] = NAI; g_mfN[a] = 0; g_mfI[a] = 0; g_mfNew[a] = false; }
}
// the earliest recent chart FVG of side a whose candle 1 is at or after bar b: its near edge (NAD = none)
double MfFirst(int a, int b)
{
   double e = NAD;
   int bb = NAI;
   for (int q = 0; q < g_mfN[a]; q++)
   {
      int w = (g_mfI[a] - 1 - q + 2 * MFMAX) % MFMAX;
      if (g_mfB[a][w] >= b && (bb == NAI || g_mfB[a][w] < bb)) { bb = g_mfB[a][w]; e = g_mfE[a][w]; }
   }
   return e;
}
void MsBar()
{
   g_msU = false; g_msD = false;
   if (!S.obM || !S.mssOn) return;
   for (int k = 5; k > 0; k--) { g_mo[k] = g_mo[k - 1]; g_mh[k] = g_mh[k - 1]; g_ml[k] = g_ml[k - 1]; g_mc[k] = g_mc[k - 1]; }
   g_mo[0] = g_o; g_mh[0] = g_h; g_ml[0] = g_l; g_mc[0] = g_c;
   if (g_mn < 6) g_mn++;
   for (int a = 0; a < 2; a++)
   {
      int d = a == 0 ? 1 : -1;
      g_mfNew[a] = false;
      if (g_mn < 3 || !(d == 1 ? g_ml[0] > g_mh[2] : g_mh[0] < g_ml[2])) continue;
      bool ob = S.znOb2;
      for (int k = 2; k <= 4 && k < g_mn && !ob; k++) if (d == 1 ? g_mc[k] < g_mo[k] : g_mc[k] > g_mo[k]) ob = true;
      if (!ob) continue;
      g_mfC1[a] = EN.bi - 2; g_mfNew[a] = true;
      int w = g_mfI[a];
      g_mfB[a][w] = EN.bi - 2; g_mfE[a][w] = d == 1 ? g_ml[0] : g_mh[0];
      g_mfI[a] = (w + 1) % MFMAX;
      if (g_mfN[a] < MFMAX) g_mfN[a]++;
   }
   int N = S.mssN, n = EN.bufHi.Size();
   if (n >= 2 * N + 1)
   {
      int c = n - 1 - N;
      bool ph = true, pl = true;
      for (int j = n - 1 - 2 * N; j <= n - 1; j++)
      {
         if (j == c) continue;
         if (EN.bufHi.At(j) >= EN.bufHi.At(c)) ph = false;
         if (EN.bufLo.At(j) <= EN.bufLo.At(c)) pl = false;
      }
      if (ph) { g_msSw[0] = EN.bufHi.At(c); g_msSwB[0] = EN.bi - N; }
      if (pl) { g_msSw[1] = EN.bufLo.At(c); g_msSwB[1] = EN.bi - N; }
   }
   bool sU = (S.useCho && EN.evCU) || (S.useBos && EN.evBU), sD = (S.useCho && EN.evCD) || (S.useBos && EN.evBD);
   for (int a = 0; a < 2; a++)
   {
      int d = a == 0 ? 1 : -1;
      if (IsNa(g_msSw[a]) || !(d == 1 ? g_c > g_msSw[a] : g_c < g_msSw[a])) continue;
      double piv = g_msSw[a];
      int    pb = g_msSwB[a];
      g_msSw[a] = NAD;
      if (d != g_T15 || sU || sD) continue;
      double lp = NAD;
      int    lb = NAI;
      EN.RetExt(pb - 1, d == -1, true, lp, lb);   // the lowest low (buy) / highest high (sell) from the swing candle to this one
      if (IsNa(lp) || g_mfC1[a] == NAI || g_mfC1[a] < lb) continue;
      if (ZnCount(d, 2) == 0) continue;
      if (d == 1) g_msU = true; else g_msD = true;
      g_msPiv = piv; g_msLow = lp; g_msLowB = lb;
   }
}

'''
s = s[:a] + ZONE + s[b:]

# ---------------------------------------------------------------- money: the every-other-day mode after the pause (section 8)
rep('''   int    cntSeqCap, dayTrades, lsRun, cntLs, ldRun, cntLd, prevDom;
   double basNow;    // v12.2: the base risk in use (the profit step with Rule A / B / C split)
   long   ldUntil, prevWk, liveT;''', '''   int    cntSeqCap, dayTrades, lsRun, cntLs, ldRun, cntLd, prevDom;
   double basNow;    // v12.2: the base risk in use (the profit step with Rule A / B / C split)
   long   ldUntil, prevWk, liveT;
   bool   ldAft, ldAlt;   // v15.1: after a pause (counting the losses in a row again), in the every-other-day mode
   int    ld2Run, cntLd2;
   long   ldAltD;         //   the day (session timezone, days since 1970) that mode started''')
rep('''      cntSeqCap = 0; dayTrades = 0; lsRun = 0; cntLs = 0; ldRun = 0; cntLd = 0; prevDom = -1;
      basNow = 0;
      ldUntil = LNONE; prevWk = LNONE;''', '''      cntSeqCap = 0; dayTrades = 0; lsRun = 0; cntLs = 0; ldRun = 0; cntLd = 0; prevDom = -1;
      basNow = 0;
      ldUntil = LNONE; prevWk = LNONE;
      ldAft = false; ldAlt = false; ld2Run = 0; cntLd2 = 0; ldAltD = LNONE;''')
rep('''   bool   LdHalt(long t) { return S.ldOn && ldUntil != LNONE && t < ldUntil; }
''', '''   bool   LdHalt(long t) { return S.ldOn && ldUntil != LNONE && t < ldUntil; }
   // v15.1: the every-other-day mode - no new trades the rest of the day it started, then only on every (skip + 1)-th trading day
   // (Monday - Friday; every day with 'Trade 24/7') until a winning trade
   bool   AltHalt(long t)
   {
      if (!S.ldOn || !ldAlt) return false;
      long dn = FloorDivL(SessLoc(t), 86400);
      if (dn <= ldAltD) return true;
      int w = DowDays(dn);
      if (!S.wk247 && (w == 7 || w == 1)) return true;
      long full = (dn - ldAltD) / 7, rem = (dn - ldAltD) % 7;
      long m = full * (S.wk247 ? 7 : 5);
      for (long k = 1; k <= rem; k++) { int ww = DowDays(ldAltD + full * 7 + k); if (S.wk247 || (ww != 7 && ww != 1)) m++; }
      return m % (S.ldSkip + 1) != 0;
   }
''')
rep('''         if (S.ldOn && Counts(g_io[ks[a]].cls[ix[a]].tIn) && !(ldUntil != LNONE && gx < ldUntil))
         {
            ldRun = gp < 0 ? ldRun + 1 : (gp > 0 ? 0 : ldRun);
            if (ldRun >= S.ldN) { ldUntil = LdUntil(gx); ldRun = 0; cntLd++; }
         }''', '''         if (S.ldOn && Counts(g_io[ks[a]].cls[ix[a]].tIn) && !(ldUntil != LNONE && gx < ldUntil))
         {
            if (ldAlt) { if (gp > 0) { ldAlt = false; ldAft = false; ldRun = 0; } }   // v15.1: a winning trade ends that mode
            else if (ldAft)
            {   // v15.1: after the pause - losses in a row start the every-other-day mode, a winning trade = back to normal
               ld2Run = gp < 0 ? ld2Run + 1 : (gp > 0 ? 0 : ld2Run);
               if (gp > 0) { ldAft = false; ld2Run = 0; ldRun = 0; }
               else if (ld2Run >= S.ldN2) { ldAlt = true; ldAltD = FloorDivL(SessLoc(gx), 86400); ld2Run = 0; cntLd2++; }
            }
            else
            {
               ldRun = gp < 0 ? ldRun + 1 : (gp > 0 ? 0 : ldRun);
               if (ldRun >= S.ldN) { ldUntil = LdUntil(gx); ldRun = 0; cntLd++; ldAft = S.ldN2 > 0; ld2Run = 0; }
            }
         }''')

# ---------------------------------------------------------------- one side: the setup's zones, MSS, confirmation
rep('''   int    znTf, cntOb;                // v15.0: the zone of the setup (timeframe 0-2, 9 = the CHOCH* line, -1 = none); skipped (no zone)
   double znTop, znBot;''', '''   int    znTf, cntOb;                // v15.0: the zone of the setup (timeframe 0-2, 9 = the CHOCH* line, -1 = none); skipped (no zone)
   int    nSup;                       // v15.1: the zones that allowed the waiting setup (timeframe, kind, side, top, bottom, candle time;
   int    supTf[ZMAX + 1], supK[ZMAX + 1], supD[ZMAX + 1];   //   the CHOCH* line: 9, 2, 0, 0, 0, its leg) - all gone = cancelled
   double supT[ZMAX + 1], supB[ZMAX + 1];
   long   supT0[ZMAX + 1];
   int    src;                        // v15.1: 0 = a chart CHOCH / BOS setup, 1 = an MSS setup
   double msLow, msAnch, cfTop, cfPb; // v15.1 MSS: its low (buy) / high, the move's extreme since (rule 1), the first FVG's near edge,
   int    msBar, cf, cfTchB;          //   the pullback low; the MSS bar; confirmation 0 none, 1 waiting for the pullback, 2 for the new FVG
   int    cntMs, cntMsCf, cntMsF;     //   MSS setups, confirmed, failed''')
rep('''      znTf = -1; znTop = NAD; znBot = NAD; cntOb = 0;''', '''      znTf = -1; cntOb = 0; nSup = 0;
      src = 0; msLow = NAD; msAnch = NAD; cfTop = NAD; cfPb = NAD; msBar = NAI; cf = 0; cfTchB = NAI; cntMs = 0; cntMsCf = 0; cntMsF = 0;''')
rep('''   string XSkip(int d, double piv, double opl)
   {''', '''   string XSkip(int d, double piv, double opl, int lb)
   {''')
rep('''      int lb = d == 1 ? EN.bi - EN.flr.x1 : EN.bi - EN.cel.x1;
      if (S.legMin > 0 && lb < S.legMin)''', '''      if (S.legMin > 0 && lb < S.legMin)''')
rep('''      if (g_money[mi].LdHalt(g_t)) return "loss pause (days)";''', '''      if (g_money[mi].LdHalt(g_t)) return "loss pause (days)";
      if (g_money[mi].AltHalt(g_t)) return "loss pause (every other day)";   // v15.1''')
rep('''      if (dir != 0 && (!go || (td != 0 && td != dir))) Cancel(!go ? "CANCELLED - blocked (" + blk + ")" : "CANCELLED - trend flipped");''',
    '''      if (dir != 0 && (!go || (src == 0 && td != 0 && td != dir))) Cancel(!go ? "CANCELLED - blocked (" + blk + ")" : "CANCELLED - trend flipped");
      // v15.1: an MSS setup (any chart trend) goes when the chart prints a CHOCH / BOS the other way
      if (dir != 0 && src == 1 && (dir == 1 ? (S.useCho && EN.evCD) || (S.useBos && EN.evBD) : (S.useCho && EN.evCU) || (S.useBos && EN.evBU))) Cancel("CANCELLED - CHOCH / BOS the other way");''')
rep('''      if (S.obM && dir != 0 && znTf >= 0 && znTf <= 2 && ZnDead(znTf, znTop, znBot)) Cancel("CANCELLED - its zone was broken by a close");''',
    '''      // v15.1: ... when ALL the zones that allowed it are gone (broken by a close of their own timeframe, made before a new leg)
      if (S.obM && dir != 0 && nSup > 0 && g_zdN > 0)
      {
         for (int i = nSup - 1; i >= 0; i--)
            if (ZnIsGone(supTf[i], supK[i], supD[i], supT[i], supB[i], supT0[i]))
            {
               for (int j = i; j + 1 < nSup; j++) { supTf[j] = supTf[j + 1]; supK[j] = supK[j + 1]; supD[j] = supD[j + 1]; supT[j] = supT[j + 1]; supB[j] = supB[j + 1]; supT0[j] = supT0[j + 1]; }
               nSup--;
            }
         if (nSup == 0) Cancel("CANCELLED - its zones are gone (broken by a close / a new higher timeframe leg)");
      }''')
rep('''      if (S.bosCnl && dir != 0 && armBar != NAI && EN.bi > armBar && ((dir == 1 && EN.evBU) || (dir == -1 && EN.evBD)))''',
    '''      if (S.bosCnl && dir != 0 && src == 0 && armBar != NAI && EN.bi > armBar && ((dir == 1 && EN.evBU) || (dir == -1 && EN.evBD)))''')
rep('''      if (dir != 0 && rule == 3 && ((mktBar != NAI && EN.bi > mktBar) || (armBar != NAI && EN.bi > armBar + 1))) Cancel("CANCELLED - the entry at the signal close did not fill");
      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with
      if (dir != 0 && rule != 2 && rule != 3 && !(S.once && placed))''', '''      if (dir != 0 && rule == 3 && ((mktBar != NAI && EN.bi > mktBar) || (armBar != NAI && EN.bi > armBar + 1))) Cancel("CANCELLED - the entry at the signal close did not fill");
      // v15.1: an MSS waiting for its confirmation (rule 4): the price beyond the MSS low (high) = it failed; a pullback to the first FVG
      // of the MSS move, then a NEW chart FVG with its order block (candle 1 at or after the pullback candle) = enter at its close
      if (dir != 0 && rule == 4)
      {
         if (dir == 1 ? g_l < msLow : g_h > msLow) { cntMsF++; Cancel("CANCELLED - MSS failed (the price went beyond the MSS " + (dir == 1 ? (string)"low " : "high ") + TkS(msLow) + ")"); }
         else
         {
            if (EN.bi > msBar) cfPb = IsNa(cfPb) ? (dir == 1 ? g_l : g_h) : (dir == 1 ? Mn(cfPb, g_l) : Mx(cfPb, g_h));
            int fa = dir == 1 ? 0 : 1;
            if (cf == 2 && g_mfNew[fa] && g_mfC1[fa] >= cfTchB)
            {
               double lv = S.mssSt == 1 ? cfPb : msLow;
               sl = dir == 1 ? lv - BufAt(lv) : lv + BufAt(lv);
               rule = 3; cf = 3; armBar = EN.bi; mktBar = NAI;
               cntMsCf++;
               Note(Id() + " MSS CONFIRMED - entry at the close, stop " + TkS(sl));
            }
            if (cf == 1 && EN.bi > msBar && !IsNa(cfTop) && (dir == 1 ? g_l <= cfTop : g_h >= cfTop)) { cf = 2; cfTchB = EN.bi; }
         }
      }
      if (dir != 0 && src == 1) msAnch = dir == 1 ? Mx(msAnch, g_h) : Mn(msAnch, g_l);   // v15.1: the MSS move's extreme (rule 1)
      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with
      if (dir != 0 && src == 0 && rule != 2 && rule != 3 && !(S.once && placed))''')
rep('''      bool sigUp = (S.useCho && EN.evCU) || (S.useBos && EN.evBU);
      bool sigDn = (S.useCho && EN.evCD) || (S.useBos && EN.evBD);
      bool opp   = (pos > 0 && sigDn) || (pos < 0 && sigUp);''', '''      bool isMs  = g_msU || g_msD;   // v15.1: an MSS (never on a candle with a chart CHOCH / BOS signal)
      bool sigUp = (S.useCho && EN.evCU) || (S.useBos && EN.evBU) || g_msU;
      bool sigDn = (S.useCho && EN.evCD) || (S.useBos && EN.evBD) || g_msD;
      bool opp   = (pos > 0 && sigDn) || (pos < 0 && sigUp);''')
rep('''      string sg = ((EN.evCU || EN.evCD) && S.useCho) ? "CHOCH" : "BOS";''',
    '''      string sg = isMs ? "MSS" : (((EN.evCU || EN.evCD) && S.useCho) ? "CHOCH" : "BOS");''')
rep('''         if (S.cancelSig && dir != 0) Cancel("CANCELLED - new signal");''',
    '''         // v15.1: a CHOCH / BOS the same way that no zone allows (its visit gave the MSS) leaves a waiting MSS setup alone
         bool keepMs = dir != 0 && src == 1 && !isMs && dir == (sigUp ? 1 : -1) && ZnCount(dir, 1) == 0;
         if (S.cancelSig && dir != 0 && !keepMs) Cancel("CANCELLED - new signal");''')
rep('''            double piv  = sigUp ? g_ceilPrev : g_florPrev;
            double opl  = NAD;
            if (d == 1 && EN.flr.ok) opl = EN.flr.price;
            if (d == -1 && EN.cel.ok) opl = EN.cel.price;''', '''            double piv  = isMs ? g_msPiv : (sigUp ? g_ceilPrev : g_florPrev);
            double opl  = NAD;
            if (isMs) opl = g_msLow;   // v15.1: an MSS - the broken swing, the MSS low (high) is the stop level
            else
            {
               if (d == 1 && EN.flr.ok) opl = EN.flr.price;
               if (d == -1 && EN.cel.ok) opl = EN.cel.price;
            }''')
rep('''            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;''', '''            // v15.1: an MSS entered on its confirmation uses none of rules 1 / 2 / 3
            bool msCf = isMs && S.mssCf;
            if (msCf) { use = true; hfSkip = false; r3Use = false; r3Far = false; r3Fb = false; }
            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;''')
rep('''               zk = d == g_T15 ? ZnAllow(d) : 0;''', '''               zk = d == g_T15 ? ZnCount(d, isMs ? 2 : 1) : 0;''')
rep('''            if (use && !IsNa(opl)) xs = XSkip(d, piv, opl);''',
    '''            if (use && !IsNa(opl)) xs = XSkip(d, piv, opl, isMs ? EN.bi - g_msLowB : (d == 1 ? EN.bi - EN.flr.x1 : EN.bi - EN.cel.x1));''')
rep('''               rule    = r3Use ? 3 : ((agree && S.r2 && !S.agn) ? 2 : 1);
               mktBar  = NAI;
               sl      = d == 1 ? opl - BufAt(opl) : opl + BufAt(opl);
               fix     = rule == 2 ? piv : NAD;
               znTf    = -1; znTop = NAD; znBot = NAD;
               if (S.obM) { if (zk > 0) { znTf = g_zn[zk - 1].tf; znTop = g_zn[zk - 1].top; znBot = g_zn[zk - 1].bot; } else znTf = 9; }
               Note(sg + ": " + Id() + (rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED")) + (!S.obM ? (string)"" : (znTf == 9 ? (string)" (CHOCH* line)" : " (" + ZnName(znTf) + (g_zn[zk - 1].kind == 0 ? " order block)" : " FVG)"))) + (!r3Fb ? (string)"" : (IsNa(r3B) ? (string)" (RULE 3: no broken level - fall back)" : " (RULE 3: close " + DoubleToString(r3B, 2) + " beyond the broken level - fall back)")));''',
    '''               rule    = r3Use ? 3 : ((agree && S.r2 && !S.agn) ? 2 : 1);
               mktBar  = NAI;
               sl      = d == 1 ? opl - BufAt(opl) : opl + BufAt(opl);
               fix     = rule == 2 ? piv : NAD;
               znTf    = -1;
               nSup    = 0;
               string zt = "";
               if (S.obM)
               {   // v15.1: every zone that allowed it (the setup goes when they are ALL gone); the notes name the biggest timeframe's
                  for (int a = 0; a < g_zcN; a++)
                  {
                     int i = g_zc[a];
                     if (i >= 0) { supTf[nSup] = g_zn[i].tf; supK[nSup] = g_zn[i].kind; supD[nSup] = g_zn[i].dir; supT[nSup] = g_zn[i].top; supB[nSup] = g_zn[i].bot; supT0[nSup] = g_zn[i].t0; }
                     else        { supTf[nSup] = 9; supK[nSup] = 2; supD[nSup] = 0; supT[nSup] = 0; supB[nSup] = 0; supT0[nSup] = g_znLegE; }
                     nSup++;
                  }
                  int pk = ZnPick();
                  znTf = pk == -1 ? 9 : (pk >= 0 ? g_zn[pk].tf : -1);
                  zt = pk == -1 ? (string)" (CHOCH* line)" : (pk >= 0 ? " (" + ZnName(znTf) + (g_zn[pk].kind == 0 ? " order block" : " FVG") + (nSup > 1 ? ", " + IntegerToString(nSup) + " zones)" : ")") : (string)"");
               }
               src = isMs ? 1 : 0;
               cf  = 0;
               if (isMs)
               {   // v15.1: the MSS - its low (high), the move's extreme since (rule 1); with the confirmation: wait (rule 4)
                  msLow = opl; msBar = EN.bi;
                  double ap = NAD;
                  int    ab = NAI;
                  EN.RetExt(g_msLowB - 1, d == 1, true, ap, ab);
                  msAnch = ap;
                  cntMs++;
                  if (S.mssCf) { rule = 4; cf = 1; cfTop = MfFirst(d == 1 ? 0 : 1, g_msLowB); cfTchB = NAI; cfPb = NAD; fix = NAD; }
               }
               Note(sg + ": " + Id() + (rule == 4 ? " WAITING for the MSS confirmation (pullback to " + TkS(cfTop) + ")" : (rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED"))) + zt + (!r3Fb ? (string)"" : (IsNa(r3B) ? (string)" (RULE 3: no broken level - fall back)" : " (RULE 3: close " + DoubleToString(r3B, 2) + " beyond the broken level - fall back)")));''')
rep('''         ent = rule == 3 ? g_c : ((S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb)));''',
    '''         ent = rule == 4 ? NAD : (rule == 3 ? g_c : ((S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : (src == 1 ? RetLvl(dir, msAnch, msLow, S.pb) : RetLvl(td, g_mAnch, g_mOrig, S.pb)))));''')
rep('''         double pdL = S.pdOn ? RetLvl(td, g_mAnch, g_mOrig, S.pdPct) : NAD;''',
    '''         double pdL = S.pdOn ? (src == 1 ? RetLvl(dir, msAnch, msLow, S.pdPct) : RetLvl(td, g_mAnch, g_mOrig, S.pdPct)) : NAD;''')

# ---------------------------------------------------------------- setup and one bar
rep('''   ZnReset();   // v15.0
   g_nSides''', '''   ZnReset();   // v15.0
   MsReset();   // v15.1
   g_htS = LNONE;
   g_nSides''')
rep('''void CoreBar(long t, double o, double h, double l, double c, double eq, int htT, double htO, double htX, int htE)
{
   g_t = t; g_o = o; g_h = h; g_l = l; g_c = c; g_eq = eq;
   g_zbOn = false;   // v15.0''', '''void CoreBar(long t, double o, double h, double l, double c, double eq, int htT, double htO, double htX, int htE, long htS)
{
   g_t = t; g_o = o; g_h = h; g_l = l; g_c = c; g_eq = eq;
   g_zbN = 0;   // v15.1''')
rep('''   g_htE = S.u15 ? htE : 0;
   ZnBar();   // v15.0: zones in the leg's zone, touches, visits''', '''   g_htE = S.u15 ? htE : 0;
   g_htS = S.u15 ? htS : LNONE;   // v15.1
   ZnBar();   // v15.0: zones in the leg's zone, touches, visits
   MsBar();   // v15.1: the chart's swings, FVGs and the MSS''')
rep('''   bool dead = S.timeOn && (S.hrFlat != S.hrOn ?''', '''   bool dead = S.timeOn && S.flOn && (S.hrFlat != S.hrOn ?''')
rep('''      if ((g_T15 == 1 && sU) || (g_T15 == -1 && sD)) { ZnBox(g_T15); ZnFreeze(g_T15); }
   }
   // v15.0: only a zone broken by a close on THIS bar cancels a waiting setup (as in TradingView) - forget this bar's
   if (g_znDn > 0) { for (int i = 0; i < 32; i++) g_znDtf[i] = -1; g_znDn = 0; }''', '''      if ((g_T15 == 1 && sU) || (g_T15 == -1 && sD)) { ZnMark(g_T15, 1); ZnFreeze(g_T15, 1); }
      else if (g_msU || g_msD) { ZnMark(g_T15, 2); ZnFreeze(g_T15, 2); }   // v15.1: an MSS closes the visit too
   }
   // only a zone gone on THIS bar cancels a waiting setup (as in TradingView) - forget this bar's
   g_zdN = 0;''')

# ---------------------------------------------------------------- MT5 part: settings, checks
rep('''   S.znPct = InZnPct; S.znBig = InZnBig; S.znOb = InZnOb; S.znFvg = InZnFvg; S.znHalf = InZnHalf; S.znTwo = InZnTwo; S.znLine = InZnLine;
''', '''   S.znPct = InZnPct; S.znBig = InZnBig; S.znOb = InZnOb; S.znFvg = InZnFvg; S.znHalf = InZnHalf; S.znTwo = InZnTwo; S.znLine = InZnLine;
   S.pxOff = InPxOff; S.fl1m = InFl1m; S.znLast = InZnLast; S.znSw = InZnSw; S.znOb2 = InZnOb2;   // v15.1
   S.mssOn = InMssOn; S.mssN = InMssN; S.mssCf = InMssCf; S.mssSt = (int)InMssSt; S.ldN2 = InLdN2; S.ldSkip = InLdSkip;
''')
rep('''   if ((int)InSig >= 12 && !InZnOb && !InZnFvg) return "Order block zone mode (section 2): turn on 'use order blocks' or 'use FVGs'";
''', '''   if ((int)InSig >= 12 && !InZnOb && !InZnFvg) return "Order block zone mode (section 2): turn on 'use order blocks' or 'use FVGs'";
   // v15.1
   if ((int)InSig >= 12 && InZnLast && !InZnOb) return "Only trade from the last zone (section 2): the last zone is an order block - turn on 'use order blocks'";
   if (InMssN < 1 || InMssN > 10) return "MSS swing (section 2): candles on each side must be 1 - 10";
   if (InLdN2 < 0 || InLdN2 > 50 || InLdSkip < 1 || InLdSkip > 10) return "Pause (section 8): losses after the pause 0 - 50, days skipped 1 - 10";
   if (InZnV0 < 0 || InZnV0 > 100 || InZnV1 < 0 || InZnV1 > 100 || InZnV2 < 0 || InZnV2 > 100) return "Zone fill visible % (section 13) must be 0 - 100";
''')

# ---------------------------------------------------------------- MT5 part: the leg start time, the zone candles' close times
rep('''void HtfStep(MqlRates &r)
{
   HT.Step(r.open, r.high, r.low, r.close);
   ZnCandle(0, SrvToUtc(r.time), r.open, r.high, r.low, r.close);   // v15.0: zones of the higher timeframe''', '''// v15.1: the close of a candle of period p that opened at t (server time; a month: the 1st of the next month)
datetime TfEnd(ENUM_TIMEFRAMES p, datetime t)
{
   if (p != PERIOD_MN1) return t + PeriodSeconds(p);
   int y = 0, m = 0, d = 0;
   CivilFromDays(FloorDivL((long)t, 86400), y, m, d);
   if (++m > 12) { m = 1; y++; }
   return (datetime)(DaysFromCivil(y, m, 1) * 86400);
}
void HtfStep(MqlRates &r)
{
   HT.tNow = SrvToUtc(r.time);   // v15.1: the leg start time
   HT.Step(r.open, r.high, r.low, r.close);
   ZnCandle(0, SrvToUtc(r.time), SrvToUtc(TfEnd(g_htf, r.time)), r.open, r.high, r.low, r.close);   // v15.0: zones of the higher timeframe''')
rep('''         if (zr[i].time > g_znFed[j] && zr[i].time < hc) { ZnCandle(j, SrvToUtc(zr[i].time), zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }''',
    '''         if (zr[i].time > g_znFed[j] && zr[i].time < hc) { ZnCandle(j, SrvToUtc(zr[i].time), SrvToUtc(TfEnd(g_znPer[j], zr[i].time)), zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }''')
rep('''      for (int i = 0; i < m; i++) if (zr[i].time < zc0) { ZnCandle(j, SrvToUtc(zr[i].time), zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }''',
    '''      for (int i = 0; i < m; i++) if (zr[i].time < zc0) { ZnCandle(j, SrvToUtc(zr[i].time), SrvToUtc(TfEnd(g_znPer[j], zr[i].time)), zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }''')
rep('''   int    ht = 0, he = 0;
   double ho = NAD, hx = NAD;
   if (g_htfUse) { ht = HT.tTrend; ho = HT.outO; hx = HT.outX; he = HT.evN; }
   CoreBar(SrvToUtc(r.time), r.open, r.high, r.low, r.close, dry ? 0.0 : AccountInfoDouble(ACCOUNT_EQUITY), ht, ho, hx, he);''',
    '''   int    ht = 0, he = 0;
   double ho = NAD, hx = NAD;
   long   hs = LNONE;
   if (g_htfUse) { ht = HT.tTrend; ho = HT.outO; hx = HT.outX; he = HT.evN; hs = HT.legT; }
   CoreBar(SrvToUtc(r.time), r.open, r.high, r.low, r.close, dry ? 0.0 : AccountInfoDouble(ACCOUNT_EQUITY), ht, ho, hx, he, hs);''')

# ---------------------------------------------------------------- MT5 part: drawing the zone boxes
rep('''      if (InZnBox && g_zbOn) DrawZnBox();   // v15.0''', '''      if (InZnBox && g_zbN > 0) DrawZnBox();   // v15.1: every zone that counted for a signal on this bar''')
rep('''void DrawZnBox();   // v15.0
''', '''void DrawZnBox();   // v15.0 / v15.1
void DrawZnAll(datetime tNow);   // v15.1
''')
a = s.index('// v15.0: the zone that was touched and then gave the chart signal with the higher timeframe: a box from the zone\'s candle (the')
b = s.index('// a higher-timeframe CHOCH / BOS that just happened: the broken level')
DRAW = r'''// v15.1: the zone boxes. A zone that counted for a with-HTF signal: ONE box (named by the zone, so its next signal stretches it), from
// the zone's candle (the CHOCH* line: its first touch) to its last signal, text '1h OB x3'; green = buy zone, red = sell zone
// (darker when it was the last zone at that signal); an FVG with 'far half' ON is drawn as its far half. The newest 440 are kept.
string g_zbNm[];
int    g_zbHd = 0;
string TfShort(int j)
{
   ENUM_TIMEFRAMES p = g_znPer[j];
   if (p == PERIOD_M15) return "15m";
   if (p == PERIOD_H1) return "1h";
   if (p == PERIOD_H4) return "4h";
   if (p == PERIOD_D1) return "1D";
   if (p == PERIOD_W1) return "1W";
   if (p == PERIOD_MN1) return "1M";
   return TfName(p);
}
string ZnBoxNm(string pre, int tf, int kind, int dir, long key) { return g_P + pre + IntegerToString(tf) + IntegerToString(kind) + (dir == 1 ? "u" : "d") + IntegerToString(key); }
void ZnRect(string nm, datetime t1, double p1, datetime t2, double p2, color c, bool fill, int width, string tip)
{
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_RECTANGLE, 0, t1, p1, t2, p2);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
   }
   else { ObjectMove(0, nm, 0, t1, p1); ObjectMove(0, nm, 1, t2, p2); }
   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   ObjectSetInteger(0, nm, OBJPROP_FILL, fill);
   ObjectSetInteger(0, nm, OBJPROP_WIDTH, width);
   ObjectSetString(0, nm, OBJPROP_TOOLTIP, tip);
}
void DrawZnBox()
{
   for (int a = 0; a < g_zbN; a++)
   {
      int    tf = g_zb[a].tf, kd = g_zb[a].kind, dr = g_zb[a].dir;
      string nm = ZnBoxNm("Z", tf, kd, dr, tf == 9 ? (long)g_zb[a].leg : g_zb[a].t0);
      string tx = (tf == 9 ? "HTF CHOCH* line" : TfShort(tf) + (kd == 0 ? " OB" : " FVG")) + (g_zb[a].n > 1 ? " x" + IntegerToString(g_zb[a].n) : "");
      color  c  = dr == 1 ? (g_zb[a].last ? clrDarkGreen : clrSeaGreen) : (g_zb[a].last ? clrMaroon : clrIndianRed);
      double tp = g_zb[a].top, bt = g_zb[a].bot;
      if (kd == 1 && S.znHalf) { double m = (tp + bt) / 2.0; if (dr == 1) tp = m; else bt = m; }
      datetime t1 = UtcToSrv(g_zb[a].t0), t2 = UtcToSrv(g_zb[a].t1);
      if (ObjectFind(0, nm) < 0)
      {
         int n = ArraySize(g_zbNm);
         ArrayResize(g_zbNm, n + 1, 256);
         g_zbNm[n] = nm;
         if (n + 1 - g_zbHd > 440) { DelObj(g_zbNm[g_zbHd]); g_zbHd++; }
         if (g_zbHd > 2000) { int m = ArraySize(g_zbNm) - g_zbHd; for (int i = 0; i < m; i++) g_zbNm[i] = g_zbNm[g_zbHd + i]; ArrayResize(g_zbNm, m); g_zbHd = 0; }
      }
      ZnRect(nm, t1, tp, t2, bt, c, true, 1, tx + (dr == 1 ? " (buy) " : " (sell) ") + TkS(g_zb[a].bot) + " - " + TkS(g_zb[a].top));
      DrawText(nm + "t", t1, dr == 1 ? tp : bt, tx, c, dr == 1 ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
   }
}
// v15.1 'show all zones': every live zone of the higher timeframe direction in the leg's zone that has not given a signal yet (those
// have their signal box), redrawn on every new bar to the current candle: the order block / FVG colour mixed with the chart background
// (visible % per timeframe: MT5 boxes cannot be see-through), a border on the higher timeframe's zones; the last zone darker
color ZnMix(color c, int pct)
{
   long bg = ChartGetInteger(0, CHART_COLOR_BACKGROUND);
   int  v = MxI(0, MnI(100, pct));
   int  r = (int)(bg & 0xFF) + ((int)(c & 0xFF) - (int)(bg & 0xFF)) * v / 100;
   int  g = (int)((bg >> 8) & 0xFF) + ((int)((c >> 8) & 0xFF) - (int)((bg >> 8) & 0xFF)) * v / 100;
   int  b = (int)((bg >> 16) & 0xFF) + ((int)((c >> 16) & 0xFF) - (int)((bg >> 16) & 0xFF)) * v / 100;
   return (color)(r | (g << 8) | (b << 16));
}
void DrawZnAll(datetime tNow)
{
   ObjectsDeleteAll(0, g_P + "ZA");
   if (!InZnAll || !S.obM) return;
   for (int i = 0; i < g_znN; i++)
   {
      if (!g_zn[i].q || g_zn[i].spent || g_zn[i].n > 0) continue;
      int    tf = g_zn[i].tf, kd = g_zn[i].kind, dr = g_zn[i].dir;
      bool   last = i == g_lz;
      color  c  = kd == 0 ? (dr == 1 ? InZnCObB : InZnCObS) : (dr == 1 ? InZnCFvB : InZnCFvS);
      int    v  = tf == 0 ? InZnV0 : (tf == 1 ? InZnV1 : InZnV2);
      if (last) v = MnI(90, v + 25);
      double tp = g_zn[i].top, bt = g_zn[i].bot;
      if (kd == 1 && S.znHalf) { double m = (tp + bt) / 2.0; if (dr == 1) tp = m; else bt = m; }
      string nm = ZnBoxNm("ZA", tf, kd, dr, g_zn[i].t0);
      string tx = TfShort(tf) + (kd == 0 ? " OB" : " FVG") + (last ? " (last)" : "");
      datetime t1 = UtcToSrv(g_zn[i].t0);
      ZnRect(nm, t1, tp, tNow, bt, ZnMix(c, v), true, 1, tx + (dr == 1 ? " (buy) " : " (sell) ") + TkS(g_zn[i].bot) + " - " + TkS(g_zn[i].top));
      if (tf == 0 || last) ZnRect(nm + "b", t1, tp, tNow, bt, c, false, last ? 2 : 1, tx);
      DrawText(nm + "t", t1, dr == 1 ? tp : bt, tx, tf == 0 ? c : InZnCLb, dr == 1 ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
   }
}
'''
s = s[:a] + DRAW + s[b:]
rep('''void DrawAll(datetime tNow)
{
   DrawHtfLive(tNow);''', '''void DrawAll(datetime tNow)
{
   DrawHtfLive(tNow);
   DrawZnAll(tNow);   // v15.1''')

# ---------------------------------------------------------------- MT5 part: the table
rep('''   return (g_T15 == 1 ? "buy zones " : (g_T15 == -1 ? "sell zones " : "zones ")) + s + "  |  touched " + I2(t) + (S.znLine && g_zl.tch && !g_zl.spent ? " + CHOCH* line" : "") +
          "  |  skipped (no zone) " + CntTxt(17);''', '''   string lz = g_lz >= 0 ? "  |  last zone " + TfShort(g_zn[g_lz].tf) + " OB " + TkS(g_zn[g_lz].bot) + " - " + TkS(g_zn[g_lz].top) : "";
   string ms = S.mssOn ? "  |  MSS " + CntTxt(18) + (S.mssCf ? " (confirmed " + CntTxt(19) + ", failed " + CntTxt(32) + ")" : "") : "";
   return (g_T15 == 1 ? "buy zones " : (g_T15 == -1 ? "sell zones " : "zones ")) + s + "  |  touched " + I2(t) + (S.znLine && g_zl.tch && !g_zl.spent ? " + CHOCH* line" : "") +
          "  |  skipped (no zone) " + CntTxt(17) + lz + ms;''')
rep('''   if (what == 17) return g_side[k].cntOb;   // v15.0''', '''   if (what == 17) return g_side[k].cntOb;   // v15.0
   if (what == 18) return g_side[k].cntMs;   // v15.1
   if (what == 19) return g_side[k].cntMsCf;
   if (what == 32) return g_side[k].cntMsF;''')
rep('''   string t = g_money[mi].LdHalt(g_t) ? "PAUSED until " + SessTime(g_money[mi].ldUntil, true) : I2(g_money[mi].ldRun) + " of " + I2(S.ldN) + " losses in a row";
   return t + "  |  pauses so far " + I2(g_money[mi].cntLd);''', '''   string t = g_money[mi].LdHalt(g_t) ? "PAUSED until " + SessTime(g_money[mi].ldUntil, true) : I2(g_money[mi].ldRun) + " of " + I2(S.ldN) + " losses in a row";
   if (S.ldN2 > 0)   // v15.1: after the pause / the every-other-day mode
      t = g_money[mi].ldAlt ? (g_money[mi].AltHalt(g_t) ? "EVERY OTHER DAY - not today" : "EVERY OTHER DAY - a trading day") + (string)" (until a winning trade)" :
          (g_money[mi].ldAft && !g_money[mi].LdHalt(g_t) ? "after the pause: " + I2(g_money[mi].ld2Run) + " of " + I2(S.ldN2) + " losses in a row" : t);
   return t + "  |  pauses so far " + I2(g_money[mi].cntLd) + (S.ldN2 > 0 ? " / every-other-day " + I2(g_money[mi].cntLd2) : "");''')
rep('''          !S.ldOn ? clrGray : (g_money[mi].LdHalt(g_t) ? clrRed : clrAqua));
   Row("HTF EQUILIBRIUM FIRST (section 4)"''', '''          !S.ldOn ? clrGray : (g_money[mi].LdHalt(g_t) || g_money[mi].AltHalt(g_t) ? clrRed : clrAqua));
   Row("HTF EQUILIBRIUM FIRST (section 4)"''')

# ---------------------------------------------------------------- MT5 part: restart safety (the setup's zones, MSS, confirmation)
rep('''      GvSet(GvSide(k, "zf"), g_side[k].znTf); GvSet(GvSide(k, "zt"), g_side[k].znTop); GvSet(GvSide(k, "zb"), g_side[k].znBot);   // v15.0''',
    '''      GvSet(GvSide(k, "zf"), g_side[k].znTf);   // v15.0
      // v15.1: the zones that allowed the waiting setup (the first 12), the MSS and its confirmation
      int ns = MnI(g_side[k].nSup, 12);
      GvSet(GvSide(k, "zn"), ns);
      for (int j = 0; j < ns; j++)
      {
         string z = GvSide(k, "z" + IntegerToString(j));
         GvSet(z + "f", g_side[k].supTf[j] * 100 + g_side[k].supK[j] * 10 + g_side[k].supD[j] + 1); GvSet(z + "t", g_side[k].supT[j]);
         GvSet(z + "b", g_side[k].supB[j]); GvSet(z + "0", (double)g_side[k].supT0[j]);
      }
      GvSet(GvSide(k, "src"), g_side[k].src); GvSet(GvSide(k, "mlo"), g_side[k].msLow); GvSet(GvSide(k, "man"), g_side[k].msAnch);
      GvSet(GvSide(k, "mbt"), g_side[k].msBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].msBar));
      GvSet(GvSide(k, "cf"), g_side[k].cf); GvSet(GvSide(k, "cft"), g_side[k].cfTop); GvSet(GvSide(k, "cfp"), g_side[k].cfPb);
      GvSet(GvSide(k, "cfb"), g_side[k].cfTchB == NAI ? -1.0 : (double)TimeOfBar(g_side[k].cfTchB));''')
rep('''      g_side[k].znTf = (int)GvGet(GvSide(k, "zf"), -1); g_side[k].znTop = GvGet(GvSide(k, "zt"), NAD); g_side[k].znBot = GvGet(GvSide(k, "zb"), NAD);   // v15.0''',
    '''      g_side[k].znTf = (int)GvGet(GvSide(k, "zf"), -1);   // v15.0
      // v15.1: the zones that allowed it (a zone is found again by its timeframe, kind, side, prices and candle time; the CHOCH* line by
      // its leg number), the MSS and its confirmation (bars kept as candle times)
      g_side[k].nSup = MnI((int)GvGet(GvSide(k, "zn"), 0), 12);
      for (int j = 0; j < g_side[k].nSup; j++)
      {
         string z = GvSide(k, "z" + IntegerToString(j));
         int f = (int)GvGet(z + "f", 0);
         g_side[k].supTf[j] = f / 100; g_side[k].supK[j] = (f / 10) % 10; g_side[k].supD[j] = f % 10 - 1;
         g_side[k].supT[j] = GvGet(z + "t", 0); g_side[k].supB[j] = GvGet(z + "b", 0); g_side[k].supT0[j] = (long)GvGet(z + "0", 0);
      }
      g_side[k].src = (int)GvGet(GvSide(k, "src"), 0); g_side[k].msLow = GvGet(GvSide(k, "mlo"), NAD); g_side[k].msAnch = GvGet(GvSide(k, "man"), NAD);
      double mbt = GvGet(GvSide(k, "mbt"), -1);
      g_side[k].msBar = mbt < 0 ? NAI : BarOfTime((datetime)mbt);
      g_side[k].cf = (int)GvGet(GvSide(k, "cf"), 0); g_side[k].cfTop = GvGet(GvSide(k, "cft"), NAD); g_side[k].cfPb = GvGet(GvSide(k, "cfp"), NAD);
      double cfb = GvGet(GvSide(k, "cfb"), -1);
      g_side[k].cfTchB = cfb < 0 ? NAI : BarOfTime((datetime)cfb);''')

# ---------------------------------------------------------------- fix (found by the v15.1 restart check, there since v11.0): trades of one
# side that close in the same second (two stacked trades closed together) were counted for the loss pause / losses in a row in the
# order the broker closed them when live, but in entry order after a restart (and in the core / TradingView). Now always the older
# entry first (then the main part before the early-profit part), live and after a restart. The core is unchanged.
rep('''   for (int k = 0; k < 2; k++)   // oldest exit first
      for (int a = 1; a < g_io[k].nCls; a++)
         for (int b = a; b > 0 && g_io[k].cls[b - 1].tOut > g_io[k].cls[b].tOut; b--)''',
    '''   for (int k = 0; k < 2; k++)   // oldest exit first; the same second: the older entry first (v15.1 - like the core and TradingView)
      for (int a = 1; a < g_io[k].nCls; a++)
         for (int b = a; b > 0 && ClsAfter(g_io[k].cls[b - 1], g_io[k].cls[b]); b--)''')
rep('''void AddCls(int k, long pid, int dir, double q, double pnl, long tIn, long tOut, int seq, int piece, int why)
{''', '''// v15.1: the order of two closed trades: exit time, then entry time, then the main part before the early-profit part
bool ClsAfter(const ClsRec &a, const ClsRec &b) { return a.tOut > b.tOut || (a.tOut == b.tOut && (a.tIn > b.tIn || (a.tIn == b.tIn && a.piece > b.piece))); }
void AddCls(int k, long pid, int dir, double q, double pnl, long tIn, long tOut, int seq, int piece, int why)
{''')
rep('''         bool swap = evBar[x] > evBar[y] || (evBar[x] == evBar[y] && evKind[x] == 1 && evKind[y] == 1 && evOut[x] > evOut[y]);''',
    '''         bool swap = evBar[x] > evBar[y] || (evBar[x] == evBar[y] && evKind[x] == 1 && evKind[y] == 1 &&
                     (evOut[x] > evOut[y] || (evOut[x] == evOut[y] && (evIn[x] > evIn[y] || (evIn[x] == evIn[y] && evPiece[x] > evPiece[y])))));   // v15.1''')

assert 'ZnDead' not in s and 'g_zbOn' not in s and 'ZnAllow(' not in s and 'znTop' not in s, 'old names left'
assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)
