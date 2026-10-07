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
   InPbSwp2 = cb("pbSwp2", false);
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
   InHolTrade = cb("holTrade", true); InAuPre = (int)cl("auPre", 10); InAuPost = (int)cl("auPost", 20);
   InCalOn = cb("calOn", false); InCalCur = cfg.count("calCur") ? cfg["calCur"] : string("USD"); InCalImp = (ECalImp)cl("calImp", 0); InCalPre = (int)cl("calPre", 10);
   InCalPost = (int)cl("calPost", 20); InCalHol = cb("calHol", true); InCalSave = cb("calSave", false); InPreOn = cb("preOn", false); InPreHrs = cd("preHrs", 1.0);
   InCalToday = (ECalToday)cl("calToday", 2);
   InBuMode = (EBuMode)cl("buMode", 0); InBuPips = cd("buPips", 10.0); InBuPct = cd("buPct", 0.02); InBuPip = cd("buPip", 0.0);
   InR3On = cb("r3On", false); InR3BrkOn = cb("r3BrkOn", false); InR3Brk = cd("r3Brk", 3.0); InR3Fb = cb("r3Fb", false); InLmOn = cb("lmOn", false); InLmAmt = cd("lmAmt", 300.0); InSp1 = cd("sp1", 200.0); InSpN1 = cd("spN1", 3.0); InSp2 = cd("sp2", 500.0); InSpN2 = cd("spN2", 5.0); InSp3 = cd("sp3", 1000.0); InSpN3 = cd("spN3", 8.0); InSpInc = cd("spInc", 500.0); InSpAdd = cd("spAdd", 1.0);
   sim::calMode = (int)cl("calMode", 0); sim::calFail = cb("calFail", false); sim::calFailN = cl("calFailN", 0);
   if (cfg.count("fileDir")) sim::fileDir = cfg["fileDir"];
   if (cfg.count("simCal"))
   {   // the fake MT5 calendar: utc,text,currency,importance,type,name[,exact]
      std::ifstream cf(cfg["simCal"]); string ln; std::map<string, ulong> ids;
      while (std::getline(cf, ln))
      {
         if (ln.empty() || ln[0] == '#') continue;
         std::vector<string> f; std::stringstream ss(ln); string x; while (std::getline(ss, x, ',')) f.push_back(x);
         if (f.size() < 6) continue;
         sim::CalEv e; e.utc = atol(f[0].c_str()); e.cur = f[2]; e.imp = atoi(f[3].c_str()); e.typ = atoi(f[4].c_str()); e.name = f[5]; e.exact = f.size() < 7 || f[6] != "0";
         if (f.size() >= 13)   // forecast, actual (x 1,000,000; "" = none), result 1 good / 2 bad, percent 0/1, multiplier 0-4, digits
         {
            if (!f[7].empty()) e.fc = atol(f[7].c_str());
            if (!f[8].empty()) e.ac = atol(f[8].c_str());
            e.impact = atoi(f[9].c_str()); e.pct = atoi(f[10].c_str()); e.mult = atoi(f[11].c_str()); e.dig = atoi(f[12].c_str());
         }
         string key = e.cur + "|" + e.name + "|" + f[3] + "|" + f[4] + "|" + (e.exact ? "1" : "0");
         if (!ids.count(key)) { ulong id = ids.size() + 1; ids[key] = id; }
         e.eid = ids[key];
         sim::cal.push_back(e);
      }
   }
   InExec = (EExec)cl("exec", 0); InWarm = cl("warm", 100000000); InSrvHours = 2.0; InSrvDst = DST_EU;
   InDraw = cb("draw", false); InStatOn = cb("table", false); InHtfDraw = cb("draw", false); InShow = cb("draw", false);
   InStatRows = (ETblRows)cl("tableRows", 0); InStatPos = (ETblPos)cl("tablePos", 7); InStatSize = (ETblSize)cl("tableSize", 1); InHtfMarks = cl("htfMarks", 50);
   sim::tester = (int)cl("tester", 1);
   sim::chartSec = (int)cl("chartSec", 60);
   _Period = sim::chartSec == 900 ? PERIOD_M15 : (sim::chartSec == 300 ? PERIOD_M5 : (sim::chartSec == 3600 ? PERIOD_H1 : PERIOD_M1));
   InHtf = (EHtf)cl("htf", 0);
   sim::balance = cd("eq0", 10000);
   sim::commPerLot = cd("comm", 0.3) * 100.0;
   sim::spread = cd("spread", 0.0);
   long restartEvery = cl("restartEvery", 0);
   // the computer sleeps / the connection drops: every ~sleepEvery bars the EA gets no ticks for sleepMin..sleepMax bars
   // (from a random tick to a random tick); the broker goes on (pending orders fill, stops and targets hit);
   // sleepRestart 1 = the terminal is restarted at the wake-up instead (the EA is loaded again)
   long sleepEvery = cl("sleepEvery", 0), sleepMin = cl("sleepMin", 2), sleepMax = cl("sleepMax", 2);
   bool sleepRestart = cb("sleepRestart", false);
   if (sleepEvery > 0 && (restartEvery > 0 || sleepMin < 1 || sleepMax < sleepMin)) { fprintf(stderr, "sleep: sleepMin >= 1, sleepMax >= sleepMin, no restartEvery\n"); return 1; }
   FILE *wf = cfg.count("wakeLog") ? fopen(cfg["wakeLog"].c_str(), "w") : nullptr;   // one line per wake-up
   if (wf) fprintf(wf, "time,bar,tick,ntick,slept_bar,slept_tick,deals_before,deals_after\n");
   std::mt19937 srng((unsigned)cl("sleepSeed", 777));
   sim::verbose = (int)cl("verbose", 0);   // 1 = the EA's Print lines to stderr
   FILE *bk = cfg.count("dropLog") ? fopen(cfg["dropLog"].c_str(), "w") : nullptr;   // v12.3: the book at every catch-up check
   if (bk)
   {
      sim::printTo = bk; sim::verbose = 1;   // the EA's Print lines (the drops) go in between, in order
      fprintf(bk, "H,now,when,hi,lo,side,sdir,sseq,piece,on,dir,seq,ent,mkt\n");
      sim::onDrop = [bk](double hi, double lo, datetime when) {
         for (int k = 0; k < g_nSides; k++)
            for (int p = 0; p < 2; p++)
            {
               int i = k * 2 + p;
               fprintf(bk, "H,%ld,%ld,%.2f,%.2f,%d,%d,%d,%d,%d,%d,%d,%.5f,%d\n", (long)sim::now, (long)when, hi, lo, k, g_side[k].dir, g_side[k].seq, p,
                       g_vb[i].on ? 1 : 0, g_vb[i].dir, g_vb[i].seq, g_vb[i].ent, g_vb[i].mkt ? 1 : 0);
            }
         fflush(bk);
      };
   }
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
   if (cb("initOnly", false)) { fprintf(stderr, "init only\n"); return 0; }
   long nTicks = 0, restarts = 0;
   long nextRestart = restartEvery > 0 ? from + 1 + (long)(rng() % restartEvery) : -1;
   long slB = sleepEvery > 0 ? from + 1 + (long)(srng() % (2 * sleepEvery)) : -1, slT = -1, wkB = -1, wkT = -1, nSleeps = 0;
   bool asleep = false; long sleptBar = -1, sleptTick = -1;
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
      if (i == slB && !asleep) slT = (long)(srng() % ticks.size());
      if (i == wkB && asleep) wkT = (long)(srng() % ticks.size());
      for (size_t j = 0; j < ticks.size(); j++)
      {
         sim::now = b.t + (datetime)(j * 59 / ticks.size());
         sim::bid = ticks[j]; sim::ask = sim::bid + sim::spread;
         sim::firstTickOfBar = j == 0;
         if (j == 0) { sim::curHi = ticks[j]; sim::curLo = ticks[j]; } else { sim::curHi = std::max(sim::curHi, ticks[j]); sim::curLo = std::min(sim::curLo, ticks[j]); }
         if (!asleep && i == slB && (long)j == slT)
         {   // the computer goes to sleep
            asleep = true; sleptBar = i; sleptTick = (long)j; nSleeps++;
            wkB = i + sleepMin + (long)(srng() % (sleepMax - sleepMin + 1)); wkT = -1;
         }
         bool waking = asleep && i == wkB && (long)j == wkT;
         if (asleep && !waking)
         {   // asleep: the broker works, the EA hears nothing
            BrokerTick();
            sim::pendingTx.clear();
            sim::prevPx = sim::bid;
            nTicks++;
            continue;
         }
         if (waking) { asleep = false; slB = i + 1 + (long)(srng() % (2 * sleepEvery)); }
         BrokerTick();
         if (waking && sleepRestart) sim::pendingTx.clear();   // a freshly loaded EA hears nothing of the past
         for (ulong d : sim::pendingTx) { MqlTradeTransaction tr; tr.type = TRADE_TRANSACTION_DEAL_ADD; tr.deal = d; MqlTradeRequest rq; MqlTradeResult rs; OnTradeTransaction(tr, rq, rs); }
         sim::pendingTx.clear();
         long dealsBefore = (long)sim::deals.size();   // fills by the broker at this tick are not the EA's doing
         if (waking && sleepRestart)
         {   // the terminal was closed: the EA is loaded again at the wake-up
            OnDeinit(REASON_CLOSE);
            g_ready = false; g_lastBar = 0; g_curOpen = 0; g_mark = 0; g_lastErr = "";
            if (OnInit() != INIT_SUCCEEDED) { fprintf(stderr, "re-init failed\n"); return 1; }
         }
         if ((long)j == restartTick)
         {   // a terminal restart inside this bar: the EA is unloaded and loaded again (its memory is rebuilt from scratch)
            OnDeinit(REASON_CLOSE);
            g_ready = false; g_lastBar = 0; g_curOpen = 0; g_mark = 0; g_lastErr = "";
            if (OnInit() != INIT_SUCCEEDED) { fprintf(stderr, "re-init failed\n"); return 1; }
            restarts++;
            nextRestart = i + 1 + (long)(rng() % restartEvery);
         }
         OnTick();
         if (waking && wf) fprintf(wf, "%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld\n", (long)sim::now, i, (long)j, (long)ticks.size(), sleptBar, sleptTick, dealsBefore, (long)sim::deals.size());
         if (nTicks % 997 == 0) OnTimer();
         if (nTicks % 100003 == 0) OnChartEvent(CHARTEVENT_CHART_CHANGE, 0, 0.0, "");
         sim::prevPx = sim::bid;
         nTicks++;
      }
   }
   if (cb("dump", false))
   {   // the table as it is at the end of the run
      TblRows();
      for (int i = 0; i < g_rN; i++) fprintf(stderr, "%-44s | %s\n", g_rL[i].c_str(), g_rV[i].c_str());
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
   if (wf) fclose(wf);
   if (bk) fclose(bk);
   if (cfg.count("dealsOut"))
   {   // every deal with its exact time: time,dir(+1 buy -1 sell),entry(0 in 1 out),position,price,volume,comment
      FILE *df = fopen(cfg["dealsOut"].c_str(), "w");
      fprintf(df, "time,type,entry,pid,price,vol,cmt\n");
      for (auto &d : sim::deals) fprintf(df, "%ld,%d,%d,%lu,%.5f,%.4f,%s\n", (long)d.time, d.type == DEAL_TYPE_BUY ? 1 : -1, d.entry == DEAL_ENTRY_IN ? 0 : 1, (unsigned long)d.pid, d.price, d.vol, d.cmt.c_str());
      fclose(df);
   }
   if (sleepEvery > 0) fprintf(stderr, "sleeps %ld\n", nSleeps);
   fprintf(stderr, "ticks %ld restarts %ld trades %d net %.2f open %d calcalls %ld\n", nTicks, restarts, n, net, (int)sim::pos.size(), sim::calCalls);
   return 0;
}
