//+------------------------------------------------------------------+
//| SMC Structure EA v12.3 (+ hedge) - MetaTrader 5 Expert Advisor     |
//| The TradingView strategy "SMC Structure Strategy" v12.2, same      |
//| rules, plus a hedge mode (longs and shorts at the same time).      |
//| Owner: Punit. Read SMC_Structure_EA_v12.0_NOTES.txt first.          |
//+------------------------------------------------------------------+
#property copyright   "Punit"
#property version     "12.30"
#property description "SMC Structure EA v12.3 - the TradingView strategy v12.2 rules in MetaTrader 5, plus a hedge mode."
#property description "Bar-close logic like TradingView. Test it in the Strategy Tester and on a demo account first."

#include <Trade\Trade.mqh>

//---------------------------------------------------------------- choices
enum ESig
{
   SIG_CHOCH       = 0,   // CHOCH only
   SIG_BOS         = 1,   // BOS only
   SIG_BOTH        = 2,   // CHOCH and BOS
   SIG_CHOCH_FAV   = 3,   // CHOCH only - higher timeframe favourable
   SIG_BOS_FAV     = 4,   // BOS only - higher timeframe favourable
   SIG_BOTH_FAV    = 5,   // CHOCH and BOS - higher timeframe favourable
   SIG_CHOCH_AGN   = 6,   // CHOCH only - against the higher timeframe
   SIG_BOS_AGN     = 7,   // BOS only - against the higher timeframe
   SIG_BOTH_AGN    = 8,   // CHOCH and BOS - against the higher timeframe
   SIG_CHOCH_AUTO  = 9,   // CHOCH only - auto: against HTF to equilibrium, then with HTF
   SIG_BOS_AUTO    = 10,  // BOS only - auto: against HTF to equilibrium, then with HTF
   SIG_BOTH_AUTO   = 11   // CHOCH and BOS - auto: against HTF to equilibrium, then with HTF
};
enum EEntMode
{
   ENT_CONT = 0,      // Continuous - follow the level
   ENT_ONCE = 1       // Send once - place it and leave it
};
enum EHtf
{
   HTF_AUTO = 0,      // Auto - paired with the chart
   HTF_M15 = 1,       // 15m
   HTF_H1 = 2,        // 1h
   HTF_H4 = 3,        // 4h
   HTF_D1 = 4,        // 1D
   HTF_W1 = 5,        // 1W
   HTF_MN = 6         // 1M
};
enum ESess
{
   SESS_AUTO = 0,     // Auto - off on daily charts and above
   SESS_ALWAYS = 1,   // Always apply
   SESS_NEVER = 2     // Never apply
};
enum EDst
{
   DST_NONE = 0,      // No summer time
   DST_EU = 1,        // European summer time (last Sunday of March - last Sunday of October)
   DST_US = 2         // US summer time (2nd Sunday of March - 1st Sunday of November)
};
enum ESize
{
   SIZE_RISK = 0,     // Risk-based off the stop
   SIZE_QTY = 1,      // Fixed quantity
   SIZE_CASH = 2      // Fixed cash per trade
};
enum ESeq
{
   SEQ_OFF = 0,       // Off
   SEQ_A = 1,         // Rule A - recover losses + base profit
   SEQ_B = 2,         // Rule B - double the losses
   SEQ_C = 3,         // Rule C - carry the losses
   SEQ_AP = 4,        // Rule A+ (only when total P&L is below 0: that loss + amount)
   SEQ_BP = 5,        // Rule B+ (only when total P&L is below 0: 2 x that loss)
   SEQ_CP = 6,        // Rule C+ (only when total P&L is below 0: that loss)
   SEQ_AS = 7,        // Rule A split (A, the base grows with the profit - group 43)
   SEQ_BS = 8,        // Rule B split (B, the base grows with the profit - group 43)
   SEQ_CS = 9         // Rule C split (C, the base grows with the profit - group 43)
};
enum ECap
{
   CAP_CLAMP = 0,     // Clamp to the cap and carry on
   CAP_DAY = 1,       // Stop for the rest of the day
   CAP_PERM = 2,      // Stop permanently
   CAP_BASE = 3       // Start again from the base risk (forget the losses)
};
enum ESeqFrom
{
   SF_ALL = 0,        // The whole history of this EA on this account
   SF_LIVE = 1,       // When the EA first started on this account (automatic)
   SF_DATE = 2        // A date I choose
};
enum ECm
{
   CM_OFF = 0,        // Off
   CM_AUTO = 1,       // Auto - per lot, contract size from the symbol
   CM_LOT = 2,        // Per lot - I set the contract size
   CM_PCT = 3,        // Percent of trade value
   CM_FIX = 4         // Fixed cash per order
};
enum EWkDay
{
   WK_THU = 5,        // Thursday
   WK_FRI = 6,        // Friday
   WK_SAT = 7         // Saturday
};
enum ENwExit
{
   NW_CLOSE = 0,      // Close any open trade
   NW_LEAVE = 1       // Leave open trades alone
};
enum EPtPer
{
   PT_TOTAL = 0,      // Total since the start date
   PT_DAY = 1,        // Each day (starts again tomorrow)
   PT_WEEK = 2        // Each week (starts again on Monday)
};
enum ENdScope
{
   ND_MONTH = 0,      // This month only
   ND_EVERY = 1       // Every month
};
enum EUsClk
{
   US_AUTO = 0,       // Auto - follows US summer / winter time
   US_EDT = 1,        // Always summer time (EDT, UTC-4)
   US_EST = 2         // Always winter time (EST, UTC-5)
};
enum EDir
{
   DIR_BOTH = 0,      // Both
   DIR_LONG = 1,      // Longs only
   DIR_SHORT = 2,     // Shorts only
   DIR_HEDGE = 3      // Hedge - longs and shorts at the same time (two sides)
};
enum EHedgeMoney
{
   HM_OWN = 0,        // Each side its own (like two TradingView copies)
   HM_SHARED = 1      // Shared by both sides (one loss memory for the account)
};
enum ETrMode
{
   TR_LEVEL = 0,      // Behind the CHOCH* level (slower)
   TR_SWING = 1       // Behind every new swing (faster)
};
enum EFl
{
   FL_OFF = 0,        // Off
   FL_SIZE = 1,       // On - size every trade from the cushion (risk grows with profit)
   FL_CAP = 2         // On - only cap the risk (base / loss recovery, never above the cushion %)
};
enum ETblPos
{
   TP_TL = 0,         // Top left
   TP_TC = 1,         // Top center
   TP_TR = 2,         // Top right
   TP_ML = 3,         // Middle left
   TP_MR = 4,         // Middle right
   TP_BL = 5,         // Bottom left
   TP_BC = 6,         // Bottom center
   TP_BR = 7          // Bottom right
};
enum ETblSize
{
   TS_SMALL = 0,      // Small
   TS_NORMAL = 1,     // Normal
   TS_LARGE = 2       // Large
};
enum EAudSz
{
   AS_SMALL = 0,      // Small
   AS_NORMAL = 1,     // Normal
   AS_LARGE = 2,      // Large
   AS_HUGE = 3        // Huge
};
enum ETblRows
{
   TR_FULL = 0,       // Full - every row, like TradingView
   TR_SHORT = 1       // Short - the main rows only
};
enum EExec
{
   EX_TOUCH = 0,      // Like TradingView: market order when the chart price touches the entry
   EX_PEND = 1        // Pending limit order at the broker
};
enum ECalImp
{
   CI_HIGH = 0,       // High impact only
   CI_HIGHMED = 1     // High and medium impact
};
enum EBuMode
{
   BU_PRICE = 0,      // Price (as now)
   BU_PIPS = 1,       // Pips (auto per market)
   BU_PCT = 2         // % of price
};
enum ECalToday
{
   CT_OFF = 0,        // Off
   CT_HIGH = 1,       // High impact
   CT_HIGHMED = 2     // High and medium impact
};

//---------------------------------------------------------------- settings (same names, order and defaults as TradingView v12.2)
input group "Market structure - engine rules (change the signals themselves)"
input bool     InAltMode   = false;   // ALTERNATE rule: BOS is valid only AFTER IDM
input bool     InPbBodyOn  = false;   // PULLBACK RULE 1 - each of the 3 candles: body bigger than its longest wick
input bool     InPbBodyRef = false;   // PULLBACK RULE 2 - close beyond the previous candle's BODY (carries rule 1)
input bool     InPbSwp2    = false;   // PULLBACK RULE 3 - two candles are enough once the opposite live level is taken

input group "20. Strategy - entries, session, targets"
input bool     InOn        = true;    // Enable trading
input bool     InR1        = true;    // RULE 1 - pullback % entry
input bool     InR2        = true;    // RULE 2 - entry at the broken pivot, higher timeframe must AGREE
input ESig     InSig       = SIG_CHOCH; // Take trades on
input double   InPb        = 50.0;    //   - RULE 1 pullback % (1 - 99)
input double   InRR        = 1.0;     // Target - R multiple of the entry-to-stop distance
input double   InSlBuf     = 0.0;     // Stop buffer beyond the CHOCH* level, in price
input bool     InRev       = true;    // Opposite signal while in a trade: close and reverse
input EEntMode InEntMode   = ENT_CONT; // Entry order handling
input EHtf     InHtf       = HTF_AUTO; // Higher timeframe for RULE 2
input ESess    InSessMode  = SESS_AUTO; // Time-of-day filters
input double   InTzHours   = 5.5;     // Session timezone - hours from UTC (India 5.5, London 0, New York -5)
input EDst     InTzDst     = DST_NONE; // Session timezone - summer time (India: none, London: European, New York: US)
input int      InHrOn      = 6;       // Take entries from (hour)
input int      InHrOff     = 23;      // Stop taking entries at (hour)
input int      InHrFlat    = 2;       // Force-close any open trade at (hour)
input bool     InShow      = true;    // Draw entry / stop / target levels
input bool     InStatOn    = true;    // Show the counter table (like TradingView)
input bool     InAudit     = false;   // Signal audit - a label on the chart for every signal (what happened to it) + the Experts journal
input ETblPos  InStatPos   = TP_BR;   //   - table position
input ETblSize InStatSize  = TS_NORMAL; //   - table text size
input ETblRows InStatRows  = TR_FULL; //   - table rows

input group "21. Position size and risk"
input ESize    InSize      = SIZE_RISK; // Position size
input double   InRisk      = 50.0;    //   - BASE risk per trade, in account currency
input double   InQty       = 1.0;     //   - fixed quantity (units: 1 = one ounce of gold)
input double   InCash      = 1000.0;  //   - fixed cash per trade
input double   InLotStep   = 0.01;    // Round the size to the broker's lot step (0 = off)
input double   InRndMax    = 25.0;    //   - but never let rounding raise the risk by more than (%)
input double   InLev       = 30.0;    // Max leverage (position value / equity)
input ESeq     InSeqMode   = SEQ_OFF; // Loss-recovery sizing
input double   InSeqMax    = 500.0;   //   - HARD CAP on risk per trade
input ECap     InCapAct    = CAP_PERM; //   - when the cap is reached
input double   InSeqAdd    = 50.0;    //   - Rule A: amount added on top of the losses carried
input ESeqFrom InSeqFrom   = SF_ALL;  //   - loss recovery counts from
input datetime InSeqFromT  = D'2026.01.01 00:00'; //   - the date (only for 'A date I choose'), UTC
input double   InSplit     = 1.0;     //   - split the loss over this many trades (1 - 20)

input group "23. Commission / broker charges (used to SIZE trades; real costs come from the broker)"
input ECm      InCmMode    = CM_AUTO; // Commission model
input double   InCmLot     = 0.0;     //   - charge per LOT, ONE side
input double   InCmUnit    = 100.0;   //   - units per lot (manual mode only)
input double   InCmPct     = 0.05;    //   - percent of trade value, ONE side
input double   InCmFix     = 3.50;    //   - fixed cash per order
input bool     InCmTgt     = true;    // Push the target out to cover the commission

input group "24. Safety - every one of these is optional"
input bool     InCancelSig = true;    // Cancel an unfilled order on ANY new signal
input int      InExpBars   = 0;       // Cancel an unfilled order after N bars (0 = never)
input double   InMinStop   = 0.0;     // Skip the setup if the stop is CLOSER than this (price)
input double   InMaxStop   = 0.0;     // Skip the setup if the stop is FURTHER than this (price)
input int      InMaxTrades = 0;       // Max trades per day (0 = no limit)
input double   InDayLoss   = 0.0;     // Stop for the day after losing this much (0 = off)
input double   InDD        = 0.0;     // Stop after an equity drawdown of this % (0 = off)
input bool     InWkFlat    = true;    // Flatten and stop before the weekend
input EWkDay   InWkDay     = WK_FRI;  //   - cutoff day
input int      InWkHr      = 21;      //   - cutoff hour
input bool     InWk247     = false;   // Trade 24/7 - allow weekends (crypto)
input bool     InBosCnl    = true;    // Cancel a waiting order when a new BOS prints before it fills

input group "25. News / blackout windows - no trading inside these times"
input bool     InNewsOn    = true;    // News windows ON (OFF = no news and no US-holiday blocks at all)
input ENwExit  InNwExit    = NW_CLOSE; // When a window starts
input bool     InNw1On     = false;   // Window 1 - block trading
input string   InNw1       = "1725-1835"; //   - window 1 time (HHMM-HHMM, session timezone)
input bool     InNw2On     = false;   // Window 2 - block trading
input string   InNw2       = "1800-1900"; //   - window 2 time
input bool     InNw3On     = false;   // Window 3 - block trading
input string   InNw3       = "2330-0030"; //   - window 3 time

input group "26. Live-trading realism"
input double   InSprd      = 0.0;     // Broker spread, in price, for SIZING (0 = not modelled)

input group "27. Profit target - stop new trades"
input bool     InPtOn      = false;   // Stop taking new trades once the profit target is reached
input double   InPtAmt     = 500.0;   //   - profit target, in account currency
input EPtPer   InPtPer     = PT_TOTAL; //   - count the profit
input datetime InPtFrom    = D'2000.01.01 00:00'; //   - start date (only for Total), UTC

input group "28. News windows - only on chosen dates"
input bool     InNdOn      = false;   // News windows work ONLY on the dates below
input string   InNdList    = "";      //   - dates (day of the month), e.g. 3, 12-14, 28
input ENdScope InNdScope   = ND_MONTH; //   - these dates are for

input group "29. Automatic US news schedule, US clock, US holidays"
input bool     InAuOn      = false;   // Automatic US news windows (dates worked out by rule)
input bool     InAuNfp     = true;    //   - NFP jobs report - 08:30 New York
input bool     InAuJc      = true;    //   - Weekly jobless claims - every Thursday 08:30 New York
input bool     InAuIsmM    = true;    //   - ISM Manufacturing PMI - 1st working day 10:00 New York
input bool     InAuIsmS    = true;    //   - ISM Services PMI - 3rd working day 10:00 New York
input int      InAuPre     = 10;      //   - block from this many minutes BEFORE the release
input int      InAuPost    = 20;      //   - until this many minutes AFTER the release
input EUsClk   InUsClk     = US_AUTO; // US clock (summer / winter time)
input bool     InNwNy      = false;   // Read the group 25 window times in New York time
input bool     InHolTrade  = true;    // Trade on US market holidays

input group "31. Stacked BOS trades"
input int      InMaxOpen   = 0;       // Max trades open at the same time (0 = no limit)

input group "32. Stop management - step stop / break-even"
input bool     InMvStep    = false;   // Step stop - at every 1R, move the stop up one step
input bool     InMvBe      = false;   // Break-even only - once a candle CLOSES beyond 1R

input group "33. Trade direction and HEDGE"
input EDir     InDirMode   = DIR_BOTH; // Trade direction
input EHedgeMoney InHedgeMoney = HM_OWN; //   - hedge: loss recovery, floor, pause and daily limits

input group "34. v9.0 ideas - each one OFF by default"
input bool     InBkOn      = false;   // a. Smaller risk for stacked BOS trades
input double   InBkPct     = 50.0;    //   - risk of each stacked BOS trade, % of the normal risk
input bool     InHfOn      = false;   // b. Higher-timeframe filter - take a signal only in the higher timeframe direction
input bool     InTrOn      = false;   // c. Structure trailing stop
input ETrMode  InTrMode    = TR_LEVEL; //   - the stop follows
input bool     InLqOn      = false;   // d. Target at the next liquidity (the nearest untaken swing high / low)
input double   InLqMin     = 1.5;     //   - only a swing at least this far from the entry, in R
input bool     InPpOn      = false;   // e. Partial profit - a smaller part of every setup takes profit early
input double   InPpPct     = 50.0;    //   - size of the early part, % of the setup
input double   InPpR       = 1.0;     //   - early target, in R
input bool     InPpBe      = true;    //   - then move the rest to break-even
input bool     InPdOn      = false;   // f. Premium / discount filter - buy only at a discount, sell only at a premium
input double   InPdPct     = 50.0;    //   - the line, % of the leg (50 = the middle)
input bool     InLsOn      = false;   // g. Pause for the rest of the day after losses in a row
input int      InLsN       = 3;       //   - losses in a row

input group "35. Account floor + profit lock"
input EFl      InFlMode    = FL_OFF;  // Account floor - never lose more than the amount below, keep part of every new high
input double   InFlAmt     = 2000.0;  //   - the most the account may lose (below the start)
input double   InFlLock    = 50.0;    //   - lock this % of every new profit high
input double   InFlPct     = 2.5;     //   - risk per trade, % of the cushion above the floor

input group "36. Pause for days after losses in a row"
input bool     InLdOn      = false;   // Pause for some days after losses in a row
input int      InLdN       = 3;       //   - losses in a row
input int      InLdD       = 2;       //   - days to pause (after the rest of that day)

input group "37. Higher timeframe equilibrium first"
input bool     InEqOn      = false;   // Trade only after the higher timeframe pulled back to its equilibrium
input double   InEqPct     = 50.0;    //   - the equilibrium, % pullback of the higher timeframe leg

input group "40. EA - broker, clocks, chart"
input long     InMagic     = 111001;  // Magic number (a different one on every chart that runs this EA)
input string   InCmt       = "SMC";   // Order comment (text before the trade id)
input EExec    InExec      = EX_TOUCH; // How entries are executed
input int      InSlip      = 30;      // Max slippage for market orders, in points
input double   InSrvHours  = 2.0;     // Broker server time - hours from UTC in winter (FxPro: 2)
input EDst     InSrvDst    = DST_EU;  // Broker server time - summer time rule (FxPro: European)
input int      InWarm      = 20000;   // Bars of history used to build the structure before trading
input int      InResume    = 5;       // After a restart, keep a waiting setup if at most this many bars were missed
input bool     InDraw      = true;    // Draw the main structure (BOS* / CHOCH* lines, CHOCH / BOS marks)
input int      InDrawMax   = 200;     //   - how many past CHOCH / BOS marks to keep
input bool     InHtfDraw   = true;    // Draw the higher timeframe on this chart (its BOS* / CHOCH* levels, equilibrium)
input int      InHtfMarks  = 50;      //   - how many past higher-timeframe CHOCH / BOS marks to keep (0 = none)

input group "41. News from the MT5 economic calendar + no new trades before news"
input bool     InCalOn     = false;   // Economic calendar news windows (from MT5; needs group 25 'News windows ON')
input string   InCalCur    = "USD";   //   - currencies (comma list, e.g. USD or USD,EUR)
input ECalImp  InCalImp    = CI_HIGH; //   - which news
input int      InCalPre    = 10;      //   - block from this many minutes BEFORE the release
input int      InCalPost   = 20;      //   - until this many minutes AFTER the release
input bool     InCalHol    = true;    //   - calendar holidays too (only when 'Trade on US market holidays' is OFF)
input bool     InCalSave   = false;   //   - save the calendar to a file for the Strategy Tester (live chart only)
input bool     InPreOn     = false;   // No NEW trades in the hours before news (calendar news and group 29 US releases)
input double   InPreHrs    = 1.0;     //   - hours before the release (e.g. 1, 2 or 0.5)
input ECalToday InCalToday = CT_HIGHMED; // Show today's news in the table (time, impact, forecast / actual) - display only

input group "38. Stop buffer unit - price, pips or % (v11.2)"
input EBuMode  InBuMode    = BU_PRICE; // Stop buffer unit (also for group 24 'skip closer / further than')
input double   InBuPips    = 10.0;    //   - stop buffer in pips
input double   InBuPct     = 0.02;    //   - stop buffer in % of price
input double   InBuPip     = 0.0;     //   - pip size (0 = automatic)
input group "39. RULE 3 - enter at the close of the signal candle (v12.0)"
input bool     InR3On      = false;   // RULE 3 - enter at the close of the signal candle
input bool     InR3BrkOn   = false;   //   - RULE 3: only if the close is near the broken level
input double   InR3Brk     = 3.0;     //   - the most the close may be beyond the broken level
input bool     InR3Fb      = false;   //   - if the close is too far: fall back to RULE 1 / 2
input group "42. Loss recovery - start again from the base (v12.1)"
input bool     InLmOn      = false;   // Start again from the base risk when the losses carried reach
input double   InLmAmt     = 300.0;   //   - losses carried, in account currency
input group "43. Rule A / B / C split - the base risk grows with the profit (v12.2)"
input double   InSp1       = 200.0;   // Step 1 - total profit of at least
input double   InSpN1      = 3.0;     //   - split it into this many parts
input double   InSp2       = 500.0;   // Step 2 - total profit of at least
input double   InSpN2      = 5.0;     //   - split it into this many parts
input double   InSp3       = 1000.0;  // Step 3 - total profit of at least
input double   InSpN3      = 8.0;     //   - split it into this many parts
input double   InSpInc     = 500.0;   // Then a new step every this much more profit  (0 = no more steps)
input double   InSpAdd     = 1.0;     //   - each new step is split into this many more parts
input group "44. Signal audit labels on the chart (v12.3)"
input EAudSz   InAudSz     = AS_LARGE; // Audit label size (the labels show when 'Signal audit' in group 20 is ON)
input int      InAudMax    = 200;     //   - how many audit labels to keep on the chart (0 = none, the journal only)

//---------------------------------------------------------------- arrays used by the core (MQL5 version)
class CArrD
{
public:
   double v[];
   int    n;
   CArrD() { n = 0; }
   void   Clear()           { n = 0; ArrayResize(v, 0, 8192); }
   void   Add(double x)     { if (n >= ArraySize(v)) ArrayResize(v, n + 1, 8192); v[n] = x; n++; }
   double At(int i)         { return v[i]; }
   int    Size()            { return n; }
   void   DropFirst(int k)  { if (k <= 0) return; if (k >= n) { n = 0; return; } for (int i = 0; i + k < n; i++) v[i] = v[i + k]; n -= k; }
   void   RemoveAt(int i)   { for (int j = i; j + 1 < n; j++) v[j] = v[j + 1]; n--; }
};
class CArrI
{
public:
   int    v[];
   int    n;
   CArrI() { n = 0; }
   void   Clear()           { n = 0; ArrayResize(v, 0, 8192); }
   void   Add(int x)        { if (n >= ArraySize(v)) ArrayResize(v, n + 1, 8192); v[n] = x; n++; }
   int    At(int i)         { return v[i]; }
   int    Size()            { return n; }
   void   DropFirst(int k)  { if (k <= 0) return; if (k >= n) { n = 0; return; } for (int i = 0; i + k < n; i++) v[i] = v[i + k]; n -= k; }
   void   RemoveAt(int i)   { for (int j = i; j + 1 < n; j++) v[j] = v[j + 1]; n--; }
};

//==CORE-BEGIN==
//+------------------------------------------------------------------+
//| CORE: the v11.1 rules. Plain code only - the offline test        |
//| (tools/ea) compiles this same text as C++ and compares every     |
//| trade with the simulator that matches TradingView.               |
//| All times in the core are UTC epoch seconds.                     |
//+------------------------------------------------------------------+
#define NAD   (-1.0e300)
#define NAI   (-2147483647)
#define LNONE (-1)
#define MAXP  128
#define MAXF  16

bool   IsNa(double x)            { return x < -1.0e299; }
double Mx(double a, double b)    { return a > b ? a : b; }
double Mn(double a, double b)    { return a < b ? a : b; }
int    MxI(int a, int b)         { return a > b ? a : b; }
int    MnI(int a, int b)         { return a < b ? a : b; }
long   FloorDivL(long a, long b) { long q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) q--; return q; }

// ---------- calendar arithmetic (no library time functions, so history and live agree) ----------
long DaysFromCivil(int y, int m, int d)
{
   int  yy  = (m <= 2) ? y - 1 : y;
   long era = (yy >= 0 ? yy : yy - 399) / 400;
   long yoe = yy - era * 400;
   int  mp  = (m > 2) ? m - 3 : m + 9;
   long doy = (153 * mp + 2) / 5 + d - 1;
   long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
   return era * 146097 + doe - 719468;
}
void CivilFromDays(long zd, int &y, int &m, int &d)
{
   long z   = zd + 719468;
   long era = (z >= 0 ? z : z - 146096) / 146097;
   long doe = z - era * 146097;
   long yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
   long doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
   long mp  = (5 * doy + 2) / 153;
   d = (int)(doy - (153 * mp + 2) / 5 + 1);
   m = (int)(mp < 10 ? mp + 3 : mp - 9);
   y = (int)(yoe + era * 400 + (m <= 2 ? 1 : 0));
}
// 1 = Sunday ... 7 = Saturday (the TradingView numbering)
int  DowDays(long z)              { long w = (z + 4) % 7; if (w < 0) w += 7; return (int)w + 1; }
int  DaysInMonth(int y, int m)    { int y2 = m == 12 ? y + 1 : y; int m2 = m == 12 ? 1 : m + 1; return (int)(DaysFromCivil(y2, m2, 1) - DaysFromCivil(y, m, 1)); }
long NthSunday(int y, int m, int n) { long d1 = DaysFromCivil(y, m, 1); int w = DowDays(d1); return d1 + ((8 - w) % 7) + 7 * (n - 1); }
long LastSunday(int y, int m)     { int L = DaysInMonth(y, m); long dl = DaysFromCivil(y, m, L); return dl - (DowDays(dl) - 1); }
// offset of a clock from UTC at the instant utc. rule: 0 none, 1 EU summer time, 2 US summer time
long TzOff(long utc, long base, int rule)
{
   if (rule == 0) return base;
   int y = 0, m = 0, d = 0;
   CivilFromDays(FloorDivL(utc, 86400), y, m, d);
   long s = 0, e = 0;
   if (rule == 1) { s = LastSunday(y, 3) * 86400 + 3600; e = LastSunday(y, 10) * 86400 + 3600; }
   else           { s = NthSunday(y, 3, 2) * 86400 + 7200 - base; e = NthSunday(y, 11, 1) * 86400 + 7200 - (base + 3600); }
   return (utc >= s && utc < e) ? base + 3600 : base;
}
long LocToUtc(long loc, long base, int rule) { long u = loc - base; long off = TzOff(u, base, rule); return loc - off; }
int  MinOfDay(long loc)                      { long s = loc % 86400; if (s < 0) s += 86400; return (int)(s / 60); }
int  DAhead(int t, int a)                    { return ((a - t) % 1440 + 1440) % 1440; }
// does the bar [t, t+len) touch the window [a, b)? (TradingView f_ovl)
bool Ovl(int t, int len, int a, int b)       { int span = ((b - a) % 1440 + 1440) % 1440; return span > 0 && (DAhead(a, t) < span || DAhead(t, a) < len); }

// ---------- dynamic arrays used by the core (MQL5 and C++ each define CArrD / CArrI) ----------

// ---------- settings ----------
class CSet
{
public:
   bool   altMode, pbBodyOn, pbBodyRef, pbSwp2;
   bool   on, r1, r2;
   int    sig;
   double pb, rr, slBuf;
   bool   rev, once;
   int    sessMode;
   long   tzBase;
   int    tzRule;
   int    hrOn, hrOff, hrFlat;
   int    sizeMode;
   double risk, qty, cash, lotStep, rndMax, lev;
   int    seqMode;
   double seqMax;
   int    capAct;
   double seqAdd;
   int    seqFrom;
   long   seqFromT;
   double split;
   int    cmMode;
   double cmLot, cmUnit, cmPct, cmFix;
   bool   cmTgt;
   bool   cancelSig;
   int    expBars;
   double minStop, maxStop;
   int    maxTrades;
   double dayLoss, dd;
   bool   wkFlat;
   int    wkDay, wkHr;
   bool   wk247, bosCnl;
   bool   newsOn;
   int    nwExit;
   bool   nw1On, nw2On, nw3On;
   int    nw1A, nw1B, nw2A, nw2B, nw3A, nw3B;
   double sprd;
   bool   ptOn;
   double ptAmt;
   int    ptPer;
   long   ptFrom;
   bool   ndOn;
   bool   ndDays[32];
   int    ndScope;
   bool   auOn, auNfp, auJc, auIsmM, auIsmS;
   int    auPre, auPost, usClk;
   bool   nwNy, holTrade;
   int    maxOpen;
   bool   mvStep, mvBe;
   int    dirMode, hedgeMoney;
   bool   bkOn;
   double bkPct;
   bool   hfOn, trOn;
   int    trMode;
   bool   lqOn;
   double lqMin;
   bool   ppOn;
   double ppPct, ppR;
   bool   ppBe, pdOn;
   double pdPct;
   bool   lsOn;
   int    lsN;
   int    flMode;
   double flAmt, flLock, flPct;
   bool   ldOn;
   int    ldN, ldD;
   bool   eqOn;
   double eqPct;
   bool   calOn, calHol, preOn;
   int    calPre, calPost;
   long   preSec;
   int    buMode;
   double buPips, buPct, pipSz;
   bool   r3On, r3BrkOn, r3Fb; // v12.0: rule 3, 'only if the close is near the broken level', 'too far: fall back to rule 1 / 2'
   bool   lmOn;                // v12.1: group 42 - start again from the base when the losses carried reach lmAmt
   double lmAmt;
   double sp1, spN1, sp2, spN2, sp3, spN3, spInc, spAdd;   // v12.2: group 43 - the profit steps of Rule A / B / C split
   double r3Brk;
   // broker facts, set by the adapter
   int    cs;
   double cmLots, uv, minLot, tick;
   bool   htfOk;
   // worked out by Derive()
   bool   fav, agn, autoM, useCho, useBos, hfEff, u15, timeOn, intra, mvOn, mgOn, seqPlus;
   int    bMin, mvKMax;
   CSet() { for (int i = 0; i < 32; i++) ndDays[i] = false; calOn = false; calHol = false; preOn = false; calPre = 0; calPost = 0; preSec = 0; buMode = 0; buPips = 0; buPct = 0; pipSz = 0; r3On = false; r3BrkOn = false; r3Fb = false; r3Brk = 0; lmOn = false; lmAmt = 0; sp1 = 0; spN1 = 1; sp2 = 0; spN2 = 1; sp3 = 0; spN3 = 1; spInc = 0; spAdd = 0; }
   void Derive()
   {
      fav    = sig >= 3 && sig <= 5;
      agn    = sig >= 6 && sig <= 8;
      autoM  = sig >= 9;
      int b  = sig % 3;
      useCho = b != 1;
      useBos = b != 0;
      hfEff  = hfOn || fav;
      u15    = on && (r2 || hfEff || eqOn || agn || autoM) && htfOk;
      intra  = cs < 86400;
      timeOn = sessMode == 1 ? true : (sessMode == 2 ? false : intra);
      bMin   = MxI(1, cs / 60);
      mvOn   = mvStep || mvBe;
      mgOn   = mvOn || trOn || (ppOn && ppBe);
      mvKMax = MxI(0, (int)MathCeil(rr - 1e-9) - 1);
      seqPlus = seqMode >= 4 && seqMode <= 6;
   }
};
CSet S;

// v11.2: the stop buffer beyond the level lv, in price (pips x pip, or % of the level, rounded to the price step; else the group 20 buffer)
double RoundTick(double x) { return S.tick > 0 ? MathRound(x / S.tick) * S.tick : x; }
double BufAt(double lv)
{
   if (S.buMode == 1) return RoundTick(S.buPips * S.pipSz);
   if (S.buMode == 2) return RoundTick(lv * S.buPct / 100.0);
   return S.slBuf;
}
// v11.2: a group 24 limit (skip the setup if the stop is closer / further than) in price: pips, or % of the entry price
double LimAt(double v, double ent) { return S.buMode == 1 ? v * S.pipSz : (S.buMode == 2 ? ent * v / 100.0 : v); }

// ---------- time helpers on the chosen clocks ----------
long SessLoc(long utc) { return utc + TzOff(utc, S.tzBase, S.tzRule); }
long NyOff(long utc)   { if (S.usClk == 1) return -14400; if (S.usClk == 2) return -18000; return TzOff(utc, -18000, 2); }
long NyLoc(long utc)   { return utc + NyOff(utc); }
int  DomOf(long loc)   { int y = 0, m = 0, d = 0; CivilFromDays(FloorDivL(loc, 86400), y, m, d); return d; }

// ---------- US calendar (group 29), exactly as the Pine code ----------
int  UDow(int y, int m, int d) { return DowDays(DaysFromCivil(y, m, d)); }
void UAddD(int y, int m, int d, int n, int &ry, int &rm, int &rd) { CivilFromDays(DaysFromCivil(y, m, d) + n, ry, rm, rd); }
int  UNthDow(int y, int m, int w, int n) { return 1 + (w - UDow(y, m, 1) + 7) % 7 + 7 * (n - 1); }
int  ULastDow(int y, int m, int w) { int L = DaysInMonth(y, m); return L - (UDow(y, m, L) - w + 7) % 7; }
bool UObs(int y, int MM, int DD, int m, int d) { int w = UDow(y, MM, DD); return m == MM && d == (w == 7 ? DD - 1 : (w == 1 ? DD + 1 : DD)); }
// 0 = no holiday; 1 New Year, 2 Martin Luther King, 3 Presidents, 4 Memorial, 5 Juneteenth, 6 Independence, 7 Labor,
// 8 Thanksgiving, 9 Christmas, 10 Good Friday (only when gf)
int UsHol(int y, int m, int d, bool gf)
{
   if (m == 1 && ((d == 1 && UDow(y, 1, 1) != 1 && UDow(y, 1, 1) != 7) || (d == 2 && UDow(y, 1, 1) == 1))) return 1;
   if (m == 1 && d == UNthDow(y, 1, 2, 3)) return 2;
   if (m == 2 && d == UNthDow(y, 2, 2, 3)) return 3;
   if (m == 5 && d == ULastDow(y, 5, 2)) return 4;
   if (y >= 2022 && UObs(y, 6, 19, m, d)) return 5;
   if (UObs(y, 7, 4, m, d)) return 6;
   if (m == 9 && d == UNthDow(y, 9, 2, 1)) return 7;
   if (m == 11 && d == UNthDow(y, 11, 5, 4)) return 8;
   if (UObs(y, 12, 25, m, d)) return 9;
   if (gf && (m == 3 || m == 4))
   {
      int a  = y % 19;
      int b  = y / 100;
      int c  = y % 100;
      int h  = (19 * a + b - b / 4 - (b - (b + 8) / 25 + 1) / 3 + 15) % 30;
      int l  = (32 + 2 * (b % 4) + 2 * (c / 4) - h - c % 4) % 7;
      int q  = (a + 11 * h + 22 * l) / 451;
      int gy = 0, gm = 0, gd = 0;
      UAddD(y, (h + l - 7 * q + 114) / 31, (h + l - 7 * q + 114) % 31 + 1, -2, gy, gm, gd);
      if (m == gm && d == gd) return 10;
   }
   return 0;
}
string UsHolName(int k)
{
   if (k == 1) return "New Year";
   if (k == 2) return "Martin Luther King Day";
   if (k == 3) return "Presidents' Day";
   if (k == 4) return "Memorial Day";
   if (k == 5) return "Juneteenth";
   if (k == 6) return "Independence Day";
   if (k == 7) return "Labor Day";
   if (k == 8) return "Thanksgiving";
   if (k == 9) return "Christmas";
   if (k == 10) return "Good Friday";
   return "";
}
// NFP: third Friday after the week (Sun-Sat) holding the 12th of the previous month
void UNfp(int y, int m, int &ry, int &rm, int &rd)
{
   int py = m == 1 ? y - 1 : y;
   int pm = m == 1 ? 12 : m - 1;
   UAddD(py, pm, 12 + (7 - UDow(py, pm, 12)) % 7, 20, ry, rm, rd);
   int a = 0, b = 0, c = 0;
   if (rm == 1 && rd <= 3) { UAddD(ry, rm, rd, 7, a, b, c); ry = a; rm = b; rd = c; }
   if (UsHol(ry, rm, rd, false) != 0) { UAddD(ry, rm, rd, -1, a, b, c); ry = a; rm = b; rd = c; }
}
// n-th US working day of the month (0 = not a working day, or later than the 10th)
int UBday(int y, int m, int d)
{
   int n = 0;
   if (d <= 10 && UDow(y, m, d) != 1 && UDow(y, m, d) != 7 && UsHol(y, m, d, false) == 0)
      for (int k = 1; k <= d; k++)
      {
         int w = UDow(y, m, k);
         if (w != 1 && w != 7 && UsHol(y, m, k, false) == 0) n++;
      }
   return n;
}
long NyInstant(int y, int m, int d, int hh, int mm)
{
   long loc = DaysFromCivil(y, m, d) * 86400 + hh * 3600 + mm * 60;
   if (S.usClk == 1) return loc + 14400;
   if (S.usClk == 2) return loc + 18000;
   return LocToUtc(loc, -18000, 2);
}
// the enabled releases on one New York date (LNONE = none)
void UAuDay(int y, int m, int d, long &t1, long &t2, long &t3, long &t4)
{
   int fy = 0, fm = 0, fd = 0, ty = 0, tm = 0, td = 0;
   UNfp(y, m, fy, fm, fd);
   UAddD(y, m, d, 1, ty, tm, td);
   int  w  = UDow(y, m, d);
   bool jc = (w == 5 && UsHol(y, m, d, false) == 0) || (w == 4 && UsHol(ty, tm, td, false) != 0);
   int  bd = (S.auIsmM || S.auIsmS) ? UBday(y, m, d) : 0;
   int  sh = m == 1 ? 1 : 0;
   t1 = (S.auNfp && fy == y && fm == m && fd == d) ? NyInstant(y, m, d, 8, 30) : LNONE;
   t2 = (S.auJc && jc) ? NyInstant(y, m, d, 8, 30) : LNONE;
   t3 = (S.auIsmM && bd == 1 + sh) ? NyInstant(y, m, d, 10, 0) : LNONE;
   t4 = (S.auIsmS && bd == 3 + sh) ? NyInstant(y, m, d, 10, 0) : LNONE;
}

// ---------- structure engine (main tier) ----------
struct Trk
{
   bool   isHigh;
   double potential;
   int    potentialBar;
   int    count;
   double refLevel;
   bool   swept;
};
void TrkInit(Trk &t, bool hi) { t.isHigh = hi; t.potential = NAD; t.potentialBar = NAI; t.count = 0; t.refLevel = NAD; t.swept = false; }
// TradingView SwingTracker.update: a swing confirms after 3 pullback candles (2 once the opposite level is swept)
void TrkUpdate(Trk &t, double swpLvl, double o, double h, double l, double c, int bi, double &confP, int &confB)
{
   confP = NAD;
   confB = NAI;
   bool   bearC = c < o;
   bool   bullC = c > o;
   double bd    = MathAbs(c - o);
   double wk    = Mx(h - Mx(o, c), Mn(o, c) - l);
   bool   pbQ   = !(S.pbBodyOn || S.pbBodyRef) || bd > wk;
   bool   pb    = (t.isHigh ? bearC : bullC) && pbQ;
   double rf    = S.pbBodyRef ? (t.isHigh ? Mn(o, c) : Mx(o, c)) : (t.isHigh ? l : h);
   bool newExt  = IsNa(t.potential) || (t.isHigh ? h >= t.potential : l <= t.potential);
   if (newExt)
   {
      t.potential    = t.isHigh ? h : l;
      t.potentialBar = bi;
      t.count        = pb ? 1 : 0;
      t.refLevel     = pb ? rf : NAD;
      t.swept        = false;
      return;
   }
   if (!IsNa(swpLvl) && (t.isHigh ? l < swpLvl : h > swpLvl)) t.swept = true;
   if (!pb) return;
   bool beyond = !IsNa(t.refLevel) && (t.isHigh ? c < t.refLevel : c > t.refLevel);
   if (t.count == 0) { t.count = 1; t.refLevel = rf; }
   else if ((t.count == 1 && beyond && t.swept) || (t.count == 2 && beyond))
   {
      confP          = t.potential;
      confB          = t.potentialBar;
      t.potential    = t.isHigh ? h : l;
      t.potentialBar = bi;
      t.count        = 1;
      t.refLevel     = rf;
      t.swept        = false;
   }
   else if (t.count == 1 && beyond) { t.count = 2; t.refLevel = rf; }
}

// a live structure line: the ceiling (BOS* / CHOCH* above the price) or the floor
struct SLn
{
   bool   ok;
   int    x1;
   double price;
   int    sid;
   int    born;
   double swpP;
   int    swpB;
   double refP;
   double idmP;
   int    idmB;
   bool   idmHit;
   bool   swpT;
};
void SLnMake(SLn &s, double p, int b, int sid, int born)
{
   s.ok = true; s.x1 = b; s.price = p; s.sid = sid; s.born = born; s.swpP = NAD; s.swpB = NAI; s.refP = NAD;
   s.idmP = NAD; s.idmB = NAI; s.idmHit = false; s.swpT = false;
}

class CEngine
{
public:
   CArrD  bufHi, bufLo, msLoP, msHiP;
   CArrI  msLoB, msHiB, mnHiB, mnLoB;
   double allHi, allLo, mRunHi, mRunLo;
   Trk    hiT, loT;
   int    trendDir, bi;
   SLn    cel, flr;
   bool   evBU, evBD, evCU, evCD;
   double swH, swL;
   double brkP;     // the level broken on this bar (drawing)
   int    brkX;
   CEngine() { Reset(); }
   void Reset()
   {
      bufHi.Clear(); bufLo.Clear(); msLoP.Clear(); msHiP.Clear(); msLoB.Clear(); msHiB.Clear(); mnHiB.Clear(); mnLoB.Clear();
      allHi = NAD; allLo = NAD; mRunHi = NAD; mRunLo = NAD;
      TrkInit(hiT, true); TrkInit(loT, false);
      trendDir = 0; bi = -1;
      cel.ok = false; flr.ok = false;
      evBU = false; evBD = false; evCU = false; evCD = false; swH = NAD; swL = NAD; brkP = NAD; brkX = NAI;
   }
   // f_retExtreme (inc = false: up to the previous bar) / f_retExtInc (inc = true: up to this bar)
   void RetExt(int fromBar, bool findHigh, bool inc, double &p, int &b)
   {
      int sz = bufLo.Size();
      int jEnd = sz - 1;
      p = NAD;
      b = NAI;
      if (inc ? jEnd < 0 : jEnd <= 0) return;
      int last = inc ? jEnd : jEnd - 1;
      int j0   = MxI(0, MnI(fromBar - bi + sz, last));
      int base = bi - sz + 1;
      for (int j = j0; j <= last; j++)
      {
         double v = findHigh ? bufHi.At(j) : bufLo.At(j);
         if (IsNa(p) || (findHigh ? v >= p : v <= p)) { p = v; b = base + j; }
      }
   }
   bool SwpConf(CArrI &arrB, int swpB)
   {
      if (swpB == NAI) return false;
      for (int i = arrB.Size() - 1; i >= 0; i--)
      {
         int cb = arrB.At(i);
         if (cb == swpB) return true;
         if (cb < swpB) return false;
      }
      return false;
   }
   void LastMinor(bool wantLow, int beforeBar, double &p, int &b)
   {
      p = NAD;
      b = NAI;
      if (wantLow)
      {
         for (int i = msLoB.Size() - 1; i >= 0; i--)
            if (msLoB.At(i) < beforeBar) { p = msLoP.At(i); b = msLoB.At(i); return; }
      }
      else
      {
         for (int i = msHiB.Size() - 1; i >= 0; i--)
            if (msHiB.At(i) < beforeBar) { p = msHiP.At(i); b = msHiB.At(i); return; }
      }
   }
   // the inducement (IDM) of a new line - only the ALTERNATE rule uses it
   void ArmIdm(SLn &s, double h, double l)
   {
      if (!s.ok) return;
      bool isCeil = s.sid == 0 || s.sid == 2;
      double ip = NAD;
      int ib = NAI;
      LastMinor(isCeil, s.x1, ip, ib);
      s.idmP = ip;
      s.idmB = ib;
      s.idmHit = false;
      if (!IsNa(ip))
      {
         double xp = NAD;
         int xb = NAI;
         RetExt(s.x1, !isCeil, false, xp, xb);
         bool past = !IsNa(xp) && (isCeil ? xp < ip : xp > ip);
         bool now  = isCeil ? l < ip : h > ip;
         if (past || now) s.idmHit = true;
      }
   }
   void Step(double o, double h, double l, double c)
   {
      bi++;
      evBU = false; evBD = false; evCU = false; evCD = false; brkP = NAD; brkX = NAI;
      bufHi.Add(h);
      bufLo.Add(l);
      if (bufHi.Size() > 5150) { int cut = bufHi.Size() - 4900; bufHi.DropFirst(cut); bufLo.DropFirst(cut); }
      allHi = IsNa(allHi) ? h : Mx(allHi, h);
      allLo = IsNa(allLo) ? l : Mn(allLo, l);
      int n = bufHi.Size();
      if (bi >= 2 && n >= 3)
      {
         double l1 = bufLo.At(n - 2), l2 = bufLo.At(n - 3), h1 = bufHi.At(n - 2), h2 = bufHi.At(n - 3);
         if (l1 < l2 && l1 < l) { msLoB.Add(bi - 1); msLoP.Add(l1); if (msLoB.Size() > 200) { msLoB.DropFirst(1); msLoP.DropFirst(1); } }
         if (h1 > h2 && h1 > h) { msHiB.Add(bi - 1); msHiP.Add(h1); if (msHiB.Size() > 200) { msHiB.DropFirst(1); msHiP.DropFirst(1); } }
      }
      double swpH = (S.pbSwp2 && flr.ok) ? flr.price : NAD;
      double swpL = (S.pbSwp2 && cel.ok) ? cel.price : NAD;
      double phP = NAD, plP = NAD;
      int    phB = NAI, plB = NAI;
      TrkUpdate(hiT, swpH, o, h, l, c, bi, phP, phB);
      TrkUpdate(loT, swpL, o, h, l, c, bi, plP, plB);
      swH = phP;
      swL = plP;
      if (!IsNa(phP)) { mnHiB.Add(phB); if (mnHiB.Size() > 300) mnHiB.DropFirst(1); }
      if (!IsNa(plP)) { mnLoB.Add(plB); if (mnLoB.Size() > 300) mnLoB.DropFirst(1); }
      if (!IsNa(phP))
      {
         bool cSw = cel.ok && !IsNa(cel.swpP);
         bool cEq = cel.ok && phP == cel.price;
         bool adopt = trendDir == 0 ? (phP >= allHi && !cSw && !cEq) : !cel.ok;
         if (adopt) { SLnMake(cel, phP, phB, trendDir == -1 ? 2 : 0, bi); ArmIdm(cel, h, l); }
      }
      if (!IsNa(plP))
      {
         bool fSw = flr.ok && !IsNa(flr.swpP);
         bool fEq = flr.ok && plP == flr.price;
         bool adopt = trendDir == 0 ? (plP <= allLo && !fSw && !fEq) : !flr.ok;
         if (adopt) { SLnMake(flr, plP, plB, trendDir == 1 ? 3 : 1, bi); ArmIdm(flr, h, l); }
      }
      if (cel.ok && !cel.idmHit && !IsNa(cel.idmP) && l < cel.idmP) cel.idmHit = true;
      if (flr.ok && !flr.idmHit && !IsNa(flr.idmP) && h > flr.idmP) flr.idmHit = true;
      // the ceiling
      if (cel.ok && bi > cel.born)
      {
         if (c > cel.price && (trendDir == -1 || !S.altMode || cel.idmHit || IsNa(cel.idmP)))
         {
            bool isCho = trendDir == -1;
            evCU = isCho;
            evBU = !isCho;
            brkP = cel.price;
            brkX = cel.x1;
            double rp = NAD;
            int rb = NAI;
            RetExt(cel.x1, false, true, rp, rb);
            if (!IsNa(rp)) { SLnMake(flr, rp, rb, 3, bi); ArmIdm(flr, h, l); }
            trendDir = 1;
            cel.ok = false;
         }
         else
         {
            if (h > cel.price)
            {
               if (IsNa(cel.swpP) || h > cel.swpP) { cel.swpP = h; cel.swpB = bi; cel.swpT = false; }
               if (S.altMode && !cel.idmHit && !IsNa(cel.idmP) && c > cel.price && !IsNa(cel.swpP))
               {
                  double mp = cel.swpP;
                  int mb = cel.swpB, md = cel.sid;
                  SLnMake(cel, mp, mb, md, bi);
                  ArmIdm(cel, h, l);
               }
            }
            if (!IsNa(cel.swpP) && IsNa(cel.refP)) { double rp = NAD; int rb = NAI; RetExt(cel.x1, false, false, rp, rb); cel.refP = rp; }
            if (cel.swpB != NAI && cel.swpB == bi && trendDir == 1 && !IsNa(cel.refP) && l < cel.refP) cel.swpT = true;
            if (trendDir == 1 && !IsNa(cel.swpP) && !IsNa(cel.refP) && l < cel.refP && (!cel.swpT || SwpConf(mnHiB, cel.swpB)))
            {
               double sp = cel.swpP;
               int sb = cel.x1, sd = cel.sid;
               SLnMake(cel, sp, sb, sd, bi);
               ArmIdm(cel, h, l);
            }
         }
      }
      // the floor
      if (flr.ok && bi > flr.born)
      {
         if (c < flr.price && (trendDir == 1 || !S.altMode || flr.idmHit || IsNa(flr.idmP)))
         {
            bool isCho = trendDir == 1;
            evCD = isCho;
            evBD = !isCho;
            brkP = flr.price;
            brkX = flr.x1;
            double rp = NAD;
            int rb = NAI;
            RetExt(flr.x1, true, true, rp, rb);
            if (!IsNa(rp)) { SLnMake(cel, rp, rb, 2, bi); ArmIdm(cel, h, l); }
            trendDir = -1;
            flr.ok = false;
         }
         else
         {
            if (l < flr.price)
            {
               if (IsNa(flr.swpP) || l < flr.swpP) { flr.swpP = l; flr.swpB = bi; flr.swpT = false; }
               if (S.altMode && !flr.idmHit && !IsNa(flr.idmP) && c < flr.price && !IsNa(flr.swpP))
               {
                  double mp = flr.swpP;
                  int mb = flr.swpB, md = flr.sid;
                  SLnMake(flr, mp, mb, md, bi);
                  ArmIdm(flr, h, l);
               }
            }
            if (!IsNa(flr.swpP) && IsNa(flr.refP)) { double rp = NAD; int rb = NAI; RetExt(flr.x1, true, false, rp, rb); flr.refP = rp; }
            if (flr.swpB != NAI && flr.swpB == bi && trendDir == -1 && !IsNa(flr.refP) && h > flr.refP) flr.swpT = true;
            if (trendDir == -1 && !IsNa(flr.swpP) && !IsNa(flr.refP) && h > flr.refP && (!flr.swpT || SwpConf(mnLoB, flr.swpB)))
            {
               double sp = flr.swpP;
               int sb = flr.x1, sd = flr.sid;
               SLnMake(flr, sp, sb, sd, bi);
               ArmIdm(flr, h, l);
            }
         }
      }
      if (evBU || evBD || evCU || evCD) { mRunHi = h; mRunLo = l; }
      else { mRunHi = IsNa(mRunHi) ? h : Mx(mRunHi, h); mRunLo = IsNa(mRunLo) ? l : Mn(mRunLo, l); }
   }
   void Anchors(double &a, double &g)
   {
      a = NAD;
      g = NAD;
      if (trendDir == 1)       { a = mRunHi; g = mRunLo; if (flr.ok) g = flr.price; }
      else if (trendDir == -1) { a = mRunLo; g = mRunHi; if (cel.ok) g = cel.price; }
   }
};
CEngine EN;

double RetLvl(int d, double anch, double orig, double pct)
{
   if (d == 1 && !IsNa(anch) && !IsNa(orig) && anch > orig) return anch - (anch - orig) * pct / 100.0;
   if (d == -1 && !IsNa(anch) && !IsNa(orig) && orig > anch) return anch + (orig - anch) * pct / 100.0;
   return NAD;
}

// ---------- higher-timeframe engine (fed with CLOSED higher-timeframe candles) ----------
class CHtf
{
public:
   Trk    tkHi, tkLo;
   double tAllHi, tAllLo, tRunLo, tRunHi, tCeil, tFlor, outO, outX;
   int    tCeilB, tFlorB, tTrend, evN, hb;
   bool   brkNow, brkUp, brkCho;   // a CHOCH / BOS on this candle (drawing only)
   double brkP;
   int    brkB;
   CHtf() { Reset(); }
   void Reset()
   {
      TrkInit(tkHi, true); TrkInit(tkLo, false);
      tAllHi = NAD; tAllLo = NAD; tRunLo = NAD; tRunHi = NAD; tCeil = NAD; tFlor = NAD; outO = NAD; outX = NAD;
      tCeilB = NAI; tFlorB = NAI; tTrend = 0; evN = 0; hb = -1;
      brkNow = false; brkUp = false; brkCho = false; brkP = NAD; brkB = NAI;
   }
   void Step(double o, double h, double l, double c)
   {
      hb++;
      brkNow = false;
      tAllHi = IsNa(tAllHi) ? h : Mx(tAllHi, h);
      tAllLo = IsNa(tAllLo) ? l : Mn(tAllLo, l);
      tRunLo = IsNa(tRunLo) ? l : Mn(tRunLo, l);
      tRunHi = IsNa(tRunHi) ? h : Mx(tRunHi, h);
      double cfH = NAD, cfL = NAD;
      int cbH = NAI, cbL = NAI;
      TrkUpdate(tkHi, S.pbSwp2 ? tFlor : NAD, o, h, l, c, hb, cfH, cbH);
      TrkUpdate(tkLo, S.pbSwp2 ? tCeil : NAD, o, h, l, c, hb, cfL, cbL);
      if (!IsNa(cfH))
      {
         bool ad = tTrend == 0 ? cfH >= tAllHi : IsNa(tCeil);
         if (ad || (!IsNa(tCeil) && cfH == tCeil)) { tCeil = cfH; tCeilB = hb; tRunLo = l; }
      }
      if (!IsNa(cfL))
      {
         bool ad = tTrend == 0 ? cfL <= tAllLo : IsNa(tFlor);
         if (ad || (!IsNa(tFlor) && cfL == tFlor)) { tFlor = cfL; tFlorB = hb; tRunHi = h; }
      }
      if (!IsNa(tCeil) && tCeilB != NAI && hb > tCeilB && c > tCeil)
      { brkNow = true; brkUp = true; brkCho = tTrend == -1; brkP = tCeil; brkB = tCeilB; tTrend = 1; tFlor = tRunLo; tFlorB = hb; tRunHi = h; tCeil = NAD; tCeilB = NAI; evN++; }
      else if (!IsNa(tFlor) && tFlorB != NAI && hb > tFlorB && c < tFlor)
      { brkNow = true; brkUp = false; brkCho = tTrend == 1; brkP = tFlor; brkB = tFlorB; tTrend = -1; tCeil = tRunHi; tCeilB = hb; tRunLo = l; tFlor = NAD; tFlorB = NAI; evN++; }
      if (tTrend == 1)       { outX = tRunHi; outO = IsNa(tFlor) ? tRunLo : tFlor; }
      else if (tTrend == -1) { outX = tRunLo; outO = IsNa(tCeil) ? tRunHi : tCeil; }
      else                   { outO = NAD; outX = NAD; }
   }
};
CHtf HT;

// ---------- what the broker reports for one side on one bar ----------
struct PosRec
{
   long   id;
   long   ticket;
   int    dir;
   double q;
   double ent;
   double sl;
   double tgt;
   long   tOpen;
   int    seq;
   int    piece;
};
struct FillRec
{
   long   id;
   int    dir;
   double q;
   double ent;
   long   t;
   int    seq;
   int    piece;
   bool   atOpen;   // filled at once when the order was sent (the price was already through it)
};
struct ClsRec
{
   long   id;
   int    dir;
   double q;
   double pnl;
   long   tIn;
   long   tOut;
   int    seq;
   int    piece;
   int    why;      // 1 stop, 2 target, 0 anything else
};
class CSideIO
{
public:
   int     nPos, nFill, nCls;
   PosRec  pos[MAXP];
   FillRec fill[MAXF];
   ClsRec  cls[MAXP];
   CSideIO() { Clear(); }
   void Clear() { nPos = 0; nFill = 0; nCls = 0; }
};
CSideIO g_io[2];

// a trade whose stop the strategy manages (group 32, trailing stop, break-even after the early profit)
struct TrkRec
{
   long   id;
   long   ticket;
   int    dir;
   double ent;
   double r;
   double be;
   double sl;
   double tgt;
   double q;
   int    step;
   int    bar;
   bool   mv;
   bool   pp;
   int    seq;
   int    piece;
};

// ---------- broker actions (the MQL5 part sends real orders; the test emulates TradingView) ----------
void BkCancel(int side);
void BkCancelPiece(int side, int piece);
void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt);
void BkCloseAll(int side, string why);
void BkSetStop(int side, long ticket, int dir, double sl, double tgt);
void BkNote(int side, string msg);

// ---------- state shared by both sides ----------
int    g_nSides = 1;
int    g_sideMi[2];
int    g_sideDir[2];
bool   g_dry = false;
long   g_t = 0, g_now = 0;
double g_o = 0, g_h = 0, g_l = 0, g_c = 0, g_eq = 0;
int    g_tM = 0;
bool   g_win = true, g_flatNow = false, g_wkBlock = false, g_wkNow = false, g_nwNow = false, g_holNow = false;
bool   g_deadPrev = false, g_wkPrev = false;
int    g_T15 = 0, g_htE = 0, g_prevE = 0, g_autoDir = 0;
double g_htO = NAD, g_htX = NAD;
bool   g_eqOpen = false, g_eqBlock = false, g_firstBar = true;
double g_cmU = 0, g_cmPx = 0, g_mAnch = NAD, g_mOrig = NAD, g_eqLvl = NAD;
double g_ceilPrev = NAD, g_florPrev = NAD;
CArrD  g_lqH, g_lqL;
int    g_auKey = -1, g_holT0 = 0, g_holT1 = 0;
long   g_auT1 = LNONE, g_auT2 = LNONE, g_auT3 = LNONE, g_auT4 = LNONE;
// group 41: the chosen economic-calendar news (UTC seconds, oldest first) and holiday days (New York date, days since 1970),
// both filled by the MT5 part; tomorrow's group 29 releases (for 'no new trades before news')
CArrD  g_calT;
CArrI  g_calHol;
int    g_calI = 0;
bool   g_calH0 = false, g_calH1 = false, g_preNow = false, g_holCal = false;
long   g_auN1 = LNONE, g_auN2 = LNONE, g_auN3 = LNONE, g_auN4 = LNONE;

// ---------- costs and size (f_stCmU / f_stCmF / f_stQty) ----------
double CmU(double ent)
{
   double c = 0.0;
   if (S.cmMode == 1 || S.cmMode == 2) c = S.cmLots > 0 ? 2.0 * S.cmLot / S.cmLots : 0.0;
   else if (S.cmMode == 3) c = 2.0 * S.cmPct / 100.0 * Mx(ent, 0.0) * S.uv;
   return c + (S.sprd > 0 ? S.sprd * S.uv : 0.0);
}
double CmF()    { return S.cmMode == 4 ? 2.0 * S.cmFix : 0.0; }
double LotDiv() { return S.cmLots > 0 ? S.cmLots : 1.0; }
void Qty(double ent, double rsk, double amt, double pos, double &q, bool &cap)
{
   q = 0.0;
   double per = 0.0;
   double val = ent > 0 ? ent * S.uv : 0.0;
   if (S.sizeMode == 1) q = S.qty;
   else if (S.sizeMode == 2) q = val > 0 ? S.cash / val : 0.0;
   else
   {
      per = rsk * S.uv + CmU(ent);
      double net = Mx(0.0, amt - CmF());
      q = per > 0 ? net / per : 0.0;
   }
   double st  = (S.lotStep > 0 && S.cmLots > 0) ? S.lotStep * S.cmLots : 0.0;
   double raw = q;
   if (st > 0)
   {
      q = MathFloor(raw / st + 0.5) * st;
      if (S.rndMax > 0 && per > 0 && amt > 0 && q * per + CmF() > amt * (1.0 + S.rndMax / 100.0)) q = MathFloor(raw / st) * st;
   }
   double lim = (val > 0 && S.lev > 0) ? Mx(0.0, g_eq * S.lev / val - MathAbs(pos)) : 0.0;
   cap = val > 0 && S.lev > 0 && q > lim;
   if (cap) q = st > 0 ? MathFloor(lim / st) * st : lim;
}
// nearest untaken swing at or beyond lim (idea d)
double LqNear(int dir, double lim)
{
   double b = NAD;
   if (IsNa(lim)) return b;
   if (dir == 1)
   {
      for (int i = 0; i < g_lqH.Size(); i++) { double v = g_lqH.At(i); if (v >= lim && (IsNa(b) || v < b)) b = v; }
   }
   else
   {
      for (int i = 0; i < g_lqL.Size(); i++) { double v = g_lqL.At(i); if (v <= lim && (IsNa(b) || v > b)) b = v; }
   }
   return b;
}

// ---------- news windows (groups 25, 28, 29) ----------
bool NdOk(long ts)
{
   if (!S.ndOn) return true;
   long lt = SessLoc(ts);
   int y = 0, m = 0, d = 0, ny = 0, nm = 0, nd = 0;
   CivilFromDays(FloorDivL(lt, 86400), y, m, d);
   if (!S.ndDays[d]) return false;
   if (S.ndScope == 1) return true;
   CivilFromDays(FloorDivL(SessLoc(g_now), 86400), ny, nm, nd);
   return m == nm && y == ny;
}
bool NwHit(bool on, int a, int b, int t, int len, long tc)
{
   if (!on || a < 0 || b < 0) return false;
   int span = ((b - a) % 1440 + 1440) % 1440;
   if (span <= 0) return false;
   int back = DAhead(a, t);
   int fwd  = DAhead(t, a);
   return (back < span && NdOk(tc - (long)back * 60)) || (fwd < len && NdOk(tc + (long)fwd * 60));
}
bool AuHit(long T, long tc, long lenS) { return T != LNONE && tc < T + (long)S.auPost * 60 && tc + lenS > T - (long)S.auPre * 60; }
// group 41: does the next bar [tc, tc + lenS) touch [T - hours before, T)? (no NEW trades there)
bool PreHit(long T, long tc, long lenS) { return T != LNONE && S.preSec > 0 && tc < T && tc + lenS > T - S.preSec; }
bool CalHolOn(long dn) { for (int i = 0; i < g_calHol.Size(); i++) if ((long)g_calHol.At(i) == dn) return true; return false; }
// the MT5 part calls this after it replaced g_calT / g_calHol
void CalChanged() { g_calI = 0; g_auKey = -1; }
void NewsFlags(long tc)
{
   bool auNow = false, calNow = false;
   g_holNow = false;
   g_holCal = false;
   g_preNow = false;
   bool auUse = S.newsOn && S.intra && (S.auOn || !S.holTrade);
   bool chUse = S.calOn && S.calHol && !S.holTrade;
   bool apUse = S.auOn && S.preOn;
   long lenS = (long)S.bMin * 60;
   if (auUse)
   {
      int y = 0, m = 0, d = 0;
      CivilFromDays(FloorDivL(NyLoc(tc), 86400), y, m, d);
      int key = y * 10000 + m * 100 + d;
      if (key != g_auKey)
      {
         g_auKey = key;
         int hy = 0, hm = 0, hd = 0;
         UAddD(y, m, d, 1, hy, hm, hd);
         g_holT0 = S.holTrade ? 0 : UsHol(y, m, d, true);
         g_holT1 = S.holTrade ? 0 : UsHol(hy, hm, hd, true);
         if (S.auOn) UAuDay(y, m, d, g_auT1, g_auT2, g_auT3, g_auT4);
         if (chUse) { long dn = DaysFromCivil(y, m, d); g_calH0 = CalHolOn(dn); g_calH1 = CalHolOn(dn + 1); }
         if (apUse) UAuDay(hy, hm, hd, g_auN1, g_auN2, g_auN3, g_auN4);
      }
      if (S.auOn) auNow = AuHit(g_auT1, tc, lenS) || AuHit(g_auT2, tc, lenS) || AuHit(g_auT3, tc, lenS) || AuHit(g_auT4, tc, lenS);
      if (!S.holTrade) g_holNow = g_holT0 != 0 || (g_holT1 != 0 && DomOf(NyLoc(tc + lenS - 1)) != DomOf(NyLoc(tc)));
      if (chUse)
      {
         bool ch = g_calH0 || (g_calH1 && DomOf(NyLoc(tc + lenS - 1)) != DomOf(NyLoc(tc)));
         g_holCal = ch && !g_holNow;
         g_holNow = g_holNow || ch;
      }
      if (apUse) g_preNow = PreHit(g_auT1, tc, lenS) || PreHit(g_auT2, tc, lenS) || PreHit(g_auT3, tc, lenS) || PreHit(g_auT4, tc, lenS) ||
                            PreHit(g_auN1, tc, lenS) || PreHit(g_auN2, tc, lenS) || PreHit(g_auN3, tc, lenS) || PreHit(g_auN4, tc, lenS);
   }
   // group 41: the economic-calendar news windows, and 'no new trades before news'
   if (S.newsOn && S.intra && S.calOn)
   {
      long pre = (long)S.calPre * 60, post = (long)S.calPost * 60;
      long ahead = (S.preOn && S.preSec > pre) ? S.preSec : pre;
      while (g_calI < g_calT.Size() && (long)g_calT.At(g_calI) + post <= tc) g_calI++;
      for (int i = g_calI; i < g_calT.Size(); i++)
      {
         long T = (long)g_calT.At(i);
         if (T - ahead >= tc + lenS) break;
         if (tc < T + post && tc + lenS > T - pre) calNow = true;
         if (S.preOn && PreHit(T, tc, lenS)) g_preNow = true;
      }
   }
   int tMw = S.nwNy ? MinOfDay(NyLoc(tc)) : g_tM;
   bool win = S.intra && (NwHit(S.nw1On, S.nw1A, S.nw1B, tMw, S.bMin, tc) || NwHit(S.nw2On, S.nw2A, S.nw2B, tMw, S.bMin, tc) || NwHit(S.nw3On, S.nw3A, S.nw3B, tMw, S.bMin, tc));
   g_nwNow = S.newsOn && (win || auNow || g_holNow || calNow);
}

// v12.2: Rule A / B / C split - the base risk from the profit steps of group 43: the step reached / its parts (0 = no step)
double StepBase(double pf)
{
   double a = 0, n = 1;
   if (S.sp1 > 0 && pf >= S.sp1 - 0.005 && S.sp1 > a) { a = S.sp1; n = S.spN1; }
   if (S.sp2 > 0 && pf >= S.sp2 - 0.005 && S.sp2 > a) { a = S.sp2; n = S.spN2; }
   if (S.sp3 > 0 && pf >= S.sp3 - 0.005 && S.sp3 > a)
   {
      a = S.sp3;
      n = S.spN3;
      if (S.spInc > 0)
      {
         double k = MathFloor((pf - S.sp3 + 0.005) / S.spInc);
         a = S.sp3 + k * S.spInc;
         n = S.spN3 + k * S.spAdd;
      }
   }
   return a > 0 ? a / n : 0.0;
}
// ---------- money: loss recovery, floor, daily limits, pause (one per side, or one shared) ----------
class CMoney
{
public:
   double seqLoss, seqTot, flPnl, flPeak, dayPnl, ptPnl, peakEq, riskNow, flFloor, flCush, flRisk;
   bool   seqHalt, seqCapOn, dayHalt, ptHalt, ddHit;
   int    cntSeqCap, dayTrades, lsRun, cntLs, ldRun, cntLd, prevDom;
   int    cntLm;     // v12.1: times the losses carried reached the group 42 mark
   double basNow;    // v12.2: the base risk in use (the profit step with Rule A / B / C split)
   long   ldUntil, prevWk, liveT;
   CMoney() { liveT = LNONE; Reset(); }
   void Reset()
   {
      seqLoss = 0; seqTot = 0; flPnl = 0; flPeak = 0; dayPnl = 0; ptPnl = 0; peakEq = NAD; riskNow = 0; flFloor = 0; flCush = 0; flRisk = 0;
      seqHalt = false; seqCapOn = false; dayHalt = false; ptHalt = false; ddHit = false;
      cntSeqCap = 0; dayTrades = 0; lsRun = 0; cntLs = 0; ldRun = 0; cntLd = 0; prevDom = -1;
      cntLm = 0; basNow = 0;
      ldUntil = LNONE; prevWk = LNONE;
   }
   double Car()        { return S.seqPlus ? Mx(0.0, -seqTot) : seqLoss; }
   bool   Counts(long tIn)
   {
      if (S.seqFrom == 0) return true;
      if (S.seqFrom == 2) return tIn >= S.seqFromT;
      return liveT != LNONE && tIn >= liveT;
   }
   bool   LdHalt(long t) { return S.ldOn && ldUntil != LNONE && t < ldUntil; }
   long   LdUntil(long t)
   {
      long dn0 = FloorDivL(SessLoc(t), 86400);
      int n = 0, k = 0;
      while (n < S.ldD && k < 500)
      {
         k++;
         int w = DowDays(dn0 + k);
         if (S.wk247 || (w != 7 && w != 1)) n++;
      }
      return LocToUtc((dn0 + k + 1) * 86400, S.tzBase, S.tzRule);
   }
   // the start of a bar (t = its open): new day / new week resets, before this bar's fills and exits are counted
   void NewBar(long t)
   {
      long dn = FloorDivL(SessLoc(t), 86400);
      int y = 0, m = 0, d = 0;
      CivilFromDays(dn, y, m, d);
      bool newDay = prevDom >= 0 && d != prevDom;
      prevDom = d;
      long wk = FloorDivL(dn + 3, 7);
      bool newWk = prevWk != LNONE && wk != prevWk;
      prevWk = wk;
      if (newDay) { dayTrades = 0; dayPnl = 0; dayHalt = false; lsRun = 0; }
      if (newDay && seqHalt && S.capAct == 1) { seqHalt = false; seqLoss = 0; seqTot = 0; seqCapOn = false; }
      if ((S.ptPer == 1 && newDay) || (S.ptPer == 2 && newWk)) { ptPnl = 0; ptHalt = false; }
   }
   // the trades closed on this bar (all sides that use this money), added together, oldest first
   void Closes(int mi)
   {
      int ks[256];
      int ix[256];
      int n = 0;
      for (int k = 0; k < g_nSides; k++)
      {
         if (g_sideMi[k] != mi) continue;
         for (int i = 0; i < g_io[k].nCls && n < 256; i++)
         {
            int j = n;
            while (j > 0 && g_io[ks[j - 1]].cls[ix[j - 1]].tOut > g_io[k].cls[i].tOut) { ks[j] = ks[j - 1]; ix[j] = ix[j - 1]; j--; }
            ks[j] = k;
            ix[j] = i;
            n++;
         }
      }
      if (n == 0) return;
      double sqSum = 0;
      for (int a = 0; a < n; a++)
      {
         double pf = g_io[ks[a]].cls[ix[a]].pnl;
         dayPnl += pf;
         if (S.ptPer != 0 || g_io[ks[a]].cls[ix[a]].tOut >= S.ptFrom) ptPnl += pf;
         if (Counts(g_io[ks[a]].cls[ix[a]].tIn)) sqSum += pf;
      }
      double debt = seqLoss - sqSum;
      seqLoss = debt < 0.005 ? 0.0 : debt;
      seqTot += sqSum;
      flPnl  += sqSum;
      flPeak  = Mx(flPeak, flPnl);
      // v12.1: group 42 - the losses carried reached the mark: they are forgotten, the next trade risks the base again
      if (S.lmOn && S.seqMode != 0 && Car() >= S.lmAmt - 0.005) { seqLoss = 0; seqTot = 0; cntLm++; }
      if (Car() <= 0.005 && S.capAct != 2) { seqHalt = false; seqCapOn = false; }
      for (int a = 0; a < n; a++)
      {
         if (g_io[ks[a]].cls[ix[a]].piece == 1) continue;
         double gp = g_io[ks[a]].cls[ix[a]].pnl;
         long   gx = g_io[ks[a]].cls[ix[a]].tOut;
         lsRun = gp < 0 ? lsRun + 1 : 0;
         if (S.ldOn && Counts(g_io[ks[a]].cls[ix[a]].tIn) && !(ldUntil != LNONE && gx < ldUntil))
         {
            ldRun = gp < 0 ? ldRun + 1 : (gp > 0 ? 0 : ldRun);
            if (ldRun >= S.ldN) { ldUntil = LdUntil(gx); ldRun = 0; cntLd++; }
         }
      }
   }
   // the risk of the next order (Rule A / B / C, A+ / B+ / C+, the hard cap, the account floor)
   void Risk()
   {
      riskNow = S.risk;
      double car = Car();
      if (S.seqMode == 1 || S.seqMode == 4) riskNow = car > 0.005 ? Mx(S.risk, (car + S.seqAdd) / S.split) : S.risk;
      else if (S.seqMode == 2 || S.seqMode == 5) riskNow = car > 0.005 ? Mx(S.risk, 2.0 * car / S.split) : S.risk;
      else if (S.seqMode == 3 || S.seqMode == 6) riskNow = car > 0.005 ? Mx(S.risk, car / S.split) : S.risk;
      // v12.2: Rule A / B / C split - the base grows in steps with the total profit (never below the base risk, never above the cap)
      basNow = S.seqMode >= 7 ? Mx(S.risk, Mn(StepBase(flPnl), S.seqMax)) : S.risk;
      if (S.seqMode == 7) riskNow = car > 0.005 ? Mx(basNow, (car + S.seqAdd) / S.split) : basNow;
      else if (S.seqMode == 8) riskNow = car > 0.005 ? Mx(basNow, 2.0 * car / S.split) : basNow;
      else if (S.seqMode == 9) riskNow = car > 0.005 ? Mx(basNow, car / S.split) : basNow;
      if (S.seqMode != 0 && S.flMode != 1 && riskNow > S.seqMax)
      {
         if (!seqCapOn) { cntSeqCap++; seqCapOn = true; }
         riskNow = S.seqMax;
         if (S.capAct == 3)
         {  // v12.1: the losses carried are forgotten and the next trade risks the base again (never above the cap)
            if (car > 0.005) { seqLoss = 0; seqTot = 0; seqCapOn = false; }
            riskNow = Mn(basNow, S.seqMax);
         }
         else if (S.capAct != 0) seqHalt = true;
      }
      else seqCapOn = false;
      flFloor = -S.flAmt + S.flLock / 100.0 * flPeak;
      flCush  = Mx(0.0, flPnl - flFloor);
      flRisk  = S.flPct / 100.0 * flCush;
      if (S.flMode == 1) riskNow = flRisk;
      else if (S.flMode == 2) riskNow = Mn(riskNow, flRisk);
   }
   void Halts(double eq, bool withEq)
   {
      if (withEq)
      {
         peakEq = IsNa(peakEq) ? eq : Mx(peakEq, eq);
         ddHit = S.dd > 0 && !IsNa(peakEq) && peakEq > 0 && (peakEq - eq) / peakEq * 100.0 >= S.dd;
      }
      if (S.dayLoss > 0 && dayPnl <= -S.dayLoss) dayHalt = true;
      if (S.maxTrades > 0 && dayTrades >= S.maxTrades) dayHalt = true;
      if (S.lsOn && lsRun >= S.lsN && !dayHalt) { dayHalt = true; cntLs++; }
      if (S.ptOn && ptPnl >= S.ptAmt) ptHalt = true;
   }
};
CMoney g_money[2];

// ---------- one strategy side: Both / Longs only / Shorts only, or one half of the hedge ----------
class CSide
{
public:
   int    k, dirF, mi;
   int    dir, rule, armBar, seq, mktBar;
   double sl, fix, lastEnt, lastSl, lastTgt, lastQ, entLock, addRk, lastTp1, openSl, openTgt, planTgt, ent, tgt;
   bool   ordLive, lastCapQ, placed, ppSent;
   string closeWhy, last;
   int    cntArm, cntFill, cntCanc, cntSkip, cntR1, cntR2, cntDir, cntHf, cntPd, cntBosCnl, cntExp, cntCap, cntMoves;
   int    cntR3, cntR3Far, cntR3Fb;   // v12.0
   int    ntrk;
   TrkRec trk[MAXP];
   CSide() { k = 0; dirF = 0; mi = 0; Reset(); }
   void Reset()
   {
      dir = 0; rule = 0; armBar = NAI; seq = 0; mktBar = NAI;
      sl = NAD; fix = NAD; lastEnt = NAD; lastSl = NAD; lastTgt = NAD; lastQ = NAD; entLock = NAD; addRk = 1.0; lastTp1 = NAD;
      openSl = NAD; openTgt = NAD; planTgt = NAD; ent = NAD; tgt = NAD;
      ordLive = false; lastCapQ = false; placed = false; ppSent = false;
      closeWhy = ""; last = "";
      cntArm = 0; cntFill = 0; cntCanc = 0; cntSkip = 0; cntR1 = 0; cntR2 = 0; cntDir = 0; cntHf = 0; cntPd = 0; cntBosCnl = 0; cntExp = 0; cntCap = 0; cntMoves = 0;
      cntR3 = 0; cntR3Far = 0; cntR3Fb = 0;
      ntrk = 0;
   }
   double PosSize()        { double s = 0; for (int i = 0; i < g_io[k].nPos; i++) s += g_io[k].pos[i].dir * g_io[k].pos[i].q; return s; }
   int    PosIndex(long id) { for (int i = 0; i < g_io[k].nPos; i++) if (g_io[k].pos[i].id == id) return i; return -1; }
   int    TrkIndex(long id) { for (int i = 0; i < ntrk; i++) if (trk[i].id == id) return i; return -1; }
   void   TrkRemove(int i)  { for (int j = i; j + 1 < ntrk; j++) trk[j] = trk[j + 1]; ntrk--; }
   string Id()              { return (dir == 1 ? "L" : "S") + IntegerToString(seq); }
   void   Note(string s)    { last = s; BkNote(k, s); }
   void   CancelSent()      { if (ordLive) BkCancel(k); ordLive = false; }
   void   Cancel(string why) { Note(why); CancelSent(); cntCanc++; dir = 0; }
   // an entry filled on this bar (TradingView's newest entry bar)
   void OnFills()
   {
      if (g_io[k].nFill == 0) return;
      openSl  = IsNa(lastSl) ? sl : lastSl;
      openTgt = IsNa(lastTgt) ? planTgt : lastTgt;
      if (S.mgOn && !IsNa(openSl) && !IsNa(openTgt))
      {
         for (int i = 0; i < g_io[k].nFill; i++)
         {
            long id = g_io[k].fill[i].id;
            int pi = PosIndex(id);
            if (pi < 0 || TrkIndex(id) >= 0 || ntrk >= MAXP) continue;
            // TradingView's entry price: the limit level, or the bar open when the price was already through it
            double kp  = (!g_io[k].fill[i].atOpen && g_io[k].pos[pi].seq == seq && !IsNa(lastEnt)) ? lastEnt : g_io[k].pos[pi].ent;
            double kq  = g_io[k].pos[pi].q;
            int    kd  = g_io[k].pos[pi].dir;
            bool   kpp = g_io[k].pos[pi].piece == 1;
            double psl = IsNa(g_io[k].pos[pi].sl) ? openSl : g_io[k].pos[pi].sl;
            double ptg = g_io[k].pos[pi].tgt;
            if (IsNa(ptg)) ptg = (kpp && !IsNa(lastTp1)) ? lastTp1 : openTgt;
            double cst = S.uv > 0 ? (g_cmU + (kq > 0 ? CmF() / kq : 0.0)) / S.uv : 0.0;
            trk[ntrk].id = id;
            trk[ntrk].ticket = g_io[k].pos[pi].ticket;
            trk[ntrk].dir = kd;
            trk[ntrk].ent = kp;
            trk[ntrk].r = MathAbs(kp - psl);
            trk[ntrk].be = kd == 1 ? kp + cst : kp - cst;
            trk[ntrk].sl = psl;
            trk[ntrk].tgt = ptg;
            trk[ntrk].q = kq;
            trk[ntrk].step = 0;
            trk[ntrk].bar = EN.bi;
            trk[ntrk].mv = false;
            trk[ntrk].pp = false;
            trk[ntrk].seq = g_io[k].pos[pi].seq;
            trk[ntrk].piece = g_io[k].pos[pi].piece;
            ntrk++;
         }
      }
      // the two parts of a setup fill together; a part still waiting is cancelled
      if (ppSent) BkCancel(k);
      ppSent = false;
      if (dir != 0) Note(Id() + " FILLED");
      dir = 0;
      ordLive = false;
      cntFill++;
      g_money[mi].dayTrades++;
      if (rule == 3) cntR3++; else if (rule == 2) cntR2++; else cntR1++;
      if (lastCapQ) cntCap++;
   }
   // idea e: the early part closed in profit by its own target or stop - the rest goes to break-even
   void OnCloses()
   {
      if (!S.ppOn) return;
      for (int i = 0; i < g_io[k].nCls; i++)
      {
         if (g_io[k].cls[i].piece != 1 || g_io[k].cls[i].why == 0 || g_io[k].cls[i].pnl <= 0) continue;
         for (int j = 0; j < ntrk; j++)
            if (trk[j].seq == g_io[k].cls[i].seq && trk[j].piece == 0 && trk[j].dir == g_io[k].cls[i].dir) trk[j].pp = true;
      }
   }
   // group 32 step stop / break-even, idea c trailing stop, idea e break-even - at the bar close
   void Manage()
   {
      for (int i = ntrk - 1; i >= 0; i--)
      {
         int pi = PosIndex(trk[i].id);
         if (pi < 0) { TrkRemove(i); continue; }
         double ns = trk[i].sl;
         int    td = trk[i].dir;
         double tr = trk[i].r;
         if (S.mvOn && S.mvKMax >= 1 && tr > 0)
         {
            int kk = trk[i].step;
            if (S.mvStep)
            {
               double ref = EN.bi == trk[i].bar ? g_c : (td == 1 ? g_h : g_l);
               int got = (int)MathFloor((td == 1 ? ref - trk[i].ent : trk[i].ent - ref) / tr);
               kk = MxI(trk[i].step, MnI(got, S.mvKMax));
            }
            else if (trk[i].step == 0 && (td == 1 ? g_c >= trk[i].ent + tr : g_c <= trk[i].ent - tr)) kk = 1;
            double cc = kk == 1 ? trk[i].be : (td == 1 ? Mx(trk[i].be, trk[i].ent + (kk - 1) * tr) : Mn(trk[i].be, trk[i].ent - (kk - 1) * tr));
            if (kk > trk[i].step && (td == 1 ? cc < trk[i].ent + kk * tr : cc > trk[i].ent - kk * tr))
            {
               ns = td == 1 ? Mx(ns, cc) : Mn(ns, cc);
               trk[i].step = kk;
            }
         }
         if (S.trOn && EN.bi > trk[i].bar)
         {
            double lv = NAD;
            if (S.trMode == 1) lv = td == 1 ? EN.swL : EN.swH;
            else if (td == 1 && EN.trendDir == 1 && EN.flr.ok) lv = EN.flr.price;
            else if (td == -1 && EN.trendDir == -1 && EN.cel.ok) lv = EN.cel.price;
            if (!IsNa(lv))
            {
               double l2 = td == 1 ? lv - BufAt(lv) : lv + BufAt(lv);
               if (td == 1 ? l2 < g_c : l2 > g_c) ns = td == 1 ? Mx(ns, l2) : Mn(ns, l2);
            }
         }
         if (trk[i].pp && S.ppBe) ns = td == 1 ? Mx(ns, trk[i].be) : Mn(ns, trk[i].be);
         if (ns != trk[i].sl)
         {
            trk[i].sl = ns;
            trk[i].mv = true;
            BkSetStop(k, g_io[k].pos[pi].ticket, td, ns, trk[i].tgt);
            cntMoves++;
         }
      }
   }
   string Blocked()
   {
      if (!S.on) return "trading off";
      if (g_money[mi].ddHit) return "drawdown stop";
      if (g_holNow) return g_holCal ? "holiday (calendar)" : "US holiday";
      if (g_nwNow) return "news window";
      if (g_preNow) return "news soon - no new trades";
      if (g_wkBlock) return "weekend";
      if (g_money[mi].dayHalt) return "daily limit";
      if (g_money[mi].seqHalt) return "risk cap";
      if (g_money[mi].ptHalt) return "profit target";
      if (g_money[mi].LdHalt(g_t)) return "loss pause (days)";
      if (g_eqBlock) return "waiting for the higher timeframe equilibrium";
      return "";
   }
   // everything after the exits: cancels, closes, a new signal, the order
   void Decide()
   {
      double pos = PosSize();
      int    nOpen = g_io[k].nPos;
      int    td = EN.trendDir;
      string blk = Blocked();
      bool   go = blk == "";
      closeWhy = "";
      if (dir != 0 && (!go || (td != 0 && td != dir))) Cancel(!go ? "CANCELLED - blocked (" + blk + ")" : "CANCELLED - trend flipped");
      if (S.fav && dir != 0 && g_T15 != dir) Cancel("CANCELLED - higher timeframe flipped");
      if (S.agn && dir != 0 && g_T15 != -dir) Cancel("CANCELLED - higher timeframe now agrees");
      if (S.autoM && dir != 0 && dir != g_autoDir) Cancel("CANCELLED - auto mode switched side");
      if (S.bosCnl && dir != 0 && armBar != NAI && EN.bi > armBar && ((dir == 1 && EN.evBU) || (dir == -1 && EN.evBD)))
      {
         cntBosCnl++;
         Cancel("CANCELLED - new BOS before the fill");
      }
      // v12.0: a rule 3 entry at the signal close has ONE chance - sent on the signal candle (or the next one when an
      // opposite trade had to close first), filled at the next open; never sent again at a later price
      if (dir != 0 && rule == 3 && ((mktBar != NAI && EN.bi > mktBar) || (armBar != NAI && EN.bi > armBar + 1))) Cancel("CANCELLED - the entry at the signal close did not fill");
      // RULE 1 follows the live level; RULE 2 keeps the stop it was armed with
      if (dir != 0 && rule != 2 && rule != 3 && !(S.once && placed))
      {
         double live = NAD;
         if (dir == 1 && EN.flr.ok) live = EN.flr.price;
         if (dir == -1 && EN.cel.ok) live = EN.cel.price;
         if (!IsNa(live)) sl = dir == 1 ? live - BufAt(live) : live + BufAt(live);
      }
      if (g_wkNow)
      {
         if (pos != 0) closeWhy = "Weekend flat";
         if (dir != 0) { cntCanc++; Note("CANCELLED - weekend"); }
         CancelSent();
         dir = 0;
      }
      if (g_nwNow)
      {
         if (S.nwExit == 0 && pos != 0) closeWhy = g_holNow ? (g_holCal ? "Holiday (calendar)" : "US holiday") : "News window";
         if (dir != 0) { cntCanc++; Note(g_holNow ? (g_holCal ? "CANCELLED - holiday (calendar)" : "CANCELLED - US holiday") : "CANCELLED - news window"); }
         CancelSent();
         dir = 0;
      }
      if (S.expBars > 0 && dir != 0 && armBar != NAI && EN.bi - armBar >= S.expBars) { cntExp++; Cancel("CANCELLED - expired"); }
      if (g_flatNow)
      {
         if (pos != 0) closeWhy = "Time flat";
         if (dir != 0) { cntCanc++; Note("CANCELLED - force-close hour"); }
         CancelSent();
         dir = 0;
      }
      if (!g_win)
      {
         CancelSent();
         if (dir != 0) { cntCanc++; Note("CANCELLED - session ended"); }
         dir = 0;
      }
      bool sigUp = (S.useCho && EN.evCU) || (S.useBos && EN.evBU);
      bool sigDn = (S.useCho && EN.evCD) || (S.useBos && EN.evBD);
      bool opp   = (pos > 0 && sigDn) || (pos < 0 && sigUp);
      bool oppCh = (pos > 0 && EN.evCD) || (pos < 0 && EN.evCU);
      if (S.on && S.rev && (opp || oppCh)) closeWhy = opp ? "Opposite signal" : "Opposite CHOCH";
      string sg = ((EN.evCU || EN.evCD) && S.useCho) ? "CHOCH" : "BOS";
      sg = sg + (sigUp ? " up" : " dn");
      if ((sigUp || sigDn) && !go) Note(sg + ": SKIP - " + blk);
      if ((sigUp || sigDn) && go)
      {
         if (S.cancelSig && dir != 0) Cancel("CANCELLED - new signal");
         bool addB = S.useBos && ((pos > 0 && EN.evBU) || (pos < 0 && EN.evBD));
         bool full = addB && S.maxOpen > 0 && nOpen >= S.maxOpen;
         addB = addB && !full;
         bool take  = g_win && (pos == 0 || (opp && S.rev) || addB);
         bool dirNo = dirF != 0 && (sigUp ? dirF == -1 : dirF == 1);
         if (dirNo) cntDir++;
         if (take && !dirNo)
         {
            int    d    = sigUp ? 1 : -1;
            double piv  = sigUp ? g_ceilPrev : g_florPrev;
            double opl  = NAD;
            if (d == 1 && EN.flr.ok) opl = EN.flr.price;
            if (d == -1 && EN.cel.ok) opl = EN.cel.price;
            bool agree = (d == 1 && g_T15 == 1) || (d == -1 && g_T15 == -1);
            bool agst  = (d == 1 && g_T15 == -1) || (d == -1 && g_T15 == 1);
            bool use = false;
            if (S.autoM)     use = g_autoDir != 0 && d == g_autoDir && (g_eqOpen ? ((S.r2 && !IsNa(piv)) || (!S.r2 && S.r1)) : S.r1);
            else if (S.agn)  use = agst && S.r1;
            else if (agree)  use = (S.r2 && !IsNa(piv)) || (!S.r2 && S.r1);
            else             use = S.r1 && !S.hfEff;
            bool hfSkip = (S.autoM && !use) || (!S.autoM && S.agn && !agst && S.r1) || (!S.autoM && !S.agn && !agree && S.r1 && S.hfEff);
            // v12.0: rule 3 - enter at the close of this candle (rules 1 / 2 not used; the higher-timeframe filters still apply,
            // no agreement needed - like rule 1). Optionally only when the close is near the broken level (the pivot); a close
            // too far is skipped, or (fall-back switch ON) keeps the normal rule 1 / 2 setup computed above.
            double r3B   = IsNa(piv) ? NAD : d * (g_c - piv);
            bool   r3Far = S.r3On && S.r3BrkOn && (IsNa(r3B) || r3B > LimAt(S.r3Brk, g_c));
            bool   r3Fb  = r3Far && S.r3Fb && (S.r1 || S.r2);
            bool   r3Use = S.r3On && !r3Fb;
            bool   useM  = S.autoM ? (g_autoDir != 0 && d == g_autoDir) : (S.agn ? agst : (agree || !S.hfEff));
            if (r3Use)
            {
               hfSkip = !r3Far && !useM;
               use    = !r3Far && useM;
               if (r3Far) cntR3Far++;
            }
            if (r3Fb) cntR3Fb++;
            if (hfSkip) cntHf++;
            if (use && !IsNa(opl))
            {
               if (dir != 0) cntCanc++;
               CancelSent();
               cntArm++;
               placed  = false;
               entLock = NAD;
               armBar  = EN.bi;
               seq++;
               ppSent  = false;
               addRk   = (addB && S.bkOn) ? S.bkPct / 100.0 : 1.0;
               dir     = d;
               rule    = r3Use ? 3 : ((agree && S.r2 && !S.agn) ? 2 : 1);
               mktBar  = NAI;
               sl      = d == 1 ? opl - BufAt(opl) : opl + BufAt(opl);
               fix     = rule == 2 ? piv : NAD;
               Note(sg + ": " + Id() + (rule == 3 ? " R3 ARMED - entry at the close" : (rule == 2 ? " R2 ARMED" : " R1 ARMED")) + (!r3Fb ? (string)"" : (IsNa(r3B) ? (string)" (RULE 3: no broken level - fall back)" : " (RULE 3: close " + DoubleToString(r3B, 2) + " beyond the broken level - fall back)")));
            }
            else if (r3Use && r3Far) Note(sg + ": SKIP - RULE 3: " + (IsNa(r3B) ? (string)"no broken level" : "close " + DoubleToString(r3B, 2) + " beyond the broken level"));
            else if (!use) Note(sg + ": SKIP - " + (S.autoM ? "auto mode side / rule" : (S.agn ? "not against the higher timeframe" : (agree && !r3Use ? "no broken pivot" : "higher timeframe filter"))));
            else Note(sg + ": SKIP - no stop level");
         }
         else Note(sg + ": SKIP - " + (dirNo ? "trade direction" : (!g_win ? "outside session hours" : (opp ? "in a trade (reverse is off)" : (full ? "max trades open" : "already in a trade the same way")))));
      }
      // the plan: entry, stop, target
      ent = NAD;
      tgt = NAD;
      if (dir != 0)
      {
         ent = rule == 3 ? g_c : ((S.once && placed && !IsNa(entLock)) ? entLock : (rule == 2 ? fix : RetLvl(td, g_mAnch, g_mOrig, S.pb)));
         if (!IsNa(ent) && !IsNa(sl))
         {
            double r = MathAbs(ent - sl);
            tgt = dir == 1 ? ent + r * S.rr + g_cmPx : ent - r * S.rr - g_cmPx;
            if (S.lqOn)
            {
               double lq = LqNear(dir, dir == 1 ? ent + S.lqMin * r : ent - S.lqMin * r);
               if (!IsNa(lq)) tgt = lq;
            }
         }
      }
      if (go && dir != 0 && (pos == 0 || (dir == 1 ? pos > 0 : pos < 0)) && g_win && !IsNa(ent) && !IsNa(tgt) && !IsNa(sl))
      {
         bool   sane = dir == 1 ? ent > sl : ent < sl;
         double r = MathAbs(ent - sl);
         double q = 0.0;
         bool   qCap = false;
         Qty(ent, r, g_money[mi].riskNow * addRk, pos, q, qCap);
         bool lotOk = S.minLot <= 0 || S.cmLots <= 0 || q / S.cmLots >= S.minLot - 1e-9;
         bool dOk   = (S.minStop <= 0 || r >= LimAt(S.minStop, ent)) && (S.maxStop <= 0 || r <= LimAt(S.maxStop, ent)) && lotOk;
         double pdL = S.pdOn ? RetLvl(td, g_mAnch, g_mOrig, S.pdPct) : NAD;
         bool pdOk  = !S.pdOn || (!IsNa(pdL) && (dir == 1 ? ent <= pdL + S.tick / 2 : ent >= pdL - S.tick / 2));
         bool qOk   = q / LotDiv() >= 0.00000001;
         if (sane && dOk && pdOk && qOk && r > 0 && (!S.once || !placed))
         {
            placed  = true;
            entLock = ent;
            planTgt = tgt;
            if (!ordLive || ent != lastEnt || sl != lastSl || tgt != lastTgt || q != lastQ)
            {
               double q1 = 0.0;
               if (S.ppOn)
               {
                  double stp = (S.lotStep > 0 && S.cmLots > 0) ? S.lotStep * S.cmLots : 0.0;
                  q1 = stp > 0 ? MathFloor(q * S.ppPct / 100.0 / stp + 0.5) * stp : q * S.ppPct / 100.0;
                  double lt1 = LotDiv();
                  bool tiny = q1 / lt1 < 0.00000001 || (q - q1) / lt1 < 0.00000001 ||
                              (S.minLot > 0 && S.cmLots > 0 && (q1 / S.cmLots < S.minLot - 1e-9 || (q - q1) / S.cmLots < S.minLot - 1e-9));
                  if (tiny || q1 >= q) q1 = 0.0;
               }
               BkPlace(k, seq, 0, dir, ent, sl, tgt, q - q1, rule == 3);
               if (q1 > 0)
               {
                  double add = (S.cmTgt && S.uv > 0) ? g_cmU * (S.ppR + 1.0) / S.uv : 0.0;
                  double tp1 = dir == 1 ? ent + r * S.ppR + add : ent - r * S.ppR - add;
                  tp1 = dir == 1 ? Mn(tp1, tgt) : Mx(tp1, tgt);
                  BkPlace(k, seq, 1, dir, ent, sl, tp1, q1, rule == 3);
                  ppSent  = true;
                  lastTp1 = tp1;
               }
               else if (ppSent) { BkCancelPiece(k, 1); ppSent = false; }
               ordLive  = true;
               if (rule == 3 && mktBar == NAI) mktBar = EN.bi;
               lastCapQ = qCap;
               lastEnt  = ent;
               lastSl   = sl;
               lastTgt  = tgt;
               lastQ    = q;
            }
         }
         else if (!sane || !dOk || !pdOk || !qOk || r <= 0)
         {
            Note(!sane ? "CANCELLED - entry beyond the stop" : (!pdOk ? "CANCELLED - premium / discount filter" : (!lotOk ? "CANCELLED - below the minimum lot" : (!dOk ? "CANCELLED - stop too close / too far" : "CANCELLED - size is zero"))));
            CancelSent();
            if (!dOk) cntSkip++;
            if (!pdOk) cntPd++;
            cntCanc++;
            dir = 0;
         }
      }
      if (closeWhy != "") BkCloseAll(k, closeWhy);
   }
};
CSide g_side[2];

// ---------- setup and one bar ----------
void CoreSetup()
{
   S.Derive();
   EN.Reset();
   HT.Reset();
   g_nSides = S.dirMode == 3 ? 2 : 1;
   for (int k = 0; k < 2; k++)
   {
      g_side[k].Reset();
      g_side[k].k = k;
      g_sideDir[k] = S.dirMode == 1 ? 1 : (S.dirMode == 2 ? -1 : (S.dirMode == 3 ? (k == 0 ? 1 : -1) : 0));
      g_side[k].dirF = g_sideDir[k];
      g_sideMi[k] = (S.dirMode == 3 && S.hedgeMoney == 0) ? k : 0;
      g_side[k].mi = g_sideMi[k];
      g_money[k].Reset();
      g_io[k].Clear();
   }
   g_deadPrev = false; g_wkPrev = false; g_T15 = 0; g_htE = 0; g_prevE = 0; g_autoDir = 0;
   g_eqOpen = false; g_eqBlock = false; g_firstBar = true; g_ceilPrev = NAD; g_florPrev = NAD;
   g_lqH.Clear(); g_lqL.Clear();
   g_auKey = -1; g_holT0 = 0; g_holT1 = 0; g_auT1 = LNONE; g_auT2 = LNONE; g_auT3 = LNONE; g_auT4 = LNONE;
   g_calI = 0; g_calH0 = false; g_calH1 = false; g_preNow = false; g_holCal = false; g_auN1 = LNONE; g_auN2 = LNONE; g_auN3 = LNONE; g_auN4 = LNONE;
}
// one CLOSED chart bar. t = its open (UTC). ht* = the higher timeframe after its last CLOSED candle
void CoreBar(long t, double o, double h, double l, double c, double eq, int htT, double htO, double htX, int htE)
{
   g_t = t; g_o = o; g_h = h; g_l = l; g_c = c; g_eq = eq;
   EN.Step(o, h, l, c);
   EN.Anchors(g_mAnch, g_mOrig);
   g_T15 = S.u15 ? htT : 0;
   g_htO = S.u15 ? htO : NAD;
   g_htX = S.u15 ? htX : NAD;
   g_htE = S.u15 ? htE : 0;
   // the session clock, at the bar CLOSE
   long tc  = t + S.cs;
   long loc = SessLoc(tc);
   g_tM = MinOfDay(loc);
   g_win = !S.timeOn || S.cs >= 86400 || S.hrOn == S.hrOff || Ovl(g_tM, S.bMin, S.hrOn * 60, S.hrOff * 60);
   bool dead = S.timeOn && (S.hrFlat != S.hrOn ? Ovl(g_tM, S.bMin, S.hrFlat * 60, S.hrOn * 60) : DAhead(g_tM, S.hrFlat * 60) < S.bMin);
   g_flatNow = dead && !g_deadPrev;
   g_deadPrev = dead;
   int cDow = DowDays(FloorDivL(loc, 86400));
   g_wkBlock = !S.wk247 && S.timeOn && S.wkFlat && ((cDow == S.wkDay && (g_tM >= S.wkHr * 60 || DAhead(g_tM, S.wkHr * 60) < S.bMin)) || (S.wkDay != 7 && cDow == 7) || cDow == 1);
   g_wkNow = g_wkBlock && !g_wkPrev;
   g_wkPrev = g_wkBlock;
   NewsFlags(tc);
   g_cmU  = CmU(c);
   g_cmPx = (S.cmTgt && S.uv > 0) ? g_cmU * (S.rr + 1.0) / S.uv : 0.0;
   if (!g_dry)
   {
      int nm = (S.dirMode == 3 && S.hedgeMoney == 0) ? 2 : 1;
      for (int m = 0; m < nm; m++) g_money[m].NewBar(t);
      for (int k = 0; k < g_nSides; k++) g_side[k].OnFills();
      for (int m = 0; m < nm; m++) g_money[m].Closes(m);
      for (int k = 0; k < g_nSides; k++) { g_side[k].OnCloses(); g_side[k].Manage(); }
   }
   // idea d: the liquidity pools (untaken swing highs / lows)
   if (S.lqOn)
   {
      if (!IsNa(EN.swH)) { g_lqH.Add(EN.swH); if (g_lqH.Size() > 60) g_lqH.DropFirst(1); }
      if (!IsNa(EN.swL)) { g_lqL.Add(EN.swL); if (g_lqL.Size() > 60) g_lqL.DropFirst(1); }
      for (int i = g_lqH.Size() - 1; i >= 0; i--) if (g_lqH.At(i) <= h) g_lqH.RemoveAt(i);
      for (int i = g_lqL.Size() - 1; i >= 0; i--) if (g_lqL.At(i) >= l) g_lqL.RemoveAt(i);
   }
   if (!g_dry)
   {
      int nm = (S.dirMode == 3 && S.hedgeMoney == 0) ? 2 : 1;
      for (int m = 0; m < nm; m++) { g_money[m].Risk(); g_money[m].Halts(eq, true); }
   }
   // group 37 / auto modes: a new higher-timeframe CHOCH / BOS closes the gate, a touch of the equilibrium opens it
   if (!g_firstBar && g_htE != g_prevE) g_eqOpen = false;
   g_prevE = g_htE;
   g_firstBar = false;
   g_eqLvl = RetLvl(g_T15, g_htX, g_htO, S.eqPct);
   if ((S.eqOn || S.autoM) && !g_eqOpen && !IsNa(g_eqLvl) && ((g_T15 == 1 && l <= g_eqLvl) || (g_T15 == -1 && h >= g_eqLvl))) g_eqOpen = true;
   g_eqBlock = S.eqOn && !S.autoM && !g_eqOpen;
   g_autoDir = S.autoM ? (g_eqOpen ? g_T15 : -g_T15) : 0;
   if (!g_dry)
      for (int k = 0; k < g_nSides; k++) g_side[k].Decide();
   if (EN.cel.ok) g_ceilPrev = EN.cel.price;
   if (EN.flr.ok) g_florPrev = EN.flr.price;
}
//==CORE-END==

//+------------------------------------------------------------------+
//| MT5 PART: real orders, deals, clocks, restart safety, drawing.   |
//| The core above decides; this part only carries the decisions out |
//| and reports back what the broker did, bar by bar.                |
//+------------------------------------------------------------------+
CTrade          g_trade;
string          g_sym;
ENUM_TIMEFRAMES g_tf, g_htf;
int             g_cs = 60, g_htfSec = 900;
double          g_contract = 100, g_volMin = 0.01, g_volMax = 100, g_volStep = 0.01, g_tickSize = 0.01, g_point = 0.01;
int             g_digits = 2;
bool            g_ready = false, g_tester = false, g_visual = false, g_netting = false, g_htfUse = false, g_badInit = false;
datetime        g_lastBar = 0;      // open time (server) of the last processed CLOSED bar
datetime        g_curOpen = 0;      // open time (server) of the bar in progress
datetime        g_htfFed = 0;       // open time (server) of the last higher-timeframe candle fed to the engine
string          g_P = "";           // prefix of this EA's global variables and chart objects
string          g_AP = "";          // v12.3: prefix of the signal audit labels (they stay when the EA restarts)
string          g_audCur[2];        // v12.3: the audit label of each side's setup (armed, waiting or filled)
int             g_audSeq[2];        // v12.3: its setup number
datetime        g_audT = 0;         // v12.3: the candle being read, its high and low (where a signal's label goes)
double          g_audH = 0, g_audL = 0;
ENUM_ORDER_TYPE_TIME g_otime = ORDER_TIME_GTC;
long            g_srvBase = 7200;

// the orders the core wants: [side * 2 + piece]. Touch mode: watched by the EA. Pending mode: mirrored at the broker.
struct VOrd
{
   bool   on;
   int    seq;
   int    dir;
   double ent;
   double sl;
   double tgt;
   double lots;
   long   ticket;
   int    fails;
   bool   mkt;     // v12.0: a rule 3 entry - a market order at once
};
VOrd     g_vb[4];
ulong    g_clsTk[];                 // trades to close at market (retried until done)
string   g_clsWhy[];
ulong    g_stpTk[];                 // stop moves to send (retried until done)
double   g_stpSl[];
int      g_stpDir[];
ulong    g_done[];                  // deals already reported to the core
datetime g_doneT[];
string   g_note[2];
datetime g_bt[];                    // open time of every processed bar: g_bt[i] = bar index g_btBase + i
int      g_btBase = 0;
int      g_mark = 0;                // CHOCH / BOS marks drawn so far
string   g_lastErr = "";
bool     g_dealFlag = true;         // a deal happened (OnTradeTransaction) - the history needs reading
long     g_gapPos[];                // trades opened at once because the price was already through the entry
bool     g_inBar = false;           // true while the orders of a just-closed bar are being carried out
// the counter table: counts since the EA started
int      g_cntCho = 0, g_cntBos = 0, g_exTgt = 0, g_exStop = 0, g_exMv = 0, g_exOpp = 0, g_exFlat = 0, g_exNews = 0, g_exOther = 0;
int      g_closedN = 0, g_refused = 0;
double   g_costPaid = 0, g_lastRisk = NAD, g_lastLots = NAD, g_lastCost = NAD, g_lastPosCost = 0;
datetime g_startT = 0;
ulong    g_cwTk[];                  // trades the EA closed itself, and why (for the exit counts)
string   g_cwWhy[];
string   g_rL[], g_rV[];            // table rows: label, value, colour
color    g_rC[];
int      g_rN = 0, g_tblShown = 0;
// the higher timeframe on the chart
datetime g_hbt[];                   // open time of every higher-timeframe candle fed: g_hbt[i] = candle g_hbBase + i
int      g_hbBase = 0, g_hmark = 0;
datetime g_htfEvSrv = 0;            // close of the higher-timeframe candle with the last CHOCH / BOS
long     g_slowMin = -1;            // the table's slow rows, worked out once a minute
string   g_newsTxt = "", g_clockTxt = "", g_holTxt = "";
// group 41: the economic calendar
#define CAL_FILE "SMC_calendar.csv"
string   g_calCur[];                // the chosen currencies, upper case
long     g_crT[];                   // the records read: UTC time (a holiday: 00:00 UTC of its date)
long     g_crS[];                   //   broker (server) time as MT5 gave it
string   g_crC[];                   //   currency
int      g_crI[];                   //   importance: 3 high, 2 medium, 1 low, 0 none
int      g_crY[];                   //   type: 0 event, 1 indicator, 2 holiday
string   g_crN[];                   //   name
int      g_crO[];                   //   the records in time order (indexes)
int      g_crR[];                   //   result after the release: 1 good / 2 bad for the currency, 0 not known
string   g_crF[];                   //   forecast, as text ("" = none)
string   g_crA[];                   //   actual, as text ("" = not out yet)
long     g_tdT[];                   // the news for the table's "today" rows (all chosen currencies, high / medium): UTC time
string   g_tdN[], g_tdC[], g_tdF[], g_tdA[];
int      g_tdI[], g_tdR[];
int      g_tdP = 0;                 //   first one not before today
long     g_cvT[];                   // the chosen news, oldest first (for the table): UTC time
string   g_cvN[];                   //   and name
int      g_cvI = 0;                 //   first one not over yet (the table)
long     g_chD[];                   // the chosen holidays: day number (New York date)
string   g_chN[];
datetime g_calLoad = 0;             // live: when the calendar was last read (server time)
string   g_calSrc = "";             // where the news came from, for the table
bool     g_calOk = false;           // a list is loaded
bool     g_calRule = true;          // calendar times -> UTC: true = the broker clock rule (group 40), false = the broker offset of today
string   g_calHow = "";
long     g_calEnd = LNONE;          // tester: the file covers news up to here (UTC)
long     g_calBeg = LNONE;
bool     g_calWarned = false;
bool     g_calPicked = false;       // live: the clock check was done
bool     g_calSaved = false;        // live: the file was saved
datetime g_calSaveTry = 0;
string   g_calTxt = "", g_calHolTxt = "";

//---------------------------------------------------------------- functions defined further down
void DrawBar(MqlRates &r);
void DrawAll(datetime tNow);
void DrawHtfMark(datetime tEnd);
void Panel();
void ExecuteAll();
bool TryInit();
void ProcessBar(MqlRates &r, bool dry, datetime tEnd);
void SaveState(datetime barTime);

//---------------------------------------------------------------- small helpers
long     SrvToUtc(datetime s) { return LocToUtc((long)s, g_srvBase, (int)InSrvDst); }
datetime UtcToSrv(long u)     { return (datetime)(u + TzOff(u, g_srvBase, (int)InSrvDst)); }
double   UnitValue()
{
   double tv = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_SIZE);
   if (tv <= 0 || ts <= 0 || g_contract <= 0) return S.uv > 0 ? S.uv : 1.0;
   return tv / ts / g_contract;
}
// v11.2: the pip of this market (stop buffer unit 'Pips') - gold 0.10, silver 0.01, Bitcoin 1, Ethereum 0.10,
// forex 0.0001 (JPY 0.01), anything else 10 x the price step - the same table as the TradingView strategy
bool   SymHas(string up, string a) { return StringFind(up, a) >= 0; }
bool   SymStarts(string up, string a) { return StringFind(up, a) == 0; }
double PipAuto()
{
   string up = g_sym;
   StringToUpper(up);
   string base = SymbolInfoString(g_sym, SYMBOL_CURRENCY_BASE), prof = SymbolInfoString(g_sym, SYMBOL_CURRENCY_PROFIT);
   StringToUpper(base);
   StringToUpper(prof);
   if (SymHas(up, "XAU") || SymHas(up, "GOLD") || base == "XAU") return 0.1;
   if (SymHas(up, "XAG") || SymHas(up, "SILVER") || base == "XAG") return 0.01;
   if (base == "BTC" || SymStarts(up, "BTC") || SymStarts(up, "BITCOIN")) return 1.0;
   if (base == "ETH" || SymStarts(up, "ETH") || SymStarts(up, "ETHEREUM")) return 0.1;
   long cm = SymbolInfoInteger(g_sym, SYMBOL_TRADE_CALC_MODE);
   if (cm == SYMBOL_CALC_MODE_FOREX || cm == SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE) return prof == "JPY" ? 0.01 : 0.0001;
   return 10.0 * g_tickSize;
}
double NormDn(double p) { return NormalizeDouble(MathFloor(p / g_tickSize + 1e-7) * g_tickSize, g_digits); }
double NormUp(double p) { return NormalizeDouble(MathCeil(p / g_tickSize - 1e-7) * g_tickSize, g_digits); }
double NormLots(double q)
{
   double lots = q / g_contract;
   lots = MathFloor(lots / g_volStep + 1e-6) * g_volStep;
   if (lots > g_volMax) lots = g_volMax;
   return NormalizeDouble(lots, 8);
}
double StopsGap() { return (double)SymbolInfoInteger(g_sym, SYMBOL_TRADE_STOPS_LEVEL) * g_point; }
int    SideOf(int dir) { return S.dirMode == 3 ? (dir == 1 ? 0 : 1) : 0; }
string TradeId(int dir, int seq, int piece) { return (dir == 1 ? "L" : "S") + IntegerToString(seq) + (piece == 1 ? "p" : ""); }
string CmtOf(int dir, int seq, int piece) { return InCmt + " " + TradeId(dir, seq, piece); }
void   Log(string s) { Print(s); g_lastErr = s; }
// "SMC L12p" -> seq 12, piece 1
bool ParseCmt(string c, int &seq, int &piece)
{
   seq = -1;
   piece = 0;
   string pre = InCmt + " ";
   if (StringFind(c, pre) != 0) return false;
   string t = StringSubstr(c, StringLen(pre));
   int e = StringLen(t);
   if (e < 2) return false;
   ushort c0 = StringGetCharacter(t, 0);
   if (c0 != 'L' && c0 != 'S') return false;
   if (StringGetCharacter(t, e - 1) == 'p') { piece = 1; e--; }
   string num = StringSubstr(t, 1, e - 1);
   for (int i = 0; i < StringLen(num); i++) { ushort ch = StringGetCharacter(num, i); if (ch < '0' || ch > '9') return false; }
   seq = (int)StringToInteger(num);
   return true;
}
bool IsDigits(string s) { if (StringLen(s) == 0) return false; for (int i = 0; i < StringLen(s); i++) { ushort ch = StringGetCharacter(s, i); if (ch < '0' || ch > '9') return false; } return true; }
// "1725-1835" -> minutes of the day of the part starting at p; -1 if unreadable
int Hm(string s, int p)
{
   string h = StringSubstr(s, p, 2), m = StringSubstr(s, p + 2, 2);
   if (!IsDigits(h) || !IsDigits(m)) return -1;
   return (int)StringToInteger(h) * 60 + (int)StringToInteger(m);
}
// group 28: "3, 12-14 28" -> day-of-month flags
void NdParse(string s)
{
   for (int i = 0; i < 32; i++) S.ndDays[i] = false;
   string t = s;
   StringReplace(t, ";", ",");
   StringReplace(t, " ", ",");
   for (int i = 0; i < 3; i++) { StringReplace(t, ",-", "-"); StringReplace(t, "-,", "-"); }
   string parts[];
   int n = StringSplit(t, ',', parts);
   for (int i = 0; i < n; i++)
   {
      string p = parts[i];
      if (StringLen(p) == 0) continue;
      if (StringFind(p, "-") >= 0)
      {
         string ab[];
         if (StringSplit(p, '-', ab) == 2 && IsDigits(ab[0]) && IsDigits(ab[1]))
         {
            int x = (int)StringToInteger(ab[0]), y = (int)StringToInteger(ab[1]);
            int lo = MxI(1, MnI(x, y)), hi = MnI(31, MxI(x, y));
            for (int k = lo; k <= hi; k++) S.ndDays[k] = true;
         }
      }
      else if (IsDigits(p))
      {
         int x = (int)StringToInteger(p);
         if (x >= 1 && x <= 31) S.ndDays[x] = true;
      }
   }
}
string NdText() { string t = ""; for (int k = 1; k <= 31; k++) if (S.ndDays[k]) t = t + (t == "" ? "" : ", ") + IntegerToString(k); return t; }

//---------------------------------------------------------------- settings from the inputs
void FillSettings()
{
   S.altMode = InAltMode; S.pbBodyOn = InPbBodyOn; S.pbBodyRef = InPbBodyRef; S.pbSwp2 = InPbSwp2;
   S.on = InOn; S.r1 = InR1; S.r2 = InR2; S.sig = (int)InSig;
   S.pb = InPb; S.rr = InRR; S.slBuf = InSlBuf; S.rev = InRev; S.once = InEntMode == ENT_ONCE;
   S.sessMode = (int)InSessMode; S.tzBase = (long)MathRound(InTzHours * 3600.0); S.tzRule = (int)InTzDst;
   S.hrOn = InHrOn; S.hrOff = InHrOff; S.hrFlat = InHrFlat;
   S.sizeMode = (int)InSize; S.risk = InRisk; S.qty = InQty; S.cash = InCash; S.lotStep = InLotStep; S.rndMax = InRndMax; S.lev = InLev;
   S.seqMode = (int)InSeqMode; S.seqMax = InSeqMax; S.capAct = (int)InCapAct; S.seqAdd = InSeqAdd;
   S.seqFrom = (int)InSeqFrom; S.seqFromT = (long)InSeqFromT; S.split = InSplit;
   S.cmMode = (int)InCmMode; S.cmLot = InCmLot; S.cmUnit = InCmUnit; S.cmPct = InCmPct; S.cmFix = InCmFix; S.cmTgt = InCmTgt;
   S.cancelSig = InCancelSig; S.expBars = InExpBars; S.minStop = InMinStop; S.maxStop = InMaxStop; S.maxTrades = InMaxTrades;
   S.dayLoss = InDayLoss; S.dd = InDD; S.wkFlat = InWkFlat; S.wkDay = (int)InWkDay; S.wkHr = InWkHr; S.wk247 = InWk247; S.bosCnl = InBosCnl;
   S.newsOn = InNewsOn; S.nwExit = (int)InNwExit; S.nw1On = InNw1On; S.nw2On = InNw2On; S.nw3On = InNw3On;
   S.nw1A = Hm(InNw1, 0); S.nw1B = Hm(InNw1, 5); S.nw2A = Hm(InNw2, 0); S.nw2B = Hm(InNw2, 5); S.nw3A = Hm(InNw3, 0); S.nw3B = Hm(InNw3, 5);
   S.sprd = InSprd; S.ptOn = InPtOn; S.ptAmt = InPtAmt; S.ptPer = (int)InPtPer; S.ptFrom = (long)InPtFrom;
   S.ndOn = InNdOn; S.ndScope = (int)InNdScope; NdParse(InNdList);
   S.auOn = InAuOn; S.auNfp = InAuNfp; S.auJc = InAuJc; S.auIsmM = InAuIsmM; S.auIsmS = InAuIsmS; S.auPre = InAuPre; S.auPost = InAuPost;
   S.usClk = (int)InUsClk; S.nwNy = InNwNy; S.holTrade = InHolTrade;
   S.maxOpen = InMaxOpen; S.mvStep = InMvStep; S.mvBe = InMvBe; S.dirMode = (int)InDirMode; S.hedgeMoney = (int)InHedgeMoney;
   S.bkOn = InBkOn; S.bkPct = InBkPct; S.hfOn = InHfOn; S.trOn = InTrOn; S.trMode = (int)InTrMode; S.lqOn = InLqOn; S.lqMin = InLqMin;
   S.ppOn = InPpOn; S.ppPct = InPpPct; S.ppR = InPpR; S.ppBe = InPpBe; S.pdOn = InPdOn; S.pdPct = InPdPct; S.lsOn = InLsOn; S.lsN = InLsN;
   S.flMode = (int)InFlMode; S.flAmt = InFlAmt; S.flLock = InFlLock; S.flPct = InFlPct;
   S.ldOn = InLdOn; S.ldN = InLdN; S.ldD = InLdD; S.eqOn = InEqOn; S.eqPct = InEqPct;
   S.calOn = InCalOn; S.calHol = InCalHol; S.calPre = InCalPre; S.calPost = InCalPost; S.preOn = InPreOn; S.preSec = (long)MathRound(InPreHrs * 3600.0);
   S.buMode = (int)InBuMode; S.buPips = InBuPips; S.buPct = InBuPct; S.pipSz = InBuPip > 0 ? InBuPip : PipAuto();
   S.r3On = InR3On; S.r3BrkOn = InR3BrkOn; S.r3Brk = InR3Brk; S.r3Fb = InR3Fb;
   S.lmOn = InLmOn; S.lmAmt = InLmAmt;
   S.sp1 = InSp1; S.spN1 = InSpN1; S.sp2 = InSp2; S.spN2 = InSpN2; S.sp3 = InSp3; S.spN3 = InSpN3; S.spInc = InSpInc; S.spAdd = InSpAdd;
   S.cs = g_cs;
   S.cmLots = InCmMode == CM_LOT ? InCmUnit : g_contract;
   S.uv = 1.0;
   S.uv = UnitValue();
   S.minLot = g_volMin;
   S.tick = g_tickSize;
   S.htfOk = g_htfSec > g_cs;
}
string CheckInputs()
{
   if (InPb < 1 || InPb > 99) return "RULE 1 pullback % must be 1 - 99";
   if (InRR < 0.1 || InRR > 20) return "Target R must be 0.1 - 20";
   if (InSlBuf < 0) return "Stop buffer cannot be negative";
   if (InHrOn < 0 || InHrOn > 23 || InHrOff < 0 || InHrOff > 23 || InHrFlat < 0 || InHrFlat > 23 || InWkHr < 0 || InWkHr > 23) return "Hours must be 0 - 23";
   if (InTzHours < -12 || InTzHours > 14 || InSrvHours < -12 || InSrvHours > 14) return "Timezone hours must be -12 .. 14";
   if (InRisk < 0.01 || InQty <= 0 || InCash < 0.01) return "Risk / quantity / cash must be above 0";
   if (InLotStep < 0 || InRndMax < 0 || InRndMax > 500) return "Lot step / rounding limit out of range";
   if (InLev < 1 || InLev > 500) return "Max leverage must be 1 - 500";
   if (InSeqMax < 0.01 || InSeqAdd < 0) return "Hard cap / Rule A amount out of range";
   if (InSplit < 1 || InSplit > 20) return "Split must be 1 - 20";
   if (InCmLot < 0 || InCmUnit <= 0 || InCmPct < 0 || InCmFix < 0 || InSprd < 0) return "Commission / spread values cannot be negative";
   if (InExpBars < 0 || InMinStop < 0 || InMaxStop < 0 || InMaxTrades < 0 || InDayLoss < 0 || InDD < 0 || InDD > 100) return "Safety values out of range";
   if (InAuPre < 0 || InAuPre > 240 || InAuPost < 1 || InAuPost > 480) return "US news minutes out of range";
   if (InMaxOpen < 0 || InMaxOpen > 100) return "Max trades open must be 0 - 100";
   if (InBkPct < 1 || InBkPct > 100 || InLqMin < 0.1 || InPpPct < 1 || InPpPct > 99 || InPpR < 0.1 || InPdPct < 1 || InPdPct > 99 || InLsN < 1) return "A group 34 value is out of range";
   if (InFlAmt < 0.01 || InFlLock < 0 || InFlLock > 100 || InFlPct < 0.5 || InFlPct > 50) return "Account floor values out of range";
   if (InLdN < 1 || InLdN > 50 || InLdD < 1 || InLdD > 60) return "Pause values out of range";
   if (InEqPct < 1 || InEqPct > 99) return "Equilibrium % must be 1 - 99";
   if (InWarm < 500) return "Use at least 500 bars of history";
   if (InCalPre < 0 || InCalPre > 240 || InCalPost < 1 || InCalPost > 480) return "Calendar news minutes out of range (before 0 - 240, after 1 - 480)";
   if (InPreHrs < 0.1 || InPreHrs > 24) return "Hours before news must be 0.1 - 24";
   if ((InCalOn || InCalSave) && ArraySize(g_calCur) == 0) return "Calendar currencies: give at least one, e.g. USD";
   if (InBuPips < 0 || InBuPct < 0 || InBuPct > 10 || InBuPip < 0) return "Stop buffer unit (group 38): pips and pip size 0 or more, % 0 - 10";
   if (InR3Brk < 0) return "Rule 3 (group 39): the distance from the broken level must be 0 or more";
   if (InLmAmt < 0.01) return "Loss mark (group 42): the losses carried must be 0.01 or more";
   if (InAudMax < 0) return "Audit labels (group 44): how many to keep must be 0 or more";
   if (InSp1 < 0 || InSp2 < 0 || InSp3 < 0 || InSpInc < 0 || InSpAdd < 0 || InSpN1 < 1 || InSpN2 < 1 || InSpN3 < 1) return "Profit steps (group 43): amounts 0 or more, parts 1 or more";
   if (StringLen(InCmt) < 1 || StringLen(InCmt) > 16 || StringFind(InCmt, " ") >= 0) return "Order comment: 1 - 16 characters, no spaces";
   return "";
}
ENUM_TIMEFRAMES HtfOf()
{
   if (InHtf == HTF_M15) return PERIOD_M15;
   if (InHtf == HTF_H1) return PERIOD_H1;
   if (InHtf == HTF_H4) return PERIOD_H4;
   if (InHtf == HTF_D1) return PERIOD_D1;
   if (InHtf == HTF_W1) return PERIOD_W1;
   if (InHtf == HTF_MN) return PERIOD_MN1;
   if (g_cs <= 60) return PERIOD_M15;
   if (g_cs <= 300) return PERIOD_H1;
   if (g_cs <= 900) return PERIOD_H4;
   if (g_cs <= 3600) return PERIOD_D1;
   if (g_cs <= 14400) return PERIOD_W1;
   return PERIOD_MN1;
}
string TfName(ENUM_TIMEFRAMES tf)
{
   string s = EnumToString(tf);
   StringReplace(s, "PERIOD_", "");
   return s;
}

//---------------------------------------------------------------- broker actions asked for by the core
void BkCancel(int side) { g_vb[side * 2].on = false; g_vb[side * 2 + 1].on = false; }
void BkCancelPiece(int side, int piece) { g_vb[side * 2 + piece].on = false; }
void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt)
{
   int i = side * 2 + piece;
   if (!g_vb[i].on || g_vb[i].seq != seq || g_vb[i].dir != dir) g_vb[i].fails = 0;
   g_vb[i].on   = true;
   g_vb[i].seq  = seq;
   g_vb[i].dir  = dir;
   g_vb[i].ent  = ent;
   g_vb[i].sl   = sl;
   g_vb[i].tgt  = tgt;
   g_vb[i].lots = NormLots(q);
   g_vb[i].mkt  = mkt;
   if (g_vb[i].lots < g_volMin - 1e-9) { g_vb[i].on = false; Log("Order " + TradeId(dir, seq, piece) + " skipped: " + DoubleToString(g_vb[i].lots, 2) + " lots is below the broker minimum"); }
}
void BkCloseAll(int side, string why)
{
   for (int i = 0; i < g_io[side].nPos; i++)
   {
      ulong tk = (ulong)g_io[side].pos[i].ticket;
      bool have = false;
      for (int j = 0; j < ArraySize(g_clsTk); j++) if (g_clsTk[j] == tk) have = true;
      if (have) continue;
      int n = ArraySize(g_clsTk);
      ArrayResize(g_clsTk, n + 1);
      ArrayResize(g_clsWhy, n + 1);
      g_clsTk[n] = tk;
      g_clsWhy[n] = why;
   }
}
void BkSetStop(int side, long ticket, int dir, double sl, double tgt)
{
   for (int j = 0; j < ArraySize(g_stpTk); j++)
      if (g_stpTk[j] == (ulong)ticket) { g_stpSl[j] = sl; g_stpDir[j] = dir; return; }
   int n = ArraySize(g_stpTk);
   ArrayResize(g_stpTk, n + 1);
   ArrayResize(g_stpSl, n + 1);
   ArrayResize(g_stpDir, n + 1);
   g_stpTk[n] = (ulong)ticket;
   g_stpSl[n] = sl;
   g_stpDir[n] = dir;
}
// v12.3: the signal audit labels on the chart (group 20 'Signal audit' + group 44)
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
   int n = StringSplit(tip, '\n', ln);
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
   AudShow(nm, sg + "  HTF " + (!g_htfUse ? "off" : (g_T15 == 1 ? "up" : (g_T15 == -1 ? "dn" : "-"))) + "\n" + AudTm(g_audT) + "  " + st);
   if (StringFind(st, "ARMED") >= 0) { g_audCur[side] = nm; g_audSeq[side] = g_side[side].seq; }
   AudTrim();
}
// what happened next to the side's setup: FILLED, CANCELLED - ..., REFUSED ...
void AudEnd(int side, string st, datetime t)
{
   string nm = g_audCur[side];
   if (nm == "" || ObjectFind(0, nm) < 0) return;
   AudShow(nm, ObjectGetString(0, nm, OBJPROP_TOOLTIP) + "\n" + AudTm(t) + "  " + st);
}
// the broker side (book entry i): only for the setup the label belongs to
void AudRef(int i, string st) { if (AudOn() && g_vb[i].seq == g_audSeq[i / 2]) AudEnd(i / 2, st, TimeCurrent()); }
void BkNote(int side, string msg)
{
   g_note[side] = msg;
   if (InAudit && !g_dry) Print("[", S.dirMode == 3 ? (side == 0 ? "long side" : "short side") : "strategy", "] ", TimeToString(g_audT, TIME_DATE | TIME_MINUTES), " ", msg);
   if (!AudOn()) return;
   if (StringFind(msg, "CHOCH ") == 0 || StringFind(msg, "BOS ") == 0) AudNew(side, msg);
   else AudEnd(side, msg, g_audT);
}

//---------------------------------------------------------------- deals already reported
bool IsDone(ulong dk) { for (int i = ArraySize(g_done) - 1; i >= 0; i--) if (g_done[i] == dk) return true; return false; }
void MarkDone(ulong dk, datetime t)
{
   int n = ArraySize(g_done);
   ArrayResize(g_done, n + 1, 1024);
   ArrayResize(g_doneT, n + 1, 1024);
   g_done[n] = dk;
   g_doneT[n] = t;
}
void TrimDone(datetime older)
{
   int n = ArraySize(g_done), w = 0;
   for (int i = 0; i < n; i++) if (g_doneT[i] >= older) { g_done[w] = g_done[i]; g_doneT[w] = g_doneT[i]; w++; }
   ArrayResize(g_done, w, 1024);
   ArrayResize(g_doneT, w, 1024);
}
bool OurDeal(ulong dk)
{
   if (HistoryDealGetString(dk, DEAL_SYMBOL) != g_sym || HistoryDealGetInteger(dk, DEAL_MAGIC) != InMagic) return false;
   long ty = HistoryDealGetInteger(dk, DEAL_TYPE);
   return ty == DEAL_TYPE_BUY || ty == DEAL_TYPE_SELL;
}
bool PosOpenNow(long pid)
{
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if (tk == 0) continue;
      if (PositionGetInteger(POSITION_IDENTIFIER) == pid && PositionGetInteger(POSITION_MAGIC) == InMagic) return true;
   }
   return false;
}
// one position from its deals: in-deal facts, total money (profit + commission + swap + fee), last exit
bool PosSummary(long pid, datetime &tIn, datetime &tOut, double &pnl, int &dir, double &q, double &ent, int &seq, int &piece, int &why)
{
   if (!HistorySelectByPosition(pid)) return false;
   tIn = 0; tOut = 0; pnl = 0; dir = 0; q = 0; ent = 0; seq = -1; piece = 0; why = 0;
   g_lastPosCost = 0;
   bool haveIn = false;
   int n = HistoryDealsTotal();
   for (int i = 0; i < n; i++)
   {
      ulong dk = HistoryDealGetTicket(i);
      if (dk == 0 || !OurDeal(dk)) continue;
      double cm = HistoryDealGetDouble(dk, DEAL_COMMISSION) + HistoryDealGetDouble(dk, DEAL_SWAP) + HistoryDealGetDouble(dk, DEAL_FEE);
      pnl += HistoryDealGetDouble(dk, DEAL_PROFIT) + cm;
      g_lastPosCost += cm;
      long en = HistoryDealGetInteger(dk, DEAL_ENTRY);
      datetime dt = (datetime)HistoryDealGetInteger(dk, DEAL_TIME);
      if (en == DEAL_ENTRY_IN && !haveIn)
      {
         haveIn = true;
         tIn = dt;
         dir = HistoryDealGetInteger(dk, DEAL_TYPE) == DEAL_TYPE_BUY ? 1 : -1;
         q = HistoryDealGetDouble(dk, DEAL_VOLUME) * g_contract;
         ent = HistoryDealGetDouble(dk, DEAL_PRICE);
         ParseCmt(HistoryDealGetString(dk, DEAL_COMMENT), seq, piece);
      }
      else if (en != DEAL_ENTRY_IN && dt >= tOut)
      {
         tOut = dt;
         long rs = HistoryDealGetInteger(dk, DEAL_REASON);
         why = rs == DEAL_REASON_SL ? 1 : (rs == DEAL_REASON_TP ? 2 : 0);
      }
   }
   return haveIn;
}
void AddPos(int k, long pid, long tk, int dir, double q, double ent, double sl, double tp, long tOpen, int seq, int piece)
{
   if (g_io[k].nPos >= MAXP) return;
   int i = g_io[k].nPos++;
   g_io[k].pos[i].id = pid; g_io[k].pos[i].ticket = tk; g_io[k].pos[i].dir = dir; g_io[k].pos[i].q = q; g_io[k].pos[i].ent = ent;
   g_io[k].pos[i].sl = sl; g_io[k].pos[i].tgt = tp; g_io[k].pos[i].tOpen = tOpen; g_io[k].pos[i].seq = seq; g_io[k].pos[i].piece = piece;
}
void AddCls(int k, long pid, int dir, double q, double pnl, long tIn, long tOut, int seq, int piece, int why)
{
   if (g_io[k].nCls >= MAXP) return;
   int i = g_io[k].nCls++;
   g_io[k].cls[i].id = pid; g_io[k].cls[i].dir = dir; g_io[k].cls[i].q = q; g_io[k].cls[i].pnl = pnl; g_io[k].cls[i].tIn = tIn;
   g_io[k].cls[i].tOut = tOut; g_io[k].cls[i].seq = seq; g_io[k].cls[i].piece = piece; g_io[k].cls[i].why = why;
}
// the exit counts of the table: target / stop / moved stop (the broker's reason), or why the EA closed it
void CountExit(long pid, int dir, int why)
{
   g_closedN++;
   g_costPaid += -g_lastPosCost;
   string cw = "";
   for (int j = ArraySize(g_cwTk) - 1; j >= 0; j--) if (g_cwTk[j] == (ulong)pid) { cw = g_cwWhy[j]; break; }
   int k  = SideOf(dir);
   int ti = g_side[k].TrkIndex(pid);
   bool mv = ti >= 0 && g_side[k].trk[ti].mv;
   if (why == 2) g_exTgt++;
   else if (why == 1) { if (mv) g_exMv++; else g_exStop++; }
   else if (StringFind(cw, "Opposite") == 0) g_exOpp++;
   else if (cw == "Weekend flat" || cw == "Time flat") g_exFlat++;
   else if (cw == "News window" || cw == "US holiday" || cw == "Holiday (calendar)") g_exNews++;
   else if (cw == "moved stop already passed") g_exMv++;
   else g_exOther++;
}
// what happened up to tEnd (the open of the next bar): open trades at the bar close, entries and exits of this bar
void GatherIO(datetime tEnd)
{
   for (int k = 0; k < 2; k++) g_io[k].Clear();
   for (int i = 0; i < PositionsTotal(); i++)
   {
      ulong tk = PositionGetTicket(i);
      if (tk == 0) continue;
      if (PositionGetString(POSITION_SYMBOL) != g_sym || PositionGetInteger(POSITION_MAGIC) != InMagic) continue;
      datetime to = (datetime)PositionGetInteger(POSITION_TIME);
      if (to >= tEnd) continue;
      int dir = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
      int seq = -1, piece = 0;
      ParseCmt(PositionGetString(POSITION_COMMENT), seq, piece);
      double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
      AddPos(SideOf(dir), PositionGetInteger(POSITION_IDENTIFIER), (long)tk, dir, PositionGetDouble(POSITION_VOLUME) * g_contract,
             PositionGetDouble(POSITION_PRICE_OPEN), sl > 0 ? sl : NAD, tp > 0 ? tp : NAD, SrvToUtc(to), seq, piece);
   }
   if (!g_dealFlag) return;
   if (!HistorySelect(tEnd - 9 * 86400, TimeCurrent() + 86400)) return;
   bool later = false;
   long closedIds[], afterIds[];
   int nc = 0, na = 0;
   int nd = HistoryDealsTotal();
   for (int i = 0; i < nd; i++)
   {
      ulong dk = HistoryDealGetTicket(i);
      if (dk == 0 || !OurDeal(dk)) continue;
      datetime dt = (datetime)HistoryDealGetInteger(dk, DEAL_TIME);
      long en = HistoryDealGetInteger(dk, DEAL_ENTRY);
      long pid = HistoryDealGetInteger(dk, DEAL_POSITION_ID);
      if (dt >= tEnd) later = true;
      if (en == DEAL_ENTRY_IN)
      {
         if (dt >= tEnd || IsDone(dk)) continue;
         MarkDone(dk, dt);
         int dir = HistoryDealGetInteger(dk, DEAL_TYPE) == DEAL_TYPE_BUY ? 1 : -1;
         int k = SideOf(dir);
         if (g_io[k].nFill >= MAXF) continue;
         int seq = -1, piece = 0;
         ParseCmt(HistoryDealGetString(dk, DEAL_COMMENT), seq, piece);
         int f = g_io[k].nFill++;
         g_io[k].fill[f].id = pid; g_io[k].fill[f].dir = dir; g_io[k].fill[f].q = HistoryDealGetDouble(dk, DEAL_VOLUME) * g_contract;
         g_io[k].fill[f].ent = HistoryDealGetDouble(dk, DEAL_PRICE); g_io[k].fill[f].t = SrvToUtc(dt); g_io[k].fill[f].seq = seq; g_io[k].fill[f].piece = piece;
         g_io[k].fill[f].atOpen = false;
         for (int x = 0; x < ArraySize(g_gapPos); x++) if (g_gapPos[x] == pid) g_io[k].fill[f].atOpen = true;
      }
      else if (dt >= tEnd)
      {
         bool have = false;
         for (int j = 0; j < na; j++) if (afterIds[j] == pid) have = true;
         if (!have) { ArrayResize(afterIds, na + 1); afterIds[na++] = pid; }
      }
      else if (!IsDone(dk))
      {
         MarkDone(dk, dt);
         bool have = false;
         for (int j = 0; j < nc; j++) if (closedIds[j] == pid) have = true;
         if (!have) { ArrayResize(closedIds, nc + 1); closedIds[nc++] = pid; }
      }
   }
   TrimDone(tEnd - 10 * 86400);
   g_dealFlag = later;
   datetime tIn = 0, tOut = 0;
   double pnl = 0, q = 0, ent = 0;
   int dir = 0, seq = -1, piece = 0, why = 0;
   // trades open at the bar close that closed since (on the first tick of the new bar)
   for (int j = 0; j < na; j++)
   {
      if (PosOpenNow(afterIds[j])) continue;
      if (!PosSummary(afterIds[j], tIn, tOut, pnl, dir, q, ent, seq, piece, why)) continue;
      if (tIn >= tEnd) continue;
      AddPos(SideOf(dir), afterIds[j], afterIds[j], dir, q, ent, NAD, NAD, SrvToUtc(tIn), seq, piece);
   }
   // trades that closed during this bar (a trade only counts once it is fully closed)
   for (int j = 0; j < nc; j++)
   {
      if (PosOpenNow(closedIds[j])) continue;
      if (!PosSummary(closedIds[j], tIn, tOut, pnl, dir, q, ent, seq, piece, why)) continue;
      AddCls(SideOf(dir), closedIds[j], dir, q, pnl, SrvToUtc(tIn), SrvToUtc(tOut), seq, piece, why);
      CountExit(closedIds[j], dir, why);
   }
   // the risk of the newest entry (table row 'Last trade risk')
   for (int k = 0; k < 2; k++)
      for (int f = 0; f < g_io[k].nFill; f++)
         for (int i = 0; i < g_io[k].nPos; i++)
            if (g_io[k].pos[i].id == g_io[k].fill[f].id && !IsNa(g_io[k].pos[i].sl))
            {
               double qq = g_io[k].pos[i].q, ee = g_io[k].pos[i].ent;
               g_lastCost = qq * CmU(ee) + CmF();
               g_lastRisk = qq * MathAbs(ee - g_io[k].pos[i].sl) * UnitValue() + g_lastCost;
               g_lastLots = qq / g_contract;
            }
   for (int k = 0; k < 2; k++)   // oldest exit first
      for (int a = 1; a < g_io[k].nCls; a++)
         for (int b = a; b > 0 && g_io[k].cls[b - 1].tOut > g_io[k].cls[b].tOut; b--)
         {
            ClsRec tmp = g_io[k].cls[b];
            g_io[k].cls[b] = g_io[k].cls[b - 1];
            g_io[k].cls[b - 1] = tmp;
         }
}

//---------------------------------------------------------------- carrying out the core's decisions
bool RetryCode(uint rc)
{
   return rc == TRADE_RETCODE_REQUOTE || rc == TRADE_RETCODE_PRICE_CHANGED || rc == TRADE_RETCODE_PRICE_OFF || rc == TRADE_RETCODE_TIMEOUT ||
          rc == TRADE_RETCODE_CONNECTION || rc == TRADE_RETCODE_TOO_MANY_REQUESTS || rc == TRADE_RETCODE_LOCKED || rc == TRADE_RETCODE_FROZEN ||
          rc == TRADE_RETCODE_MARKET_CLOSED || rc == TRADE_RETCODE_SERVER_DISABLES_AT || rc == TRADE_RETCODE_CLIENT_DISABLES_AT || rc == TRADE_RETCODE_TRADE_DISABLED;
}
void DoCloses()
{
   for (int j = ArraySize(g_clsTk) - 1; j >= 0; j--)
   {
      bool gone = !PositionSelectByTicket(g_clsTk[j]);
      if (!gone)
      {
         if (g_trade.PositionClose(g_clsTk[j], (ulong)InSlip))
         {
            gone = true;
            int nw = ArraySize(g_cwTk);
            if (nw >= 300) { for (int x = 0; x + 1 < nw; x++) { g_cwTk[x] = g_cwTk[x + 1]; g_cwWhy[x] = g_cwWhy[x + 1]; } nw--; }
            ArrayResize(g_cwTk, nw + 1);
            ArrayResize(g_cwWhy, nw + 1);
            g_cwTk[nw] = g_clsTk[j];
            g_cwWhy[nw] = g_clsWhy[j];
         }
         else
         {
            uint rc = g_trade.ResultRetcode();
            if (!RetryCode(rc)) { Log("Close of #" + IntegerToString((long)g_clsTk[j]) + " (" + g_clsWhy[j] + ") failed: " + g_trade.ResultRetcodeDescription()); gone = true; }
         }
      }
      if (gone)
      {
         int n = ArraySize(g_clsTk);
         for (int x = j; x + 1 < n; x++) { g_clsTk[x] = g_clsTk[x + 1]; g_clsWhy[x] = g_clsWhy[x + 1]; }
         ArrayResize(g_clsTk, n - 1);
         ArrayResize(g_clsWhy, n - 1);
      }
   }
}
void CloseNow(ulong tk, string why)
{
   for (int j = 0; j < ArraySize(g_clsTk); j++) if (g_clsTk[j] == tk) return;
   int n = ArraySize(g_clsTk);
   ArrayResize(g_clsTk, n + 1);
   ArrayResize(g_clsWhy, n + 1);
   g_clsTk[n] = tk;
   g_clsWhy[n] = why;
}
void DoStops()
{
   for (int j = ArraySize(g_stpTk) - 1; j >= 0; j--)
   {
      bool done = true;
      if (PositionSelectByTicket(g_stpTk[j]))
      {
         int    dir = g_stpDir[j];
         double sl  = dir == 1 ? NormDn(g_stpSl[j]) : NormUp(g_stpSl[j]);
         double tp  = PositionGetDouble(POSITION_TP);
         double bid = SymbolInfoDouble(g_sym, SYMBOL_BID), ask = SymbolInfoDouble(g_sym, SYMBOL_ASK);
         double gap = StopsGap();
         // the price is already beyond the new stop: TradingView fills it at once - close at market
         if ((dir == 1 && bid <= sl) || (dir == -1 && ask >= sl)) CloseNow(g_stpTk[j], "moved stop already passed");
         else if (MathAbs(PositionGetDouble(POSITION_SL) - sl) >= g_tickSize / 2)
         {
            if ((dir == 1 && bid - sl < gap) || (dir == -1 && sl - ask < gap)) done = false;   // too close for the broker now - try again
            else if (!g_trade.PositionModify(g_stpTk[j], sl, tp))
            {
               uint rc = g_trade.ResultRetcode();
               if (RetryCode(rc) || rc == TRADE_RETCODE_INVALID_STOPS) done = false;
               else Log("Stop move of #" + IntegerToString((long)g_stpTk[j]) + " failed: " + g_trade.ResultRetcodeDescription());
            }
         }
      }
      if (done)
      {
         int n = ArraySize(g_stpTk);
         for (int x = j; x + 1 < n; x++) { g_stpTk[x] = g_stpTk[x + 1]; g_stpSl[x] = g_stpSl[x + 1]; g_stpDir[x] = g_stpDir[x + 1]; }
         ArrayResize(g_stpTk, n - 1);
         ArrayResize(g_stpSl, n - 1);
         ArrayResize(g_stpDir, n - 1);
      }
   }
}
// a market order for book entry i (the entry was touched, or a pending order cannot be placed because the price is already through it)
void SendMarket(int i)
{
   int    dir = g_vb[i].dir;
   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID), ask = SymbolInfoDouble(g_sym, SYMBOL_ASK);
   double sl  = dir == 1 ? NormDn(g_vb[i].sl) : NormUp(g_vb[i].sl);
   double tp  = dir == 1 ? NormUp(g_vb[i].tgt) : NormDn(g_vb[i].tgt);
   double ref = dir == 1 ? bid : ask, gap = StopsGap();
   string id  = TradeId(dir, g_vb[i].seq, i % 2);
   if ((dir == 1 && (sl >= ref - gap || tp <= ref + gap)) || (dir == -1 && (sl <= ref + gap || tp >= ref - gap)))
   {
      Log("Entry " + id + " skipped: the price is already past its stop or target (TradingView would open and close it at once)");
      AudRef(i, "SKIPPED - the price was already past the stop or target");
      g_vb[i].on = false;
      return;
   }
   bool ok = dir == 1 ? g_trade.Buy(g_vb[i].lots, g_sym, 0.0, sl, tp, CmtOf(dir, g_vb[i].seq, i % 2))
                      : g_trade.Sell(g_vb[i].lots, g_sym, 0.0, sl, tp, CmtOf(dir, g_vb[i].seq, i % 2));
   uint rc = g_trade.ResultRetcode();
   if (ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED))
   {
      g_vb[i].on = false;
      if (g_inBar)
      {
         int n = ArraySize(g_gapPos);
         if (n >= 50) { for (int x = 0; x + 1 < n; x++) g_gapPos[x] = g_gapPos[x + 1]; n--; }
         ArrayResize(g_gapPos, n + 1);
         g_gapPos[n] = (long)g_trade.ResultOrder();
      }
      return;
   }
   if (RetryCode(rc) && g_vb[i].fails < 50) { g_vb[i].fails++; return; }
   Log("Entry " + id + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription());
   AudRef(i, "REFUSED BY THE BROKER - " + g_trade.ResultRetcodeDescription());
   g_refused++;
   g_vb[i].on = false;
}
// touch mode: fill when the chart price (bid) reaches the entry - what TradingView does on its chart
void CheckTouch()
{
   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID);
   if (bid <= 0) return;
   for (int i = 0; i < 4; i++)   // the level on the price grid, rounded the safe way (a buy lower, a sell higher), like a pending order
      if (g_vb[i].on && (g_vb[i].mkt || (g_vb[i].dir == 1 && bid <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && bid >= NormUp(g_vb[i].ent)))) SendMarket(i);
}
bool PosWithComment(string cmt)
{
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if (tk == 0) continue;
      if (PositionGetString(POSITION_SYMBOL) == g_sym && PositionGetInteger(POSITION_MAGIC) == InMagic && PositionGetString(POSITION_COMMENT) == cmt) return true;
   }
   return false;
}
bool OurOrder(ulong tk)
{
   if (!OrderSelect(tk)) return false;
   return OrderGetString(ORDER_SYMBOL) == g_sym && OrderGetInteger(ORDER_MAGIC) == InMagic;
}
// pending mode: keep one broker order per book entry, equal to what the core wants
void SyncPending()
{
   double bid = SymbolInfoDouble(g_sym, SYMBOL_BID), ask = SymbolInfoDouble(g_sym, SYMBOL_ASK);
   if (bid <= 0 || ask <= 0) return;
   double gap = StopsGap();
   for (int i = 0; i < 4; i++)
   {
      ulong tk = (ulong)g_vb[i].ticket;
      bool exists = tk != 0 && OurOrder(tk);
      if (!g_vb[i].on)
      {
         if (exists) { if (g_trade.OrderDelete(tk) || !OurOrder(tk)) g_vb[i].ticket = 0; }
         else g_vb[i].ticket = 0;
         continue;
      }
      if (g_vb[i].mkt)
      {   // v12.0: a rule 3 entry is a market order at once (no pending order)
         if (exists) { if (!g_trade.OrderDelete(tk)) continue; g_vb[i].ticket = 0; }
         if (PosWithComment(CmtOf(g_vb[i].dir, g_vb[i].seq, i % 2))) { g_vb[i].on = false; continue; }
         SendMarket(i);
         continue;
      }
      int    dir = g_vb[i].dir;
      double px  = dir == 1 ? NormDn(g_vb[i].ent) : NormUp(g_vb[i].ent);
      double sl  = dir == 1 ? NormDn(g_vb[i].sl) : NormUp(g_vb[i].sl);
      double tp  = dir == 1 ? NormUp(g_vb[i].tgt) : NormDn(g_vb[i].tgt);
      string cmt = CmtOf(dir, g_vb[i].seq, i % 2);
      if (exists)
      {
         bool sameSetup = OrderGetString(ORDER_COMMENT) == cmt && MathAbs(OrderGetDouble(ORDER_VOLUME_CURRENT) - g_vb[i].lots) < g_volStep / 2;
         if (!sameSetup)
         {   // another setup or another size: replace the order (a pending order's size cannot be changed)
            if (!g_trade.OrderDelete(tk)) continue;
            g_vb[i].ticket = 0;
            exists = false;
            tk = 0;
         }
      }
      if (exists)
      {
         bool same = MathAbs(OrderGetDouble(ORDER_PRICE_OPEN) - px) < g_tickSize / 2 && MathAbs(OrderGetDouble(ORDER_SL) - sl) < g_tickSize / 2 && MathAbs(OrderGetDouble(ORDER_TP) - tp) < g_tickSize / 2;
         if (same) continue;
         if ((dir == 1 && px >= ask) || (dir == -1 && px <= bid))
         {   // the new entry is already through the price: TradingView fills at once - delete and buy / sell at market
            if (g_trade.OrderDelete(tk)) { g_vb[i].ticket = 0; SendMarket(i); }
            continue;
         }
         if (!g_trade.OrderModify(tk, px, sl, tp, g_otime, 0))
         {
            uint rc = g_trade.ResultRetcode();
            if (!RetryCode(rc) && rc != TRADE_RETCODE_INVALID_PRICE && rc != TRADE_RETCODE_INVALID_STOPS) Log("Order change " + cmt + " failed: " + g_trade.ResultRetcodeDescription());
         }
         continue;
      }
      if (tk != 0)
      {   // our order is gone: filled -> done; cancelled / expired / rejected -> place it again; not known yet -> wait
         if (PosWithComment(cmt)) { g_vb[i].on = false; g_vb[i].ticket = 0; continue; }
         if (!HistoryOrderSelect(tk)) continue;
         long st = HistoryOrderGetInteger(tk, ORDER_STATE);
         if (st == ORDER_STATE_FILLED || st == ORDER_STATE_PARTIAL) { g_vb[i].on = false; g_vb[i].ticket = 0; continue; }
         if (st != ORDER_STATE_CANCELED && st != ORDER_STATE_EXPIRED && st != ORDER_STATE_REJECTED) continue;
         if (st == ORDER_STATE_REJECTED) g_vb[i].fails++;
         g_vb[i].ticket = 0;
         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker 5 times - setup dropped"); AudRef(i, "REFUSED BY THE BROKER (5 times)"); g_refused++; g_vb[i].on = false; continue; }
      }
      if ((dir == 1 && px >= ask) || (dir == -1 && px <= bid)) { SendMarket(i); continue; }
      if ((dir == 1 && ask - px < gap) || (dir == -1 && px - bid < gap)) continue;   // too close for a pending order now - wait
      bool ok = dir == 1 ? g_trade.BuyLimit(g_vb[i].lots, px, g_sym, sl, tp, g_otime, 0, cmt)
                         : g_trade.SellLimit(g_vb[i].lots, px, g_sym, sl, tp, g_otime, 0, cmt);
      uint rc = g_trade.ResultRetcode();
      if (ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_PLACED)) g_vb[i].ticket = (long)g_trade.ResultOrder();
      else if (!RetryCode(rc))
      {
         g_vb[i].fails++;
         if (g_vb[i].fails > 5) { Log("Order " + cmt + " REFUSED by the broker: " + g_trade.ResultRetcodeDescription()); AudRef(i, "REFUSED BY THE BROKER - " + g_trade.ResultRetcodeDescription()); g_refused++; g_vb[i].on = false; }
      }
   }
}
void ExecuteAll()
{
   g_inBar = true;
   DoCloses();
   DoStops();
   DoCloses();
   if (InExec == EX_TOUCH) CheckTouch();
   else SyncPending();
   g_inBar = false;
}
// v12.3: after a gap - the computer slept, the connection dropped, or the EA was off for a few candles - the missed
// candles are read WITHOUT opening trades. A waiting entry whose price was reached while the EA was offline is dropped:
// TradingView would have filled it then, the EA cannot copy that, so there is no late entry at another price. A market
// entry (rule 3) of a missed candle is dropped the same way. A real fill by the broker (pending mode) is kept.
bool FilledReal(int dir, int seq, int piece)
{
   string cmt = CmtOf(dir, seq, piece);
   if (PosWithComment(cmt)) return true;
   if (!HistorySelect(TimeCurrent() - 10 * 86400, TimeCurrent() + 86400)) return false;
   for (int i = HistoryDealsTotal() - 1; i >= 0; i--)
   {
      ulong dk = HistoryDealGetTicket(i);
      if (dk == 0 || !OurDeal(dk)) continue;
      if (HistoryDealGetInteger(dk, DEAL_ENTRY) == DEAL_ENTRY_IN && HistoryDealGetString(dk, DEAL_COMMENT) == cmt) return true;
   }
   return false;
}
int DropReached(double hi, double lo, datetime when)
{
   int d = 0;
   for (int k = 0; k < g_nSides; k++)
   {
      if (g_side[k].dir == 0) continue;
      bool hit = false, hitMkt = false;
      double hitPx = 0;
      for (int p = 0; p < 2; p++)
      {
         int i = k * 2 + p;
         if (!g_vb[i].on || g_vb[i].seq != g_side[k].seq) continue;
         bool reached = g_vb[i].mkt || (g_vb[i].dir == 1 && lo <= NormDn(g_vb[i].ent)) || (g_vb[i].dir == -1 && hi >= NormUp(g_vb[i].ent));
         if (reached && !FilledReal(g_vb[i].dir, g_vb[i].seq, p)) { hit = true; hitMkt = g_vb[i].mkt; hitPx = g_vb[i].ent; }
      }
      if (!hit) continue;
      Print("SMC EA: setup ", TradeId(g_side[k].dir, g_side[k].seq, 0), " dropped - its entry ", hitMkt ? "(market, rule 3)" : DoubleToString(hitPx, g_digits),
            " was reached while the EA was offline (candle ", TimeToString(when), "), no late entry");
      g_audT = when;   // the candle where it was reached (for the audit)
      g_side[k].Cancel("CANCELLED - entry reached while the EA was offline");
      d++;
   }
   return d;
}
void CatchUp(MqlRates &rr[], int i0, int n, datetime t0, bool live)
{
   int m = 0, d = 0;
   g_dealFlag = true;   // the broker may have filled or closed trades meanwhile - read the deals
   for (int i = i0; i < n; i++)
   {
      if (live && (rr[i].time <= g_lastBar || rr[i].time >= t0)) continue;
      d += DropReached(rr[i].high, rr[i].low, rr[i].time);   // the orders that were waiting during this candle
      ProcessBar(rr[i], false, i + 1 < n ? rr[i + 1].time : t0);
      if (live) { g_lastBar = rr[i].time; SaveState(g_lastBar); }
      m++;
   }
   if (m == 0) return;
   // the candle forming now: the part of it before this tick was offline too (nothing to check at its very first price)
   double fh = iHigh(g_sym, g_tf, 0), fl = iLow(g_sym, g_tf, 0);
   if (TimeCurrent() > t0 || fh > fl) d += DropReached(fh, fl, t0);
   ExecuteAll();   // exits and stop moves the core asked for, and the setups that are still waiting
   if (live) SaveState(g_lastBar);   // the orders just sent
   Print("SMC EA: ", m, " candle(s) missed (computer asleep, no connection or a restart) - read without opening trades", d > 0 ? ", " + IntegerToString(d) + " waiting entry(ies) dropped" : "");
}
void DeleteOurPending()
{
   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong tk = OrderGetTicket(i);
      if (tk != 0 && OurOrder(tk)) g_trade.OrderDelete(tk);
   }
   for (int i = 0; i < 4; i++) { g_vb[i].on = false; g_vb[i].ticket = 0; }
}

//---------------------------------------------------------------- higher timeframe: closed candles only
datetime HtfOpenOf(datetime t)
{
   int sh = iBarShift(g_sym, g_htf, t, false);
   if (sh < 0) return 0;
   return iTime(g_sym, g_htf, sh);
}
bool HtfDrawOn() { return InHtfDraw && g_htfUse && (!g_tester || g_visual); }
void PushHtfTime(datetime t)
{
   int n = ArraySize(g_hbt);
   if (n >= 7000)
   {
      for (int i = 0; i + 1000 < n; i++) g_hbt[i] = g_hbt[i + 1000];
      n -= 1000;
      g_hbBase += 1000;
   }
   ArrayResize(g_hbt, n + 1, 1024);
   g_hbt[n] = t;
}
datetime TimeOfHtf(int hb)
{
   int n = ArraySize(g_hbt);
   if (n == 0) return 0;
   int i = hb - g_hbBase;
   if (i < 0) i = 0;
   if (i >= n) i = n - 1;
   return g_hbt[i];
}
// one CLOSED higher-timeframe candle into the engine
void HtfStep(MqlRates &r)
{
   HT.Step(r.open, r.high, r.low, r.close);
   PushHtfTime(r.time);
   g_htfFed = r.time;
   if (HT.brkNow)
   {
      g_htfEvSrv = r.time + g_htfSec;
      if (HtfDrawOn()) DrawHtfMark(r.time + g_htfSec);
   }
}
// feed every higher-timeframe candle that closed before the candle holding this chart bar
bool FeedHtf(datetime barOpen)
{
   if (!g_htfUse) return true;
   datetime hc = HtfOpenOf(barOpen);
   if (hc == 0) return false;
   if (hc <= g_htfFed + 1) return true;
   MqlRates hr[];
   int n = CopyRates(g_sym, g_htf, g_htfFed + 1, hc - 1, hr);
   if (n < 0) return false;
   for (int i = 0; i < n; i++)
      if (hr[i].time > g_htfFed && hr[i].time < hc) HtfStep(hr[i]);
   return true;
}

//---------------------------------------------------------------- bar times (for drawing) and one bar
void PushBarTime(datetime t)
{
   int n = ArraySize(g_bt);
   if (n >= 7000)
   {
      for (int i = 0; i + 1000 < n; i++) g_bt[i] = g_bt[i + 1000];
      n -= 1000;
      g_btBase += 1000;
   }
   ArrayResize(g_bt, n + 1, 1024);
   g_bt[n] = t;
}
datetime TimeOfBar(int bi)
{
   int n = ArraySize(g_bt);
   if (n == 0) return 0;
   int i = bi - g_btBase;
   if (i < 0) i = 0;
   if (i >= n) i = n - 1;
   return g_bt[i];
}
int BarOfTime(datetime t)
{
   for (int i = ArraySize(g_bt) - 1; i >= 0; i--) if (g_bt[i] <= t) return g_btBase + i;
   return NAI;
}
void ProcessBar(MqlRates &r, bool dry, datetime tEnd)
{
   FeedHtf(r.time);
   if (!dry) GatherIO(tEnd);
   S.uv  = UnitValue();
   g_now = SrvToUtc(TimeCurrent());
   g_dry = dry;
   g_audT = r.time; g_audH = r.high; g_audL = r.low;   // v12.3: where a signal's audit label goes
   PushBarTime(r.time);
   int    ht = 0, he = 0;
   double ho = NAD, hx = NAD;
   if (g_htfUse) { ht = HT.tTrend; ho = HT.outO; hx = HT.outX; he = HT.evN; }
   CoreBar(SrvToUtc(r.time), r.open, r.high, r.low, r.close, dry ? 0.0 : AccountInfoDouble(ACCOUNT_EQUITY), ht, ho, hx, he);
   if (S.useCho && (EN.evCU || EN.evCD)) g_cntCho++;
   if (S.useBos && (EN.evBU || EN.evBD)) g_cntBos++;
   if (!g_tester || g_visual)
   {
      if (InDraw) DrawBar(r);
      if (!dry) DrawAll(r.time);
   }
}

//---------------------------------------------------------------- loss memory etc. rebuilt from this EA's real deals
void ReplayMoney(datetime tLimit)
{
   if (!HistorySelect(0, TimeCurrent() + 86400)) return;
   long pids[];
   datetime dts[];
   long ens[];
   int n = 0;
   int nd = HistoryDealsTotal();
   for (int i = 0; i < nd; i++)
   {
      ulong dk = HistoryDealGetTicket(i);
      if (dk == 0 || !OurDeal(dk)) continue;
      datetime dt = (datetime)HistoryDealGetInteger(dk, DEAL_TIME);
      if (dt >= tLimit) continue;
      MarkDone(dk, dt);
      ArrayResize(pids, n + 1, 1024); ArrayResize(dts, n + 1, 1024); ArrayResize(ens, n + 1, 1024);
      pids[n] = HistoryDealGetInteger(dk, DEAL_POSITION_ID);
      dts[n] = dt;
      ens[n] = HistoryDealGetInteger(dk, DEAL_ENTRY);
      n++;
   }
   if (n == 0) return;
   // events: entries (by their bar) and closed trades (by the bar of their last exit)
   long   evBar[];
   int    evKind[], evSide[], evSeq[], evPiece[], evWhy[], evDir[];
   double evPnl[], evQ[];
   long   evIn[], evOut[], evPid[];
   int    ne = 0;
   long   seen[];
   int    ns = 0;
   for (int i = 0; i < n; i++)
   {
      bool have = false;
      for (int j = 0; j < ns; j++) if (seen[j] == pids[i]) { have = true; break; }
      if (have) continue;
      ArrayResize(seen, ns + 1, 1024);
      seen[ns++] = pids[i];
      datetime tIn = 0, tOut = 0;
      double pnl = 0, q = 0, ent = 0;
      int dir = 0, seq = -1, piece = 0, why = 0;
      if (!PosSummary(pids[i], tIn, tOut, pnl, dir, q, ent, seq, piece, why)) continue;
      int add = 1;
      bool closed = tOut > 0 && tOut < tLimit && !PosOpenNow(pids[i]);
      if (closed) add = 2;
      for (int ai = 0; ai < add; ai++)
      {
         ArrayResize(evBar, ne + 1, 1024); ArrayResize(evKind, ne + 1, 1024); ArrayResize(evSide, ne + 1, 1024); ArrayResize(evSeq, ne + 1, 1024);
         ArrayResize(evPiece, ne + 1, 1024); ArrayResize(evWhy, ne + 1, 1024); ArrayResize(evDir, ne + 1, 1024); ArrayResize(evPnl, ne + 1, 1024);
         ArrayResize(evQ, ne + 1, 1024); ArrayResize(evIn, ne + 1, 1024); ArrayResize(evOut, ne + 1, 1024); ArrayResize(evPid, ne + 1, 1024);
         datetime te = ai == 0 ? tIn : tOut;
         int sh = iBarShift(g_sym, g_tf, te, false);
         evBar[ne] = sh >= 0 ? (long)iTime(g_sym, g_tf, sh) : (long)te;
         evKind[ne] = ai;         // 0 entry, 1 close
         evSide[ne] = SideOf(dir); evSeq[ne] = seq; evPiece[ne] = piece; evWhy[ne] = why; evDir[ne] = dir; evPnl[ne] = pnl; evQ[ne] = q;
         evIn[ne] = SrvToUtc(tIn); evOut[ne] = SrvToUtc(tOut); evPid[ne] = pids[i];
         ne++;
      }
   }
   // in time order (bar, then exit time)
   int ord[];
   ArrayResize(ord, ne);
   for (int i = 0; i < ne; i++) ord[i] = i;
   for (int sa = 1; sa < ne; sa++)
      for (int sb = sa; sb > 0; sb--)
      {
         int x = ord[sb - 1], y = ord[sb];
         bool swap = evBar[x] > evBar[y] || (evBar[x] == evBar[y] && evKind[x] == 1 && evKind[y] == 1 && evOut[x] > evOut[y]);
         if (!swap) break;
         ord[sb - 1] = y;
         ord[sb] = x;
      }
   int nm = (S.dirMode == 3 && S.hedgeMoney == 0) ? 2 : 1;
   int ev = 0;
   while (ev < ne)
   {
      long bar = evBar[ord[ev]];
      for (int k = 0; k < 2; k++) g_io[k].Clear();
      bool filled[2];
      filled[0] = false;
      filled[1] = false;
      while (ev < ne && evBar[ord[ev]] == bar)
      {
         int e = ord[ev];
         if (evKind[e] == 0) filled[evSide[e]] = true;
         else AddCls(evSide[e], evPid[e], evDir[e], evQ[e], evPnl[e], evIn[e], evOut[e], evSeq[e], evPiece[e], evWhy[e]);
         ev++;
      }
      for (int m = 0; m < nm; m++) g_money[m].NewBar(SrvToUtc((datetime)bar));
      for (int k = 0; k < g_nSides; k++) if (filled[k]) g_money[g_sideMi[k]].dayTrades++;
      for (int m = 0; m < nm; m++) { g_money[m].Closes(m); g_money[m].Risk(); g_money[m].Halts(0.0, false); }
   }
   for (int k = 0; k < 2; k++) g_io[k].Clear();
}

//---------------------------------------------------------------- restart safety: the waiting setup and the managed stops
string GvSide(int k, string f) { return g_P + "s" + IntegerToString(k) + f; }
void   GvSet(string name, double v) { GlobalVariableSet(name, v); }
double GvGet(string name, double def) { return GlobalVariableCheck(name) ? GlobalVariableGet(name) : def; }
void SaveState(datetime barTime)
{
   if (g_tester) return;
   for (int k = 0; k < g_nSides; k++)
   {
      GvSet(GvSide(k, "dir"), g_side[k].dir);       GvSet(GvSide(k, "rule"), g_side[k].rule);   GvSet(GvSide(k, "sl"), g_side[k].sl);
      GvSet(GvSide(k, "fix"), g_side[k].fix);       GvSet(GvSide(k, "ol"), g_side[k].ordLive ? 1 : 0);
      GvSet(GvSide(k, "le"), g_side[k].lastEnt);    GvSet(GvSide(k, "ls"), g_side[k].lastSl);   GvSet(GvSide(k, "lt"), g_side[k].lastTgt);
      GvSet(GvSide(k, "lq"), g_side[k].lastQ);      GvSet(GvSide(k, "lc"), g_side[k].lastCapQ ? 1 : 0);
      GvSet(GvSide(k, "pl"), g_side[k].placed ? 1 : 0); GvSet(GvSide(k, "el"), g_side[k].entLock);
      GvSet(GvSide(k, "ab"), g_side[k].armBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].armBar));
      GvSet(GvSide(k, "seq"), g_side[k].seq);       GvSet(GvSide(k, "ak"), g_side[k].addRk);    GvSet(GvSide(k, "ps"), g_side[k].ppSent ? 1 : 0);
      GvSet(GvSide(k, "tp1"), g_side[k].lastTp1);   GvSet(GvSide(k, "os"), g_side[k].openSl);   GvSet(GvSide(k, "ot"), g_side[k].openTgt);
      GvSet(GvSide(k, "pt"), g_side[k].planTgt);
      GvSet(GvSide(k, "mb"), g_side[k].mktBar == NAI ? -1.0 : (double)TimeOfBar(g_side[k].mktBar));
      for (int j = 0; j < g_side[k].ntrk; j++)
      {
         string id = IntegerToString(g_side[k].trk[j].id);
         GvSet(g_P + "r" + id, g_side[k].trk[j].r);
         GvSet(g_P + "k" + id, g_side[k].trk[j].step + (g_side[k].trk[j].mv ? 10 : 0) + (g_side[k].trk[j].pp ? 100 : 0));
         GvSet(g_P + "b" + id, (double)TimeOfBar(g_side[k].trk[j].bar));
         GvSet(g_P + "e" + id, g_side[k].trk[j].ent);
      }
   }
   for (int i = 0; i < 4; i++)
   {
      string v = g_P + "v" + IntegerToString(i);
      GvSet(v + "on", g_vb[i].on ? 1 : 0); GvSet(v + "seq", g_vb[i].seq); GvSet(v + "dir", g_vb[i].dir); GvSet(v + "ent", g_vb[i].ent);
      GvSet(v + "sl", g_vb[i].sl); GvSet(v + "tg", g_vb[i].tgt); GvSet(v + "lot", g_vb[i].lots); GvSet(v + "tk", (double)g_vb[i].ticket);
      GvSet(v + "mk", g_vb[i].mkt ? 1 : 0);
   }
   GvSet(g_P + "T", (double)barTime);
   GvSet(g_P + "mode", (double)(InDirMode * 10 + InExec));
   GvSet(g_P + "cs", (double)g_cs);
}
void RestoreSides()
{
   for (int k = 0; k < g_nSides; k++)
   {
      g_side[k].dir = (int)GvGet(GvSide(k, "dir"), 0);      g_side[k].rule = (int)GvGet(GvSide(k, "rule"), 0);
      g_side[k].seq = (int)GvGet(GvSide(k, "seq"), 0);      // v12.3: the setup number goes on (it went back to 0 before)
      g_side[k].sl = GvGet(GvSide(k, "sl"), NAD);           g_side[k].fix = GvGet(GvSide(k, "fix"), NAD);
      g_side[k].ordLive = GvGet(GvSide(k, "ol"), 0) > 0.5;
      g_side[k].lastEnt = GvGet(GvSide(k, "le"), NAD);      g_side[k].lastSl = GvGet(GvSide(k, "ls"), NAD);
      g_side[k].lastTgt = GvGet(GvSide(k, "lt"), NAD);      g_side[k].lastQ = GvGet(GvSide(k, "lq"), NAD);
      g_side[k].lastCapQ = GvGet(GvSide(k, "lc"), 0) > 0.5; g_side[k].placed = GvGet(GvSide(k, "pl"), 0) > 0.5;
      g_side[k].entLock = GvGet(GvSide(k, "el"), NAD);
      double ab = GvGet(GvSide(k, "ab"), -1);
      g_side[k].armBar = ab < 0 ? NAI : BarOfTime((datetime)ab);
      g_side[k].addRk = GvGet(GvSide(k, "ak"), 1.0);        g_side[k].ppSent = GvGet(GvSide(k, "ps"), 0) > 0.5;
      g_side[k].lastTp1 = GvGet(GvSide(k, "tp1"), NAD);     g_side[k].openSl = GvGet(GvSide(k, "os"), NAD);
      g_side[k].openTgt = GvGet(GvSide(k, "ot"), NAD);      g_side[k].planTgt = GvGet(GvSide(k, "pt"), NAD);
      double mb = GvGet(GvSide(k, "mb"), -1);
      g_side[k].mktBar = mb < 0 ? NAI : BarOfTime((datetime)mb);
      // v12.3: the audit label of the kept setup (named by its signal candle) goes on
      if (g_side[k].dir != 0 && g_side[k].armBar != NAI) { g_audCur[k] = g_AP + IntegerToString(k) + "_" + IntegerToString((long)TimeOfBar(g_side[k].armBar)); g_audSeq[k] = g_side[k].seq; }
   }
   for (int i = 0; i < 4; i++)
   {
      string v = g_P + "v" + IntegerToString(i);
      g_vb[i].on = GvGet(v + "on", 0) > 0.5; g_vb[i].seq = (int)GvGet(v + "seq", 0); g_vb[i].dir = (int)GvGet(v + "dir", 0);
      g_vb[i].ent = GvGet(v + "ent", 0); g_vb[i].sl = GvGet(v + "sl", 0); g_vb[i].tgt = GvGet(v + "tg", 0); g_vb[i].lots = GvGet(v + "lot", 0);
      g_vb[i].ticket = (long)GvGet(v + "tk", 0); g_vb[i].fails = 0; g_vb[i].mkt = GvGet(v + "mk", 0) > 0.5;
      if (g_vb[i].on && (i / 2 >= g_nSides || g_vb[i].dir == 0 || g_vb[i].lots <= 0)) g_vb[i].on = false;
   }
}
// managed stops (group 32, trailing, break-even) for the trades open now
void RebuildTrk()
{
   for (int k = 0; k < 2; k++) g_side[k].ntrk = 0;
   if (!S.mgOn) return;
   for (int i = 0; i < PositionsTotal(); i++)
   {
      ulong tk = PositionGetTicket(i);
      if (tk == 0) continue;
      if (PositionGetString(POSITION_SYMBOL) != g_sym || PositionGetInteger(POSITION_MAGIC) != InMagic) continue;
      int    dir = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1;
      int    k   = SideOf(dir);
      if (k >= g_nSides || g_side[k].ntrk >= MAXP) continue;
      long   pid = PositionGetInteger(POSITION_IDENTIFIER);
      string id  = IntegerToString(pid);
      double ent = GvGet(g_P + "e" + IntegerToString(PositionGetInteger(POSITION_IDENTIFIER)), PositionGetDouble(POSITION_PRICE_OPEN));
      double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
      double q   = PositionGetDouble(POSITION_VOLUME) * g_contract;
      int    seq = -1, piece = 0;
      ParseCmt(PositionGetString(POSITION_COMMENT), seq, piece);
      double cst = S.uv > 0 ? (CmU(ent) + (q > 0 ? CmF() / q : 0.0)) / S.uv : 0.0;
      int    kf  = (int)GvGet(g_P + "k" + id, 0);
      double bt  = GvGet(g_P + "b" + id, -1);
      int    j   = g_side[k].ntrk++;
      g_side[k].trk[j].id = pid; g_side[k].trk[j].ticket = (long)tk; g_side[k].trk[j].dir = dir; g_side[k].trk[j].ent = ent;
      g_side[k].trk[j].r = GvGet(g_P + "r" + id, sl > 0 ? MathAbs(ent - sl) : 0.0);
      g_side[k].trk[j].be = dir == 1 ? ent + cst : ent - cst;
      g_side[k].trk[j].sl = sl > 0 ? sl : NAD; g_side[k].trk[j].tgt = tp > 0 ? tp : NAD; g_side[k].trk[j].q = q;
      g_side[k].trk[j].step = kf % 10; g_side[k].trk[j].mv = (kf / 10) % 10 == 1; g_side[k].trk[j].pp = kf / 100 == 1;
      int b = bt < 0 ? NAI : BarOfTime((datetime)bt);
      g_side[k].trk[j].bar = b == NAI ? EN.bi - 1 : b;
      g_side[k].trk[j].seq = seq; g_side[k].trk[j].piece = piece;
   }
}
// global variables of trades that are no longer open
void CleanGv()
{
   if (g_tester) return;
   for (int i = GlobalVariablesTotal() - 1; i >= 0; i--)
   {
      string nm = GlobalVariableName(i);
      if (StringFind(nm, g_P) != 0) continue;
      string rest = StringSubstr(nm, StringLen(g_P));
      if (StringLen(rest) < 2) continue;
      ushort c0 = StringGetCharacter(rest, 0);
      if (c0 != 'r' && c0 != 'k' && c0 != 'b' && c0 != 'e') continue;
      string num = StringSubstr(rest, 1);
      if (!IsDigits(num)) continue;
      if (!PosOpenNow(StringToInteger(num))) GlobalVariableDel(nm);
   }
}

//---------------------------------------------------------------- group 41: news from the MT5 economic calendar
// Live: read from MT5's own calendar (and read again every hour). Strategy Tester: MT5 has no calendar there, so the
// EA reads the file it saved on a live chart (Common\Files\SMC_calendar.csv, times in UTC).
void CalParseCur()
{
   string parts[];
   ArrayResize(g_calCur, 0);
   int n = StringSplit(InCalCur, ',', parts);
   for (int i = 0; i < n; i++)
   {
      string c = parts[i];
      StringTrimLeft(c);
      StringTrimRight(c);
      StringToUpper(c);
      if (StringLen(c) == 0) continue;
      int k = ArraySize(g_calCur);
      ArrayResize(g_calCur, k + 1);
      g_calCur[k] = c;
   }
}
bool CalCurOk(string c) { for (int i = 0; i < ArraySize(g_calCur); i++) if (g_calCur[i] == c) return true; return false; }
bool CalImpOk(int imp)  { return imp == 3 || (InCalImp == CI_HIGHMED && imp == 2); }
bool CalShow()          { return InCalToday != CT_OFF && InStatOn && (!g_tester || g_visual); }   // today's news in the table (display only)
bool CalWanted()        { return InCalOn || (InCalSave && !g_tester) || CalShow(); }
void CalCut(int k)
{
   ArrayResize(g_crT, k); ArrayResize(g_crS, k); ArrayResize(g_crC, k); ArrayResize(g_crI, k); ArrayResize(g_crY, k); ArrayResize(g_crN, k);
   ArrayResize(g_crR, k); ArrayResize(g_crF, k); ArrayResize(g_crA, k);
}
void CalClear() { CalCut(0); }
void CalAdd(long t, long srv, string cur, int imp, int typ, string name, int res, string fc, string ac)
{
   int k = ArraySize(g_crT);
   ArrayResize(g_crT, k + 1, 4096); ArrayResize(g_crS, k + 1, 4096); ArrayResize(g_crC, k + 1, 4096);
   ArrayResize(g_crI, k + 1, 4096); ArrayResize(g_crY, k + 1, 4096); ArrayResize(g_crN, k + 1, 4096);
   ArrayResize(g_crR, k + 1, 4096); ArrayResize(g_crF, k + 1, 4096); ArrayResize(g_crA, k + 1, 4096);
   g_crT[k] = t; g_crS[k] = srv; g_crC[k] = cur; g_crI[k] = imp; g_crY[k] = typ; g_crN[k] = name;
   g_crR[k] = res; g_crF[k] = fc; g_crA[k] = ac;
}
// a calendar number as text, e.g. "0.3%", "254K" ("" = no value)
string CalNum(long raw, int pct, int mult, int dig)
{
   if (raw == LONG_MIN) return "";
   string sf = mult == 1 ? "K" : (mult == 2 ? "M" : (mult == 3 ? "B" : (mult == 4 ? "T" : "")));
   return DoubleToString(raw / 1000000.0, dig) + sf + (pct == 1 ? "%" : "");
}
// one currency from the MT5 calendar, broker times [from, to]: holidays, and news with an exact time of medium / high impact
bool CalReadCur(string cur, datetime from, datetime to)
{
   MqlCalendarValue v[];
   ResetLastError();
   if (!CalendarValueHistory(v, from, to, NULL, cur)) return false;
   ulong  eId[];
   int    eTyp[], eImp[], eExact[], ePct[], eMult[], eDig[];
   string eName[];
   int n = ArraySize(v);
   for (int i = 0; i < n; i++)
   {
      int e = -1;
      for (int j = ArraySize(eId) - 1; j >= 0; j--) if (eId[j] == v[i].event_id) { e = j; break; }
      if (e < 0)
      {
         MqlCalendarEvent ev;
         if (!CalendarEventById(v[i].event_id, ev)) continue;
         e = ArraySize(eId);
         ArrayResize(eId, e + 1, 256); ArrayResize(eTyp, e + 1, 256); ArrayResize(eImp, e + 1, 256); ArrayResize(eExact, e + 1, 256); ArrayResize(eName, e + 1, 256);
         ArrayResize(ePct, e + 1, 256); ArrayResize(eMult, e + 1, 256); ArrayResize(eDig, e + 1, 256);
         eId[e]    = v[i].event_id;
         eTyp[e]   = ev.type == CALENDAR_TYPE_HOLIDAY ? 2 : (ev.type == CALENDAR_TYPE_INDICATOR ? 1 : 0);
         eImp[e]   = ev.importance == CALENDAR_IMPORTANCE_HIGH ? 3 : (ev.importance == CALENDAR_IMPORTANCE_MODERATE ? 2 : (ev.importance == CALENDAR_IMPORTANCE_LOW ? 1 : 0));
         eExact[e] = ev.time_mode == CALENDAR_TIMEMODE_DATETIME ? 1 : 0;
         ePct[e]   = ev.unit == CALENDAR_UNIT_PERCENT ? 1 : 0;
         eMult[e]  = ev.multiplier == CALENDAR_MULTIPLIER_THOUSANDS ? 1 : (ev.multiplier == CALENDAR_MULTIPLIER_MILLIONS ? 2 :
                     (ev.multiplier == CALENDAR_MULTIPLIER_BILLIONS ? 3 : (ev.multiplier == CALENDAR_MULTIPLIER_TRILLIONS ? 4 : 0)));
         eDig[e]   = (int)ev.digits;
         if (eDig[e] > 6) eDig[e] = 6;
         string nm = ev.name;
         StringReplace(nm, ",", ";");
         eName[e]  = nm;
      }
      if (eTyp[e] != 2 && (eImp[e] < 2 || eExact[e] == 0)) continue;
      int res = v[i].impact_type == CALENDAR_IMPACT_POSITIVE ? 1 : (v[i].impact_type == CALENDAR_IMPACT_NEGATIVE ? 2 : 0);
      CalAdd(0, (long)v[i].time, cur, eImp[e], eTyp[e], eName[e], res, CalNum(v[i].forecast_value, ePct[e], eMult[e], eDig[e]), CalNum(v[i].actual_value, ePct[e], eMult[e], eDig[e]));
   }
   return true;
}
// MT5 gives calendar times on the broker clock. For past dates it may use the broker's clock rule (summer / winter)
// or simply the offset of today. US releases at 08:30 New York decide which one gives the right times.
long CalOffNow() { return (long)MathRound((double)(TimeTradeServer() - TimeGMT()) / 900.0) * 900; }
long CalNyMin(long utc) { return MinOfDay(utc + TzOff(utc, -18000, 2)); }
void CalPickClock()
{
   int a = 0, b = 0;
   long off = CalOffNow();
   for (int i = 0; i < ArraySize(g_crS); i++)
   {
      if (g_crC[i] != "USD" || g_crY[i] == 2) continue;
      if (CalNyMin(SrvToUtc((datetime)g_crS[i])) == 510) b++;
      if (CalNyMin(g_crS[i] - off) == 510) a++;
   }
   g_calRule = b >= a;
   g_calHow = g_calRule ? "broker clock rule (group 40)" : (string)"broker offset of today (UTC" + (off >= 0 ? "+" : "") + DoubleToString(off / 3600.0, 1) + ")";
   Print("SMC EA: calendar times -> UTC by the ", g_calHow, " (US releases at 08:30 New York: ", b, " with the clock rule, ", a, " with today's offset)");
}
// broker times -> UTC (news) / day number (holidays: the date as MT5 shows it)
void CalToUtc()
{
   long off = CalOffNow();
   for (int i = 0; i < ArraySize(g_crS); i++)
   {
      if (g_crY[i] == 2) g_crT[i] = FloorDivL(g_crS[i], 86400) * 86400;
      else g_crT[i] = g_calRule ? SrvToUtc((datetime)g_crS[i]) : g_crS[i] - off;
   }
}
// read every chosen currency (and USD, for the clock check) between two broker times
bool CalReadAll(datetime from, datetime to, bool pick)
{
   CalClear();
   bool ok = true;
   for (int i = 0; i < ArraySize(g_calCur); i++) if (!CalReadCur(g_calCur[i], from, to)) ok = false;
   if (!ok) return false;
   if (pick)
   {
      if (!CalCurOk("USD"))
      {   // USD only for the clock check: read it, check, then drop it
         int k0 = ArraySize(g_crT);
         if (CalReadCur("USD", from, to)) CalPickClock();
         else { g_calRule = true; g_calHow = "broker clock rule (group 40)"; }
         CalCut(k0);
      }
      else CalPickClock();
   }
   CalToUtc();
   return true;
}
// the records in time order -> g_crO (indexes)
int CalOrder()
{
   int n = ArraySize(g_crT);
   long key[];
   ArrayResize(key, n);
   for (int i = 0; i < n; i++) key[i] = g_crT[i] * 1048576 + i;
   if (n > 1) ArraySort(key);
   ArrayResize(g_crO, n);
   for (int i = 0; i < n; i++) g_crO[i] = (int)(key[i] % 1048576);
   return n;
}
// the records -> the core (news and holidays of the chosen currencies) and the table
void CalApply()
{
   int n = CalOrder();
   g_calT.Clear();
   g_calHol.Clear();
   ArrayResize(g_cvT, 0); ArrayResize(g_cvN, 0); ArrayResize(g_chD, 0); ArrayResize(g_chN, 0);
   ArrayResize(g_tdT, 0); ArrayResize(g_tdN, 0); ArrayResize(g_tdC, 0); ArrayResize(g_tdF, 0); ArrayResize(g_tdA, 0); ArrayResize(g_tdI, 0); ArrayResize(g_tdR, 0);
   g_cvI = 0;
   g_tdP = 0;
   int tdMin = InCalToday == CT_HIGH ? 3 : 2;
   for (int j = 0; j < n; j++)
   {
      int i = g_crO[j];
      if (!CalCurOk(g_crC[i])) continue;
      if (InCalToday != CT_OFF && g_crY[i] != 2 && g_crI[i] >= tdMin)
      {
         int q = ArraySize(g_tdT);
         ArrayResize(g_tdT, q + 1, 4096); ArrayResize(g_tdN, q + 1, 4096); ArrayResize(g_tdC, q + 1, 4096); ArrayResize(g_tdF, q + 1, 4096);
         ArrayResize(g_tdA, q + 1, 4096); ArrayResize(g_tdI, q + 1, 4096); ArrayResize(g_tdR, q + 1, 4096);
         g_tdT[q] = g_crT[i]; g_tdN[q] = g_crN[i]; g_tdC[q] = g_crC[i]; g_tdF[q] = g_crF[i]; g_tdA[q] = g_crA[i]; g_tdI[q] = g_crI[i]; g_tdR[q] = g_crR[i];
      }
      if (g_crY[i] == 2)
      {
         long dn = FloorDivL(g_crT[i], 86400);
         int k = ArraySize(g_chD);
         if (k > 0 && g_chD[k - 1] == dn) continue;
         ArrayResize(g_chD, k + 1, 256); ArrayResize(g_chN, k + 1, 256);
         g_chD[k] = dn; g_chN[k] = g_crN[i];
         g_calHol.Add((int)dn);
         continue;
      }
      if (!CalImpOk(g_crI[i])) continue;
      int k = ArraySize(g_cvT);
      ArrayResize(g_cvT, k + 1, 4096); ArrayResize(g_cvN, k + 1, 4096);
      g_cvT[k] = g_crT[i];
      g_cvN[k] = g_crN[i] + " (" + g_crC[i] + (g_crI[i] == 3 ? ", high)" : ", medium)");
      if (g_calT.Size() == 0 || (long)g_calT.At(g_calT.Size() - 1) != g_crT[i]) g_calT.Add((double)g_crT[i]);
   }
   CalChanged();
   g_calOk = true;
}
// live: the next five weeks (and the last three days), read again every 10 minutes
void CalLoadLive()
{
   datetime now = TimeTradeServer();
   g_calLoad = now;
   if (!g_calPicked && CalReadAll(now - 366 * 86400, now, true)) g_calPicked = true;
   if (!CalReadAll(now - 3 * 86400, now + 35 * 86400, false))
   {
      Print("SMC EA: the MT5 economic calendar did not answer (error ", GetLastError(), ") - the last list is kept");
      if (!g_calOk) g_calSrc = "NOT AVAILABLE - no calendar news blocks";
      return;
   }
   CalApply();
   MqlDateTime md;
   TimeToStruct(now, md);
   g_calSrc = (string)"MT5 calendar (live), read " + (md.hour < 10 ? "0" : "") + IntegerToString(md.hour) + ":" + (md.min < 10 ? "0" : "") + IntegerToString(md.min) +
              " broker time: " + IntegerToString(ArraySize(g_cvT)) + " news, " + IntegerToString(ArraySize(g_chD)) + " holidays";
}
string CalDate(long utc) { int y = 0, m = 0, d = 0; CivilFromDays(FloorDivL(utc, 86400), y, m, d); return IntegerToString(y) + "." + (m < 10 ? "0" : "") + IntegerToString(m) + "." + (d < 10 ? "0" : "") + IntegerToString(d); }
string CalHm(long utc)   { int mm = MinOfDay(utc); return (mm / 60 < 10 ? "0" : "") + IntegerToString(mm / 60) + ":" + (mm % 60 < 10 ? "0" : "") + IntegerToString(mm % 60); }
// live chart, 'save the calendar' ON: 1 Jan 2020 .. two months ahead -> Common\Files\SMC_calendar.csv
void CalSave()
{
   datetime now = TimeTradeServer();
   g_calSaveTry = now;
   if (!CalReadAll(D'2020.01.01 00:00', now + 60 * 86400, true)) { Print("SMC EA: the MT5 economic calendar did not answer (error ", GetLastError(), ") - nothing saved yet, trying again in a minute"); return; }
   int n = CalOrder();
   int h = FileOpen(CAL_FILE, FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON);
   if (h == INVALID_HANDLE) { Print("SMC EA: cannot write ", CAL_FILE, " (error ", GetLastError(), ")"); return; }
   string cs = "";
   for (int i = 0; i < ArraySize(g_calCur); i++) cs = cs + "," + g_calCur[i];
   long nowU = SrvToUtc(now);
   FileWriteString(h, "# SMC EA - MT5 economic calendar, times in UTC, saved " + CalDate(nowU) + " " + CalHm(nowU) + " UTC. Times converted by the " + g_calHow + "\r\n");
   FileWriteString(h, "#cur" + cs + "\r\n");
   FileWriteString(h, "#saved," + IntegerToString(nowU) + "\r\n");
   FileWriteString(h, "# utc_seconds,utc_time,currency,importance (3 high / 2 medium),type (0 event / 1 indicator / 2 holiday),name,result (1 good / 2 bad for the currency),forecast,actual\r\n");
   int nn = 0, nh = 0;
   for (int j = 0; j < n; j++)
   {
      int i = g_crO[j];
      FileWriteString(h, IntegerToString(g_crT[i]) + "," + CalDate(g_crT[i]) + " " + CalHm(g_crT[i]) + "," + g_crC[i] + "," + IntegerToString(g_crI[i]) + "," +
                         IntegerToString(g_crY[i]) + "," + g_crN[i] + "," + IntegerToString(g_crR[i]) + "," + g_crF[i] + "," + g_crA[i] + "\r\n");
      if (g_crY[i] == 2) nh++; else nn++;
   }
   FileClose(h);
   g_calSaved = true;
   Print("SMC EA: calendar saved - ", nn, " news and ", nh, " holidays (", StringSubstr(cs, 1), ") from 2020.01.01 to ", CalDate(nowU + 60 * 86400),
         " -> Common\\Files\\", CAL_FILE, ". The Strategy Tester can use it now.");
}
// Strategy Tester: the saved file. false = no file, or a chosen currency is not in it
bool CalLoadFile(string &why)
{
   CalClear();
   int h = FileOpen(CAL_FILE, FILE_READ | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ);
   if (h == INVALID_HANDLE) { why = (string)"the calendar file Common\\Files\\" + CAL_FILE + " was not found"; return false; }
   string fc = ",";
   long saved = LNONE;
   while (!FileIsEnding(h))
   {
      string ln = FileReadString(h);
      StringTrimRight(ln);
      if (StringLen(ln) == 0) continue;
      if (StringSubstr(ln, 0, 5) == "#cur,") { fc = StringSubstr(ln, 4) + ","; continue; }
      if (StringSubstr(ln, 0, 7) == "#saved,") { saved = StringToInteger(StringSubstr(ln, 7)); continue; }
      if (StringGetCharacter(ln, 0) == '#') continue;
      string f[];
      int nf = StringSplit(ln, ',', f);
      if (nf < 6) continue;
      CalAdd(StringToInteger(f[0]), 0, f[2], (int)StringToInteger(f[3]), (int)StringToInteger(f[4]), f[5],
             nf >= 9 ? (int)StringToInteger(f[6]) : 0, nf >= 9 ? f[7] : "", nf >= 9 ? f[8] : "");
   }
   FileClose(h);
   for (int i = 0; i < ArraySize(g_calCur); i++)
      if (StringFind(fc, "," + g_calCur[i] + ",") < 0) { why = "the calendar file has no " + g_calCur[i] + " news (it has " + StringSubstr(fc, 1, StringLen(fc) - 2) + ")"; return false; }
   CalApply();
   g_calBeg = D'2020.01.01 00:00';
   g_calEnd = saved == LNONE ? LNONE : saved + 7 * 86400;
   g_calSrc = (string)"file " + CAL_FILE + ": " + IntegerToString(ArraySize(g_cvT)) + " news, " + IntegerToString(ArraySize(g_chD)) + " holidays" +
              (saved == LNONE ? "" : ", saved " + CalDate(saved));
   return true;
}
// at the start. false = the tester cannot run these settings (no file)
bool CalInit(string &why)
{
   why = "";
   g_calOk = false;
   g_calSrc = "";
   g_calWarned = false;
   g_calPicked = false;
   g_calSaved = false;
   g_calEnd = LNONE;
   g_calBeg = LNONE;
   g_calT.Clear();
   g_calHol.Clear();
   ArrayResize(g_cvT, 0); ArrayResize(g_cvN, 0); ArrayResize(g_chD, 0); ArrayResize(g_chN, 0);
   g_cvI = 0;
   CalChanged();
   if (!CalWanted()) return true;
   if (g_tester)
   {
      if (InCalSave) Print("SMC EA: 'save the calendar' works on a live chart only (the Strategy Tester has no MT5 calendar)");
      if (!InCalOn)
      {   // only for the table's "today" rows: no file = no rows, the test still runs
         string w2 = "";
         if (CalShow() && !CalLoadFile(w2)) g_calSrc = w2;
         return true;
      }
      if (!CalLoadFile(why)) return false;
      Print("SMC EA: calendar news from the ", g_calSrc);
      return true;
   }
   if (InCalSave) CalSave();
   if (!InCalOn && !CalShow()) return true;
   // live: which clock MT5 uses for calendar times (from the last year of US releases), then the next five weeks
   g_calRule = true;
   g_calHow = "broker clock rule (group 40)";
   CalLoadLive();
   if (!g_calOk && InCalOn) Alert("SMC EA: 'Economic calendar news' is ON but the MT5 calendar is not available - trading WITHOUT calendar news blocks until it answers");
   return true;
}
// a news of the table's list came out in the last 30 minutes and its actual number is not in yet
bool CalAwait()
{
   long now = SrvToUtc(TimeCurrent());
   for (int i = ArraySize(g_tdT) - 1; i >= 0 && g_tdT[i] > now - 1800; i--) if (g_tdT[i] <= now && g_tdA[i] == "") return true;
   return false;
}
// live: read again every 10 minutes (every minute while it does not answer, or while a result is awaited).
// Tester: warn once if the test runs past the file
void CalTick()
{
   if (!g_tester)
   {
      datetime now = TimeTradeServer();
      if (InCalSave && !g_calSaved && now - g_calSaveTry >= 60) CalSave();
      if ((InCalOn || CalShow()) && now - g_calLoad >= (!g_calOk || (CalShow() && CalAwait()) ? 60 : 600)) CalLoadLive();
      return;
   }
   if (!InCalOn) return;
   if (g_calWarned || g_calEnd == LNONE) return;
   long t = SrvToUtc(TimeCurrent());
   if (t > g_calEnd || t < g_calBeg)
   {
      g_calWarned = true;
      Print("SMC EA WARNING: this test runs outside the dates of the calendar file (2020.01.01 .. ", CalDate(g_calEnd), ") - no calendar news there. Save the file again on a live chart.");
   }
}

//---------------------------------------------------------------- start: build the structure on history, then trade
bool TryInit()
{
   if (g_badInit) return false;
   datetime t0 = iTime(g_sym, g_tf, 0);
   if (t0 == 0) return false;
   if (!g_tester && !SeriesInfoInteger(g_sym, g_tf, SERIES_SYNCHRONIZED)) return false;
   if (g_htfUse && !g_tester && !SeriesInfoInteger(g_sym, g_htf, SERIES_SYNCHRONIZED)) { iTime(g_sym, g_htf, 0); return false; }
   MqlRates rr[];
   int n = CopyRates(g_sym, g_tf, 1, InWarm, rr);
   if (n <= 10) return false;
   S.uv = UnitValue();
   CoreSetup();
   for (int k = 0; k < 2; k++) g_note[k] = "";
   ArrayResize(g_bt, 0);
   g_btBase = 0;
   ArrayResize(g_done, 0);
   ArrayResize(g_doneT, 0);
   g_dealFlag = true;
   ArrayResize(g_hbt, 0);
   g_hbBase = 0;
   g_htfEvSrv = 0;
   g_cntCho = 0; g_cntBos = 0; g_exTgt = 0; g_exStop = 0; g_exMv = 0; g_exOpp = 0; g_exFlat = 0; g_exNews = 0; g_exOther = 0;
   g_closedN = 0; g_refused = 0; g_costPaid = 0; g_lastRisk = NAD; g_lastLots = NAD; g_lastCost = NAD;
   g_startT = TimeCurrent();
   g_slowMin = -1;
   ArrayResize(g_gapPos, 0);
   ArrayResize(g_clsTk, 0);
   ArrayResize(g_clsWhy, 0);
   ArrayResize(g_stpTk, 0);
   ArrayResize(g_stpSl, 0);
   ArrayResize(g_stpDir, 0);
   for (int i = 0; i < 4; i++) { g_vb[i].on = false; g_vb[i].ticket = 0; g_vb[i].fails = 0; g_vb[i].seq = 0; g_vb[i].dir = 0; }
   // "when the EA first started" for the loss recovery
   long liveT = LNONE;
   if (InSeqFrom == SF_LIVE)
   {
      if (g_tester) liveT = SrvToUtc(TimeCurrent());
      else
      {
         string nm = g_P + "live";
         if (!GlobalVariableCheck(nm)) GlobalVariableSet(nm, (double)TimeCurrent());
         liveT = SrvToUtc((datetime)GlobalVariableGet(nm));
      }
   }
   for (int k = 0; k < 2; k++) g_money[k].liveT = liveT;
   // higher timeframe: the candles before the first chart bar
   g_htfFed = 0;
   if (g_htfUse)
   {
      datetime hc0 = HtfOpenOf(rr[0].time);
      if (hc0 == 0) return false;
      MqlRates hr[];
      int m = CopyRates(g_sym, g_htf, hc0 - 1, 3000, hr);   // -1 = no candle before the first chart bar
      for (int i = 0; i < m; i++) if (hr[i].time < hc0) HtfStep(hr[i]);
      if (g_htfFed == 0) g_htfFed = hc0 - 1;
   }
   // a waiting setup saved before a restart a few bars ago?
   int resume = -1;
   if (!g_tester && GlobalVariableCheck(g_P + "T") && (int)GvGet(g_P + "mode", -1) == InDirMode * 10 + InExec && (int)GvGet(g_P + "cs", -1) == g_cs)
   {
      datetime st = (datetime)GvGet(g_P + "T", 0);
      for (int i = n - 1; i >= 0 && i >= n - 1 - InResume; i--) if (rr[i].time == st) { resume = i; break; }
   }
   int lastDry = resume >= 0 ? resume : n - 1;
   for (int i = 0; i <= lastDry; i++) ProcessBar(rr[i], true, i + 1 < n ? rr[i + 1].time : t0);
   datetime tLimit = lastDry + 1 < n ? rr[lastDry + 1].time : t0;
   ReplayMoney(tLimit);
   if (resume >= 0)
   {
      RestoreSides();
      for (int i = 0; i < 4; i++)   // a pending order the book no longer wants
         if (InExec == EX_PEND && g_vb[i].ticket != 0 && !g_vb[i].on && OurOrder((ulong)g_vb[i].ticket)) g_trade.OrderDelete((ulong)g_vb[i].ticket);
      Print("SMC EA: resumed after a restart (", n - 1 - resume, " bar(s) missed)");
   }
   else
   {
      int del = 0;
      for (int i = OrdersTotal() - 1; i >= 0; i--) { ulong tk = OrderGetTicket(i); if (tk != 0 && OurOrder(tk)) { g_trade.OrderDelete(tk); del++; } }
      if (del > 0) Print("SMC EA: ", del, " old pending order(s) of this EA deleted - the EA waits for the next signal");
      if (!g_tester) for (int k = 0; k < g_nSides; k++) g_side[k].seq = (int)GvGet(GvSide(k, "seq"), 0);
   }
   RebuildTrk();
   CleanGv();
   CatchUp(rr, lastDry + 1, n, t0, false);   // v12.3: the candles missed while the EA was off - read without opening trades
   g_dry = false;
   if (!g_tester || g_visual) DrawAll(rr[n - 1].time);
   g_lastBar = rr[n - 1].time;
   g_curOpen = t0;
   g_ready = true;
   SaveState(g_lastBar);
   Panel();
   Print("SMC EA v12.3 ready: ", n, " bars of history, structure ", EN.trendDir == 1 ? "UP" : (EN.trendDir == -1 ? "DOWN" : "not set yet"),
         ", higher timeframe ", g_htfUse ? TfName(g_htf) : "not used", ", mode ", EnumToString(InDirMode), ", entries ", InExec == EX_TOUCH ? "touch (like TradingView)" : "pending orders");
   return true;
}

//---------------------------------------------------------------- chart drawing
void DrawLine(string nm, datetime t1, double p, datetime t2, color c, int style, int width, bool ray)
{
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_TREND, 0, t1, p, t2, p);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);
   }
   else
   {
      ObjectMove(0, nm, 0, t1, p);
      ObjectMove(0, nm, 1, t2, p);
   }
   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   ObjectSetInteger(0, nm, OBJPROP_STYLE, style);
   ObjectSetInteger(0, nm, OBJPROP_WIDTH, width);
   ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, ray);
}
void DrawText(string nm, datetime t, double p, string txt, color c, int anchor)
{
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_TEXT, 0, t, p);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
   }
   else ObjectMove(0, nm, 0, t, p);
   ObjectSetString(0, nm, OBJPROP_TEXT, txt);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 8);
   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anchor);
}
void DrawBar(MqlRates &r)
{
   datetime tNow = r.time;
   if (EN.brkX != NAI)
   {
      bool up = EN.evBU || EN.evCU;
      bool cho = EN.evCU || EN.evCD;
      string nm = g_P + "m" + IntegerToString(g_mark);
      color c = up ? clrTeal : clrCrimson;
      DrawLine(nm, TimeOfBar(EN.brkX), EN.brkP, tNow, c, cho ? STYLE_SOLID : STYLE_DASH, 1, false);
      DrawText(nm + "t", tNow, EN.brkP, cho ? "CHOCH" : "BOS", c, up ? ANCHOR_RIGHT_LOWER : ANCHOR_RIGHT_UPPER);
      if (g_mark >= InDrawMax) { string old = g_P + "m" + IntegerToString(g_mark - InDrawMax); ObjectDelete(0, old); ObjectDelete(0, old + "t"); }
      g_mark++;
   }
}
void DelObj(string nm) { ObjectDelete(0, nm); ObjectDelete(0, nm + "t"); }
// a higher-timeframe CHOCH / BOS that just happened: the broken level, from where it started to the candle that broke it
void DrawHtfMark(datetime tEnd)
{
   if (InHtfMarks <= 0) return;
   string nm = g_P + "H" + IntegerToString(g_hmark);
   DrawLine(nm, TimeOfHtf(HT.brkB), HT.brkP, tEnd, clrMediumPurple, STYLE_SOLID, 2, false);
   DrawText(nm + "t", tEnd, HT.brkP, TfName(g_htf) + (HT.brkCho ? " CHOCH" : " BOS"), clrMediumPurple, HT.brkUp ? ANCHOR_RIGHT_LOWER : ANCHOR_RIGHT_UPPER);
   if (g_hmark >= InHtfMarks) DelObj(g_P + "H" + IntegerToString(g_hmark - InHtfMarks));
   g_hmark++;
}
// the higher timeframe now: its BOS* / CHOCH* levels and its equilibrium (the state after its last CLOSED candle)
void DrawHtfLive(datetime tNow)
{
   string a = g_P + "Hc", b = g_P + "Hf", e = g_P + "He", tf = TfName(g_htf);
   if (!HtfDrawOn()) { DelObj(a); DelObj(b); DelObj(e); return; }
   if (!IsNa(HT.tCeil))
   {
      DrawLine(a, TimeOfHtf(HT.tCeilB), HT.tCeil, tNow, clrMediumPurple, STYLE_SOLID, 2, true);
      DrawText(a + "t", tNow, HT.tCeil, tf + (HT.tTrend == 1 ? " BOS*" : (HT.tTrend == -1 ? " CHOCH*" : " high*")), clrMediumPurple, ANCHOR_RIGHT_LOWER);
   }
   else DelObj(a);
   if (!IsNa(HT.tFlor))
   {
      DrawLine(b, TimeOfHtf(HT.tFlorB), HT.tFlor, tNow, clrMediumPurple, STYLE_SOLID, 2, true);
      DrawText(b + "t", tNow, HT.tFlor, tf + (HT.tTrend == -1 ? " BOS*" : (HT.tTrend == 1 ? " CHOCH*" : " low*")), clrMediumPurple, ANCHOR_RIGHT_UPPER);
   }
   else DelObj(b);
   double eq = RetLvl(HT.tTrend, HT.outX, HT.outO, S.eqPct);
   if (!IsNa(eq))
   {
      datetime t1 = g_htfEvSrv > 0 && g_htfEvSrv < tNow ? g_htfEvSrv : tNow - 60 * g_cs;
      DrawLine(e, t1, eq, tNow, clrMediumPurple, STYLE_DOT, 1, true);
      DrawText(e + "t", tNow, eq, tf + " EQ " + DoubleToString(S.eqPct, 1) + "%", clrMediumPurple, ANCHOR_RIGHT_LOWER);
   }
   else DelObj(e);
}
// everything that follows the price, redrawn at every candle close (each part has its own switch)
void DrawAll(datetime tNow)
{
   DrawHtfLive(tNow);
   string a = g_P + "cel", b = g_P + "flr";
   if (!InDraw) { DelObj(a); DelObj(b); }
   else if (EN.cel.ok)
   {
      DrawLine(a, TimeOfBar(EN.cel.x1), EN.cel.price, tNow, clrCrimson, STYLE_DOT, 1, true);
      DrawText(a + "t", TimeOfBar(EN.cel.x1), EN.cel.price, EN.trendDir == 1 ? "BOS*" : (EN.trendDir == -1 ? "CHOCH*" : "high*"), clrCrimson, ANCHOR_LEFT_LOWER);
   }
   else DelObj(a);
   if (InDraw && EN.flr.ok)
   {
      DrawLine(b, TimeOfBar(EN.flr.x1), EN.flr.price, tNow, clrTeal, STYLE_DOT, 1, true);
      DrawText(b + "t", TimeOfBar(EN.flr.x1), EN.flr.price, EN.trendDir == -1 ? "BOS*" : (EN.trendDir == 1 ? "CHOCH*" : "low*"), clrTeal, ANCHOR_LEFT_UPPER);
   }
   else if (InDraw) DelObj(b);
   for (int k = 0; k < 2; k++)
   {
      string e = g_P + "e" + IntegerToString(k), s = g_P + "s" + IntegerToString(k), t = g_P + "t" + IntegerToString(k);
      if (InShow && k < g_nSides && g_side[k].dir != 0 && !IsNa(g_side[k].ent))
      {
         datetime t2 = tNow + 10 * g_cs;
         DrawLine(e, tNow, g_side[k].ent, t2, clrOrange, STYLE_SOLID, 2, false);
         DrawLine(s, tNow, g_side[k].sl, t2, clrRed, STYLE_SOLID, 2, false);
         if (!IsNa(g_side[k].tgt)) DrawLine(t, tNow, g_side[k].tgt, t2, clrDodgerBlue, STYLE_SOLID, 2, false);
      }
      else { ObjectDelete(0, e); ObjectDelete(0, s); ObjectDelete(0, t); }
   }
}

//---------------------------------------------------------------- the counter table (like TradingView)
string Px(double p) { return IsNa(p) ? "-" : DoubleToString(p, g_digits); }
string Mo(double v) { return DoubleToString(v, 2); }
string I2(int v)    { return IntegerToString(v); }
string Two(int v)   { return (v < 10 ? "0" : "") + IntegerToString(v); }
string MonName(int m)
{
   string n = "JanFebMarAprMayJunJulAugSepOctNovDec";
   return (m >= 1 && m <= 12) ? StringSubstr(n, (m - 1) * 3, 3) : "?";
}
string DayName(int w)   // 1 = Sunday ... 7 = Saturday
{
   string n = "SunMonTueWedThuFriSat";
   return (w >= 1 && w <= 7) ? StringSubstr(n, (w - 1) * 3, 3) : "?";
}
// an instant (UTC) on the session clock, e.g. "Fri 07 Nov 19:00"
string SessTime(long utc, bool withDay)
{
   long loc = SessLoc(utc);
   long dn  = FloorDivL(loc, 86400);
   int y = 0, m = 0, d = 0;
   CivilFromDays(dn, y, m, d);
   int mm = MinOfDay(loc);
   string t = Two(d) + " " + MonName(m) + " " + Two(mm / 60) + ":" + Two(mm % 60);
   return withDay ? DayName(DowDays(dn)) + " " + t : t;
}
void Row(string l, string v, color c)
{
   if (g_rN >= ArraySize(g_rL)) { ArrayResize(g_rL, g_rN + 16); ArrayResize(g_rV, g_rN + 16); ArrayResize(g_rC, g_rN + 16); }
   g_rL[g_rN] = l == "" ? " " : l;
   g_rV[g_rN] = v == "" ? "-" : v;
   g_rC[g_rN] = c;
   g_rN++;
}
int SideCnt(int k, int what)
{
   if (what == 0) return g_side[k].cntArm;
   if (what == 1) return g_side[k].cntFill;
   if (what == 2) return g_side[k].cntCanc;
   if (what == 3) return g_side[k].cntSkip;
   if (what == 4) return g_side[k].cntR1;
   if (what == 5) return g_side[k].cntR2;
   if (what == 6) return g_side[k].cntDir;
   if (what == 7) return g_side[k].cntHf;
   if (what == 8) return g_side[k].cntPd;
   if (what == 9) return g_side[k].cntBosCnl;
   if (what == 10) return g_side[k].cntExp;
   if (what == 11) return g_side[k].cntCap;
   if (what == 13) return g_side[k].cntR3;
   if (what == 14) return g_side[k].cntR3Far;
   if (what == 15) return g_side[k].cntR3Fb;
   return g_side[k].cntMoves;
}
int    CntSum(int what) { int t = 0; for (int k = 0; k < g_nSides; k++) t += SideCnt(k, what); return t; }
string CntTxt(int what)
{
   if (g_nSides == 1) return I2(SideCnt(0, what));
   return I2(SideCnt(0, what) + SideCnt(1, what)) + "  (L " + I2(SideCnt(0, what)) + " / S " + I2(SideCnt(1, what)) + ")";
}
int    MoneyN() { return (S.dirMode == 3 && S.hedgeMoney == 0) ? 2 : 1; }
string MonTxt(string a, string b) { return MoneyN() == 2 ? "L " + a + "  |  S " + b : a; }
string SideName(int k, string what, string single) { return S.dirMode == 3 ? (k == 0 ? "LONG side - " : "SHORT side - ") + what : single; }
string StructTxt()
{
   string t = EN.trendDir == 1 ? "UP" : (EN.trendDir == -1 ? "DOWN" : "not set yet");
   string hi = EN.trendDir == 1 ? "BOS* " : (EN.trendDir == -1 ? "CHOCH* " : "high* ");
   string lo = EN.trendDir == -1 ? "BOS* " : (EN.trendDir == 1 ? "CHOCH* " : "low* ");
   return t + "  |  " + hi + (EN.cel.ok ? Px(EN.cel.price) : "-") + "  |  " + lo + (EN.flr.ok ? Px(EN.flr.price) : "-");
}
string HtfNowTxt()
{
   if (!g_htfUse) return "not above the chart";
   string t = HT.tTrend == 1 ? "UP" : (HT.tTrend == -1 ? "DOWN" : "not set yet");
   if (HT.tTrend != 0 && g_htfEvSrv > 0) t = t + " since " + SessTime(SrvToUtc(g_htfEvSrv), false);
   t = t + "  |  leg " + Px(HT.outO) + " -> " + Px(HT.outX);
   if (!S.u15) t = t + "  |  not used by these settings";
   return t;
}
string WaitTxt(int k)
{
   if (g_side[k].dir == 0) return "none";
   if (IsNa(g_side[k].ent)) return g_side[k].Id() + " armed - no entry level yet";
   return g_side[k].Id() + " R" + I2(g_side[k].rule) + "  entry " + Px(g_side[k].ent) + "  stop " + Px(g_side[k].sl) + "  target " + Px(g_side[k].tgt);
}
string BlockTxt()
{
   string a = g_side[0].Blocked();
   if (g_nSides == 1 || S.hedgeMoney == 1) return a == "" ? "no" : a;
   string b = g_side[1].Blocked();
   if (a == "" && b == "") return "no";
   return "L " + (a == "" ? "no" : a) + "  |  S " + (b == "" ? "no" : b);
}
bool AnyBlocked() { for (int k = 0; k < g_nSides; k++) if (g_side[k].Blocked() != "") return true; return false; }
string OpenTxt()
{
   int n = 0;
   double pl = 0;
   for (int i = 0; i < PositionsTotal(); i++)
   {
      ulong tk = PositionGetTicket(i);
      if (tk == 0 || PositionGetString(POSITION_SYMBOL) != g_sym || PositionGetInteger(POSITION_MAGIC) != InMagic) continue;
      n++;
      pl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   }
   return n == 0 ? "none" : I2(n) + " open  |  " + (pl >= 0 ? "+" : "") + Mo(pl);
}
string RecoveryTxt()
{
   if (S.seqMode == 0) return "off";
   if (S.flMode == 1) return "not used - the account floor sizes every trade";
   string m = S.seqMode == 1 ? "A - loss since the high + " + Mo(S.seqAdd) : (S.seqMode == 2 ? "B - 2 x loss since the high" : (S.seqMode == 3 ? "C - loss since the high" :
              (S.seqMode == 4 ? "A+ - total below 0 + " + Mo(S.seqAdd) : (S.seqMode == 5 ? "B+ - 2 x total below 0" : (S.seqMode == 6 ? "C+ - total below 0" :
              (S.seqMode == 7 ? "A split - loss since the high + " + Mo(S.seqAdd) + ", base from the profit steps" : (S.seqMode == 8 ? "B split - 2 x loss since the high, base from the profit steps" :
              "C split - loss since the high, base from the profit steps")))))));
   if (S.split > 1.0) m = m + "  |  split over " + DoubleToString(S.split, 1) + " trades";
   if (S.lmOn) m = m + "  |  back to the base at " + Mo(S.lmAmt) + " carried";
   if (S.seqFrom == 0) m = m + "  |  whole history";
   else if (S.seqFrom == 2) m = m + "  |  from " + SessTime(S.seqFromT, false);
   else m = m + (g_money[0].liveT == LNONE ? "  |  from live" : "  |  from live " + SessTime(g_money[0].liveT, false));
   if (MoneyN() == 1 && S.dirMode == 3) m = m + "  |  SHARED by both sides";
   return m;
}
string CmTxt()
{
   if (S.cmMode == 0) return "off";
   if (S.cmMode == 3) return DoubleToString(S.cmPct, 3) + "% x2";
   if (S.cmMode == 4) return Mo(S.cmFix) + " per order x2";
   return Mo(S.cmLot) + " per lot x2  (1 lot = " + DoubleToString(S.cmLots, 0) + " units)";
}
string NewsDatesTxt()
{
   if (!S.newsOn) return "MASTER SWITCH OFF - no news blocks";
   if (!(S.nw1On || S.nw2On || S.nw3On)) return "off (no window on)";
   if (!S.ndOn) return "every day";
   string t = NdText();
   if (t == "") return "NO VALID DATE";
   return t + (S.ndScope == 0 ? "  (this month)" : "  (every month)");
}
// the slow rows (next US release, US clock, next US holiday) are worked out once a minute
string NextNewsCalc();
string UsClockCalc();
string UsHolCalc();
string CalNextCalc();
string CalHolCalc();
void   SlowRows()
{
   long key = SrvToUtc(TimeCurrent()) / 60;
   if (key == g_slowMin) return;
   g_slowMin  = key;
   g_newsTxt  = NextNewsCalc();
   g_clockTxt = UsClockCalc();
   g_holTxt   = UsHolCalc();
   g_calTxt   = CalNextCalc();
   g_calHolTxt = CalHolCalc();
}
string NextNewsTxt() { SlowRows(); return g_newsTxt; }
string UsClockTxt()  { SlowRows(); return g_clockTxt; }
string UsHolTxt()    { SlowRows(); return g_holTxt; }
string CalNextTxt()  { SlowRows(); return g_calTxt; }
string CalHolTxt()   { SlowRows(); return g_calHolTxt; }
// e.g. "2h 05m", "3d 4h"
string Dur(long sec)
{
   if (sec < 0) sec = 0;
   long m = sec / 60;
   if (m < 60) return IntegerToString(m) + "m";
   if (m < 1440) return IntegerToString(m / 60) + "h " + Two((int)(m % 60)) + "m";
   return IntegerToString(m / 1440) + "d " + IntegerToString((m % 1440) / 60) + "h";
}
// group 41: the next calendar news (or the window now)
string CalNextCalc()
{
   if (!S.calOn) return "off";
   if (!S.newsOn) return "master OFF";
   if (!S.intra) return "off on daily charts and above";
   if (!g_calOk) return g_calSrc == "" ? "no list" : g_calSrc;
   long now  = SrvToUtc(TimeCurrent());
   long post = (long)S.calPost * 60;
   int  n    = ArraySize(g_cvT);
   while (g_cvI < n && g_cvT[g_cvI] + post <= now) g_cvI++;
   if (g_cvI >= n) return "none ahead in the list";
   int more = 0;
   for (int j = g_cvI + 1; j < n && g_cvT[j] == g_cvT[g_cvI]; j++) more++;
   string t = g_cvN[g_cvI] + (more > 0 ? " +" + I2(more) + " more" : "") + "  " + SessTime(g_cvT[g_cvI], true);
   if (now >= g_cvT[g_cvI] - (long)S.calPre * 60) return "WINDOW NOW - " + t;
   return t + "  (in " + Dur(g_cvT[g_cvI] - now) + ")";
}
// group 41: the next calendar holiday of the chosen currencies
string CalHolCalc()
{
   if (!S.calOn) return "off";
   if (!S.calHol) return "not used (switched off)";
   if (S.holTrade) return "not used ('Trade on US market holidays' is ON)";
   if (!g_calOk) return "no list";
   long dn = FloorDivL(NyLoc(SrvToUtc(TimeCurrent())), 86400);
   for (int i = 0; i < ArraySize(g_chD); i++)
      if (g_chD[i] >= dn)
      {
         int y = 0, m = 0, d = 0;
         CivilFromDays(g_chD[i], y, m, d);
         return (g_chD[i] == dn ? "TODAY - NO trading - " : "next ") + g_chN[i] + " " + Two(d) + " " + MonName(m);
      }
   return "none ahead in the list";
}
// group 41: today's news (session clock day), with impact, forecast / actual and the result
void TodayRows(bool full)
{
   long now = SrvToUtc(TimeCurrent());
   long loc = SessLoc(now);
   long d0  = now - ((loc % 86400) + 86400) % 86400;   // today 00:00 on the session clock
   long d1  = d0 + 86400;
   long dn  = FloorDivL(loc, 86400);
   int y = 0, m = 0, d = 0;
   CivilFromDays(dn, y, m, d);
   bool blocks = S.calOn && S.newsOn && S.intra;
   string hv = !g_calOk ? (g_calSrc == "" ? "no list" : g_calSrc) :
               (blocks ? (InCalImp == CI_HIGH ? "HIGH news block trading" : "HIGH + MEDIUM news block trading") : "for information - calendar windows OFF");
   Row("TODAY'S NEWS  " + DayName(DowDays(dn)) + " " + Two(d) + " " + MonName(m), hv, g_calOk ? clrWhite : clrGray);
   if (!g_calOk) return;
   long nd = FloorDivL(NyLoc(now), 86400);
   for (int i = 0; i < ArraySize(g_chD); i++)
      if (g_chD[i] == nd) { Row("  all day  HOLIDAY", g_chN[i] + (blocks && S.calHol && !S.holTrade ? "  - NO trading" : ""), clrRed); break; }
   int n = ArraySize(g_tdT);
   while (g_tdP < n && g_tdT[g_tdP] < d0) g_tdP++;
   int shown = 0, more = 0, maxN = full ? 14 : 6;
   for (int i = g_tdP; i < n && g_tdT[i] < d1; i++)
   {
      long t = g_tdT[i];
      if (!full && t + 3600 < now) continue;   // Short table: the last hour and what is still to come
      if (shown >= maxN) { more++; continue; }
      int  mm = MinOfDay(SessLoc(t));
      bool inWin = blocks && CalImpOk(g_tdI[i]) && now >= t - (long)S.calPre * 60 && now < t + (long)S.calPost * 60;
      string st;
      if (now < t) st = "in " + Dur(t - now) + (g_tdF[i] != "" ? "  F " + g_tdF[i] : "");
      else st = (g_tdA[i] != "" ? "A " + g_tdA[i] + (g_tdF[i] != "" ? " / F " + g_tdF[i] : "") : "out") +
                (g_tdR[i] == 1 ? "  good for " + g_tdC[i] : (g_tdR[i] == 2 ? "  bad for " + g_tdC[i] : ""));
      if (inWin) st = "WINDOW NOW  " + st;
      Row("  " + Two(mm / 60) + ":" + Two(mm % 60) + "  " + (g_tdI[i] == 3 ? "HIGH" : "MEDIUM"), g_tdN[i] + " (" + g_tdC[i] + ")  " + st,
          inWin ? clrRed : (now >= t ? clrGray : (g_tdI[i] == 3 ? clrRed : clrOrange)));
      shown++;
   }
   if (shown == 0 && more == 0) Row("  -", (string)"no " + (InCalToday == CT_HIGH ? "high" : "high / medium") + " news " + (full ? "today" : "left today"), clrGray);
   if (more > 0) Row("  ...", "+" + I2(more) + " more today", clrGray);
}
// group 41: no new trades before news
string PreTxt()
{
   if (!S.preOn) return "off";
   if (!S.newsOn) return "master OFF";
   if (!S.intra) return "off on daily charts and above";
   if (!S.calOn && !S.auOn) return "ON but no news list on (group 41 calendar / group 29)";
   string h = DoubleToString(InPreHrs, 2);
   while (StringLen(h) > 1 && StringSubstr(h, StringLen(h) - 1) == "0") h = StringSubstr(h, 0, StringLen(h) - 1);
   if (StringSubstr(h, StringLen(h) - 1) == ".") h = StringSubstr(h, 0, StringLen(h) - 1);
   string src = S.calOn && S.auOn ? "calendar + US auto" : (S.calOn ? "calendar" : "US auto");
   return (g_preNow ? "NOW - no new trades  |  " : "") + h + " h before " + src + " news";
}
// the next enabled US release (group 29), up to 40 days ahead
string NextNewsCalc()
{
   if (!S.newsOn) return "master OFF";
   if (!S.auOn) return "off";
   long now = SrvToUtc(TimeCurrent());
   int y = 0, m = 0, d = 0;
   CivilFromDays(FloorDivL(NyLoc(now), 86400), y, m, d);
   for (int k = 0; k <= 40; k++)
   {
      int ky = 0, km = 0, kd = 0;
      UAddD(y, m, d, k, ky, km, kd);
      long t1 = LNONE, t2 = LNONE, t3 = LNONE, t4 = LNONE;
      UAuDay(ky, km, kd, t1, t2, t3, t4);
      long bt = LNONE;
      string bn = "";
      long post = (long)S.auPost * 60;
      if (t1 != LNONE && t1 + post > now && (bt == LNONE || t1 < bt)) { bt = t1; bn = "NFP"; }
      if (t2 != LNONE && t2 + post > now && (bt == LNONE || t2 < bt)) { bt = t2; bn = "Jobless claims"; }
      if (t3 != LNONE && t3 + post > now && (bt == LNONE || t3 < bt)) { bt = t3; bn = "ISM Manufacturing"; }
      if (t4 != LNONE && t4 + post > now && (bt == LNONE || t4 < bt)) { bt = t4; bn = "ISM Services"; }
      if (bt != LNONE) return bn + "  " + SessTime(bt, true);
   }
   return "none in the next 40 days";
}
string UsClockCalc()
{
   long now = SrvToUtc(TimeCurrent());
   int y = 0, m = 0, d = 0;
   CivilFromDays(FloorDivL(NyLoc(now), 86400), y, m, d);
   bool sum = NyOff(now) == -14400;
   long t830 = NyInstant(y, m, d, 8, 30);
   int mm = MinOfDay(SessLoc(t830));
   return (string)(sum ? "summer EDT" : "winter EST") + (S.usClk == 0 ? " (auto)" : " (forced)") + "  08:30 NY = " + Two(mm / 60) + ":" + Two(mm % 60);
}
string UsHolCalc()
{
   long now = SrvToUtc(TimeCurrent());
   int y = 0, m = 0, d = 0;
   CivilFromDays(FloorDivL(NyLoc(now), 86400), y, m, d);
   string h = "";
   for (int k = 0; k <= 370 && h == ""; k++)
   {
      int ky = 0, km = 0, kd = 0;
      UAddD(y, m, d, k, ky, km, kd);
      int hk = UsHol(ky, km, kd, true);
      if (hk != 0) h = (k == 0 ? "TODAY " : "next ") + UsHolName(hk) + " " + Two(kd) + " " + MonName(km);
   }
   return (string)(S.holTrade || !S.newsOn ? "trading normally - " : "NO trading - ") + h;
}
string FloorTxt(int mi)
{
   string t = g_money[mi].flCush <= 0.005 ? "AT THE FLOOR - no risk left  |  " : "";
   return t + "P&L " + Mo(g_money[mi].flPnl) + "  |  floor " + Mo(g_money[mi].flFloor) + "  |  cushion " + Mo(g_money[mi].flCush) + "  |  risk " + Mo(g_money[mi].flRisk);
}
string PauseTxt(int mi)
{
   string t = g_money[mi].LdHalt(g_t) ? "PAUSED until " + SessTime(g_money[mi].ldUntil, true) : I2(g_money[mi].ldRun) + " of " + I2(S.ldN) + " losses in a row";
   return t + "  |  pauses so far " + I2(g_money[mi].cntLd);
}
string EqTxt()
{
   string tf = TfName(g_htf);
   if (S.autoM)
   {
      if (!S.htfOk) return "auto mode - higher timeframe not above the chart - no trades";
      if (g_autoDir == 0) return "AUTO - no higher timeframe leg yet";
      string sd = g_autoDir == 1 ? "longs" : "shorts";
      return g_eqOpen ? "AUTO part 2 - WITH the " + tf + " (" + sd + ")  |  equilibrium " + Px(g_eqLvl) + " touched"
                      : "AUTO part 1 - AGAINST the " + tf + " (" + sd + ")  |  waiting for " + Px(g_eqLvl);
   }
   if (!S.eqOn) return "off";
   if (!S.htfOk) return "higher timeframe not above the chart";
   return g_eqOpen ? "OPEN - equilibrium touched (" + Px(g_eqLvl) + ")" : "WAITING for the equilibrium " + Px(g_eqLvl);
}
// a number without trailing zeros, e.g. 0.1, 0.0001, 10
string Num(double v)
{
   string t = DoubleToString(v, 8);
   while (StringLen(t) > 1 && StringSubstr(t, StringLen(t) - 1) == "0") t = StringSubstr(t, 0, StringLen(t) - 1);
   if (StringSubstr(t, StringLen(t) - 1) == ".") t = StringSubstr(t, 0, StringLen(t) - 1);
   return t;
}
// v12.2: group 43 - the profit and the base risk of Rule A / B / C split
string SpTxt()
{
   if (S.seqMode < 7) return "off";
   return MonTxt("profit " + Mo(g_money[0].flPnl) + "  ->  base " + Mo(g_money[0].basNow), "profit " + Mo(g_money[1].flPnl) + "  ->  base " + Mo(g_money[1].basNow));
}
// v12.1: the hard cap row, and group 42 (the loss mark)
string CapTxt() { return S.capAct == 3 ? " x back to the base" : ""; }
string LmTxt()
{
   if (!S.lmOn) return "off";
   if (S.seqMode == 0) return "on - but loss recovery is Off";
   return "at " + Mo(S.lmAmt) + ":  " + MonTxt(I2(g_money[0].cntLm) + " x back to the base", I2(g_money[1].cntLm) + " x back to the base");
}
// v12.0: rule 3 - entries at the close of the signal candle (group 39)
string R3Txt()
{
   if (!S.r3On) return "off - rules 1 / 2";
   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");
   string t = "on  -  " + CntTxt(13) + " entered at the close";
   if (S.r3BrkOn) t = t + "  |  close within " + Num(S.r3Brk) + u + " of the break: " + CntTxt(14) + " skipped" + (S.r3Fb ? ", " + CntTxt(15) + " fell back to rule 1 / 2" : "");
   return t;
}
// v11.2: the stop buffer in use, in price
string BufTxt()
{
   string u = S.buMode == 1 ? " pips" : (S.buMode == 2 ? " %" : "");
   string t = S.buMode == 1 ? Num(S.buPips) + " pips x " + Num(S.pipSz) + " = " + Px(BufAt(0)) :
              (S.buMode == 2 ? Num(S.buPct) + "% of the level = " + Px(BufAt(SymbolInfoDouble(g_sym, SYMBOL_BID))) + " now" : "price " + Num(S.slBuf));
   if (S.minStop > 0 || S.maxStop > 0)
      t = t + "  |  skip closer " + (S.minStop > 0 ? Num(S.minStop) + u : "off") + " / further " + (S.maxStop > 0 ? Num(S.maxStop) + u : "off");
   return t;
}
string IdeasTxt()
{
   string t = (string)(S.bkOn ? "a " : "") + (S.hfOn ? "b " : "") + (S.trOn ? "c " : "") + (S.lqOn ? "d " : "") + (S.ppOn ? "e " : "") + (S.pdOn ? "f " : "") + (S.lsOn ? "g " : "");
   return t == "" ? "none" : t;
}
// all the rows, in TradingView's order, with the MT5 rows on top
void TblRows()
{
   g_rN = 0;
   bool full = InStatRows == TR_FULL;
   string tf = TfName(g_htf);
   int nm = MoneyN();
   Row("SMC STRATEGY  (EA v12.3)", "value", clrWhite);
   Row("Structure (this chart)", StructTxt(), clrAqua);
   Row("Higher timeframe " + tf + " now", HtfNowTxt(), HT.tTrend == 1 ? clrLime : (HT.tTrend == -1 ? clrRed : clrGray));
   for (int k = 0; k < g_nSides; k++)
   {
      Row(SideName(k, "waiting setup", "Waiting setup"), WaitTxt(k), g_side[k].dir != 0 ? clrYellow : clrGray);
      Row(SideName(k, "last signal", "Last signal"), g_note[k] == "" ? "-" : g_note[k], clrSilver);
   }
   Row("Open trades  |  floating P&L", OpenTxt(), clrWhite);
   if (!full)
   {
      Row("Trades entered", CntTxt(1), clrLime);
      Row("Exit - target / stop", I2(g_exTgt) + " / " + I2(g_exStop), clrTeal);
      Row("Risk NEXT trade", MonTxt(Mo(g_money[0].riskNow), Mo(g_money[1].riskNow)), g_money[0].riskNow > S.risk || (nm == 2 && g_money[1].riskNow > S.risk) ? clrOrange : clrWhite);
      if (S.seqMode != 0)
      {
         Row("Losses carried", MonTxt(Mo(g_money[0].Car()), Mo(g_money[1].Car())), g_money[0].Car() > 0 || (nm == 2 && g_money[1].Car() > 0) ? clrRed : clrGray);
         Row("Risk cap hit / HALT", MonTxt(I2(g_money[0].cntSeqCap) + CapTxt() + (g_money[0].seqHalt ? "  HALTED" : ""), I2(g_money[1].cntSeqCap) + CapTxt() + (g_money[1].seqHalt ? "  HALTED" : "")),
             g_money[0].seqHalt || (nm == 2 && g_money[1].seqHalt) ? clrRed : clrGray);
      }
      if (S.flMode != 0) for (int mi = 0; mi < nm; mi++) Row(nm == 2 ? (mi == 0 ? "ACCOUNT FLOOR - long side" : "ACCOUNT FLOOR - short side") : "ACCOUNT FLOOR (group 35)", FloorTxt(mi), g_money[mi].flCush < 0.25 * S.flAmt ? clrRed : clrAqua);
      if (S.ldOn) for (int mi = 0; mi < nm; mi++) Row(nm == 2 ? (mi == 0 ? "PAUSE - long side" : "PAUSE - short side") : "PAUSE AFTER LOSSES (group 36)", PauseTxt(mi), g_money[mi].LdHalt(g_t) ? clrRed : clrAqua);
      if (S.eqOn || S.autoM) Row("HTF EQUILIBRIUM FIRST (group 37)", EqTxt(), g_eqOpen ? clrLime : clrOrange);
      if (S.calOn) Row("Calendar news - next", CalNextTxt(), StringFind(CalNextTxt(), "WINDOW NOW") == 0 ? clrRed : clrAqua);
      if (S.preOn) Row("No new trades before news", PreTxt(), g_preNow ? clrRed : clrAqua);
      if (InCalToday != CT_OFF) TodayRows(false);
      if (S.buMode != 0) Row("Stop buffer (group 38)", BufTxt(), clrAqua);
      Row("Spread now", Px(SymbolInfoDouble(g_sym, SYMBOL_ASK) - SymbolInfoDouble(g_sym, SYMBOL_BID)), clrSilver);
      Row("BLOCKED NOW", BlockTxt(), AnyBlocked() ? clrRed : clrLime);
      int wt = ArraySize(g_clsTk) + ArraySize(g_stpTk);
      if (wt > 0) Row("Closes / stop moves waiting for the broker", I2(wt), clrRed);
      return;
   }
   int open = 0;
   for (int k = 0; k < g_nSides; k++) open += g_io[k].nPos;
   int wait = 0;
   for (int k = 0; k < g_nSides; k++) if (g_side[k].dir != 0) wait++;
   Row("CHOCH signals on the chart", S.useCho ? I2(g_cntCho) : "off", S.useCho ? clrWhite : clrGray);
   Row("BOS signals on the chart", S.useBos ? I2(g_cntBos) : "off", S.useBos ? clrWhite : clrGray);
   Row("Setups armed", CntTxt(0), clrYellow);
   Row("Trades entered", CntTxt(1) + (open > 0 ? "  (" + I2(open) + " still open)" : ""), clrLime);
   Row("  - closed by the broker or the EA", I2(g_closedN), clrGray);
   Row("  - REFUSED by the broker", I2(g_refused), g_refused > 0 ? clrRed : clrGray);
   int wt = ArraySize(g_clsTk) + ArraySize(g_stpTk);
   Row("  - closes / stop moves waiting for the broker", I2(wt), wt > 0 ? clrRed : clrGray);
   Row("  - by ENTRY RULE 1 (pullback %)", CntTxt(4), clrLime);
   Row("  - by ENTRY RULE 2 (broken pivot)", CntTxt(5), clrLime);
   if (S.r3On) Row("  - by ENTRY RULE 3 (signal close)", CntTxt(13), clrLime);
   Row("Setups cancelled, never filled", CntTxt(2) + (wait > 0 ? "  (+" + I2(wait) + " waiting)" : ""), clrOrange);
   Row("Exit - target", I2(g_exTgt), clrTeal);
   Row("Exit - stop", I2(g_exStop), clrRed);
   Row("Exit - moved stop (BE / step / trail)", !S.mgOn ? "off" : I2(g_exMv) + "  (" + I2(CntSum(12)) + " moves)", !S.mgOn ? clrGray : clrAqua);
   Row("Exit - opposite signal", I2(g_exOpp), clrMagenta);
   Row("Exit - " + Two(S.hrFlat) + ":00 flat / weekend", I2(g_exFlat), clrSilver);
   Row("Exit - news window / holiday", !S.newsOn ? "master OFF" : ((S.nw1On || S.nw2On || S.nw3On || S.auOn || S.calOn || !S.holTrade) ? I2(g_exNews) : "off"), g_exNews > 0 ? clrMagenta : clrGray);
   Row("Exit - other (manual, stop-out)", I2(g_exOther), g_exOther > 0 ? clrRed : clrGray);
   Row("Trades cut by leverage cap", CntTxt(11), CntSum(11) > 0 ? clrOrange : clrGray);
   Row("Skipped - stop distance / min lot", CntTxt(3), CntSum(3) > 0 ? clrOrange : clrGray);
   Row("Cancelled - expired unfilled", CntTxt(10), CntSum(10) > 0 ? clrOrange : clrGray);
   string rules = S.r1 && S.r2 ? "1 + 2 (dynamic)" : (S.r1 ? "1 only (pullback %)" : (S.r2 ? "2 only (HTF must agree)" : "NONE - both off"));
   if (S.fav) rules = rules + "  |  HTF favourable only";
   else if (S.agn) rules = rules + (S.r1 ? "  |  against the HTF only (rule 1)" : "  |  against the HTF needs rule 1 - NO TRADES");
   else if (S.autoM) rules = rules + (S.r1 ? "  |  auto: against the HTF, then with it" : "  |  auto: no trades before the equilibrium (rule 1 off)");
   Row("ENTRY rules in use (1 / 2)", rules, (S.r1 || S.r2) && !(S.agn && !S.r1) ? clrAqua : clrRed);
   bool hu = S.r2 || S.hfEff || S.eqOn || S.agn || S.autoM;
   Row("RULE 2 / filter higher timeframe", hu ? (S.htfOk ? tf : "off (not above chart)") : "off (rule 2 off)", hu && S.htfOk ? clrAqua : clrGray);
   Row("LOSS RECOVERY (A / B / C, A+ / B+ / C+)", RecoveryTxt(), S.seqMode == 0 || S.flMode == 1 ? clrGray : clrOrange);
   Row("Losses carried", S.seqMode == 0 ? "off" : MonTxt(Mo(g_money[0].Car()), Mo(g_money[1].Car())), S.seqMode != 0 && (g_money[0].Car() > 0 || (nm == 2 && g_money[1].Car() > 0)) ? clrRed : clrGray);
   Row("Risk NEXT trade", MonTxt(Mo(g_money[0].riskNow), Mo(g_money[1].riskNow)), g_money[0].riskNow > S.risk || (nm == 2 && g_money[1].riskNow > S.risk) ? clrOrange : clrWhite);
   Row("Risk cap hit / HALT", S.seqMode == 0 ? "off" : MonTxt(I2(g_money[0].cntSeqCap) + CapTxt() + (g_money[0].seqHalt ? "  HALTED" : ""), I2(g_money[1].cntSeqCap) + CapTxt() + (g_money[1].seqHalt ? "  HALTED" : "")),
       S.seqMode != 0 && (g_money[0].seqHalt || (nm == 2 && g_money[1].seqHalt)) ? clrRed : clrGray);
   Row("Last trade risk", IsNa(g_lastRisk) ? "-" : Mo(g_lastRisk) + "  /  " + DoubleToString(g_lastLots, 2) + " lots", clrAqua);
   bool cmOff = S.cmMode == 0 && S.sprd <= 0;
   Row("Costs last trade (for sizing)", cmOff || IsNa(g_lastCost) ? "-" : Mo(g_lastCost) + (IsNa(g_lastRisk) || g_lastRisk <= 0 ? "" : "  = " + DoubleToString(g_lastCost / g_lastRisk * 100.0, 1) + "% of risk"),
       cmOff || IsNa(g_lastCost) ? clrGray : (!IsNa(g_lastRisk) && g_lastRisk > 0 && g_lastCost / g_lastRisk > 0.25 ? clrRed : clrOrange));
   Row("Costs paid total (commission + swap)", Mo(g_costPaid), g_costPaid > 0 ? clrOrange : clrGray);
   Row("Commission model (for sizing)", CmTxt(), S.cmMode == 0 ? clrGray : clrAqua);
   Row("Spread now", Px(SymbolInfoDouble(g_sym, SYMBOL_ASK) - SymbolInfoDouble(g_sym, SYMBOL_BID)), clrSilver);
   Row("Time filters", S.timeOn ? "on" : (S.intra ? "off" : "off (daily+)"), S.timeOn ? clrAqua : clrGray);
   Row("Profit target (made / target)", !S.ptOn ? "off" : MonTxt(Mo(g_money[0].ptPnl), Mo(g_money[1].ptPnl)) + " / " + Mo(S.ptAmt) + (S.ptPer == 1 ? " today" : (S.ptPer == 2 ? " this week" : " total")) +
       (g_money[0].ptHalt || (nm == 2 && g_money[1].ptHalt) ? "  REACHED" : ""), !S.ptOn ? clrGray : clrAqua);
   Row("News windows active on", NewsDatesTxt(), S.newsOn && (S.nw1On || S.nw2On || S.nw3On) ? clrAqua : clrGray);
   Row("US news (auto) - next", NextNewsTxt(), S.newsOn && S.auOn ? clrAqua : clrGray);
   Row("US clock", UsClockTxt(), clrAqua);
   Row("US holidays", UsHolTxt(), g_holNow ? clrRed : (S.holTrade ? clrGray : clrAqua));
   Row("Calendar news (group 41) - next", CalNextTxt(), !S.calOn || !S.newsOn ? clrGray : (StringFind(CalNextTxt(), "WINDOW NOW") == 0 ? clrRed : clrAqua));
   Row("  - list from", !S.calOn ? "off" : (g_calSrc == "" ? "-" : g_calSrc), !S.calOn ? clrGray : (g_calOk ? clrAqua : clrRed));
   Row("  - calendar holidays", CalHolTxt(), StringFind(CalHolTxt(), "TODAY") == 0 ? clrRed : (S.calOn && S.calHol && !S.holTrade ? clrAqua : clrGray));
   Row("No new trades before news", PreTxt(), g_preNow ? clrRed : (S.preOn ? clrAqua : clrGray));
   if (InCalToday != CT_OFF) TodayRows(true);
   Row("Symbol  |  1 lot  |  lot step", g_sym + "  |  " + DoubleToString(g_contract, 0) + " units  |  " + DoubleToString(g_volStep, 2), clrAqua);
   Row("BLOCKED NOW", BlockTxt(), AnyBlocked() ? clrRed : clrLime);
   string dm = S.dirMode == 0 ? "both" : (S.dirMode == 1 ? "longs only - " + I2(CntSum(6)) + " signals the other way not traded" :
               (S.dirMode == 2 ? "shorts only - " + I2(CntSum(6)) + " signals the other way not traded" : (S.hedgeMoney == 0 ? "HEDGE - each side its own money" : "HEDGE - money shared by both sides")));
   Row("Trade direction (group 33)", dm, S.dirMode == 0 ? clrGray : clrAqua);
   Row("v9.0 ideas switched ON (group 34)", IdeasTxt(), IdeasTxt() == "none" ? clrGray : clrAqua);
   string ls = MonTxt(I2(g_money[0].cntLs), I2(g_money[1].cntLs));
   Row("  - skipped: HTF filter / premium-discount / paused days", CntTxt(7) + " / " + CntTxt(8) + " / " + ls, CntSum(7) + CntSum(8) > 0 ? clrOrange : clrGray);
   Row("Cancelled - new BOS before the fill", S.bosCnl ? CntTxt(9) : "off", S.bosCnl && CntSum(9) > 0 ? clrOrange : clrGray);
   for (int mi = 0; mi < nm; mi++)
      Row(nm == 2 ? (mi == 0 ? "ACCOUNT FLOOR - long side" : "ACCOUNT FLOOR - short side") : "ACCOUNT FLOOR (group 35)", S.flMode == 0 ? "off" : FloorTxt(mi),
          S.flMode == 0 ? clrGray : (g_money[mi].flCush < 0.25 * S.flAmt ? clrRed : clrAqua));
   for (int mi = 0; mi < nm; mi++)
      Row(nm == 2 ? (mi == 0 ? "PAUSE AFTER LOSSES - long side" : "PAUSE AFTER LOSSES - short side") : "PAUSE AFTER LOSSES (group 36)", !S.ldOn ? "off" : PauseTxt(mi),
          !S.ldOn ? clrGray : (g_money[mi].LdHalt(g_t) ? clrRed : clrAqua));
   Row("HTF EQUILIBRIUM FIRST (group 37)", EqTxt(), !S.eqOn && !S.autoM ? clrGray : (g_eqOpen ? clrLime : clrOrange));
   Row("STOP BUFFER (group 38)", BufTxt(), S.buMode != 0 ? clrAqua : clrGray);
   Row("RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)", R3Txt(), S.r3On ? clrAqua : clrGray);
   Row("LOSS MARK - BACK TO THE BASE (group 42)", LmTxt(), S.lmOn && S.seqMode != 0 ? clrAqua : clrGray);
   Row("PROFIT STEPS - A / B / C split (group 43)", SpTxt(), S.seqMode >= 7 ? clrAqua : clrGray);
   Row("Entries  |  magic", (string)(InExec == EX_TOUCH ? "touch (like TradingView)" : "pending orders") + "  |  " + IntegerToString(InMagic), clrSilver);
   Row("Counting since", SessTime(SrvToUtc(g_startT), true), clrGray);
}
void TblLabel(string nm, int x, int y, string txt, color c, int fs, int anchor)
{
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);
      ObjectSetString(0, nm, OBJPROP_FONT, "Consolas");
   }
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anchor);
   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, fs);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, c);
   ObjectSetString(0, nm, OBJPROP_TEXT, txt);
}
void TblBox(string nm, int x, int y, int w, int h, color bg, color border)
{
   if (ObjectFind(0, nm) < 0)
   {
      ObjectCreate(0, nm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);
      ObjectSetInteger(0, nm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   }
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, nm, OBJPROP_XSIZE, w);
   ObjectSetInteger(0, nm, OBJPROP_YSIZE, h);
   ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, border);
}
void TblDelete()
{
   ObjectDelete(0, g_P + "tb");
   ObjectDelete(0, g_P + "th");
   for (int i = 0; i < g_tblShown; i++) { ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i)); }
   g_tblShown = 0;
}
// the table: build the rows, measure them, place the box in the chosen corner, write the cells
void Panel()
{
   if (g_tester && !g_visual) return;
   if (!InStatOn || !g_ready) { if (g_tblShown > 0) TblDelete(); return; }
   TblRows();
   int fs = InStatSize == TS_SMALL ? 8 : (InStatSize == TS_LARGE ? 11 : 9);
   TextSetFont("Consolas", -fs * 10);
   uint w = 0, h = 0, w1 = 0, w2 = 0, th = 0;
   for (int i = 0; i < g_rN; i++)
   {
      if (TextGetSize(g_rL[i], w, h)) { if (w > w1) w1 = w; if (h > th) th = h; }
      if (TextGetSize(g_rV[i], w, h)) { if (w > w2) w2 = w; if (h > th) th = h; }
   }
   if (th == 0) th = (uint)(fs * 2);
   if (w1 == 0 || w2 == 0)   // no font measure: about one font size per character (Consolas)
      for (int i = 0; i < g_rN; i++)
      {
         uint a1 = (uint)(StringLen(g_rL[i]) * fs), a2 = (uint)(StringLen(g_rV[i]) * fs);
         if (a1 > w1) w1 = a1;
         if (a2 > w2) w2 = a2;
      }
   int pad = 6, gap = 16, rowH = (int)th + 3;
   int W = pad + (int)w1 + gap + (int)w2 + pad, H = 2 * pad + g_rN * rowH;
   int cw = (int)ChartGetInteger(0, CHART_WIDTH_IN_PIXELS), ch = (int)ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS, 0);
   int ps = (int)InStatPos;
   int x0 = (ps == 0 || ps == 3 || ps == 5) ? 6 : ((ps == 1 || ps == 6) ? (cw - W) / 2 : cw - W - 6);
   int y0 = ps <= 2 ? 22 : (ps <= 4 ? (ch - H) / 2 : ch - H - 6);
   if (x0 < 0) x0 = 0;
   if (y0 < 0) y0 = 0;
   TblBox(g_P + "tb", x0, y0, W, H, C'16,18,26', C'80,80,90');
   TblBox(g_P + "th", x0 + 1, y0 + 1, W - 2, pad + rowH - 1, C'28,56,110', C'28,56,110');
   for (int i = 0; i < g_rN; i++)
   {
      int y = y0 + pad + i * rowH;
      TblLabel(g_P + "tl" + I2(i), x0 + pad, y, g_rL[i], i == 0 ? clrWhite : clrSilver, fs, ANCHOR_LEFT_UPPER);
      TblLabel(g_P + "tv" + I2(i), x0 + W - pad, y, g_rV[i], g_rC[i], fs, ANCHOR_RIGHT_UPPER);
   }
   for (int i = g_rN; i < g_tblShown; i++) { ObjectDelete(0, g_P + "tl" + I2(i)); ObjectDelete(0, g_P + "tv" + I2(i)); }
   g_tblShown = g_rN;
   ChartRedraw(0);
}

//---------------------------------------------------------------- events
int OnInit()
{
   g_sym    = _Symbol;
   g_tf     = (ENUM_TIMEFRAMES)_Period;
   g_cs     = PeriodSeconds(g_tf);
   g_tester = MQLInfoInteger(MQL_TESTER) != 0;
   g_visual = MQLInfoInteger(MQL_VISUAL_MODE) != 0;
   g_ready  = false;
   g_badInit = false;
   CalParseCur();
   string bad = CheckInputs();
   if (bad != "") { Alert("SMC EA: ", bad); return INIT_PARAMETERS_INCORRECT; }
   g_contract = SymbolInfoDouble(g_sym, SYMBOL_TRADE_CONTRACT_SIZE);
   g_volMin   = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MIN);
   g_volMax   = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_MAX);
   g_volStep  = SymbolInfoDouble(g_sym, SYMBOL_VOLUME_STEP);
   g_tickSize = SymbolInfoDouble(g_sym, SYMBOL_TRADE_TICK_SIZE);
   g_point    = SymbolInfoDouble(g_sym, SYMBOL_POINT);
   g_digits   = (int)SymbolInfoInteger(g_sym, SYMBOL_DIGITS);
   if (g_contract <= 0 || g_volStep <= 0 || g_tickSize <= 0) { Alert("SMC EA: symbol information is not available yet - attach again"); return INIT_FAILED; }
   g_srvBase = (long)MathRound(InSrvHours * 3600.0);
   g_htf     = HtfOf();
   g_htfSec  = PeriodSeconds(g_htf);
   g_netting = AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   bool bos  = InSig != SIG_CHOCH && InSig != SIG_CHOCH_FAV && InSig != SIG_CHOCH_AGN && InSig != SIG_CHOCH_AUTO;
   if (g_netting && (InDirMode == DIR_HEDGE || InPpOn || bos))
   {
      Alert("SMC EA: this is a NETTING account. Hedge mode, partial profit (34 e) and BOS signals need a HEDGING account (one position per trade).");
      return INIT_PARAMETERS_INCORRECT;
   }
   if (g_netting) Print("SMC EA: netting account - one position at a time. A hedging account is recommended.");
   FillSettings();
   S.Derive();
   g_htfUse = S.htfOk;
   g_P = "SMC" + IntegerToString(InMagic) + "_" + g_sym + "_";
   g_AP = "SMCA" + IntegerToString(InMagic) + "_" + g_sym + "_";   // v12.3: the audit labels
   for (int k = 0; k < 2; k++) { g_audCur[k] = ""; g_audSeq[k] = 0; }
   if (!InAudit || InAudMax <= 0) ObjectsDeleteAll(0, g_AP);
   g_trade.SetExpertMagicNumber((ulong)InMagic);
   g_trade.SetDeviationInPoints((ulong)InSlip);
   g_trade.SetTypeFillingBySymbol(g_sym);
   g_trade.SetMarginMode();
   g_trade.LogLevel(LOG_LEVEL_ERRORS);
   long em = SymbolInfoInteger(g_sym, SYMBOL_EXPIRATION_MODE);
   g_otime = (em & SYMBOL_EXPIRATION_GTC) != 0 ? ORDER_TIME_GTC : ORDER_TIME_DAY;
   if (!g_tester)
   {
      long liveOff = (long)(TimeTradeServer() - TimeGMT());
      long ruleOff = TzOff((long)TimeGMT(), g_srvBase, (int)InSrvDst);
      if (MathAbs((double)(liveOff - ruleOff)) > 900)
         Print("SMC EA WARNING: the broker clock is UTC", liveOff >= 0 ? "+" : "", DoubleToString(liveOff / 3600.0, 1), " now, but the settings say UTC",
               ruleOff >= 0 ? "+" : "", DoubleToString(ruleOff / 3600.0, 1), ". Check 'Broker server time' in group 40 - session hours depend on it.");
   }
   if (!S.htfOk && S.on && (S.r2 || S.hfEff || S.eqOn || S.agn || S.autoM))
      Print("SMC EA: the higher timeframe ", TfName(g_htf), " is not above the chart - RULE 2 / filters work as in TradingView (no higher timeframe).");
   string cw = "";
   if (!CalInit(cw))
   {
      Alert("SMC EA: ", cw, ". Put the EA on a live (or demo) chart once with 'save the calendar to a file' ON, then test again.");
      return INIT_FAILED;
   }
   if (InPreOn && !(InCalOn || InAuOn)) Print("SMC EA: 'No new trades before news' is ON but no news list is on (group 41 calendar or group 29 automatic US news) - it does nothing");
   EventSetTimer(1);
   TryInit();
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason)
{
   EventKillTimer();
   if (reason == REASON_REMOVE || reason == REASON_ACCOUNT)
   {
      if (InExec == EX_PEND && g_ready) DeleteOurPending();
      if (!g_tester) GlobalVariableDel(g_P + "T");
   }
   ObjectsDeleteAll(0, g_P);
   if (reason == REASON_REMOVE || reason == REASON_ACCOUNT || reason == REASON_CHARTCHANGE) ObjectsDeleteAll(0, g_AP);   // v12.3: the audit labels
   Comment("");
}
void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &request, const MqlTradeResult &result)
{
   if (trans.type == TRADE_TRANSACTION_DEAL_ADD) g_dealFlag = true;
}
void OnTimer()
{
   if (!g_tester) CalTick();
   if (!g_ready) TryInit();
   else Panel();   // the table follows the price and the spread between candles
}
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if (id == CHARTEVENT_CHART_CHANGE) Panel();   // the chart was resized: place the table again
}
void OnTick()
{
   if (!g_ready) { if (!TryInit()) return; }
   datetime t0 = iTime(g_sym, g_tf, 0);
   if (t0 > g_curOpen)
   {
      // v12.3: after a gap (sleep / no connection) MT5 may still be downloading the missed candles - wait for them (up to a minute)
      if (!g_tester && t0 - g_lastBar > 2 * PeriodSeconds(g_tf) && !SeriesInfoInteger(g_sym, g_tf, SERIES_SYNCHRONIZED) && TimeCurrent() - t0 < 60) return;
      CalTick();
      MqlRates rr[];
      int n = CopyRates(g_sym, g_tf, g_lastBar + 1, t0 - 1, rr);
      if (n < 0) return;   // history not ready yet - try on the next tick
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
      g_curOpen = t0;
      Panel();
      return;
   }
   if (ArraySize(g_clsTk) > 0) DoCloses();
   if (ArraySize(g_stpTk) > 0) DoStops();
   if (InExec == EX_TOUCH) CheckTouch();
   else SyncPending();
}
