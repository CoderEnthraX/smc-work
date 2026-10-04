// Run the WHOLE EA (converted .mq5) inside the fake MetaTrader 5, tick by tick, and print every closed trade.
#include "ea_x.cpp"
#include <fstream>
#include <sstream>
#include <random>

std::map<string, string> cfg;
double cd(const char *k, double d) { auto it = cfg.find(k); return it == cfg.end() ? d : atof(it->second.c_str()); }
long   cl(const char *k, long d)   { auto it = cfg.find(k); return it == cfg.end() ? d : atol(it->second.c_str()); }
bool   cb(const char *k, bool d)   { auto it = cfg.find(k); return it == cfg.end() ? d : (it->second == "1" || it->second == "True" || it->second == "true"); }

int main(int argc, char **argv)
{
   if (argc < 4) { fprintf(stderr, "usage: simmain cfg bars.bin out.csv\n"); return 1; }
   std::ifstream f(argv[1]); string line;
   while (std::getline(f, line)) { std::istringstream ss(line); string k, v; if (ss >> k >> v) cfg[k] = v; }
   // the EA's settings (same keys as the core harness)
   InSig = (ESig)cl("sig", 0); InR1 = cb("r1", true); InR2 = cb("r2", true); InPb = cd("pb", 50); InRR = cd("rr", 3); InSlBuf = cd("slBuf", 0);
   InRev = cb("rev", true); InEntMode = cb("once", false) ? ENT_ONCE : ENT_CONT; InSessMode = (ESess)cl("sessMode", 0);
   InTzHours = cl("tzBase", 19800) / 3600.0; InTzDst = (EDst)cl("tzRule", 0); InHrOn = cl("hrOn", 6); InHrOff = cl("hrOff", 23); InHrFlat = cl("hrFlat", 2);
   InRisk = cd("risk", 50); InLotStep = cd("lotStep", 0.01); InRndMax = cd("rndMax", 25); InLev = cd("lev", 30);
   InSeqMode = (ESeq)cl("seqMode", 0); InSeqMax = cd("seqMax", 500); InCapAct = (ECap)cl("capAct", 2); InSeqAdd = cd("seqAdd", 50); InSplit = cd("split", 1);
   InSeqFrom = (ESeqFrom)cl("seqFrom", 0); InSeqFromT = cl("seqFromT", 0);
   InCmMode = CM_LOT; InCmLot = cd("cmLot", 30); InCmUnit = 100; InCmTgt = cb("cmTgt", true);
   InCancelSig = cb("cancelSig", true); InExpBars = cl("expBars", 0); InMinStop = cd("minStop", 0); InMaxStop = cd("maxStop", 0); InMaxTrades = cl("maxTrades", 0);
   InDayLoss = cd("dayLoss", 0); InWkFlat = cb("wkFlat", true); InWkDay = (EWkDay)cl("wkDay", 6); InWkHr = cl("wkHr", 21); InBosCnl = cb("bosCnl", false);
   InNewsOn = cb("newsOn", true); InAuOn = cb("auOn", false); InMaxOpen = cl("maxOpen", 0); InMvStep = cb("mvStep", false); InMvBe = cb("mvBe", false);
   InDirMode = (EDir)cl("dirMode", 0); InHedgeMoney = (EHedgeMoney)cl("hedgeMoney", 0);
   InBkOn = cb("bkOn", false); InBkPct = cd("bkPct", 50); InHfOn = cb("hfOn", false); InTrOn = cb("trOn", false); InTrMode = (ETrMode)cl("trMode", 0);
   InLqOn = cb("lqOn", false); InLqMin = cd("lqMin", 1.5); InPpOn = cb("ppOn", false); InPpPct = cd("ppPct", 50); InPpR = cd("ppR", 1); InPpBe = cb("ppBe", true);
   InPdOn = cb("pdOn", false); InPdPct = cd("pdPct", 50); InLsOn = cb("lsOn", false); InLsN = cl("lsN", 3);
   InFlMode = (EFl)cl("flMode", 0); InFlAmt = cd("flAmt", 2000); InFlLock = cd("flLock", 50); InFlPct = cd("flPct", 2.5);
   InLdOn = cb("ldOn", false); InLdN = cl("ldN", 3); InLdD = cl("ldD", 2); InEqOn = cb("eqOn", false); InEqPct = cd("eqPct", 50);
   InExec = (EExec)cl("exec", 0); InWarm = cl("warm", 100000000); InSrvHours = 2.0; InSrvDst = DST_EU; InDraw = false; InStatOn = false;
   sim::tester = (int)cl("tester", 1);
   sim::chartSec = (int)cl("chartSec", 60);
   _Period = sim::chartSec == 900 ? PERIOD_M15 : (sim::chartSec == 300 ? PERIOD_M5 : (sim::chartSec == 3600 ? PERIOD_H1 : PERIOD_M1));
   InHtf = (EHtf)cl("htf", 0);
   sim::balance = cd("eq0", 10000);
   sim::commPerLot = cd("comm", 0.3) * 100.0;
   sim::spread = cd("spread", 0.0);
   long restartEvery = cl("restartEvery", 0);
   // bars: UTC in the file -> server time (UTC+2, UTC+3 in European summer time)
   FILE *bf = fopen(argv[2], "rb");
   fseek(bf, 0, SEEK_END); long nb = ftell(bf) / 40; fseek(bf, 0, SEEK_SET);
   long to = cl("to", nb), from = cl("from", 20000);
   if (to > nb) to = nb;
   for (long i = 0; i < to; i++)
   {
      long t; double p[4];
      if (fread(&t, 8, 1, bf) != 1 || fread(p, 8, 4, bf) != 4) break;
      sim::m1.push_back(SimBar{(datetime)(t + TzOff(t, 7200, 1)), p[0], p[1], p[2], p[3]});
   }
   fclose(bf);
   std::mt19937 rng(12345);
   // start: the EA sees bars [0, from) as history
   sim::curBar = from;
   sim::now = sim::m1[from].t;
   sim::bid = sim::m1[from].o; sim::ask = sim::bid + sim::spread;
   if (OnInit() != INIT_SUCCEEDED) { fprintf(stderr, "OnInit failed\n"); return 1; }
   long nTicks = 0, restarts = 0;
   long nextRestart = restartEvery > 0 ? from + 1 + (long)(rng() % restartEvery) : -1;
   for (long i = from; i < (long)sim::m1.size(); i++)
   {
      SimBar &b = sim::m1[i];
      sim::curBar = i;
      double path[4] = {b.o, 0, 0, b.c};
      if (std::fabs(b.h - b.o) < std::fabs(b.o - b.l)) { path[1] = b.h; path[2] = b.l; } else { path[1] = b.l; path[2] = b.h; }
      std::vector<double> ticks;
      ticks.push_back(b.o);
      for (int sgm = 1; sgm < 4; sgm++)
      {
         double a = path[sgm - 1], z = path[sgm];
         long n = std::lround(std::fabs(z - a) / 0.01);
         for (long k = 1; k <= n; k++) ticks.push_back(std::round((a + (z > a ? 1 : -1) * 0.01 * k) * 100.0) / 100.0);
      }
      bool restartHere = (i == nextRestart);
      long restartTick = restartHere ? (long)(rng() % ticks.size()) : -1;
      for (size_t j = 0; j < ticks.size(); j++)
      {
         sim::now = b.t + (datetime)(j * 59 / ticks.size());
         sim::bid = ticks[j]; sim::ask = sim::bid + sim::spread;
         sim::firstTickOfBar = j == 0;
         BrokerTick();
         for (ulong d : sim::pendingTx) { MqlTradeTransaction tr; tr.type = TRADE_TRANSACTION_DEAL_ADD; tr.deal = d; MqlTradeRequest rq; MqlTradeResult rs; OnTradeTransaction(tr, rq, rs); }
         sim::pendingTx.clear();
         if ((long)j == restartTick)
         {   // a terminal restart inside this bar: the EA is unloaded and loaded again (its memory is rebuilt from scratch)
            OnDeinit(REASON_CLOSE);
            g_ready = false; g_lastBar = 0; g_curOpen = 0; g_mark = 0; g_lastErr = "";
            if (OnInit() != INIT_SUCCEEDED) { fprintf(stderr, "re-init failed\n"); return 1; }
            restarts++;
            nextRestart = i + 1 + (long)(rng() % restartEvery);
         }
         OnTick();
         sim::prevPx = sim::bid;
         nTicks++;
      }
   }
   // trades from the deals: entry and exit by position
   FILE *of = fopen(argv[3], "w");
   fprintf(of, "side,dir,ebar,ep,q,xbar,xp,why,pnl\n");
   std::map<ulong, std::vector<SimDeal *>> byPos;
   for (auto &d : sim::deals) byPos[d.pid].push_back(&d);
   auto barOf = [](datetime t) { auto it = std::upper_bound(sim::m1.begin(), sim::m1.end(), t, [](datetime x, const SimBar &b) { return x < b.t; }); return (long)(it - sim::m1.begin()) - 1; };
   double net = 0; int n = 0;
   for (auto &kv : byPos)
   {
      SimDeal *in = nullptr, *out = nullptr; double pnl = 0;
      for (auto *d : kv.second) { pnl += d->profit + d->comm; if (d->entry == DEAL_ENTRY_IN) in = d; else out = d; }
      if (!in || !out) continue;
      int dir = in->type == DEAL_TYPE_BUY ? 1 : -1;
      fprintf(of, "%d,%d,%ld,%.5f,%.4f,%ld,%.5f,%s,%.6f\n", (InDirMode == DIR_HEDGE && dir == -1) ? 1 : 0, dir, barOf(in->time), in->price, in->vol * 100.0, barOf(out->time), out->price,
              out->reason == DEAL_REASON_SL ? "SL" : (out->reason == DEAL_REASON_TP ? "TP" : "CL"), pnl);
      net += pnl; n++;
   }
   fclose(of);
   fprintf(stderr, "ticks %ld restarts %ld trades %d net %.2f open %d\n", nTicks, restarts, n, net, (int)sim::pos.size());
   return 0;
}
