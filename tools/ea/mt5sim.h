// A small fake MetaTrader 5 so the WHOLE EA file (converted by mql2cpp.py) can be compiled and run here.
// Prices: 1-minute bars turned into ticks along TradingView's path (open -> nearer extreme -> other -> close),
// one tick per 0.01. Broker: market / limit orders, SL / TP, hedging positions, deals with commission.
#pragma once
#include <string>
#include <vector>
#include <map>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <algorithm>
#include <climits>
#include <functional>
typedef std::string string;
typedef long datetime;
typedef unsigned long ulong;
typedef unsigned int uint;
typedef unsigned short ushort;
typedef int color;

template <class T> class MqlArr { public: std::vector<T> v; T &operator[](int i) { return v.at(i); } };
template <class T> int ArraySize(MqlArr<T> &a) { return (int)a.v.size(); }
template <class T> int ArrayResize(MqlArr<T> &a, int n, int reserve = 0) { a.v.resize(n); return n; }
template <class T> int ArraySize(T (&a)[1]) { return 1; }

// ---------------- enums / constants ----------------
enum ENUM_TIMEFRAMES { PERIOD_CURRENT = 0, PERIOD_M1 = 1, PERIOD_M5 = 5, PERIOD_M15 = 15, PERIOD_H1 = 16385, PERIOD_H4 = 16388, PERIOD_D1 = 16408, PERIOD_W1 = 32769, PERIOD_MN1 = 49153 };
enum ENUM_SYMBOL_INFO_DOUBLE { SYMBOL_TRADE_TICK_VALUE, SYMBOL_TRADE_TICK_SIZE, SYMBOL_TRADE_CONTRACT_SIZE, SYMBOL_VOLUME_MIN, SYMBOL_VOLUME_MAX, SYMBOL_VOLUME_STEP, SYMBOL_POINT, SYMBOL_BID, SYMBOL_ASK };
enum ENUM_SYMBOL_INFO_INTEGER { SYMBOL_TRADE_STOPS_LEVEL, SYMBOL_DIGITS, SYMBOL_EXPIRATION_MODE, SYMBOL_TRADE_CALC_MODE };
enum ENUM_SYMBOL_INFO_STRING { SYMBOL_CURRENCY_BASE, SYMBOL_CURRENCY_PROFIT };
enum ENUM_SYMBOL_CALC_MODE { SYMBOL_CALC_MODE_FOREX, SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE, SYMBOL_CALC_MODE_FUTURES, SYMBOL_CALC_MODE_CFD, SYMBOL_CALC_MODE_CFDINDEX, SYMBOL_CALC_MODE_CFDLEVERAGE };
const int SYMBOL_EXPIRATION_GTC = 1;
enum ENUM_DEAL_PROPERTY_INTEGER { DEAL_MAGIC, DEAL_TYPE, DEAL_ENTRY, DEAL_TIME, DEAL_POSITION_ID, DEAL_REASON };
enum ENUM_DEAL_PROPERTY_DOUBLE { DEAL_PROFIT, DEAL_COMMISSION, DEAL_SWAP, DEAL_FEE, DEAL_VOLUME, DEAL_PRICE };
enum ENUM_DEAL_PROPERTY_STRING { DEAL_SYMBOL, DEAL_COMMENT };
enum ENUM_DEAL_TYPE { DEAL_TYPE_BUY, DEAL_TYPE_SELL, DEAL_TYPE_BALANCE };
enum ENUM_DEAL_ENTRY { DEAL_ENTRY_IN, DEAL_ENTRY_OUT, DEAL_ENTRY_INOUT, DEAL_ENTRY_OUT_BY };
enum ENUM_DEAL_REASON { DEAL_REASON_CLIENT, DEAL_REASON_EXPERT, DEAL_REASON_SL, DEAL_REASON_TP };
enum ENUM_POSITION_PROPERTY_INTEGER { POSITION_IDENTIFIER, POSITION_MAGIC, POSITION_TIME, POSITION_TYPE };
enum ENUM_POSITION_PROPERTY_DOUBLE { POSITION_SL, POSITION_TP, POSITION_VOLUME, POSITION_PRICE_OPEN, POSITION_PROFIT, POSITION_SWAP };
enum ENUM_POSITION_PROPERTY_STRING { POSITION_SYMBOL, POSITION_COMMENT };
enum ENUM_POSITION_TYPE { POSITION_TYPE_BUY, POSITION_TYPE_SELL };
enum ENUM_ORDER_PROPERTY_INTEGER { ORDER_MAGIC, ORDER_STATE };
enum ENUM_ORDER_PROPERTY_DOUBLE { ORDER_VOLUME_CURRENT, ORDER_PRICE_OPEN, ORDER_SL, ORDER_TP };
enum ENUM_ORDER_PROPERTY_STRING { ORDER_SYMBOL, ORDER_COMMENT };
enum ENUM_ORDER_STATE { ORDER_STATE_STARTED, ORDER_STATE_PLACED, ORDER_STATE_CANCELED, ORDER_STATE_PARTIAL, ORDER_STATE_FILLED, ORDER_STATE_REJECTED, ORDER_STATE_EXPIRED };
enum ENUM_ORDER_TYPE_TIME { ORDER_TIME_GTC, ORDER_TIME_DAY };
enum ENUM_ACCOUNT_INFO_DOUBLE { ACCOUNT_EQUITY, ACCOUNT_BALANCE };
enum ENUM_ACCOUNT_INFO_INTEGER { ACCOUNT_MARGIN_MODE };
const long ACCOUNT_MARGIN_MODE_RETAIL_HEDGING = 2;
enum ENUM_SERIES_INFO_INTEGER { SERIES_SYNCHRONIZED };
enum ENUM_MQL_INFO_INTEGER { MQL_TESTER, MQL_VISUAL_MODE };
enum ENUM_OBJECT { OBJ_TREND, OBJ_TEXT, OBJ_LABEL, OBJ_RECTANGLE_LABEL };
enum ENUM_OBJECT_PROPERTY_INTEGER { OBJPROP_SELECTABLE, OBJPROP_HIDDEN, OBJPROP_BACK, OBJPROP_COLOR, OBJPROP_STYLE, OBJPROP_WIDTH, OBJPROP_RAY_RIGHT, OBJPROP_FONTSIZE, OBJPROP_ANCHOR,
   OBJPROP_CORNER, OBJPROP_XDISTANCE, OBJPROP_YDISTANCE, OBJPROP_XSIZE, OBJPROP_YSIZE, OBJPROP_BGCOLOR, OBJPROP_BORDER_TYPE };
enum ENUM_BASE_CORNER { CORNER_LEFT_UPPER };
enum ENUM_BORDER_TYPE { BORDER_FLAT };
enum ENUM_CHART_PROPERTY_INTEGER { CHART_WIDTH_IN_PIXELS, CHART_HEIGHT_IN_PIXELS, CHART_COLOR_BACKGROUND };
const int CHARTEVENT_CHART_CHANGE = 9;
enum ENUM_OBJECT_PROPERTY_STRING { OBJPROP_TEXT, OBJPROP_FONT, OBJPROP_TOOLTIP };
enum ENUM_LINE_STYLE { STYLE_SOLID, STYLE_DASH, STYLE_DOT };
enum ENUM_ANCHOR_POINT { ANCHOR_LEFT_UPPER, ANCHOR_LEFT_LOWER, ANCHOR_RIGHT_UPPER, ANCHOR_RIGHT_LOWER };
enum ENUM_LOG_LEVELS { LOG_LEVEL_NO, LOG_LEVEL_ERRORS, LOG_LEVEL_ALL };
enum ENUM_TRADE_TRANSACTION_TYPE { TRADE_TRANSACTION_ORDER_ADD, TRADE_TRANSACTION_DEAL_ADD };
enum ENUM_INIT_RETCODE { INIT_SUCCEEDED = 0, INIT_FAILED = 1, INIT_PARAMETERS_INCORRECT = 2 };
const int REASON_REMOVE = 1, REASON_RECOMPILE = 2, REASON_CHARTCHANGE = 3, REASON_CLOSE = 9, REASON_PARAMETERS = 5, REASON_ACCOUNT = 6;
const int TIME_DATE = 1, TIME_MINUTES = 2;
const color clrTeal = 1, clrCrimson = 2, clrOrange = 3, clrRed = 4, clrDodgerBlue = 5, clrWhite = 6, clrSilver = 7, clrYellow = 8, clrLime = 9, clrAqua = 10, clrMagenta = 11, clrGray = 12, clrMediumPurple = 13, clrTomato = 14, clrGreen = 15, clrDarkOrange = 16, clrMediumBlue = 17, clrDimGray = 18;
const uint TRADE_RETCODE_REQUOTE = 10004, TRADE_RETCODE_REJECT = 10006, TRADE_RETCODE_PLACED = 10008, TRADE_RETCODE_DONE = 10009, TRADE_RETCODE_DONE_PARTIAL = 10010,
           TRADE_RETCODE_ERROR = 10011, TRADE_RETCODE_TIMEOUT = 10012, TRADE_RETCODE_INVALID = 10013, TRADE_RETCODE_INVALID_VOLUME = 10014, TRADE_RETCODE_INVALID_PRICE = 10015,
           TRADE_RETCODE_INVALID_STOPS = 10016, TRADE_RETCODE_TRADE_DISABLED = 10017, TRADE_RETCODE_MARKET_CLOSED = 10018, TRADE_RETCODE_NO_MONEY = 10019,
           TRADE_RETCODE_PRICE_CHANGED = 10020, TRADE_RETCODE_PRICE_OFF = 10021, TRADE_RETCODE_TOO_MANY_REQUESTS = 10024, TRADE_RETCODE_SERVER_DISABLES_AT = 10026,
           TRADE_RETCODE_CLIENT_DISABLES_AT = 10027, TRADE_RETCODE_LOCKED = 10028, TRADE_RETCODE_FROZEN = 10029, TRADE_RETCODE_CONNECTION = 10031, TRADE_RETCODE_POSITION_CLOSED = 10036;
struct MqlRates { datetime time; double open, high, low, close; long tick_volume; int spread; long real_volume; };
struct MqlTradeTransaction { ENUM_TRADE_TRANSACTION_TYPE type; ulong deal; };
struct MqlTradeRequest { int dummy; };
struct MqlTradeResult { int dummy; };

// ---------------- the fake terminal ----------------
struct SimBar { datetime t; double o, h, l, c; };
struct SimPos { ulong ticket; int dir; double vol, price, sl, tp; datetime time; string cmt; long magic; };
struct SimOrd { ulong ticket; int dir; double vol, price, sl, tp; string cmt; long magic; };
struct SimDeal { ulong ticket; datetime time; int type, entry, reason; ulong pid; double vol, price, profit, comm; string cmt; long magic; };
namespace sim {
   string sym = "XAUUSD";
   int    tester = 1;
   std::vector<SimBar> m1;                      // server time
   std::map<int, std::vector<SimBar>> tfBars;   // by period seconds
   size_t curBar = 0;                           // index into m1 of the tick in progress
   datetime now = 0;
   double bid = 0, ask = 0, spread = 0, prevPx = 0;
   bool   firstTickOfBar = true;
   double commPerLot = 30.0, contract = 100.0;
   double balance = 1e6;
   std::vector<SimPos> pos;
   std::vector<SimOrd> ords;
   std::vector<SimDeal> deals;
   std::map<ulong, int> ordState;
   ulong nextTicket = 1000;
   std::vector<int> selDeals;
   int selPos = -1, selOrd = -1;
   std::map<string, double> gv;
   std::vector<ulong> pendingTx;
   uint lastRc = 0; ulong lastOrder = 0;
   long srvBase = 7200;
   int chartSec = 60;
   long nFills = 0;
   long tblChars = 0, tblRows = 0;
}
inline int TfSec(ENUM_TIMEFRAMES tf)
{
   switch (tf) { case PERIOD_M1: return 60; case PERIOD_M5: return 300; case PERIOD_M15: return 900; case PERIOD_H1: return 3600; case PERIOD_H4: return 14400;
                 case PERIOD_D1: return 86400; case PERIOD_W1: return 604800; case PERIOD_MN1: return 2592000; default: return sim::chartSec; }
}
inline std::vector<SimBar> &BarsOf(ENUM_TIMEFRAMES tf)
{
   int s = tf == PERIOD_CURRENT ? sim::chartSec : TfSec(tf);
   if (s == 60) return sim::m1;
   auto it = sim::tfBars.find(s);
   if (it != sim::tfBars.end()) return it->second;
   std::vector<SimBar> &v = sim::tfBars[s];
   for (auto &b : sim::m1)
   {
      datetime k = b.t - ((b.t % s) + s) % s;
      if (v.empty() || v.back().t != k) v.push_back(SimBar{k, b.o, b.h, b.l, b.c});
      else { SimBar &a = v.back(); a.h = std::max(a.h, b.h); a.l = std::min(a.l, b.l); a.c = b.c; }
   }
   return v;
}
// bars visible now: those with open <= now (the last one is still forming, built from the minutes so far)
inline int VisibleCount(ENUM_TIMEFRAMES tf)
{
   std::vector<SimBar> &v = BarsOf(tf);
   auto it = std::upper_bound(v.begin(), v.end(), sim::now, [](datetime t, const SimBar &b) { return t < b.t; });
   return (int)(it - v.begin());
}
inline SimBar VisibleBar(ENUM_TIMEFRAMES tf, int idx) { return BarsOf(tf)[idx]; }

// ---------------- MQL functions ----------------
string _Symbol = "XAUUSD";
ENUM_TIMEFRAMES _Period = PERIOD_M1;
inline double MathAbs(double x) { return std::fabs(x); }
inline double MathFloor(double x) { return std::floor(x); }
inline double MathCeil(double x) { return std::ceil(x); }
inline double MathRound(double x) { return std::round(x); }
inline double MathMax(double a, double b) { return a > b ? a : b; }
inline double MathMin(double a, double b) { return a < b ? a : b; }
inline double NormalizeDouble(double x, int d) { double p = std::pow(10.0, d); return std::round(x * p) / p; }
inline string IntegerToString(long v, int = 0, ushort = ' ') { return std::to_string(v); }
inline string DoubleToString(double v, int d = 8) { char b[64]; snprintf(b, 64, "%.*f", d, v); return b; }
inline int    StringLen(const string &s) { return (int)s.size(); }
inline string StringSubstr(const string &s, int p, int n = -1) { if (p < 0 || p >= (int)s.size()) return ""; return n < 0 ? s.substr(p) : s.substr(p, n); }
inline int    StringFind(const string &s, const string &f, int st = 0) { size_t r = s.find(f, st); return r == string::npos ? -1 : (int)r; }
inline long   StringToInteger(const string &s) { return atol(s.c_str()); }
inline ushort StringGetCharacter(const string &s, int i) { return (i >= 0 && i < (int)s.size()) ? (ushort)(unsigned char)s[i] : 0; }
inline int    StringReplace(string &s, const string &a, const string &b) { int n = 0; size_t p = 0; while ((p = s.find(a, p)) != string::npos) { s.replace(p, a.size(), b); p += b.size(); n++; } return n; }
inline int    StringSplit(const string &s, ushort sep, MqlArr<string> &out) { out.v.clear(); string cur; for (char ch : s) { if ((ushort)ch == sep) { out.v.push_back(cur); cur = ""; } else cur += ch; } out.v.push_back(cur); return (int)out.v.size(); }
template <class E> string EnumToString(E e) { return "PERIOD_" + std::to_string((int)e); }
namespace sim { int verbose = 0; FILE *printTo = nullptr; }   // printTo: where Print writes (default stderr)
inline void PutOne(std::string &o, const std::string &x) { o += x; }
inline void PutOne(std::string &o, const char *x) { o += x; }
template <class T> void PutOne(std::string &o, T x) { o += std::to_string(x); }
template <class... A> void Print(A... a) { if (!sim::verbose) return; std::string o; (PutOne(o, a), ...); fprintf(sim::printTo ? sim::printTo : stderr, "PRINT %s\n", o.c_str()); }
template <class... A> void PrintFormat(A... a) { }
template <class... A> void Alert(A... a) { std::string o; (PutOne(o, a), ...); fprintf(stderr, "ALERT %s\n", o.c_str()); }
inline void Comment(const string &) { }
inline bool EventSetTimer(int) { return true; }
inline void EventKillTimer() { }
inline long MQLInfoInteger(ENUM_MQL_INFO_INTEGER p) { return p == MQL_TESTER ? sim::tester : 0; }
inline int  PeriodSeconds(ENUM_TIMEFRAMES tf) { return TfSec(tf); }
inline datetime TimeCurrent() { return sim::now; }
inline datetime TimeTradeServer() { return sim::now; }
// FxPro clock: UTC+2, UTC+3 in European summer time (last Sunday of March 01:00 UTC .. last Sunday of October 01:00 UTC)
namespace sim {
   inline long Days(int y, int m, int d) { int yy = m <= 2 ? y - 1 : y; long era = (yy >= 0 ? yy : yy - 399) / 400; long yoe = yy - era * 400; int mp = m > 2 ? m - 3 : m + 9;
      long doy = (153 * mp + 2) / 5 + d - 1; long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy; return era * 146097 + doe - 719468; }
   inline long LastSun(int y, int m) { long dl = Days(m == 12 ? y + 1 : y, m == 12 ? 1 : m + 1, 1) - 1; long w = ((dl + 4) % 7 + 7) % 7; return dl - w; }
   inline int  YearOf(long utc) { long z = (utc >= 0 ? utc : utc - 86399) / 86400; int y = 1970; while (Days(y + 1, 1, 1) <= z) y++; while (Days(y, 1, 1) > z) y--; return y; }
   inline long EuOff(long utc) { int y = YearOf(utc); long s = LastSun(y, 3) * 86400 + 3600, e = LastSun(y, 10) * 86400 + 3600; return (utc >= s && utc < e) ? 10800 : 7200; }
   inline long SrvToUtc(long srv) { long u = srv - 7200; return srv - EuOff(u); }
}
inline datetime TimeGMT() { return sim::SrvToUtc(sim::now); }
inline string TimeToString(datetime t, int = 0) { return std::to_string(t); }
inline double SymbolInfoDouble(const string &, ENUM_SYMBOL_INFO_DOUBLE p)
{
   switch (p) { case SYMBOL_TRADE_TICK_VALUE: return 1.0; case SYMBOL_TRADE_TICK_SIZE: return 0.01; case SYMBOL_TRADE_CONTRACT_SIZE: return sim::contract;
                case SYMBOL_VOLUME_MIN: return 0.01; case SYMBOL_VOLUME_MAX: return 10000.0; case SYMBOL_VOLUME_STEP: return 0.01; case SYMBOL_POINT: return 0.01;
                case SYMBOL_BID: return sim::bid; case SYMBOL_ASK: return sim::ask; }
   return 0;
}
namespace sim { int calcMode = SYMBOL_CALC_MODE_CFDLEVERAGE; string curBase = "XAU", curProfit = "USD"; }
inline long SymbolInfoInteger(const string &, ENUM_SYMBOL_INFO_INTEGER p) { return p == SYMBOL_DIGITS ? 2 : (p == SYMBOL_EXPIRATION_MODE ? 3 : (p == SYMBOL_TRADE_CALC_MODE ? sim::calcMode : 0)); }
inline string SymbolInfoString(const string &, ENUM_SYMBOL_INFO_STRING p) { return p == SYMBOL_CURRENCY_BASE ? sim::curBase : sim::curProfit; }
inline long SeriesInfoInteger(const string &, ENUM_TIMEFRAMES, ENUM_SERIES_INFO_INTEGER) { return 1; }
inline double Floating() { double f = 0; for (auto &p : sim::pos) f += (p.dir == 1 ? sim::bid - p.price : p.price - sim::ask) * p.dir * p.dir * p.vol * sim::contract; return f; }
inline double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE p) { return p == ACCOUNT_BALANCE ? sim::balance : sim::balance + Floating(); }
inline long   AccountInfoInteger(ENUM_ACCOUNT_INFO_INTEGER) { return ACCOUNT_MARGIN_MODE_RETAIL_HEDGING; }
inline datetime iTime(const string &, ENUM_TIMEFRAMES tf, int shift) { int n = VisibleCount(tf); if (shift < 0 || shift >= n) return 0; return BarsOf(tf)[n - 1 - shift].t; }
// the high / low of a bar; shift 0 = the bar forming now: only the part of it up to this tick (curHi / curLo = this minute so far)
namespace sim { double curHi = 0, curLo = 0; std::function<void(double, double, datetime)> onDrop; }   // onDrop: a test hook (v12.3 catch-up)
inline double iHiLo(ENUM_TIMEFRAMES tf, int shift, bool hi)
{
   int n = VisibleCount(tf);
   if (shift < 0 || shift >= n) return 0;
   SimBar b = BarsOf(tf)[n - 1 - shift];
   if (shift > 0) return hi ? b.h : b.l;
   double h = sim::curHi, l = sim::curLo;
   for (size_t i = sim::curBar; i-- > 0 && sim::m1[i].t >= b.t; ) { h = std::max(h, sim::m1[i].h); l = std::min(l, sim::m1[i].l); }
   return hi ? h : l;
}
inline double iHigh(const string &, ENUM_TIMEFRAMES tf, int shift) { return iHiLo(tf, shift, true); }
inline double iLow(const string &, ENUM_TIMEFRAMES tf, int shift) { return iHiLo(tf, shift, false); }
inline int iBarShift(const string &, ENUM_TIMEFRAMES tf, datetime t, bool exact = false)
{
   std::vector<SimBar> &v = BarsOf(tf);
   int n = VisibleCount(tf);
   auto it = std::upper_bound(v.begin(), v.begin() + n, t, [](datetime x, const SimBar &b) { return x < b.t; });
   int i = (int)(it - v.begin()) - 1;
   if (i < 0) return -1;
   if (exact && v[i].t != t) return -1;
   return n - 1 - i;
}
inline int CopyRatesIdx(ENUM_TIMEFRAMES tf, int first, int last, MqlArr<MqlRates> &out)
{
   out.v.clear();
   for (int i = first; i <= last; i++) { SimBar b = VisibleBar(tf, i); out.v.push_back(MqlRates{b.t, b.o, b.h, b.l, b.c, 0, 0, 0}); }
   return (int)out.v.size();
}
inline int CopyRates(const string &, ENUM_TIMEFRAMES tf, int start, int count, MqlArr<MqlRates> &out)
{
   int n = VisibleCount(tf);
   int last = n - 1 - start, first = std::max(0, last - count + 1);
   if (last < 0) { out.v.clear(); return -1; }
   return CopyRatesIdx(tf, first, last, out);
}
inline int CopyRates(const string &, ENUM_TIMEFRAMES tf, datetime start, int count, MqlArr<MqlRates> &out)
{
   std::vector<SimBar> &v = BarsOf(tf);
   int n = VisibleCount(tf);
   auto it = std::upper_bound(v.begin(), v.begin() + n, start, [](datetime x, const SimBar &b) { return x < b.t; });
   int last = (int)(it - v.begin()) - 1;
   if (last < 0) { out.v.clear(); return -1; }
   return CopyRatesIdx(tf, std::max(0, last - count + 1), last, out);
}
inline int CopyRates(const string &, ENUM_TIMEFRAMES tf, datetime from, datetime to, MqlArr<MqlRates> &out)
{
   std::vector<SimBar> &v = BarsOf(tf);
   int n = VisibleCount(tf);
   out.v.clear();
   auto a = std::lower_bound(v.begin(), v.begin() + n, from, [](const SimBar &b, datetime x) { return b.t < x; });
   for (auto it = a; it != v.begin() + n && it->t <= to; ++it) { SimBar b = VisibleBar(tf, (int)(it - v.begin())); out.v.push_back(MqlRates{b.t, b.o, b.h, b.l, b.c, 0, 0, 0}); }
   return (int)out.v.size();
}
// global variables
inline bool     GlobalVariableCheck(const string &n) { return sim::gv.count(n) > 0; }
inline double   GlobalVariableGet(const string &n) { auto it = sim::gv.find(n); return it == sim::gv.end() ? 0 : it->second; }
inline datetime GlobalVariableSet(const string &n, double v) { sim::gv[n] = v; return sim::now; }
inline bool     GlobalVariableDel(const string &n) { return sim::gv.erase(n) > 0; }
inline int      GlobalVariablesTotal() { return (int)sim::gv.size(); }
inline string   GlobalVariableName(int i) { auto it = sim::gv.begin(); std::advance(it, i); return it->first; }
// chart objects: ignored
// chart objects: kept by name (time, price, text, tooltip, colour, anchor, font size) so the tests can read them back
struct SimObj { int type; datetime t; double p; string text, tip; long col, anchor, fsize; };
namespace sim { std::map<string, SimObj> objs; long chartBg = 0; }
inline int  ObjectFind(long, const string &n) { return sim::objs.count(n) ? 0 : -1; }
inline bool ObjectCreate(long, const string &n, ENUM_OBJECT ty, int, datetime t, double p, datetime = 0, double = 0) { sim::objs[n] = SimObj{(int)ty, t, p, "", "", 0, 0, 0}; return true; }
inline bool ObjectMove(long, const string &n, int pt, datetime t, double p) { auto it = sim::objs.find(n); if (it != sim::objs.end() && pt == 0) { it->second.t = t; it->second.p = p; } return true; }
inline bool ObjectSetInteger(long, const string &n, ENUM_OBJECT_PROPERTY_INTEGER pr, long v)
{
   auto it = sim::objs.find(n);
   if (it != sim::objs.end()) { if (pr == OBJPROP_COLOR) it->second.col = v; else if (pr == OBJPROP_ANCHOR) it->second.anchor = v; else if (pr == OBJPROP_FONTSIZE) it->second.fsize = v; }
   return true;
}
inline bool ObjectSetString(long, const string &n, ENUM_OBJECT_PROPERTY_STRING p, const string &v)
{
   if (p == OBJPROP_TEXT) { sim::tblChars += (long)v.size(); if (v.empty()) { fprintf(stderr, "EMPTY LABEL TEXT\n"); exit(3); } }
   auto it = sim::objs.find(n);
   if (it != sim::objs.end()) { if (p == OBJPROP_TEXT) it->second.text = v; else if (p == OBJPROP_TOOLTIP) it->second.tip = v; }
   return true;
}
inline string ObjectGetString(long, const string &n, ENUM_OBJECT_PROPERTY_STRING p, int = 0)
{
   auto it = sim::objs.find(n);
   if (it == sim::objs.end()) return "";
   return p == OBJPROP_TEXT ? it->second.text : (p == OBJPROP_TOOLTIP ? it->second.tip : string(""));
}
inline bool ObjectDelete(long, const string &n) { sim::objs.erase(n); return true; }
inline int  ObjectsDeleteAll(long, const string &pre) { int k = 0; for (auto it = sim::objs.begin(); it != sim::objs.end();) { if (it->first.compare(0, pre.size(), pre) == 0) { it = sim::objs.erase(it); k++; } else ++it; } return k; }
inline int  ObjectsTotal(long, int = -1, int ty = -1) { int k = 0; for (auto &o : sim::objs) if (ty < 0 || o.second.type == ty) k++; return k; }
inline string ObjectName(long, int pos, int = -1, int ty = -1) { int k = 0; for (auto &o : sim::objs) if (ty < 0 || o.second.type == ty) { if (k == pos) return o.first; k++; } return ""; }
inline long ChartGetInteger(long, ENUM_CHART_PROPERTY_INTEGER p, int = 0) { return p == CHART_COLOR_BACKGROUND ? sim::chartBg : (p == CHART_WIDTH_IN_PIXELS ? 1400 : 700); }
inline void ChartRedraw(long = 0) { }
inline bool TextSetFont(const string &, int, uint = 0, int = 0) { return true; }
inline bool TextGetSize(const string &t, uint &w, uint &h) { w = (uint)t.size() * 7; h = 14; return true; }
// positions
inline int   PositionsTotal() { return (int)sim::pos.size(); }
inline ulong PositionGetTicket(int i) { if (i < 0 || i >= (int)sim::pos.size()) return 0; sim::selPos = i; return sim::pos[i].ticket; }
inline bool  PositionSelectByTicket(ulong t) { for (size_t i = 0; i < sim::pos.size(); i++) if (sim::pos[i].ticket == t) { sim::selPos = (int)i; return true; } return false; }
inline long  PositionGetInteger(ENUM_POSITION_PROPERTY_INTEGER p)
{
   SimPos &x = sim::pos.at(sim::selPos);
   switch (p) { case POSITION_IDENTIFIER: return (long)x.ticket; case POSITION_MAGIC: return x.magic; case POSITION_TIME: return x.time; case POSITION_TYPE: return x.dir == 1 ? POSITION_TYPE_BUY : POSITION_TYPE_SELL; }
   return 0;
}
inline double PositionGetDouble(ENUM_POSITION_PROPERTY_DOUBLE p) { SimPos &x = sim::pos.at(sim::selPos); switch (p) { case POSITION_SL: return x.sl; case POSITION_TP: return x.tp; case POSITION_VOLUME: return x.vol; case POSITION_PRICE_OPEN: return x.price;
   case POSITION_PROFIT: return ((x.dir == 1 ? sim::bid : sim::ask) - x.price) * x.dir * x.vol * sim::contract; case POSITION_SWAP: return 0; } return 0; }
inline string PositionGetString(ENUM_POSITION_PROPERTY_STRING p) { SimPos &x = sim::pos.at(sim::selPos); return p == POSITION_SYMBOL ? sim::sym : x.cmt; }
// orders
inline int   OrdersTotal() { return (int)sim::ords.size(); }
inline ulong OrderGetTicket(int i) { if (i < 0 || i >= (int)sim::ords.size()) return 0; sim::selOrd = i; return sim::ords[i].ticket; }
inline bool  OrderSelect(ulong t) { for (size_t i = 0; i < sim::ords.size(); i++) if (sim::ords[i].ticket == t) { sim::selOrd = (int)i; return true; } return false; }
inline long  OrderGetInteger(ENUM_ORDER_PROPERTY_INTEGER p) { SimOrd &x = sim::ords.at(sim::selOrd); return p == ORDER_MAGIC ? x.magic : ORDER_STATE_PLACED; }
inline double OrderGetDouble(ENUM_ORDER_PROPERTY_DOUBLE p) { SimOrd &x = sim::ords.at(sim::selOrd); switch (p) { case ORDER_VOLUME_CURRENT: return x.vol; case ORDER_PRICE_OPEN: return x.price; case ORDER_SL: return x.sl; case ORDER_TP: return x.tp; } return 0; }
inline string OrderGetString(ENUM_ORDER_PROPERTY_STRING p) { SimOrd &x = sim::ords.at(sim::selOrd); return p == ORDER_SYMBOL ? sim::sym : x.cmt; }
inline bool  HistoryOrderSelect(ulong t) { return sim::ordState.count(t) > 0; }
inline long  HistoryOrderGetInteger(ulong t, ENUM_ORDER_PROPERTY_INTEGER) { return sim::ordState[t]; }
// deals
inline bool  HistorySelect(datetime a, datetime b) { sim::selDeals.clear(); for (size_t i = 0; i < sim::deals.size(); i++) if (sim::deals[i].time >= a && sim::deals[i].time <= b) sim::selDeals.push_back((int)i); return true; }
inline bool  HistorySelectByPosition(long pid) { sim::selDeals.clear(); for (size_t i = 0; i < sim::deals.size(); i++) if ((long)sim::deals[i].pid == pid) sim::selDeals.push_back((int)i); return true; }
inline int   HistoryDealsTotal() { return (int)sim::selDeals.size(); }
inline ulong HistoryDealGetTicket(int i) { return sim::deals.at(sim::selDeals.at(i)).ticket; }
inline SimDeal &DealOf(ulong t) { for (auto &d : sim::deals) if (d.ticket == t) return d; static SimDeal z; return z; }
inline long  HistoryDealGetInteger(ulong t, ENUM_DEAL_PROPERTY_INTEGER p)
{
   SimDeal &d = DealOf(t);
   switch (p) { case DEAL_MAGIC: return d.magic; case DEAL_TYPE: return d.type; case DEAL_ENTRY: return d.entry; case DEAL_TIME: return d.time; case DEAL_POSITION_ID: return (long)d.pid; case DEAL_REASON: return d.reason; }
   return 0;
}
inline double HistoryDealGetDouble(ulong t, ENUM_DEAL_PROPERTY_DOUBLE p)
{
   SimDeal &d = DealOf(t);
   switch (p) { case DEAL_PROFIT: return d.profit; case DEAL_COMMISSION: return d.comm; case DEAL_SWAP: return 0; case DEAL_FEE: return 0; case DEAL_VOLUME: return d.vol; case DEAL_PRICE: return d.price; }
   return 0;
}
inline string HistoryDealGetString(ulong t, ENUM_DEAL_PROPERTY_STRING p) { SimDeal &d = DealOf(t); return p == DEAL_SYMBOL ? sim::sym : d.cmt; }

// ---------------- the fake broker ----------------
inline void AddDeal(int dir, int entry, int reason, ulong pid, double vol, double price, double profit, const string &cmt, long magic)
{
   SimDeal d;
   d.ticket = sim::nextTicket++; d.time = sim::now; d.type = dir == 1 ? DEAL_TYPE_BUY : DEAL_TYPE_SELL; d.entry = entry; d.reason = reason; d.pid = pid;
   d.vol = vol; d.price = price; d.profit = profit; d.comm = -sim::commPerLot * vol; d.cmt = cmt; d.magic = magic;
   sim::deals.push_back(d);
   sim::balance += profit + d.comm;
   sim::pendingTx.push_back(d.ticket);
}
inline void OpenPos(int dir, double vol, double price, double sl, double tp, const string &cmt, long magic, ulong ticket)
{
   SimPos p; p.ticket = ticket; p.dir = dir; p.vol = vol; p.price = price; p.sl = sl; p.tp = tp; p.time = sim::now; p.cmt = cmt; p.magic = magic;
   sim::pos.push_back(p);
   AddDeal(dir, DEAL_ENTRY_IN, DEAL_REASON_EXPERT, ticket, vol, price, 0, cmt, magic);
   sim::nFills++;
}
inline void ClosePosAt(size_t i, double price, int reason)
{
   SimPos p = sim::pos[i];
   double profit = (price - p.price) * p.dir * p.vol * sim::contract;
   sim::pos.erase(sim::pos.begin() + i);
   AddDeal(-p.dir, DEAL_ENTRY_OUT, reason, p.ticket, p.vol, price, profit, reason == DEAL_REASON_SL ? "[sl]" : (reason == DEAL_REASON_TP ? "[tp]" : ""), p.magic);
}
// one tick: pending orders, then stops / targets. A level crossed between two ticks of the same bar fills AT the level
// (TradingView's path); a level already passed on the first tick of a bar (a gap) fills at that tick.
inline void BrokerTick()
{
   double px = sim::bid;
   for (size_t i = 0; i < sim::ords.size();)
   {
      SimOrd o = sim::ords[i];
      bool hit = o.dir == 1 ? sim::ask <= o.price : sim::bid >= o.price;
      if (hit)
      {
         double f = sim::firstTickOfBar ? (o.dir == 1 ? sim::ask : sim::bid) : o.price;
         if (!sim::firstTickOfBar && (o.dir == 1 ? sim::prevPx <= o.price : sim::prevPx >= o.price)) f = o.dir == 1 ? sim::ask : sim::bid;
         sim::ords.erase(sim::ords.begin() + i);
         sim::ordState[o.ticket] = ORDER_STATE_FILLED;
         OpenPos(o.dir, o.vol, f, o.sl, o.tp, o.cmt, o.magic, o.ticket);
      }
      else i++;
   }
   for (size_t i = 0; i < sim::pos.size();)
   {
      SimPos &p = sim::pos[i];
      double cp = p.dir == 1 ? sim::bid : sim::ask;
      bool slHit = p.sl > 0 && (p.dir == 1 ? cp <= p.sl : cp >= p.sl);
      bool tpHit = p.tp > 0 && (p.dir == 1 ? cp >= p.tp : cp <= p.tp);
      if (slHit || tpHit)
      {
         double lvl = slHit ? p.sl : p.tp;
         bool gap = sim::firstTickOfBar || (slHit ? (p.dir == 1 ? sim::prevPx <= lvl : sim::prevPx >= lvl) : (p.dir == 1 ? sim::prevPx >= lvl : sim::prevPx <= lvl));
         ClosePosAt(i, gap ? cp : lvl, slHit ? DEAL_REASON_SL : DEAL_REASON_TP);
      }
      else i++;
   }
   (void)px;
}
class CTrade
{
public:
   long magic = 0; uint rc = 0; ulong order = 0;
   void SetExpertMagicNumber(ulong m) { magic = (long)m; }
   void SetDeviationInPoints(ulong) { }
   bool SetTypeFillingBySymbol(const string &) { return true; }
   void SetMarginMode() { }
   void LogLevel(ENUM_LOG_LEVELS) { }
   uint ResultRetcode() { return rc; }
   ulong ResultOrder() { return order; }
   string ResultRetcodeDescription() { return "rc " + std::to_string(rc); }
   bool Market(int dir, double vol, double sl, double tp, const string &cmt)
   {
      double cp = dir == 1 ? sim::bid : sim::ask;
      if ((sl > 0 && (dir == 1 ? sl >= cp : sl <= cp)) || (tp > 0 && (dir == 1 ? tp <= cp : tp >= cp))) { rc = TRADE_RETCODE_INVALID_STOPS; return false; }
      if (vol < 0.01 - 1e-9) { rc = TRADE_RETCODE_INVALID_VOLUME; return false; }
      ulong t = sim::nextTicket++;
      OpenPos(dir, vol, dir == 1 ? sim::ask : sim::bid, sl, tp, cmt, magic, t);
      sim::ordState[t] = ORDER_STATE_FILLED;
      rc = TRADE_RETCODE_DONE; order = t; return true;
   }
   bool Buy(double vol, const string &, double, double sl, double tp, const string &cmt) { return Market(1, vol, sl, tp, cmt); }
   bool Sell(double vol, const string &, double, double sl, double tp, const string &cmt) { return Market(-1, vol, sl, tp, cmt); }
   bool Limit(int dir, double vol, double price, double sl, double tp, const string &cmt)
   {
      if (dir == 1 ? price >= sim::ask : price <= sim::bid) { rc = TRADE_RETCODE_INVALID_PRICE; return false; }
      if ((sl > 0 && (dir == 1 ? sl >= price : sl <= price)) || (tp > 0 && (dir == 1 ? tp <= price : tp >= price))) { rc = TRADE_RETCODE_INVALID_STOPS; return false; }
      ulong t = sim::nextTicket++;
      sim::ords.push_back(SimOrd{t, dir, vol, price, sl, tp, cmt, magic});
      sim::ordState[t] = ORDER_STATE_PLACED;
      rc = TRADE_RETCODE_DONE; order = t; return true;
   }
   bool BuyLimit(double vol, double price, const string &, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string &cmt) { return Limit(1, vol, price, sl, tp, cmt); }
   bool SellLimit(double vol, double price, const string &, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string &cmt) { return Limit(-1, vol, price, sl, tp, cmt); }
   bool OrderModify(ulong t, double price, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, double = 0)
   {
      for (auto &o : sim::ords) if (o.ticket == t)
      {
         if (o.dir == 1 ? price >= sim::ask : price <= sim::bid) { rc = TRADE_RETCODE_INVALID_PRICE; return false; }
         o.price = price; o.sl = sl; o.tp = tp; rc = TRADE_RETCODE_DONE; return true;
      }
      rc = TRADE_RETCODE_INVALID; return false;
   }
   bool OrderDelete(ulong t)
   {
      for (size_t i = 0; i < sim::ords.size(); i++) if (sim::ords[i].ticket == t) { sim::ords.erase(sim::ords.begin() + i); sim::ordState[t] = ORDER_STATE_CANCELED; rc = TRADE_RETCODE_DONE; return true; }
      rc = TRADE_RETCODE_INVALID; return false;
   }
   bool PositionClose(ulong t, ulong = ULONG_MAX)
   {
      for (size_t i = 0; i < sim::pos.size(); i++) if (sim::pos[i].ticket == t) { ClosePosAt(i, sim::pos[i].dir == 1 ? sim::bid : sim::ask, DEAL_REASON_EXPERT); rc = TRADE_RETCODE_DONE; return true; }
      rc = TRADE_RETCODE_POSITION_CLOSED; return false;
   }
   bool PositionModify(ulong t, double sl, double tp)
   {
      for (auto &p : sim::pos) if (p.ticket == t)
      {
         double cp = p.dir == 1 ? sim::bid : sim::ask;
         if (sl > 0 && (p.dir == 1 ? sl >= cp : sl <= cp)) { rc = TRADE_RETCODE_INVALID_STOPS; return false; }
         p.sl = sl; p.tp = tp; rc = TRADE_RETCODE_DONE; return true;
      }
      rc = TRADE_RETCODE_POSITION_CLOSED; return false;
   }
};

// ---------------- economic calendar and files (group 41) ----------------
enum ENUM_CALENDAR_EVENT_TYPE { CALENDAR_TYPE_EVENT, CALENDAR_TYPE_INDICATOR, CALENDAR_TYPE_HOLIDAY };
enum ENUM_CALENDAR_EVENT_IMPORTANCE { CALENDAR_IMPORTANCE_NONE, CALENDAR_IMPORTANCE_LOW, CALENDAR_IMPORTANCE_MODERATE, CALENDAR_IMPORTANCE_HIGH };
enum ENUM_CALENDAR_EVENT_TIMEMODE { CALENDAR_TIMEMODE_DATETIME, CALENDAR_TIMEMODE_DATE, CALENDAR_TIMEMODE_NOTIME, CALENDAR_TIMEMODE_TENTATIVE };
enum ENUM_CALENDAR_EVENT_UNIT { CALENDAR_UNIT_NONE, CALENDAR_UNIT_PERCENT, CALENDAR_UNIT_CURRENCY, CALENDAR_UNIT_HOUR, CALENDAR_UNIT_JOB };
enum ENUM_CALENDAR_EVENT_MULTIPLIER { CALENDAR_MULTIPLIER_NONE, CALENDAR_MULTIPLIER_THOUSANDS, CALENDAR_MULTIPLIER_MILLIONS, CALENDAR_MULTIPLIER_BILLIONS, CALENDAR_MULTIPLIER_TRILLIONS };
enum ENUM_CALENDAR_EVENT_IMPACT { CALENDAR_IMPACT_NA, CALENDAR_IMPACT_POSITIVE, CALENDAR_IMPACT_NEGATIVE };
struct MqlCalendarValue { ulong id, event_id; datetime time, period; int revision; long actual_value, prev_value, revised_prev_value, forecast_value; ENUM_CALENDAR_EVENT_IMPACT impact_type; };
struct MqlCalendarEvent { ulong id; ENUM_CALENDAR_EVENT_TYPE type; int sector, frequency; ENUM_CALENDAR_EVENT_TIMEMODE time_mode; ulong country_id; ENUM_CALENDAR_EVENT_UNIT unit;
                          ENUM_CALENDAR_EVENT_IMPORTANCE importance; ENUM_CALENDAR_EVENT_MULTIPLIER multiplier; uint digits; string source_url, event_code, name; };
struct MqlDateTime { int year, mon, day, hour, min, sec, day_of_week, day_of_year; };
namespace sim {
   struct CalEv { long utc; string cur; int imp, typ; bool exact; string name; ulong eid; long fc = LONG_MIN, ac = LONG_MIN; int impact = 0, pct = 0, mult = 0, dig = 0; };
   std::vector<CalEv> cal;        // the fake MT5 calendar (UTC; a holiday at 00:00 UTC of its date)
   int  calMode = 0;              // times shown: 0 = on the broker clock with its summer time rule, 1 = with the broker offset at the moment of the request
   bool calFail = false;          // the calendar does not answer
   long calFailN = 0;             // the first N requests do not answer
   long calCalls = 0;
   string fileDir = "simfiles/";
   std::map<int, FILE *> files;
   int nextFile = 1;
}
inline bool CalendarValueHistory(MqlArr<MqlCalendarValue> &v, datetime from, datetime to, const char *country, const string &cur)
{
   v.v.clear();
   sim::calCalls++;
   if (sim::calFail || sim::calCalls <= sim::calFailN) return false;
   long offNow = sim::EuOff(sim::SrvToUtc(sim::now));
   for (auto &e : sim::cal)
   {
      if (!cur.empty() && e.cur != cur) continue;
      long srv = e.utc + (sim::calMode == 0 || e.typ == 2 ? sim::EuOff(e.utc) : offNow);
      if (srv < from || (to != 0 && srv > to)) continue;
      MqlCalendarValue x{};
      x.id = v.v.size() + 1; x.event_id = e.eid; x.time = srv;
      bool out = e.utc <= sim::SrvToUtc(sim::now);   // like MT5: the actual number only after the release
      x.forecast_value = e.fc; x.prev_value = LONG_MIN; x.revised_prev_value = LONG_MIN;
      x.actual_value = out ? e.ac : LONG_MIN; x.impact_type = out ? (ENUM_CALENDAR_EVENT_IMPACT)e.impact : CALENDAR_IMPACT_NA;
      v.v.push_back(x);
   }
   return true;
}
inline bool CalendarEventById(ulong id, MqlCalendarEvent &ev)
{
   for (auto &e : sim::cal) if (e.eid == id)
   {
      ev = MqlCalendarEvent{};
      ev.id = id;
      ev.type = e.typ == 2 ? CALENDAR_TYPE_HOLIDAY : (e.typ == 1 ? CALENDAR_TYPE_INDICATOR : CALENDAR_TYPE_EVENT);
      ev.importance = e.imp == 3 ? CALENDAR_IMPORTANCE_HIGH : (e.imp == 2 ? CALENDAR_IMPORTANCE_MODERATE : (e.imp == 1 ? CALENDAR_IMPORTANCE_LOW : CALENDAR_IMPORTANCE_NONE));
      ev.time_mode = e.typ == 2 ? CALENDAR_TIMEMODE_DATE : (e.exact ? CALENDAR_TIMEMODE_DATETIME : CALENDAR_TIMEMODE_TENTATIVE);
      ev.name = e.name;
      ev.unit = e.pct ? CALENDAR_UNIT_PERCENT : CALENDAR_UNIT_NONE;
      ev.multiplier = (ENUM_CALENDAR_EVENT_MULTIPLIER)e.mult;
      ev.digits = (uint)e.dig;
      return true;
   }
   return false;
}
const int FILE_READ = 1, FILE_WRITE = 2, FILE_BIN = 4, FILE_CSV = 8, FILE_TXT = 16, FILE_ANSI = 32, FILE_UNICODE = 64, FILE_SHARE_READ = 128, FILE_SHARE_WRITE = 256, FILE_COMMON = 4096;
const int INVALID_HANDLE = -1;
inline int FileOpen(const string &name, int flags)
{
   if (!(flags & FILE_COMMON)) { fprintf(stderr, "FileOpen without FILE_COMMON\n"); exit(4); }
   string p = sim::fileDir + name;
   FILE *f = fopen(p.c_str(), (flags & FILE_WRITE) ? "wb" : "rb");
   if (!f) return INVALID_HANDLE;
   int h = sim::nextFile++;
   sim::files[h] = f;
   return h;
}
inline uint   FileWriteString(int h, const string &s, int = -1) { fputs(s.c_str(), sim::files.at(h)); return (uint)s.size(); }
inline string FileReadString(int h, int = -1) { FILE *f = sim::files.at(h); string s; int c; while ((c = fgetc(f)) != EOF) { if (c == '\n') break; s += (char)c; } if (!s.empty() && s.back() == '\r') s.pop_back(); return s; }
inline bool   FileIsEnding(int h) { FILE *f = sim::files.at(h); int c = fgetc(f); if (c == EOF) return true; ungetc(c, f); return false; }
inline void   FileClose(int h) { fclose(sim::files.at(h)); sim::files.erase(h); }
inline int  StringTrimLeft(string &s)  { size_t i = 0; while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) i++; s.erase(0, i); return (int)i; }
inline int  StringTrimRight(string &s) { int n = 0; while (!s.empty() && (s.back() == ' ' || s.back() == '\t' || s.back() == '\r' || s.back() == '\n')) { s.pop_back(); n++; } return n; }
inline bool StringToUpper(string &s)   { for (auto &c : s) c = (char)toupper((unsigned char)c); return true; }
inline bool ArraySort(MqlArr<long> &a) { std::sort(a.v.begin(), a.v.end()); return true; }
inline void ResetLastError() { }
inline int  GetLastError() { return 0; }
inline bool TimeToStruct(datetime t, MqlDateTime &m) { long s = ((t % 86400) + 86400) % 86400; m = MqlDateTime{}; m.hour = (int)(s / 3600); m.min = (int)(s % 3600 / 60); m.sec = (int)(s % 60); return true; }
