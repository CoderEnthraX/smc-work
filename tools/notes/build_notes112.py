# SMC_Structure_Strategy_v11.2_NOTES.txt = new v11.2 part + the v11.1 notes (from "WHAT v11.1 CHANGES" on)
import sys
R = "/home/user/smc-work/"
v111 = open(R + "SMC_Structure_Strategy_v11.1_NOTES.txt").read()
k = v111.index("-" * 74 + "\nWHAT v11.1 CHANGES")
body = v111[k:]
H = "-" * 74
CHECK5 = sys.argv[1] if len(sys.argv) > 1 else "CHECK5"


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v11.2  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v11.2.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v11.2_HANDBOOK.pdf - every setting, with
examples and the value to use.

v11.2 - the stop buffer in PRICE (as before), in PIPS (the strategy knows
  the pip of gold, silver, Bitcoin, Ethereum and forex) or in % OF PRICE.
  A new group 38 at the end of the settings. Default "Price (as now)":
  with it v11.2 trades exactly like v11.1.

SETTINGS: 122 - the 118 of v11.1 in the same places + 4 new at the end.
  Replace the code while you are FLAT (no open trade), then delete the
  alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v11.2 CHANGES", """
119. STOP BUFFER UNIT (group 38, the last 4 settings)
       Stop buffer unit              Price (as now)  /  Pips (auto per
                                     market)  /  % of price
       - stop buffer in pips         10
       - stop buffer in % of price   0.02
       - pip size (0 = automatic)    0

     WHAT IT DOES: the stop goes this far beyond the CHOCH* level - the
     same place as the group 20 stop buffer. You choose the unit:
       PRICE  the group 20 "Stop buffer ... in price" - exactly v11.1.
       PIPS   the pips x the pip of the market on the chart:
                market                  1 pip    10 pips   50 pips
                gold (XAUUSD, GOLD)     0.10     1.00      5.00
                silver (XAGUSD)         0.01     0.10      0.50
                Bitcoin                 1        10        50
                Ethereum                0.10     1.00      5.00
                EURUSD, GBPUSD, ...     0.0001   0.0010    0.0050
                USDJPY, EURJPY, ...     0.01     0.10      0.50
                anything else           10 x the smallest price step
              "pip size" (not 0) replaces the automatic pip.
       %      this % of the CHOCH* level, worked out again for every
              setup - so it grows with the price:
                0.02% of gold    at 2,000 = 0.40    at 4,140 = 0.83
                0.02% of silver  at 50 = 0.01
                0.02% of Bitcoin at 100,000 = 20
                0.02% of EURUSD  at 1.10 = 0.00022 (2.2 pips)
     The buffer is rounded to the smallest price step of the market.

     GROUP 24 FOLLOWS THE UNIT: "Skip the setup if the stop is CLOSER /
     FURTHER than" is read in the same unit:
       Pips  30 = 30 pips = 3.00 on gold
       %     0.05 = 0.05% of the entry price = 2.07 on gold at 4,140
     So set these two again when you switch the unit (0 = off stays off).

     The structure trailing stop (group 34 c) uses the same buffer. The
     group 20 stop buffer is not used in the Pips and % modes.

     THE TABLE: a new last row "STOP BUFFER (group 38)", e.g.
       10 pips x 0.1 = 1.00
       0.02% of the level = 0.83 now
     Look at it once after you switch.

     EXAMPLE (gold 1m, a bullish CHOCH*, the CHOCH* level at 4,100.00)
       unit     setting    stop at
       Price    1.0        4,099.00   (as v11.1)
       Pips     10         4,099.00   (10 x 0.10)
       Pips     50         4,095.00   (50 x 0.10)
       %        0.02       4,099.18   (0.02% of 4,100 = 0.82)
       %        0.1        4,095.90   (0.1% of 4,100 = 4.10)

120. WILL IT CHANGE YOUR RESULTS? (honest)
     The unit only changes how you TYPE the buffer: 10 pips on gold is
     exactly your 1.0 today. A different SIZE of buffer does change the
     results. Your settings, FxPro gold 1m, 2021 - Oct 2026, risk 50:
       buffer          trades    total    per trade   losing years
       1.0 (now)        2,839   -18,514    -0.13R       5 of 6
       10 pips          2,839   -18,514    -0.13R       5 of 6
       0.02%            3,061   -22,350    -0.15R       5 of 6
       0.05%            2,799   -19,840    -0.14R       6 of 6
       0.1%             2,486   -17,216    -0.14R       6 of 6
       0.2%             2,114   -12,519    -0.12R       6 of 6
       0.5%             1,654    -6,768    -0.08R       6 of 6
       5.0 (50 pips)    2,101   -10,583    -0.10R       6 of 6
     A wider buffer loses less per trade, but NO size made money over
     the 5.75 years. 0.02% is smaller than your 1.0 until gold is above
     5,000.
     3 months (OANDA, Feb 25 - May 26 2026, the simulator):
       1.0 / 10 pips  112 trades  +793     0.02%   112 trades  +794
       0.05%          105 trades  +284     0.1%    100 trades  -277
       0.2%            87 trades  -698     50 pips  99 trades  -592
     The opposite order to the 5.75 years - 3 months is not enough to
     choose a buffer.
     Silver, crypto and forex: the strategy has NOT been tested on them.
     Test there before trading them.""")

S += sec("HOW v11.2 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v11.2 without a
    syntax error. Every new name is declared before it is used and clashes
    with no old one. ASCII only; no tabs; no strategy.close_all.
  - The settings: the 118 of v11.1 unchanged in the same places + 4 new
    at the end = 122.
  - The simulator on real gold 1-minute data (Feb 25 - May 26, 2026):
      unit "Price" = v11.1, every trade, in 6 settings (plain, trailing
        stop by level and by swing, the group 24 limits, CHOCH and BOS
        with reverse, auto mode);
      10 / 25 / 50 pips = 1.0 / 2.5 / 5.0 in price, every trade;
      the group 24 limits 30 / 400 pips = 3 / 40 in price, every trade.
""" + CHECK5 + """
  - The automatic pip: 14 TradingView symbols and 21 MT5 symbol names
    (gold, silver, Bitcoin, Ethereum, other coins, forex, JPY pairs,
    platinum, indices) - all as in the table of item 119.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v11.1 NOTES - still true for v11.2. The new\n"
       "unit (item 119) is optional; with \"Price (as now)\" v11.2 works exactly\nlike v11.1.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S + BAN).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v11.2_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v11.2 notes", len(t.split("\n")), "lines")
