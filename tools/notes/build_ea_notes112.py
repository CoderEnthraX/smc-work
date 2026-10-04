# SMC_Structure_EA_v11.2_NOTES.txt = the new v11.2 part + the EA v11.1 notes
R = "/home/user/smc-work/"
old = open(R + "SMC_Structure_EA_v11.1_NOTES.txt").read()
k = old.index("1. WHAT IT IS")
body = old[k:]
NEW = """SMC STRUCTURE EA v11.2 (+ HEDGE) - NOTES
=========================================
File: SMC_Structure_EA_v11.2.mq5 (MetaTrader 5 Expert Advisor, MQL5)
Owner: Punit. Times in these notes are IST unless they say otherwise.
The EA follows the TradingView strategy v11.2. Install it like v11.1
(section 3); you can delete SMC_Structure_EA_v11.1 from MT5.


NEW IN v11.2 - THE STOP BUFFER IN PRICE, PIPS OR % OF PRICE
-----------------------------------------------------------
The same rule as the TradingView strategy v11.2 (its notes, item 119).
A new group at the END of the EA settings (after group 41), so your
saved settings keep their places:
  38. Stop buffer unit - price, pips or % (v11.2)
    Stop buffer unit             Price (as now) / Pips (auto per
                                 market) / % of price
    - stop buffer in pips        10
    - stop buffer in % of price  0.02
    - pip size (0 = automatic)   0
Default "Price (as now)": the EA trades exactly like v11.1 (tested).

THE PIP - the EA reads it from the MT5 symbol (its name, its base and
profit currency, and whether MT5 calls it forex):
  gold (XAUUSD, GOLD, XAUUSD.r)      0.10     10 pips = 1.00
  silver (XAGUSD, SILVER)            0.01     10 pips = 0.10
  Bitcoin (BTCUSD, BITCOIN)          1        10 pips = 10
  Ethereum (ETHUSD, ETHEREUM)        0.10     10 pips = 1.00
  forex (EURUSD, GBPUSD, AUDCAD)     0.0001   10 pips = 0.0010
  JPY pairs (USDJPY, EURJPY)         0.01     10 pips = 0.10
  anything else (indices, ...)       10 x the price step
"pip size" (not 0) replaces the automatic pip.

% OF PRICE: this % of the CHOCH* level, worked out for every setup -
0.02% of gold at 4,140 = 0.83. The buffer is rounded to the price step.

ALSO IN THE SAME UNIT: group 24 "Skip the setup if the stop is CLOSER /
FURTHER than" (pips, or % of the entry price) and the structure trailing
stop (group 34 c). Set the group 24 numbers again when you switch.

THE TABLE: a new row "STOP BUFFER (group 38)" (Full table), e.g.
"10 pips x 0.1 = 1.00" or "0.02% of the level = 0.83 now". The Short
table shows it when the unit is not Price.

HOW IT WAS CHECKED
  - unit Price: every earlier test file byte-identical (11 settings for
    one year, 5.75 years on 1m and 15m to the cent, the table and
    drawings on / off with restarts)
  - pips and %: the whole EA in the fake MT5 = the EA's core, trade for
    trade, to the cent, over 5.75 years, in 5 of 5 settings (touch and
    pending entries, hedge, the group 24 limits + trailing stop)
  - the EA's core = the Python simulator (a separate program): 10 of 10
    settings over 5.75 years; 10 pips = 1.0 and 50 pips = 5.0
  - restarts with pips / %: identical to no restarts
  - the automatic pip: 21 MT5 symbol names, all as in the table above
  NOT checked here: the real MQL5 compiler. Compile it (F7) and send me
  any error lines.

WILL IT CHANGE RESULTS? Only the SIZE of the buffer does. Your 1-minute
settings, 2021 - Oct 2026: 1.0 (= 10 pips) -18,514; 0.02% -22,350;
0.1% -17,216; 0.5% -6,768; 50 pips -10,583 - all lose (TradingView
notes item 120). Silver, crypto and forex are not tested at all.


""" + "=" * 74 + """
EVERYTHING BELOW IS FROM THE EA v11.1 NOTES - still true for v11.2.
(Where it says v11.1, read v11.2.)
""" + "=" * 74 + "\n\n"
t = NEW + body
assert all(ord(c) < 128 for c in t)
bad = [l for l in t.split("\n") if len(l) > 78]
assert not bad, bad
open(R + "SMC_Structure_EA_v11.2_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("EA v11.2 notes", len(t.split("\n")), "lines")
