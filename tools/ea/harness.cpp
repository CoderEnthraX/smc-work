// Offline test: the EA's core (extracted from the .mq5) + a TradingView-style broker emulator
// (the same rules as the Python simulator port111.py). Prints every closed trade.
#include <string>
#include <vector>
#include <map>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <algorithm>
typedef std::string string;
inline double MathAbs(double x)   { return std::fabs(x); }
inline double MathFloor(double x) { return std::floor(x); }
inline double MathCeil(double x)  { return std::ceil(x); }
inline double MathRound(double x) { return std::round(x); }
inline string IntegerToString(long v) { return std::to_string(v); }
inline string DoubleToString(double v, int d) { char b[64]; snprintf(b, sizeof(b), "%.*f", d, v); return string(b); }   // v12.0 notes
class CArrD { public: std::vector<double> v; void Clear() { v.clear(); } void Add(double x) { v.push_back(x); } double At(int i) { return v[i]; }
  int Size() { return (int)v.size(); } void DropFirst(int k) { if (k <= 0) return; if (k >= (int)v.size()) { v.clear(); return; } v.erase(v.begin(), v.begin() + k); }
  void RemoveAt(int i) { v.erase(v.begin() + i); } };
class CArrI { public: std::vector<int> v; void Clear() { v.clear(); } void Add(int x) { v.push_back(x); } int At(int i) { return v[i]; }
  int Size() { return (int)v.size(); } void DropFirst(int k) { if (k <= 0) return; if (k >= (int)v.size()) { v.clear(); return; } v.erase(v.begin(), v.begin() + k); }
  void RemoveAt(int i) { v.erase(v.begin() + i); } };

#include "core_x.inc"

// ---------------- emulator ----------------
struct POrd { int side, seq, piece, dir; double lim, q, sl, tgt; int pbar; double prisk; };
struct Tr { long id, xseq; int side, dir, seq, piece, ebar, xbar, pbar; long et, xt; double ep, q, sl, tgt, xp, pnl, prisk; string why; bool open, gap; };
std::vector<POrd> pend;
std::vector<Tr> trades;          // all trades; open ones have open = true
std::vector<int> opn;            // indexes into trades, in opening order
std::map<long, string> closeReq;
double comm = 0.3, eqClosed = 10000.0;
int curBar = 0;
long curT = 0;
long nextId = 1, nextX = 1;
bool verbose = false, fixTies = false, grid = false;
double GDn(double p) { return grid ? std::floor(p / 0.01 + 1e-7) / 100.0 : p; }
double GUp(double p) { return grid ? std::ceil(p / 0.01 - 1e-7) / 100.0 : p; }

void BkCancel(int side) { for (int i = (int)pend.size() - 1; i >= 0; i--) if (pend[i].side == side) pend.erase(pend.begin() + i); }
void BkCancelPiece(int side, int piece) { for (int i = (int)pend.size() - 1; i >= 0; i--) if (pend[i].side == side && pend[i].piece == piece) pend.erase(pend.begin() + i); }
void BkPlace(int side, int seq, int piece, int dir, double ent, double sl, double tgt, double q, bool mkt)
{
   double rk = g_money[g_sideMi[side]].riskNow * g_side[side].addRk;
   if (dir == 1) { ent = GDn(ent); sl = GDn(sl); tgt = GUp(tgt); } else { ent = GUp(ent); sl = GUp(sl); tgt = GDn(tgt); }
   if (mkt) ent = dir == 1 ? 1e300 : -1e300;   // v12.0: a market order = filled at the next open
   for (auto &p : pend) if (p.side == side && p.seq == seq && p.piece == piece) { p.dir = dir; p.lim = ent; p.sl = sl; p.tgt = tgt; p.q = q; p.pbar = curBar; p.prisk = rk; return; }
   pend.push_back(POrd{side, seq, piece, dir, ent, q, sl, tgt, curBar, rk});
}
void BkCloseAll(int side, string why) { for (int ix : opn) if (trades[ix].side == side) closeReq[trades[ix].id] = why; }
void BkSetStop(int side, long ticket, int dir, double sl, double tgt) { for (int ix : opn) if (trades[ix].id == ticket) trades[ix].sl = dir == 1 ? GDn(sl) : GUp(sl); }
void BkNote(int side, string msg) { if (verbose) printf("NOTE bar %d side %d: %s\n", curBar, side, msg.c_str()); }

void fillClose(int ix, double px, const char *why)
{
   Tr &t = trades[ix];
   t.xp = px; t.xbar = curBar; t.xt = curT; t.why = why; t.open = false; t.xseq = nextX++;
   t.pnl = (px - t.ep) * t.dir * t.q - 2 * comm * t.q;
   eqClosed += t.pnl;
   opn.erase(std::find(opn.begin(), opn.end(), ix));
}
void doFill(int pi, double price)
{
   POrd o = pend[pi];
   pend.erase(pend.begin() + pi);
   Tr t;
   t.id = nextId++; t.xseq = 0; t.side = o.side; t.dir = o.dir; t.seq = o.seq; t.piece = o.piece; t.ebar = curBar; t.xbar = -1; t.et = curT; t.xt = 0;
   t.ep = price; t.q = o.q; t.sl = o.sl; t.tgt = o.tgt; t.xp = 0; t.pnl = 0; t.why = ""; t.open = true; t.pbar = o.pbar; t.prisk = o.prisk; t.gap = price != o.lim;
   trades.push_back(t);
   opn.push_back((int)trades.size() - 1);
}
bool trigAt(double price)
{
   bool fired = false;
   for (int i = 0; i < (int)pend.size();)
   {
      POrd &o = pend[i];
      if ((o.dir == 1 && price <= o.lim) || (o.dir == -1 && price >= o.lim)) { doFill(i, price); fired = true; }
      else i++;
   }
   std::vector<int> cur = opn;
   for (int ix : cur)
   {
      Tr &t = trades[ix];
      if (!t.open) continue;
      if (t.dir == 1 && price <= t.sl) { fillClose(ix, price, "SL"); fired = true; }
      else if (t.dir == 1 && price >= t.tgt) { fillClose(ix, price, "TP"); fired = true; }
      else if (t.dir == -1 && price >= t.sl) { fillClose(ix, price, "SL"); fired = true; }
      else if (t.dir == -1 && price <= t.tgt) { fillClose(ix, price, "TP"); fired = true; }
   }
   return fired;
}
void brokerBar(double o, double h, double l, double c)
{
   std::vector<int> cur = opn;
   for (int ix : cur) { auto it = closeReq.find(trades[ix].id); if (it != closeReq.end()) fillClose(ix, o, it->second.c_str()); }
   closeReq.clear();
   double path[4];
   if (std::fabs(h - o) < std::fabs(o - l)) { path[0] = o; path[1] = h; path[2] = l; path[3] = c; }
   else { path[0] = o; path[1] = l; path[2] = h; path[3] = c; }
   trigAt(o);
   double curp = o;
   for (int seg = 1; seg < 4; seg++)
   {
      double a = curp, b = path[seg];
      while (true)
      {
         bool have = false; double lv = 0; int kind = 0; int which = -1;   // kind 0 entry (pend index), 1 SL, 2 TP (trade index)
         if (b < a)
         {
            for (int i = 0; i < (int)pend.size(); i++) { POrd &p = pend[i]; if (p.dir == 1 && b <= p.lim && p.lim < a && (!have || p.lim > lv)) { have = true; lv = p.lim; kind = 0; which = i; } }
            for (int ix : opn) { Tr &t = trades[ix];
               if (t.dir == 1 && b <= t.sl && t.sl < a && (!have || t.sl > lv)) { have = true; lv = t.sl; kind = 1; which = ix; }
               if (t.dir == -1 && b <= t.tgt && t.tgt < a && (!have || t.tgt > lv)) { have = true; lv = t.tgt; kind = 2; which = ix; } }
         }
         else if (b > a)
         {
            for (int i = 0; i < (int)pend.size(); i++) { POrd &p = pend[i]; if (p.dir == -1 && a < p.lim && p.lim <= b && (!have || p.lim < lv)) { have = true; lv = p.lim; kind = 0; which = i; } }
            for (int ix : opn) { Tr &t = trades[ix];
               if (t.dir == 1 && a < t.tgt && t.tgt <= b && (!have || t.tgt < lv)) { have = true; lv = t.tgt; kind = 2; which = ix; }
               if (t.dir == -1 && a < t.sl && t.sl <= b && (!have || t.sl < lv)) { have = true; lv = t.sl; kind = 1; which = ix; } }
         }
         if (!have) break;
         if (kind == 0)
         {
            int d = pend[which].dir;
            doFill(which, lv);
            for (int i = 0; i < (int)pend.size();) { if (pend[i].lim == lv && pend[i].dir == (b < a ? 1 : -1)) doFill(i, lv); else i++; }
            trigAt(lv);
            (void)d;
         }
         else { fillClose(which, lv, kind == 1 ? "SL" : "TP"); if (fixTies) trigAt(lv); }
         a = lv;
      }
      curp = b;
   }
}

// ---------------- config ----------------
std::map<string, string> cfg;
double cd(const char *k, double def) { auto it = cfg.find(k); return it == cfg.end() ? def : atof(it->second.c_str()); }
long   cl(const char *k, long def)   { auto it = cfg.find(k); return it == cfg.end() ? def : atol(it->second.c_str()); }
bool   cb(const char *k, bool def)   { auto it = cfg.find(k); return it == cfg.end() ? def : (it->second == "1" || it->second == "true" || it->second == "True"); }

int main(int argc, char **argv)
{
   if (argc < 3) { fprintf(stderr, "usage: harness config bars.bin [out.csv]\n"); return 1; }
   std::ifstream f(argv[1]); string line;
   while (std::getline(f, line)) { std::istringstream ss(line); string k, v; if (ss >> k >> v) cfg[k] = v; }
   FILE *bf = fopen(argv[2], "rb");
   fseek(bf, 0, SEEK_END); long nb = ftell(bf) / 40; fseek(bf, 0, SEEK_SET);
   std::vector<long> T(nb); std::vector<double> O(nb), H(nb), L(nb), C(nb);
   for (long i = 0; i < nb; i++) { long t; double p[4]; fread(&t, 8, 1, bf); fread(p, 8, 4, bf); T[i] = t; O[i] = p[0]; H[i] = p[1]; L[i] = p[2]; C[i] = p[3]; }
   fclose(bf);
   verbose = cb("verbose", false); fixTies = cb("fixTies", false); grid = cb("grid", false);
   // settings
   S.altMode = cb("altMode", false); S.pbBodyOn = cb("pbBodyOn", false); S.pbBodyRef = cb("pbBodyRef", false); S.pbSwp2 = cb("pbSwp2", false);
   S.on = true; S.r1 = cb("r1", true); S.r2 = cb("r2", true); S.sig = (int)cl("sig", 0);
   S.pb = cd("pb", 50); S.rr = cd("rr", 3); S.slBuf = cd("slBuf", 0); S.rev = cb("rev", true); S.once = cb("once", false);
   S.sessMode = (int)cl("sessMode", 0); S.tzBase = cl("tzBase", 19800); S.tzRule = (int)cl("tzRule", 0);
   S.hrOn = (int)cl("hrOn", 6); S.hrOff = (int)cl("hrOff", 23); S.hrFlat = (int)cl("hrFlat", 2);
   S.sizeMode = 0; S.risk = cd("risk", 50); S.qty = 1; S.cash = 1000; S.lotStep = cd("lotStep", 0.01); S.rndMax = cd("rndMax", 25); S.lev = cd("lev", 30);
   S.seqMode = (int)cl("seqMode", 0); S.seqMax = cd("seqMax", 500); S.capAct = (int)cl("capAct", 2); S.seqAdd = cd("seqAdd", 50);
   S.seqFrom = (int)cl("seqFrom", 0); S.seqFromT = cl("seqFromT", 0); S.split = cd("split", 1);
   S.cmMode = 2; S.cmLot = cd("cmLot", 30); S.cmUnit = 100; S.cmPct = 0; S.cmFix = 0; S.cmTgt = cb("cmTgt", true);
   S.cancelSig = cb("cancelSig", true); S.expBars = (int)cl("expBars", 0); S.minStop = cd("minStop", 0); S.maxStop = cd("maxStop", 0);
   S.maxTrades = (int)cl("maxTrades", 0); S.dayLoss = cd("dayLoss", 0); S.dd = 0; S.wkFlat = cb("wkFlat", true); S.wkDay = (int)cl("wkDay", 6); S.wkHr = (int)cl("wkHr", 21);
   S.wk247 = false; S.bosCnl = cb("bosCnl", false);
   S.newsOn = cb("newsOn", true); S.nwExit = 0; S.nw1On = false; S.nw2On = false; S.nw3On = false; S.nw1A = S.nw1B = S.nw2A = S.nw2B = S.nw3A = S.nw3B = -1;
   S.sprd = 0; S.ptOn = false; S.ptAmt = 500; S.ptPer = 0; S.ptFrom = 0; S.ndOn = false; S.ndScope = 0;
   S.auOn = cb("auOn", false); S.auNfp = true; S.auJc = true; S.auIsmM = true; S.auIsmS = true; S.auPre = 10; S.auPost = 20; S.usClk = 0; S.nwNy = false; S.holTrade = true;
   S.maxOpen = (int)cl("maxOpen", 0); S.mvStep = cb("mvStep", false); S.mvBe = cb("mvBe", false); S.dirMode = (int)cl("dirMode", 0); S.hedgeMoney = (int)cl("hedgeMoney", 0);
   S.bkOn = cb("bkOn", false); S.bkPct = cd("bkPct", 50); S.hfOn = cb("hfOn", false); S.trOn = cb("trOn", false); S.trMode = (int)cl("trMode", 0);
   S.lqOn = cb("lqOn", false); S.lqMin = cd("lqMin", 1.5); S.ppOn = cb("ppOn", false); S.ppPct = cd("ppPct", 50); S.ppR = cd("ppR", 1); S.ppBe = cb("ppBe", true);
   S.pdOn = cb("pdOn", false); S.pdPct = cd("pdPct", 50); S.lsOn = cb("lsOn", false); S.lsN = (int)cl("lsN", 3);
   S.flMode = (int)cl("flMode", 0); S.flAmt = cd("flAmt", 2000); S.flLock = cd("flLock", 50); S.flPct = cd("flPct", 2.5);
   S.holTrade = cb("holTrade", true); S.auPre = (int)cl("auPre", 10); S.auPost = (int)cl("auPost", 20);
   S.calOn = cb("calOn", false); S.calHol = cb("calHol", true); S.calPre = (int)cl("calPre", 10); S.calPost = (int)cl("calPost", 20);
   S.preOn = cb("preOn", false); S.preSec = (long)std::llround(cd("preHrs", 1.0) * 3600.0);
   if (cfg.count("simCal"))
   {   // group 41: the news list straight into the core (the EA's MT5 part does the same from the MT5 calendar / the saved file)
      std::ifstream cf(cfg["simCal"]); string ln; std::vector<std::pair<long, int>> rec;   // (time, 0 news / 1 holiday)
      int imp2 = (int)cl("calImp", 0) == 1 ? 2 : 3;
      string cur = cfg.count("calCur") ? cfg["calCur"] : string("USD");
      while (std::getline(cf, ln))
      {
         if (ln.empty() || ln[0] == '#') continue;
         std::vector<string> f; std::stringstream ss(ln); string x; while (std::getline(ss, x, ',')) f.push_back(x);
         if (f.size() < 6 || f[2] != cur) continue;
         long t = atol(f[0].c_str()); int imp = atoi(f[3].c_str()), typ = atoi(f[4].c_str()); bool exact = f.size() < 7 || f[6] != "0";
         if (typ == 2) rec.push_back({t, 1});
         else if (imp >= imp2 && exact) rec.push_back({t, 0});
      }
      std::sort(rec.begin(), rec.end());
      for (auto &r : rec)
      {
         if (r.second == 1) { long dn = r.first / 86400; if (g_calHol.Size() == 0 || g_calHol.At(g_calHol.Size() - 1) != dn) g_calHol.Add((int)dn); }
         else if (g_calT.Size() == 0 || (long)g_calT.At(g_calT.Size() - 1) != r.first) g_calT.Add((double)r.first);
      }
   }
   S.buMode = (int)cl("buMode", 0); S.buPips = cd("buPips", 10.0); S.buPct = cd("buPct", 0.02); S.pipSz = cd("buPip", 0.1);
   S.r3On = cb("r3On", false); S.r3BrkOn = cb("r3BrkOn", false); S.r3Brk = cd("r3Brk", 3.0); S.r3Fb = cb("r3Fb", false); S.lmOn = cb("lmOn", false); S.lmAmt = cd("lmAmt", 300.0); S.pmOn = cb("pmOn", false); S.pmAmt = cd("pmAmt", 200.0);
   S.ldOn = cb("ldOn", false); S.ldN = (int)cl("ldN", 3); S.ldD = (int)cl("ldD", 2); S.eqOn = cb("eqOn", false); S.eqPct = cd("eqPct", 50);
   S.cs = (int)cl("cs", 60); S.cmLots = 100; S.uv = 1.0; S.minLot = cd("minLot", 0.01); S.tick = 0.01;
   long htfSec = cl("htfSec", 900);
   S.htfOk = htfSec > S.cs;
   comm = cd("comm", 0.3); eqClosed = cd("eq0", 10000);
   CoreSetup();
   for (int k = 0; k < 2; k++) g_money[k].liveT = LNONE;
   // higher timeframe: aggregate by t / htfSec, value for a bar = state after the previous higher-timeframe candle
   std::vector<int> hT(nb); std::vector<double> hO(nb), hX(nb); std::vector<int> hE(nb);
   {
      long curK = -1; double ao = 0, ah = 0, al = 0, ac = 0; bool have = false;
      int lt = 0; double lo = NAD, lx = NAD; int le = 0;
      for (long i = 0; i < nb; i++)
      {
         long kk = cb("htfSrv", false) ? (T[i] + TzOff(T[i], 7200, 1)) / htfSec : T[i] / htfSec;
         if (kk != curK)
         {
            if (have) { HT.Step(ao, ah, al, ac); lt = HT.tTrend; lo = HT.outO; lx = HT.outX; le = HT.evN; }
            curK = kk; ao = O[i]; ah = H[i]; al = L[i]; ac = C[i]; have = true;
         }
         else { ah = std::max(ah, H[i]); al = std::min(al, L[i]); ac = C[i]; }
         hT[i] = lt; hO[i] = lo; hX[i] = lx; hE[i] = le;
      }
   }
   long from = cl("from", 0), to = cl("to", nb);
   for (long i = 0; i < nb && i < to; i++)
   {
      curBar = (int)i; curT = T[i];
      brokerBar(O[i], H[i], L[i], C[i]);
      for (int k = 0; k < 2; k++) g_io[k].Clear();
      for (int ix : opn)
      {
         Tr &t = trades[ix];
         CSideIO &io = g_io[t.side];
         if (io.nPos >= MAXP) continue;
         PosRec &p = io.pos[io.nPos++];
         p.id = t.id; p.ticket = t.id; p.dir = t.dir; p.q = t.q; p.ent = t.ep; p.sl = t.sl; p.tgt = t.tgt; p.tOpen = t.et; p.seq = t.seq; p.piece = t.piece;
      }
      // fills of this bar (open or already closed) in opening order, closes in closing order
      std::vector<int> cl_;
      for (int ix = 0; ix < (int)trades.size(); ix++)
      {
         Tr &t = trades[ix];
         if (t.ebar == (int)i)
         {
            CSideIO &io = g_io[t.side];
            if (io.nFill < MAXF) { FillRec &f = io.fill[io.nFill++]; f.id = t.id; f.dir = t.dir; f.q = t.q; f.ent = t.ep; f.t = t.et; f.seq = t.seq; f.piece = t.piece; f.atOpen = t.gap; }
         }
         if (!t.open && t.xbar == (int)i) cl_.push_back(ix);
      }
      std::sort(cl_.begin(), cl_.end(), [](int a, int b) { return trades[a].xseq < trades[b].xseq; });
      for (int ix : cl_)
      {
         Tr &t = trades[ix];
         CSideIO &io = g_io[t.side];
         if (io.nCls >= MAXP) continue;
         ClsRec &c = io.cls[io.nCls++];
         c.id = t.id; c.dir = t.dir; c.q = t.q; c.pnl = t.pnl; c.tIn = t.et; c.tOut = t.xt; c.seq = t.seq; c.piece = t.piece;
         c.why = t.why == "SL" ? 1 : (t.why == "TP" ? 2 : 0);
      }
      double eq = eqClosed;
      for (int ix : opn) eq += (C[i] - trades[ix].ep) * trades[ix].dir * trades[ix].q;
      g_dry = i < from;
      CoreBar(T[i], O[i], H[i], L[i], C[i], eq, hT[i], hO[i], hX[i], hE[i]);
   }
   FILE *of = argc > 3 ? fopen(argv[3], "w") : stdout;
   fprintf(of, "side,dir,ebar,ep,q,xbar,xp,why,pnl,pbar,prisk,sl0\n");
   for (auto &t : trades) if (!t.open) fprintf(of, "%d,%d,%d,%.5f,%.4f,%d,%.5f,%s,%.6f,%d,%.6f,%.5f\n", t.side, t.dir, t.ebar, t.ep, t.q, t.xbar, t.xp, t.why.c_str(), t.pnl, t.pbar, t.prisk, t.sl);
   if (of != stdout) fclose(of);
   double net = 0; int n = 0; for (auto &t : trades) if (!t.open) { net += t.pnl; n++; }
   fprintf(stderr, "trades %d net %.2f\n", n, net);
   return 0;
}
