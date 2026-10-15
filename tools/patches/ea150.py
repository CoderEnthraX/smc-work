# EA v15.0 = EA v14.0 +
#   1. section 4: 'Use these on the 1-minute chart only' (ON): above 1 minute skip closer / further, the min stop % of the price,
#      the rule 3 distance (rule 3 itself still works) and the leg size are not used; the big signal candle gets a second box for
#      charts above 1 minute (0 = off; the old box = 1-minute charts)
#   2. the loss mark (section 7 'Start again from the base risk when the losses carried reach') is removed
#   3. section 2: three 'HTF order block zone' modes - a trade only WITH the higher timeframe and only after the price touched an
#      order block / FVG of the higher timeframe or the two above it inside the pullback zone of the higher timeframe leg (or the
#      higher timeframe's CHOCH* line), then the chart's CHOCH / BOS; zone settings at the end of section 2
#   4. section 10: 'News on the 1-minute chart only' (ON): above 1 minute no news windows, no automatic US news, no calendar news,
#      no 'no new trades before news' (US holidays still work)
#   5. 'Take trades on' keeps only 6 choices (the 9 favourable / against / auto choices are gone; a saved favourable = the
#      section 4 higher-timeframe filter, a saved against / auto = the plain choice)
# usage: python3 ea150.py SMC_Structure_EA_v14.0.mq5 SMC_Structure_EA_v15.0.mq5
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
rep('//| SMC Structure EA v14.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v14.0, same      |\n',
    '//| SMC Structure EA v15.0 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v15.0, same      |\n')
rep(box('Owner: Punit. v14.0: own unit per distance, leg size, big candle.'),
    box('Owner: Punit. v15.0: order block zone modes, 1-minute-only rules.'))
rep('#property version     "14.00"', '#property version     "15.00"')
rep('#property description "SMC Structure EA v14.0 - the TradingView strategy v14.0 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v15.0 - the TradingView strategy v15.0 rules in MetaTrader 5, plus a hedge mode."')
rep('   Print("SMC EA v14.0 ready: ", n,', '   Print("SMC EA v15.0 ready: ", n,')

# ---- 5. the 6 signal choices (new numbers for the zone modes, so an old .set value 3-11 never becomes a zone mode)
rep('''   SIG_BOTH        = 2,   // CHOCH and BOS
   SIG_CHOCH_FAV   = 3,   // CHOCH only - higher timeframe favourable
   SIG_BOS_FAV     = 4,   // BOS only - higher timeframe favourable
   SIG_BOTH_FAV    = 5,   // CHOCH and BOS - higher timeframe favourable
   SIG_CHOCH_AGN   = 6,   // CHOCH only - against the higher timeframe
   SIG_BOS_AGN     = 7,   // BOS only - against the higher timeframe
   SIG_BOTH_AGN    = 8,   // CHOCH and BOS - against the higher timeframe
   SIG_CHOCH_AUTO  = 9,   // CHOCH only - auto: against HTF to equilibrium, then with HTF
   SIG_BOS_AUTO    = 10,  // BOS only - auto: against HTF to equilibrium, then with HTF
   SIG_BOTH_AUTO   = 11   // CHOCH and BOS - auto: against HTF to equilibrium, then with HTF
};''', '''   SIG_BOTH        = 2,   // CHOCH and BOS
   SIG_CHOCH_OB    = 12,  // CHOCH only - HTF order block zone
   SIG_BOS_OB      = 13,  // BOS only - HTF order block zone
   SIG_BOTH_OB     = 14   // CHOCH and BOS - HTF order block zone
};''')
rep('   bool bos  = InSig != SIG_CHOCH && InSig != SIG_CHOCH_FAV && InSig != SIG_CHOCH_AGN && InSig != SIG_CHOCH_AUTO;',
    '   bool bos  = (int)InSig % 3 != 0;   // v15.0: BOS only / CHOCH and BOS (also the zone modes 13 / 14)')

# ---- the new settings: end of sections 2, 4 and 10
rep('input bool     InPbSwp2    = false;   // PULLBACK RULE 3 - two candles are enough once the opposite live level is taken\n',
    '''input bool     InPbSwp2    = false;   // PULLBACK RULE 3 - two candles are enough once the opposite live level is taken
input double   InZnPct     = 50.0;    // HTF order block zone modes - the zone line, % pullback of the higher timeframe leg
input bool     InZnBig     = true;    //   - only the biggest timeframe's zones count (the higher timeframe + the 2 above it)
input bool     InZnOb      = true;    //   - use order blocks (the last opposite candle before a move that leaves an FVG)
input bool     InZnFvg     = true;    //   - use FVGs (only beyond the zone line)
input bool     InZnHalf    = true;    //   - FVG: only its far half counts (touched at its 50% line); OFF = the whole FVG
input bool     InZnTwo     = true;    //   - a second visit counts (it took the first visit's liquidity); OFF = the zone stops
input bool     InZnLine    = true;    //   - the higher timeframe's CHOCH* line (the leg start) counts as a zone
''')
rep('input double   InBcMax     = 0.0;     //   - skip the setup if the CHOCH / BOS candle (high - low) is BIGGER than this (% = of its close; 0 = off)\n',
    '''input double   InBcMax     = 0.0;     //   - skip the setup if the CHOCH / BOS candle (high - low) is BIGGER than this (% = of its close; 0 = off)
input bool     InM1On      = true;    // Use skip closer / further, min stop %, the rule 3 distance and the leg size on the 1-minute chart only
input double   InBcMax2    = 0.0;     // Big signal candle on charts ABOVE 1 minute - skip if BIGGER than this (unit above; 0 = off)
''')
rep('input ECalToday InCalToday = CT_HIGHMED; // Show today\'s news in the table (time, impact, forecast / actual) - display only\n',
    '''input ECalToday InCalToday = CT_HIGHMED; // Show today's news in the table (time, impact, forecast / actual) - display only
input bool     InNw1m      = true;    // News on the 1-minute chart only (above 1 minute: no news windows, no news closes; holidays still work)
''')

# ---- 2. the loss mark is removed
rep('''input bool     InLmOn      = false;   // Start again from the base risk when the losses carried reach
input double   InLmAmt     = 300.0;   //   - losses carried, in account currency
''', '')
rep('''   bool   lmOn;                // v12.1: group 42 - start again from the base when the losses carried reach lmAmt
   double lmAmt;
''', '')
rep('r3Fb = false; r3Brk = 0; lmOn = false; lmAmt = 0; sp1 = 0;', 'r3Fb = false; r3Brk = 0; sp1 = 0;')
rep('   int    cntLm;     // v12.1: times the losses carried reached the group 42 mark\n', '')
rep('      cntLm = 0; basNow = 0;\n', '      basNow = 0;\n')
rep('''      // v12.1: group 42 - the losses carried reached the mark: they are forgotten, the next trade risks the base again
      if (S.lmOn && S.seqMode != 0 && Car() >= S.lmAmt - 0.005) { seqLoss = 0; seqTot = 0; cntLm++; }
''', '')
rep('   S.lmOn = InLmOn; S.lmAmt = InLmAmt;\n', '')
rep('   if (InLmAmt < 0.01) return "Loss mark (section 7): the losses carried must be 0.01 or more";\n', '')
rep('   if (S.lmOn) m = m + "  |  back to the base at " + Mo(S.lmAmt) + " carried";\n', '')
rep('''string LmTxt()
{
   if (!S.lmOn) return "off";
   if (S.seqMode == 0) return "on - but loss recovery is Off";
   return "at " + Mo(S.lmAmt) + ":  " + MonTxt(I2(g_money[0].cntLm) + " x back to the base", I2(g_money[1].cntLm) + " x back to the base");
}
''', '')
rep('   Row("LOSS MARK - BACK TO THE BASE (section 7)", LmTxt(), S.lmOn && S.seqMode != 0 ? clrAqua : clrGray);\n', '')
rep('// v12.1: the hard cap row, and group 42 (the loss mark)\n', '// v12.1: the hard cap row\n')

# ---- core settings
rep('''   double lzMin, lzMax, bcMax;         //   and limits (0 = off)
''', '''   double lzMin, lzMax, bcMax;         //   and limits (0 = off)
   bool   m1On, x1m, nw1m;             // v15.0: section 4 rules on the 1-minute chart only (x1m = this chart is above 1 minute and
   double bcMax2, bcE;                 //   they are off); the big candle box above 1 minute and the one in use; news on 1m only
   bool   obM, znBig, znOb, znFvg, znHalf, znTwo, znLine;   // v15.0 section 2: the order block zone modes and their settings
   double znPct;
''')
rep('            uBf = 0; uSk = 0; uR3 = 0; uSp = 0; lzU = 0; bcU = 0; lzMin = 0; lzMax = 0; bcMax = 0;\n',
    '''            uBf = 0; uSk = 0; uR3 = 0; uSp = 0; lzU = 0; bcU = 0; lzMin = 0; lzMax = 0; bcMax = 0;
            m1On = false; x1m = false; nw1m = false; bcMax2 = 0; bcE = 0; obM = false; znBig = true; znOb = true; znFvg = true; znHalf = true;
            znTwo = true; znLine = true; znPct = 50;
''')
rep('''   void Derive()
   {
      fav    = sig >= 3 && sig <= 5;
      agn    = sig >= 6 && sig <= 8;
      autoM  = sig >= 9;
      int b  = sig % 3;
      useCho = b != 1;
      useBos = b != 0;
      hfEff  = hfOn || fav;
      u15    = on && (r2 || hfEff || eqOn || agn || autoM) && htfOk;''', '''   void Derive()
   {
      // v15.0: only 6 choices - a saved 'favourable' (3-5) is the section 4 higher-timeframe filter, 'against' / 'auto' (6-11)
      // the plain choice; 12-14 = the order block zone modes
      if (sig >= 3 && sig <= 5) { hfOn = true; sig -= 3; }
      else if (sig >= 6 && sig <= 11) sig = sig % 3;
      obM    = sig >= 12 && sig <= 14;
      fav    = false;
      agn    = false;
      autoM  = false;
      int b  = sig % 3;
      useCho = b != 1;
      useBos = b != 0;
      hfEff  = hfOn;
      u15    = on && (r2 || hfEff || eqOn || obM) && htfOk;
      // v15.0: section 4 - on charts above 1 minute these are not used (the switch ON); the big candle has its own box there
      x1m    = m1On && cs > 60;
      if (x1m) { minStop = 0; maxStop = 0; mnPct = 0; lzMin = 0; lzMax = 0; r3BrkOn = false; }
      bcE    = cs > 60 ? bcMax2 : bcMax;''')

# ---- 1. the big candle box in use
rep('''      if (S.bcMax > 0)
      {
         double bc = LimAt(S.bcU, S.bcMax, g_c);''', '''      if (S.bcE > 0)
      {
         double bc = LimAt(S.bcU, S.bcE, g_c);''')

# ---- 4. news on the 1-minute chart only
rep('''   int tMw = S.nwNy ? MinOfDay(NyLoc(tc)) : g_tM;
   bool win = S.intra && (NwHit(S.nw1On, S.nw1A, S.nw1B, tMw, S.bMin, tc) || NwHit(S.nw2On, S.nw2A, S.nw2B, tMw, S.bMin, tc) || NwHit(S.nw3On, S.nw3A, S.nw3B, tMw, S.bMin, tc));
''', '''   int tMw = S.nwNy ? MinOfDay(NyLoc(tc)) : g_tM;
   bool win = S.intra && (NwHit(S.nw1On, S.nw1A, S.nw1B, tMw, S.bMin, tc) || NwHit(S.nw2On, S.nw2A, S.nw2B, tMw, S.bMin, tc) || NwHit(S.nw3On, S.nw3A, S.nw3B, tMw, S.bMin, tc));
   // v15.0: news on the 1-minute chart only - above 1 minute no news window blocks or closes (US holidays still do)
   if (S.nw1m && S.cs > 60) { win = false; auNow = false; calNow = false; g_preNow = false; }
''')

# ---- 3. the zone engine (core), before the money and the sides
rep('''double CmU(double ent)
{''', '''// ---------- v15.0: the order block zone modes (section 2) ----------
// Zones come from the CLOSED candles of the higher timeframe (j = 0) and the two timeframes above it (j = 1, 2). An FVG = candle 1
// and candle 3 do not overlap; its order block = the last opposite candle among the 3 candles before the move (candles 3, 4, 5
// back). A zone goes when a candle of ITS OWN timeframe closes beyond its far side. At each chart bar a zone of the higher
// timeframe direction is 'in the zone' when it lies in the pullback zone of the higher timeframe leg (from the zone line % to
// the leg start = 100%; an order block may touch the line, an FVG's touch line must be beyond it); then the bar's low (high)
// reaching its touch line (order block: its near edge; FVG: its 50% line or its near edge) touches it. A with-HTF chart
// signal after a touch may trade; it 'closes the visit' (the visit's low / high stays); a later bar beyond that low / high
// took its liquidity: with 'second visit' ON the zone works again, OFF it stops. A new higher timeframe leg starts all
// touches again. The higher timeframe's CHOCH* line (the leg start) can work as a zone too.
#define ZMAX 60
#define ZPER 10
struct ZRec
{
   int    id, tf, dir, kind;     // kind 0 = order block, 1 = FVG
   double top, bot, ext;         // ext = the low (buy) / high (sell) of the current visit
   bool   q, tch, frz, spent;   // q = in the leg's zone at this bar, tch = touched, frz = a signal closed the visit, spent = stopped
};
ZRec   g_zn[ZMAX];
ZRec   g_zl;                     // the higher timeframe's CHOCH* line as a zone
int    g_znN = 0, g_znId = 0, g_znLegE = -1;
double g_znCo[3][6], g_znCh[3][6], g_znCl[3][6], g_znCc[3][6];   // the last closed candles of each zone timeframe (0 = newest)
int    g_znCn[3];
double g_znObT[3][2], g_znObB[3][2];   // the last order block added per timeframe and side (the same one is not added twice)
int    g_znDtf[32];                    // the zones broken by a close (timeframe, top, bottom) - a waiting setup from them is cancelled
double g_znDt[32], g_znDb[32];
int    g_znDn = 0;
void ZnClr(ZRec &z) { z.q = false; z.tch = false; z.frz = false; z.spent = false; z.ext = NAD; }
void ZnReset()
{
   g_znN = 0; g_znId = 0; g_znLegE = -1; g_znDn = 0;
   for (int j = 0; j < 3; j++)
   {
      g_znCn[j] = 0;
      for (int k = 0; k < 6; k++) { g_znCo[j][k] = NAD; g_znCh[j][k] = NAD; g_znCl[j][k] = NAD; g_znCc[j][k] = NAD; }
      for (int a = 0; a < 2; a++) { g_znObT[j][a] = NAD; g_znObB[j][a] = NAD; }
   }
   for (int i = 0; i < 32; i++) { g_znDtf[i] = -1; g_znDt[i] = NAD; g_znDb[i] = NAD; }
   g_zl.id = -1; g_zl.tf = 9; g_zl.dir = 0; g_zl.kind = 2; g_zl.top = NAD; g_zl.bot = NAD;
   ZnClr(g_zl);
}
void ZnDel(int i) { for (int k = i; k + 1 < g_znN; k++) g_zn[k] = g_zn[k + 1]; g_znN--; }
// a new zone; the oldest of the same timeframe and side goes when there are already ZPER
void ZnAdd(int j, int dir, int kind, double top, double bot)
{
   int same = 0, old = -1;
   for (int i = 0; i < g_znN; i++) if (g_zn[i].tf == j && g_zn[i].dir == dir) { same++; if (old < 0) old = i; }
   if (same >= ZPER) ZnDel(old);
   if (g_znN >= ZMAX) ZnDel(0);
   g_znId++;
   g_zn[g_znN].id = g_znId; g_zn[g_znN].tf = j; g_zn[g_znN].dir = dir; g_zn[g_znN].kind = kind; g_zn[g_znN].top = top; g_zn[g_znN].bot = bot;
   ZnClr(g_zn[g_znN]);
   g_znN++;
}
// one CLOSED candle of zone timeframe j
void ZnCandle(int j, double o, double h, double l, double c)
{
   if (!S.obM || j < 0 || j > 2) return;
   for (int i = g_znN - 1; i >= 0; i--)
      if (g_zn[i].tf == j && (g_zn[i].dir == 1 ? c < g_zn[i].bot : c > g_zn[i].top))
      {
         int w = g_znDn % 32;
         g_znDtf[w] = j; g_znDt[w] = g_zn[i].top; g_znDb[w] = g_zn[i].bot; g_znDn++;
         ZnDel(i);
      }
   for (int k = 5; k > 0; k--) { g_znCo[j][k] = g_znCo[j][k - 1]; g_znCh[j][k] = g_znCh[j][k - 1]; g_znCl[j][k] = g_znCl[j][k - 1]; g_znCc[j][k] = g_znCc[j][k - 1]; }
   g_znCo[j][0] = o; g_znCh[j][0] = h; g_znCl[j][0] = l; g_znCc[j][0] = c;
   if (g_znCn[j] < 6) g_znCn[j]++;
   if (g_znCn[j] < 3) return;
   for (int a = 0; a < 2; a++)
   {
      int d = a == 0 ? 1 : -1;
      if (!(d == 1 ? g_znCl[j][0] > g_znCh[j][2] : g_znCh[j][0] < g_znCl[j][2])) continue;
      if (S.znFvg)
      {
         if (d == 1) ZnAdd(j, 1, 1, g_znCl[j][0], g_znCh[j][2]);
         else        ZnAdd(j, -1, 1, g_znCl[j][2], g_znCh[j][0]);
      }
      if (!S.znOb) continue;
      for (int k = 2; k <= 4 && k < g_znCn[j]; k++)
         if (d == 1 ? g_znCc[j][k] < g_znCo[j][k] : g_znCc[j][k] > g_znCo[j][k])
         {
            if (g_znCh[j][k] != g_znObT[j][a] || g_znCl[j][k] != g_znObB[j][a])
            {
               ZnAdd(j, d, 0, g_znCh[j][k], g_znCl[j][k]);
               g_znObT[j][a] = g_znCh[j][k]; g_znObB[j][a] = g_znCl[j][k];
            }
            break;
         }
   }
}
bool ZnDead(int tf, double top, double bot)
{
   for (int i = 0; i < 32; i++) if (g_znDtf[i] == tf && g_znDt[i] == top && g_znDb[i] == bot) return true;
   return false;
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
      if (z.q && (d == 1 ? x <= tl : x >= tl)) { z.tch = true; z.frz = false; z.ext = x; }
      return;
   }
   if (z.spent) return;
   if (!z.frz) { z.ext = d == 1 ? Mn(z.ext, x) : Mx(z.ext, x); return; }
   if (d == 1 ? x < z.ext : x > z.ext)
   {
      if (S.znTwo) { z.frz = false; z.ext = x; }
      else z.spent = true;
   }
}
// every chart bar (after the higher timeframe values are set): which zones are in the leg's zone, touches, visits
void ZnBar()
{
   if (!S.obM) return;
   int d = g_T15;
   if (g_htE != g_znLegE)
   {
      g_znLegE = g_htE;
      for (int i = 0; i < g_znN; i++) ZnClr(g_zn[i]);
      ZnClr(g_zl);
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
}
// the zone a signal in direction d may trade from: index + 1, -1 = the CHOCH* line, 0 = none
int ZnAllow(int d)
{
   int big = -1;
   if (S.znBig) for (int i = 0; i < g_znN; i++) if (g_zn[i].dir == d && g_zn[i].q && !g_zn[i].spent) big = MxI(big, g_zn[i].tf);
   int best = 0, bt = -1;
   for (int i = 0; i < g_znN; i++)
   {
      if (g_zn[i].dir != d || !g_zn[i].tch || g_zn[i].spent) continue;
      if (S.znBig && g_zn[i].tf != big) continue;
      if (g_zn[i].tf > bt) { bt = g_zn[i].tf; best = i + 1; }
   }
   if (best == 0 && S.znLine && g_zl.dir == d && g_zl.tch && !g_zl.spent) best = -1;
   return best;
}
// a with-HTF chart signal closes the visit of every touched zone of that side
void ZnFreeze(int d)
{
   for (int i = 0; i < g_znN; i++) if (g_zn[i].dir == d && g_zn[i].tch) g_zn[i].frz = true;
   if (g_zl.dir == d && g_zl.tch) g_zl.frz = true;
}
string ZnName(int tf) { return tf == 0 ? "HTF" : (tf == 1 ? "HTF+1" : (tf == 2 ? "HTF+2" : "CHOCH* line")); }

double CmU(double ent)
{''')

# ---- the side: the zone of a setup, cancels, the check
rep('''   int    cntHgB;                     // v13.0: setups sized at the base because the other side was chasing the loss
''', '''   int    cntHgB;                     // v13.0: setups sized at the base because the other side was chasing the loss
   int    znTf, cntOb;                // v15.0: the zone of the setup (timeframe 0-2, 9 = the CHOCH* line, -1 = none); skipped (no zone)
   double znTop, znBot;
''')
rep('      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0; cntHgB = 0;\n',
    '      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0; cntHgB = 0;\n      znTf = -1; znTop = NAD; znBot = NAD; cntOb = 0;\n')
rep('''      if (S.fav && dir != 0 && g_T15 != dir) Cancel("CANCELLED - higher timeframe flipped");''',
    '''      if (S.fav && dir != 0 && g_T15 != dir) Cancel("CANCELLED - higher timeframe flipped");
      // v15.0: the zone modes trade only with the higher timeframe; a setup goes when its zone is broken by a close
      if (S.obM && dir != 0 && g_T15 != dir) Cancel("CANCELLED - higher timeframe flipped");
      if (S.obM && dir != 0 && znTf >= 0 && znTf <= 2 && ZnDead(znTf, znTop, znBot)) Cancel("CANCELLED - its zone was broken by a close");''')
rep('''            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;''', '''            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;
            // v15.0: the zone modes - only with the higher timeframe, and only after a zone was touched
            int  zk = 0;
            bool obSkip = false;
            if (S.obM)
            {
               zk = d == g_T15 ? ZnAllow(d) : 0;
               if (use && zk == 0) { use = false; obSkip = true; cntOb++; }
            }''')
rep('''               fix     = rule == 2 ? piv : NAD;
''', '''               fix     = rule == 2 ? piv : NAD;
               znTf    = -1; znTop = NAD; znBot = NAD;
               if (S.obM) { if (zk > 0) { znTf = g_zn[zk - 1].tf; znTop = g_zn[zk - 1].top; znBot = g_zn[zk - 1].bot; } else znTf = 9; }
''')
rep('''            else if (r3Use && r3Far) Note(sg + ": SKIP - RULE 3: "''',
    '''            else if (obSkip) Note(sg + ": SKIP - " + (d != g_T15 ? (string)"zone mode: not with the higher timeframe" : "zone mode: no zone touched"));
            else if (r3Use && r3Far) Note(sg + ": SKIP - RULE 3: "''')
rep('''(rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED"))''',
    '''(rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED")) + (!S.obM ? (string)"" : (znTf == 9 ? (string)" (CHOCH* line)" : " (" + ZnName(znTf) + (g_zn[zk - 1].kind == 0 ? " order block)" : " FVG)")))''')

# ---- core setup / bar
rep('''   HT.Reset();
   g_nSides = S.dirMode == 3 ? 2 : 1;''', '''   HT.Reset();
   ZnReset();   // v15.0
   g_nSides = S.dirMode == 3 ? 2 : 1;''')
rep('''   g_htE = S.u15 ? htE : 0;
''', '''   g_htE = S.u15 ? htE : 0;
   ZnBar();   // v15.0: zones in the leg's zone, touches, visits
''')
rep('''   if (!g_dry)
      for (int k = 0; k < g_nSides; k++) g_side[k].Decide();
''', '''   if (!g_dry)
      for (int k = 0; k < g_nSides; k++) g_side[k].Decide();
   // v15.0: a chart signal with the higher timeframe closes the visit of the touched zones
   if (S.obM && g_T15 != 0)
   {
      bool sU = (S.useCho && EN.evCU) || (S.useBos && EN.evBU), sD = (S.useCho && EN.evCD) || (S.useBos && EN.evBD);
      if ((g_T15 == 1 && sU) || (g_T15 == -1 && sD)) ZnFreeze(g_T15);
   }
   // v15.0: only a zone broken by a close on THIS bar cancels a waiting setup (as in TradingView) - forget this bar's
   if (g_znDn > 0) { for (int i = 0; i < 32; i++) g_znDtf[i] = -1; g_znDn = 0; }
''')

# ---- adapter: settings, checks, the zone timeframes' candles
rep('''   S.lzU = (int)InLzU; S.lzMin = InLzMin; S.lzMax = InLzMax; S.bcU = (int)InBcU; S.bcMax = InBcMax;   // v14.0 section 4
''', '''   S.lzU = (int)InLzU; S.lzMin = InLzMin; S.lzMax = InLzMax; S.bcU = (int)InBcU; S.bcMax = InBcMax;   // v14.0 section 4
   S.m1On = InM1On; S.bcMax2 = InBcMax2; S.nw1m = InNw1m;   // v15.0
   S.znPct = InZnPct; S.znBig = InZnBig; S.znOb = InZnOb; S.znFvg = InZnFvg; S.znHalf = InZnHalf; S.znTwo = InZnTwo; S.znLine = InZnLine;
''')
rep('''   if (InLzMin < 0 || InLzMax < 0 || InBcMax < 0) return "Leg size / big signal candle (section 4) cannot be negative";''',
    '''   if (InLzMin < 0 || InLzMax < 0 || InBcMax < 0 || InBcMax2 < 0) return "Leg size / big signal candle (section 4) cannot be negative";
   // v15.0
   if (InZnPct < 1 || InZnPct > 99) return "Zone line (section 2) must be 1 - 99 %";
   if ((int)InSig >= 12 && !InZnOb && !InZnFvg) return "Order block zone mode (section 2): turn on 'use order blocks' or 'use FVGs'";''')
rep('''void HtfStep(MqlRates &r)
{
   HT.Step(r.open, r.high, r.low, r.close);''', '''void HtfStep(MqlRates &r)
{
   HT.Step(r.open, r.high, r.low, r.close);
   ZnCandle(0, r.open, r.high, r.low, r.close);   // v15.0: zones of the higher timeframe''')
rep('''// v13.1: 'only with today's move' needs 14 complete days before the first live bar''',
    '''// v15.0: the order block zone timeframes above the higher timeframe (the next two of 15m, 1h, 4h, 1D, 1W, 1M) - their candles
bool            g_znUse[3];
ENUM_TIMEFRAMES g_znPer[3];
datetime        g_znFed[3];
ENUM_TIMEFRAMES ZnUp(ENUM_TIMEFRAMES p)
{
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_M15)) return PERIOD_M15;
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_H1)) return PERIOD_H1;
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_H4)) return PERIOD_H4;
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_D1)) return PERIOD_D1;
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_W1)) return PERIOD_W1;
   if (PeriodSeconds(p) < PeriodSeconds(PERIOD_MN1)) return PERIOD_MN1;
   return PERIOD_CURRENT;
}
void ZnSetup()
{
   g_znPer[0] = g_htf;
   g_znPer[1] = ZnUp(g_htf);
   g_znPer[2] = g_znPer[1] == PERIOD_CURRENT ? PERIOD_CURRENT : ZnUp(g_znPer[1]);
   for (int j = 0; j < 3; j++) { g_znUse[j] = j > 0 && S.obM && g_htfUse && g_znPer[j] != PERIOD_CURRENT; g_znFed[j] = 0; }
}
datetime ZnOpenOf(int j, datetime t)
{
   int sh = iBarShift(g_sym, g_znPer[j], t, false);
   if (sh < 0) return 0;
   return iTime(g_sym, g_znPer[j], sh);
}
bool FeedZn(datetime barOpen)
{
   for (int j = 1; j < 3; j++)
   {
      if (!g_znUse[j]) continue;
      datetime hc = ZnOpenOf(j, barOpen);
      if (hc == 0) return false;
      if (hc <= g_znFed[j] + 1) continue;
      MqlRates zr[];
      int n = CopyRates(g_sym, g_znPer[j], g_znFed[j] + 1, hc - 1, zr);
      if (n < 0) return false;
      for (int i = 0; i < n; i++)
         if (zr[i].time > g_znFed[j] && zr[i].time < hc) { ZnCandle(j, zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }
   }
   return true;
}
// v13.1: 'only with today's move' needs 14 complete days before the first live bar''')
rep('''   FeedInd(r.time);   // v13.1
''', '''   FeedInd(r.time);   // v13.1
   FeedZn(r.time);    // v15.0
''')
rep('''   for (int i = 0; i < 4; i++) if (g_indUse[i] && !g_tester && !SeriesInfoInteger(g_sym, g_indPer[i], SERIES_SYNCHRONIZED)) { iTime(g_sym, g_indPer[i], 0); return false; }
''', '''   for (int i = 0; i < 4; i++) if (g_indUse[i] && !g_tester && !SeriesInfoInteger(g_sym, g_indPer[i], SERIES_SYNCHRONIZED)) { iTime(g_sym, g_indPer[i], 0); return false; }
   for (int j = 1; j < 3; j++) if (g_znUse[j] && !g_tester && !SeriesInfoInteger(g_sym, g_znPer[j], SERIES_SYNCHRONIZED)) { iTime(g_sym, g_znPer[j], 0); return false; }
''')
rep('''   // a waiting setup saved before a restart a few bars ago?''', '''   // v15.0: the zone timeframes above the higher timeframe - their candles before the first chart bar
   for (int j = 1; j < 3; j++)
   {
      g_znFed[j] = 0;
      if (!g_znUse[j]) continue;
      datetime zc0 = ZnOpenOf(j, rr[0].time);
      if (zc0 == 0) return false;
      MqlRates zr[];
      int m = CopyRates(g_sym, g_znPer[j], zc0 - 1, 3000, zr);
      for (int i = 0; i < m; i++) if (zr[i].time < zc0) { ZnCandle(j, zr[i].open, zr[i].high, zr[i].low, zr[i].close); g_znFed[j] = zr[i].time; }
      if (g_znFed[j] == 0) g_znFed[j] = zc0 - 1;
   }
   // a waiting setup saved before a restart a few bars ago?''')
rep('''   IndSetup();   // v13.1
''', '''   IndSetup();   // v13.1
   ZnSetup();    // v15.0
''')
# a kept setup keeps its zone over a restart
rep('''      GvSet(GvSide(k, "fd"), (double)g_side[k].fstDay);   // v13.1
''', '''      GvSet(GvSide(k, "fd"), (double)g_side[k].fstDay);   // v13.1
      GvSet(GvSide(k, "zf"), g_side[k].znTf); GvSet(GvSide(k, "zt"), g_side[k].znTop); GvSet(GvSide(k, "zb"), g_side[k].znBot);   // v15.0
''')
rep('''      g_side[k].hbSeen = GvGet(GvSide(k, "hs"), 0) > 0.5;
''', '''      g_side[k].hbSeen = GvGet(GvSide(k, "hs"), 0) > 0.5;
      g_side[k].znTf = (int)GvGet(GvSide(k, "zf"), -1); g_side[k].znTop = GvGet(GvSide(k, "zt"), NAD); g_side[k].znBot = GvGet(GvSide(k, "zb"), NAD);   // v15.0
''')

# ---- table: the zone row
rep('''   if (what == 16) return g_side[k].cntHgB;''', '''   if (what == 16) return g_side[k].cntHgB;
   if (what == 17) return g_side[k].cntOb;   // v15.0''')
rep('''// v14.0: the unit of one distance as text''', '''// v15.0: the order block zone modes - zones alive per timeframe, touched now, signals skipped (no zone)
string ZnTxt()
{
   if (!S.obM) return "off";
   if (!S.htfOk) return "on - but the higher timeframe is not above the chart - no trades";
   int n[3] = {0, 0, 0}, t = 0;
   for (int i = 0; i < g_znN; i++) if (g_zn[i].dir == g_T15) { n[g_zn[i].tf]++; if (g_zn[i].tch && !g_zn[i].spent) t++; }
   string s = TfName(g_znPer[0]) + " " + I2(n[0]);
   for (int j = 1; j < 3; j++) if (g_znPer[j] != PERIOD_CURRENT) s = s + " / " + TfName(g_znPer[j]) + " " + I2(n[j]);
   return (g_T15 == 1 ? "buy zones " : (g_T15 == -1 ? "sell zones " : "zones ")) + s + "  |  touched " + I2(t) + (S.znLine && g_zl.tch && !g_zl.spent ? " + CHOCH* line" : "") +
          "  |  skipped (no zone) " + CntTxt(17);
}
// v14.0: the unit of one distance as text''')
rep('''   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (section 3)", R3Txt(), S.r3On ? clrAqua : clrGray);
''', '''   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (section 3)", R3Txt(), S.r3On ? clrAqua : clrGray);
   Row("ORDER BLOCK ZONES (section 2)", ZnTxt(), S.obM ? clrAqua : clrGray);   // v15.0
''')

assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)
