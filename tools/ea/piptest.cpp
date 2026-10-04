// the EA's automatic pip (v11.2) for many symbols, as an MT5 broker names them
#include "ea_x.cpp"
struct Case { const char *sym, *base, *prof; int cm; double tick, expect; };
int main()
{
   const int F = SYMBOL_CALC_MODE_FOREX, C = SYMBOL_CALC_MODE_CFDLEVERAGE, I = SYMBOL_CALC_MODE_CFDINDEX;
   Case cs[] = {
      {"XAUUSD", "XAU", "USD", C, 0.01, 0.1}, {"GOLD", "XAU", "USD", C, 0.01, 0.1}, {"XAUUSD.r", "XAU", "USD", C, 0.01, 0.1}, {"gold", "", "USD", C, 0.01, 0.1},
      {"XAGUSD", "XAG", "USD", C, 0.001, 0.01}, {"SILVER", "XAG", "USD", C, 0.001, 0.01},
      {"BTCUSD", "BTC", "USD", C, 0.01, 1.0}, {"BITCOIN", "", "USD", C, 0.01, 1.0}, {"ETHUSD", "ETH", "USD", C, 0.01, 0.1}, {"ETHEREUM", "", "USD", C, 0.01, 0.1},
      {"ETHBTC", "ETH", "BTC", C, 0.00001, 0.1}, {"SOLUSD", "SOL", "USD", C, 0.001, 0.01},
      {"EURUSD", "EUR", "USD", F, 0.00001, 0.0001}, {"GBPUSD", "GBP", "USD", F, 0.00001, 0.0001}, {"AUDCAD", "AUD", "CAD", F, 0.00001, 0.0001},
      {"USDJPY", "USD", "JPY", F, 0.001, 0.01}, {"EURJPY", "EUR", "JPY", F, 0.001, 0.01}, {"GBPJPY", "GBP", "JPY", SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE, 0.001, 0.01},
      {"XPTUSD", "XPT", "USD", C, 0.01, 0.1}, {"US30", "USD", "USD", I, 0.1, 1.0}, {"GER40", "EUR", "EUR", I, 0.01, 0.1},
   };
   int bad = 0;
   for (auto &c : cs)
   {
      g_sym = c.sym; sim::curBase = c.base; sim::curProfit = c.prof; sim::calcMode = c.cm; g_tickSize = c.tick;
      double p = PipAuto();
      bool ok = std::fabs(p - c.expect) < 1e-12;
      if (!ok) bad++;
      printf("%-10s pip %-8g 10 pips %-8g %s\n", c.sym, p, 10 * p, ok ? "ok" : "WRONG");
   }
   printf("%s\n", bad ? "SOME WRONG" : "ALL OK");
   return bad;
}
