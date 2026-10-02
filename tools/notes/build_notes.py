# builds SMC_Structure_Strategy_v8.4_NOTES.txt and SMC_Structure_Strategy_v9.0_NOTES.txt from the v8.3 notes
import json
R = "/home/user/smc-work/"
SIM = "/home/user/smc-work/tools/sim2/final.json"
res = {r["key"]: r for r in json.load(open(SIM))}
old = open(R + "SMC_Structure_Strategy_v8.3_NOTES.txt").read().split("\n")
# the v8.3 notes from their first section on (the header lines are replaced)
i0 = [i for i, l in enumerate(old) if l.startswith("I WAS WRONG AGAIN")][0] - 1
body83 = "\n".join(old[i0:])

H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


SHORT = {"base": "Your settings (CHOCH only, R 3)", "rev": "Close and reverse OFF", "r2": "Target R 2",
         "ln": "Entries 13-23 (London+NY)", "ny": "Entries 17-23 (New York)", "r2only": "Rule 2 only",
         "mo2": "CHOCH + BOS, max 2 open", "mo3": "CHOCH + BOS, max 3 open", "be": "Break-even at 1R",
         "step": "Step stop", "min6": "Minimum stop 6", "a": "a. BOS stack at 50% risk (max 3)",
         "b": "b. HTF filter (rule 1, R2 off)", "c1": "c. Trail behind CHOCH* level", "c2": "c. Trail behind every swing",
         "d": "d. Liquidity target, min 1.5R", "e": "e. Partial 50% at 1R + BE", "f0": "f. P/D filter, pullback 25",
         "f": "f. P/D filter 50 + pullback 50", "pb50": "   (pullback 50 alone)", "g": "g. Pause after 3 losses",
         "hedge": "Hedge: LONG + SHORT copies", "cost3": "Your settings, costs 0.3/oz",
         "C": "COMBO: rev OFF+pb50+f+step", "Cny": "COMBO + entries 17-23"}


def row(k, label=None):
    r = res[k]
    label = label or SHORT[k]
    m = r["m"]
    return "%-32s %4d %7s %4.2f %5s %6s %6s %6s" % (label[:32], r["n"], "{:+,}".format(r["net"]), r["pf"],
                                                       "{:,}".format(r["dd"]), "{:+,}".format(m[0]), "{:+,}".format(m[1]), "{:+,}".format(m[2]))


TH = ("%-32s %4s %7s %4s %5s %6s %6s %6s\n" % ("", "trds", "net", "PF", "maxDD", "mon 1", "mon 2", "mon 3") +
      "-" * 76)

# ---------------------------------------------------------------- common text
BODY_FIXES = [
    ("88 settings in\nfourteen groups:", "the settings in\nthese groups:"),
    ("""  32. Stop management - step stop / break-even  (new in v7.4, the last
      group: "Step stop" and "Break-even only", both OFF)""",
     """  32. Stop management - step stop / break-even  (new in v7.4:
      "Step stop" and "Break-even only", both OFF)
  33. Trade direction  (new in v8.4: Both / Longs only / Shorts only)
  34. v9.0 ideas - each one OFF by default  (only in v9.0)"""),
    ("""v7.3 appends its two settings (group 31) at the very end again, so
settings saved in v7.0, v7.1 or v7.2 keep their places. v7.4 appends
group 32 the same way.""", """v7.3 appends its two settings (group 31) at the very end again, so
settings saved in v7.0, v7.1 or v7.2 keep their places. v7.4 appends
group 32 the same way, v8.4 group 33 and v9.0 group 34."""),
    ("""  - It will not hold a long and a short at once. Platform limit.""",
     """  - It will not hold a long and a short at once. Platform limit.
    (v8.4: two copies of the strategy can - see TRADE DIRECTION AND THE
    HEDGE at the top.)"""),
    ("""  OFF            The new signal is ignored until the current trade finishes.""",
     """  OFF            The new signal is ignored until the current trade finishes.

v8.4: to hold a buy and a sell together, use TWO copies of the strategy
- one "Longs only", one "Shorts only", both with this setting OFF. See
TRADE DIRECTION AND THE HEDGE at the top of these notes."""),
]


def fix_body(b):
    for a, c in BODY_FIXES:
        assert b.count(a) == 1, a[:60]
        b = b.replace(a, c)
    return b


V84_HEAD = """SMC STRUCTURE STRATEGY  -  v8.4  -  HOW EVERYTHING WORKS
========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v8.4.txt      Pine Script v6      ASCII only.
Two ready-made copies of it for a hedge:
  SMC_Structure_Strategy_v8.4_LONG.txt     longs only,  tag smcL
  SMC_Structure_Strategy_v8.4_SHORT.txt    shorts only, tag smcS
Handbook: SMC_Structure_Strategy_v8.4_HANDBOOK.pdf - every setting, with
examples and the value to use.
Test report: SMC_Strategy_TEST_REPORT_v9.0.pdf - your three trade files
and every idea, tested on real gold data.

v8.4 in three lines:
  - NEW SETTING "Trade direction" (group 33): Both / Longs only / Shorts
    only. With Both (the default) v8.4 trades exactly like v8.3.
  - The symbol and the TheConnector tag are sent without spaces.
  - Price and lot settings take up to 8 decimals (0.0001 for forex works).

SETTINGS: 89 - the 88 of v8.3 in the same places, plus 1 at the very end.
  Your saved settings keep their places. Replace the code while you are
  FLAT (no open trade), then delete the alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

V84_SECTIONS = sec("WHAT v8.4 CHANGES", """
80. TRADE DIRECTION (group 33, the last setting): Both / Longs only /
    Shorts only. A signal the other way opens nothing. Its audit label
    says "SKIP - longs only" (or "shorts only"), and a new table row
    counts these signals. Everything else that signal did before, it
    still does: it cancels a waiting order the other way, and with
    "close and reverse" ON it still closes your open trades.
    Both = exactly v8.3.

81. THE SYMBOL IS SENT WITHOUT SPACES. "GOLD " or " XAUUSD", typed with
    a space by accident, reached the broker with the space and was
    refused. Spaces are now taken out, as quotes already were. The
    table row "Ticker - type / 1 lot / symbol sent" shows exactly what
    is sent.

82. THE TAG IS SENT WITHOUT SPACES OR QUOTES. The same for the
    TheConnector tag (group 30). A quote in the tag would have broken the
    message.

83. UP TO 8 DECIMALS in the price and lot settings: stop buffer (group
    20), lot step (21), minimum lot (22), minimum / maximum stop
    distance (24) and broker spread (26). TradingView rounds a typed
    number to the step of the setting, so 0.0001 became 0.00. Now up to
    8 decimals are kept. The small arrows now move in tiny steps, so
    type the number instead.

84. NOTHING ELSE CHANGES. The engine, the entries, the stops, the
    targets, the sizing, the order handling of v8.3, and the messages
    (except the spaces) are the same code.""")

V84_SECTIONS += sec("TRADE DIRECTION AND THE HEDGE", """
WHAT IT IS. A Pine strategy holds ONE net position: a sell always closes
or reverses your buys. One copy of the strategy can never hold a buy and
a sell together. Two copies can: one takes only the buys, the other only
the sells, and each keeps its own trades.

THE READY-MADE COPIES. The two files are v8.4 with four defaults changed
- nothing else:
  SMC_Structure_Strategy_v8.4_LONG.txt   title "SMC Structure Strategy
                                         LONG", Trade direction "Longs
                                         only", close and reverse OFF,
                                         tag smcL
  SMC_Structure_Strategy_v8.4_SHORT.txt  the same with "Shorts only" and
                                         tag smcS

SETTING IT UP, STEP BY STEP
  1. MT5: your FxPro account must be a HEDGING account, not netting. On a
     netting account a sell closes your buy at the broker, whatever
     TradingView does.
  2. Pine Editor: open a new script, paste the LONG file, save it (for
     example "SMC LONG") and add it to the chart. Do the same with the
     SHORT file.
  3. In EACH copy type your own settings again - a new script starts at
     the defaults. Check at least: take trades on, rule 1 pullback %,
     target R, stop buffer, session hours, force-close hour, weekend
     cutoff, risk, lot step, commission, spread, symbol, and the news
     settings.
  4. Leave the four preset values as they are: direction, close and
     reverse OFF, and the two different tags.
  5. Create ONE alert PER COPY: condition = that copy, "Order fills
     only", message ONLY {{strategy.order.alert_message}}, webhook URL
     https://webhook.theconnector.fr/YOUR_ACCESS_KEY (type your key only
     in TradingView). Both alerts go to the same webhook.
  6. Each copy has its OWN report, daily limits, loss recovery, profit
     target and "max trades open". Your total result is report 1 plus
     report 2.

WHAT IT DID IN THE TEST (real gold 1-minute data, Feb 27 to May 25 2026,
your settings; see the test report):
""" + TH + "\n" + row("base", "One copy, reverse ON (yours)") + "\n" + row("hedge", "LONG + SHORT copies, rev OFF") + "\n" +
    row("rev", "One copy, reverse OFF") + """

  The hedge made about the same as one copy, with less drawdown. One
  copy with "close and reverse" OFF did better than both. Gold fell in
  these three months, so the shorts copy made the money and the longs
  copy lost - in a rising market it would be the other way round.
  Honestly: a buy and a sell on the same symbol partly cancel out, and
  you pay costs on both. Try it on a demo account first.

WITH "CLOSE AND REVERSE" ON, the two copies behave almost exactly like
one copy (266 trades against 264 in the test). The LONG copy closes its
buys on a sell signal, and the SHORT copy opens the sell. That is also a
good check that the direction setting works.""")

V84_SECTIONS += sec("SYMBOL AND TAG WITHOUT SPACES", """
The symbol (group 30, "Symbol to send") and the TheConnector tag are
cleaned before anything is sent: spaces and quotes are taken out.
"GOLD " is sent as GOLD, " smc gold" as smcgold. A symbol never has a
space in it at any broker, so nothing that worked before changes. Leave
the symbol blank for forex pairs, as before: the chart's ticker is sent.""")

V84_SECTIONS += sec("SETTINGS WITH UP TO 8 DECIMALS", """
These settings now keep up to 8 decimals when you type them:
  group 20  Stop buffer beyond the CHOCH* level, in price
  group 21  Round the size to the broker's lot step
  group 22  Minimum lot your broker accepts
  group 24  Skip the setup if the stop is CLOSER / FURTHER than this
  group 26  Broker spread, in price
Examples: EURUSD spread 0.00012, stop buffer 0.0001; a crypto pair with
a spread of 0.00000150. The arrows next to the box now move by
0.00000001, so type the number.""")

V84_CHECK = sec("HOW v8.4 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar, pynescript) read v8.3,
    v8.4, both copies and v9.0 without a syntax error. It rejects broken
    code (tested on purpose with three broken scripts).
  - The settings: the 88 of v8.3 are in the same order and the same
    places; v8.4 adds 1 at the end; the LONG and SHORT copies have
    exactly the same settings in the same order.
  - Every new name is declared before it is used. The file is ASCII only,
    no tabs, version comment on line 2.
  - The trading logic was copied into a Python simulator and run on real
    gold 1-minute data. It reproduces your "CHOCH only" file for Feb 27 to
    May 25 2026: 187 of about 265 trades start in the same minute on the
    same side (181 also with the same size), and those trades net 1,081
    in the simulator against 1,077 in your file. The rest differ because
    the data feed is not OANDA's.
  - Longs only never took a short; shorts only never took a long; two
    copies with reverse ON gave 266 trades against 264 for one copy.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

# ---------------------------------------------------------------- v9.0
V90_HEAD = """SMC STRUCTURE STRATEGY  -  v9.0  -  HOW EVERYTHING WORKS
========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v9.0.txt      Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v9.0_HANDBOOK.pdf - every setting, with
examples and the value to use.
Test report: SMC_Strategy_TEST_REPORT_v9.0.pdf - your three trade files
and every idea, tested on real gold data.

v9.0 in three lines:
  - v8.4 (trade direction, symbol without spaces, 8 decimals) plus the
    seven "ideas to make it more profitable", each one a switch in the
    new group 34.
  - EVERY switch is OFF by default. With all of them OFF, v9.0 trades
    exactly like v8.4 - and v8.4 with "Both" exactly like v8.3.
  - Each idea was tested on real gold data before this file was made.
    Some helped, some lost - see WHICH IDEAS HELPED below.

SETTINGS: 104 - the 89 of v8.4 in the same places, plus 15 at the very
  end (group 34). Your saved settings keep their places. Replace the code
  while you are FLAT (no open trade), then delete the alert and create it
  again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

IDEAS = sec("WHAT v9.0 ADDS  -  GROUP 34, SEVEN SWITCHES, ALL OFF", """
85. a. SMALLER RISK FOR STACKED BOS TRADES
86. b. HIGHER-TIMEFRAME FILTER
87. c. STRUCTURE TRAILING STOP
88. d. TARGET AT THE NEXT LIQUIDITY
89. e. PARTIAL PROFIT
90. f. PREMIUM / DISCOUNT FILTER
91. g. PAUSE AFTER LOSSES IN A ROW
92. TABLE: "Exit - moved stop" now also counts trailing and break-even
    after the early profit; new rows "v9.0 ideas switched ON" and
    "skipped: HTF filter / premium-discount / paused days".
Each one is explained below, with what it did in the test.""")

IDEAS += sec("a. SMALLER RISK FOR STACKED BOS TRADES", """
SETTINGS: "a. Smaller risk for stacked BOS trades" (OFF) and "risk of
each stacked BOS trade, % of the normal risk" (50).

WHAT IT DOES. With BOS in "Take trades on", every same-side BOS adds a
trade (group 31). With this ON, each ADDED trade risks only this
percentage. The first trade of a move keeps the full risk. When a stack
reverses, all its trades lose together - smaller added trades lose less.

ONLY MATTERS with "BOS only" or "CHOCH and BOS". In "CHOCH only" there
are no stacked trades, so it changes nothing.

IN THE TEST: stacking BOS trades lost money in every form. With 50% risk
it lost less (""" + "{:+,}".format(res["a"]["net"]) + """ against """ + "{:+,}".format(res["mo3"]["net"]) + """ at full risk, max 3 open),
but "CHOCH only" (""" + "{:+,}".format(res["base"]["net"]) + """) was far better than both.""")

IDEAS += sec("b. HIGHER-TIMEFRAME FILTER", """
SETTING: "b. Higher-timeframe filter - take a signal only in the higher
timeframe direction" (OFF).

WHAT IT DOES. ON: a signal is taken only when the higher timeframe
(group 20 "Higher timeframe for RULE 2", 15m on a 1m chart) trends the
same way. The rest are skipped (audit label "SKIP - against the higher
timeframe (filter)").
  - With rule 2 ON: the agreeing signals use rule 2, as before. This is
    the same as "rule 2 only".
  - With rule 2 OFF and rule 1 ON: the agreeing signals use RULE 1 (the
    pullback %). This is new: rule 1, but only with the higher timeframe.
  Before v9.0, rule 2 OFF meant the higher timeframe was not even asked.

IN THE TEST: both forms lost against your settings (rule 1 with the
filter """ + "{:+,}".format(res["b"]["net"]) + """, rule 2 only """ + "{:+,}".format(res["r2only"]["net"]) + """). On 1-minute gold the 15-minute trend
was a poor guide in these months.""")

IDEAS += sec("c. STRUCTURE TRAILING STOP", """
SETTINGS: "c. Structure trailing stop" (OFF) and "the stop follows":
  Behind the CHOCH* level (slower)   - default
  Behind every new swing (faster)

WHAT IT DOES. At every candle close the stop of each open trade follows
the structure, never backwards:
  CHOCH* LEVEL: for a buy, the protected low of the up-trend - the level
  whose break would be the bearish CHOCH. It moves up after every BOS.
  EVERY NEW SWING: behind every new swing low the structure confirms
  (swing high for a sell).
The stop is placed the group 20 stop buffer beyond the level. The moved
stop is sent like a group 32 move: when TradingView's moved stop is hit,
the close message closes the trade at the broker (the broker keeps the
original stop as a safety net). With group 32 also ON, the tighter stop
wins.

IN THE TEST: behind the CHOCH* level """ + "{:+,}".format(res["c1"]["net"]) + """ (about the same as your """ + "{:+,}".format(res["base"]["net"]) + """);
behind every swing """ + "{:+,}".format(res["c2"]["net"]) + """ - the stop was too tight for 1-minute noise.""")

IDEAS += sec("d. TARGET AT THE NEXT LIQUIDITY", """
SETTINGS: "d. Target at the next liquidity" (OFF) and "only a swing at
least this far from the entry, in R" (1.5).

WHAT IT DOES. ON: the target is the nearest swing high (swing low for a
sell) that the price has NOT traded through yet - where other traders'
stops sit - but only one at least this many R away. None = the normal R
target of group 20. While the order waits the target follows new swings;
once it fills, the target stays.

IN THE TEST: at least 1.5R: """ + "{:+,}".format(res["d"]["net"]) + """ against """ + "{:+,}".format(res["base"]["net"]) + """, better in 2 of 3
months. At least 1R or 2R was worse. A small, uncertain gain.""")

IDEAS += sec("e. PARTIAL PROFIT", """
SETTINGS: "e. Partial profit" (OFF), "size of the early part, % of the
setup" (50), "early target, in R" (1.0), "then move the rest to
break-even" (ON).

WHAT IT DOES. ON: every setup is sent as TWO trades at the same price and
stop:
  - the early part: this % of the size, target at this R (pushed out to
    cover its costs, like the main target);
  - the rest: the normal target.
Each part has its own order id (L12 and L12p) and its own TheConnector
tag (smcgold-k3f9 and smcgold-k3f_). So ANY bridge can do it - TheConnector,
the MetaApi receiver - because each part is an ordinary trade. No
partial-close command is needed. When the early part hits its target, the
rest moves its stop to break-even.

GOOD TO KNOW
  - The size is split on the lot step. On gold with 50 risk and a wide
    stop the size is often only 0.01 lot (one lot step) - then it cannot
    be split and the setup is sent as one trade, as before.
  - "Max trades open" (group 31) counts each part.
  - Both parts fill together. If TradingView ever filled only one, the
    other is cancelled at once.

IN THE TEST: """ + "{:+,}".format(res["e"]["net"]) + """ against """ + "{:+,}".format(res["base"]["net"]) + """ - about the same, with a smoother curve.""")

IDEAS += sec("f. PREMIUM / DISCOUNT FILTER", """
SETTINGS: "f. Premium / discount filter" (OFF) and "the line, % of the
leg" (50 = the middle).

WHAT IT DOES. ON: a buy is placed only at a DISCOUNT - at or below this
line of the leg, measured down from its high. A sell only at a PREMIUM -
at or above it, measured up from its low. The leg is the same one rule 1
uses. A setup on the wrong side is cancelled ("CANCELLED - buy in the
premium").

IMPORTANT. Your rule 1 pullback is 25%. A 25% pullback is always ABOVE
the 50% line, so with this filter every rule 1 setup is cancelled - in
the test only 1 trade was left. Use it with a rule 1 pullback equal to
or bigger than the line: pullback 50 and line 50.

IN THE TEST, pullback 50 and line 50: """ + "{:+,}".format(res["f"]["net"]) + """, profit factor """ + str(res["f"]["pf"]) + """, max
drawdown """ + "{:,}".format(res["f"]["dd"]) + """ (yours: """ + "{:+,}".format(res["base"]["net"]) + """, """ + str(res["base"]["pf"]) + """, """ + "{:,}".format(res["base"]["dd"]) + """). Pullback 50 alone made
""" + "{:+,}".format(res["pb50"]["net"]) + """ but with drawdown """ + "{:,}".format(res["pb50"]["dd"]) + """ and a losing last month - the filter
halved the drawdown.""")

IDEAS += sec("g. PAUSE AFTER LOSSES IN A ROW", """
SETTINGS: "g. Pause for the rest of the day after losses in a row" (OFF)
and "losses in a row" (3).

WHAT IT DOES. After this many losing trades in a row (after costs) no
new trade is opened for the rest of the day (session timezone). Open
trades are not touched. A win starts the count again, and so does a new
day. With partial profit ON only the main part of each setup counts.

IN THE TEST: after 3 losses """ + "{:+,}".format(res["g"]["net"]) + """ (yours """ + "{:+,}".format(res["base"]["net"]) + """). In your three
one-year files it lost less only because it traded less - the profit per
trade did not improve. It is a brake, not an edge.""")

T_ALL = TH + "\n" + "\n".join(row(k) for k in ["base", "rev", "r2", "ln", "ny", "r2only", "mo2", "mo3", "be", "step", "min6"]) + \
    "\n" + "\n".join(row(k) for k in ["a", "b", "c1", "c2", "d", "e", "f0", "f", "pb50", "g"]) + "\n" + \
    "\n".join(row(k) for k in ["hedge", "cost3", "C", "Cny"])

RESULTS = sec("WHICH IDEAS HELPED AND WHICH LOST", """
HOW IT WAS TESTED. The strategy's logic was copied into a Python
simulator and run on real gold 1-minute data from Feb 27 to May 25 2026,
with your settings (CHOCH only, rule 1 + rule 2, pullback 25, stop buffer
1, target R 3, 50 risk, costs 0.6 per ounce, entries 06-23, flat 02:00,
weekend 23:00 Friday). It reproduces your own "CHOCH only" file for that
period: 187 of about 265 trades start in the same minute on the same
side, and those trades net 1,081 in the simulator against 1,077 in your
file. Then ONE setting was changed at a time.
Months: 1 = Feb 27-Mar 25, 2 = Mar 26-Apr 24, 3 = Apr 25-May 25.

""" + T_ALL + """

BETTER in the test: close-and-reverse OFF, New York hours only, step
stop, minimum stop 6, filter f with pullback 50, and the combination.
ABOUT THE SAME: break-even, trailing behind the CHOCH* level, partial
profit, liquidity target, pause after losses.
WORSE: rule 2 only, stacked BOS trades (at any risk), the higher-
timeframe filter, trailing behind every swing, filter f with your 25%
pullback, the hedge (about the same as one copy).

YOUR THREE ONE-YEAR FILES say the same where they can be checked:
  - Commission was 85 to 93% of the loss in 2021-22 and 2023-24. Before
    costs those years were almost flat.
  - Small stops lose most: a minimum stop of 4 to 8 would have cut the
    2021-22 loss from 9,946 to 1,092-3,459.
  - Entries 17:00-23:00 (New York) were the best hours in all three years;
    06:00-17:00 the worst.
  - "Opposite signal" exits lost money in every file - by far the most
    in 2021-22 and 2023-24 (13,754 and 15,192).
  - A smaller R target did NOT help in any year.

BE CAREFUL WITH THESE NUMBERS. Three months, 100 to 270 trades, one kind
of market (gold falling from 5,200 to 4,550). One trade is worth 50 to
150, so a difference of a few hundred can be luck. Trust only what is
better in several months AND in your yearly files. Before you trade a
change, backtest it on your chart over a full year, then check it on a
different year without changing anything.""")

RECO = sec("WHAT I RECOMMEND YOU TRY  -  in this order, one step at a time", """
  1. Group 20 "Opposite signal while in a trade: close and reverse" OFF.
     The clearest gain: better in the test, and the "Opposite signal"
     exits lost money in all three yearly files (by far the most in
     2021-22 and 2023-24).
  2. Group 24 "Skip the setup if the stop is CLOSER than this": 6 on
     gold at today's prices (less on a quiet market).
  3. v9.0 f: premium / discount filter ON, line 50, with the group 20
     rule 1 pullback at 50.
  4. Group 32 step stop ON.
  5. Optional: entries from 17:00 (group 20 "Take entries from" 17) -
     fewer trades, but the best hours in every file.
  6. Check your real broker cost. You model 0.6 per ounce per round trip
     (30 per lot per side). If FxPro charges you less, type the real
     number: at 0.3 per ounce your own settings made """ + "{:+,}".format(res["cost3"]["net"]) + """
     instead of """ + "{:+,}".format(res["base"]["net"]) + """ in the test.
  Backtest each step over a full year on your chart before you go live,
  and go live on a demo account first.""")

V90_CHECK = sec("HOW v9.0 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar, pynescript) read v9.0
    without a syntax error. It rejects broken code (tested on purpose).
  - The settings: the 89 of v8.4 are in the same order and the same
    places; the 15 new ones are at the very end (group 34).
  - Every new name is declared before it is used; ASCII only; no tabs.
  - Every switch OFF: each changed block was read line by line - it
    does exactly what the v8.4 block did (the stop moves, the fill
    records, the rule 2 choice, the size, the order sending).
  - Each idea was built the same way in the Python simulator and checked:
    partial profit - the two parts always filled together (204 setups
    split, 60 too small to split); longs only never took a short; the
    stacked trades were smaller with 50% risk; the trailing stop moved
    in 171 of 264 trades (it can only move forward).
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

HIST84 = sec("v8.4, FOR THE RECORD", "v8.4 = v8.3 + the items 80 to 84 below. v9.0 includes all of it.")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v8.3 NOTES - the history of every version and\n"
       "the full reference of every setting. It is all still true for %s.\n" + "=" * 74 + "\n")
v84 = V84_HEAD + V84_SECTIONS + V84_CHECK + BAN % "v8.4" + fix_body(body83)
v90 = V90_HEAD + IDEAS + RESULTS + RECO + V90_CHECK + HIST84 + V84_SECTIONS + V84_CHECK + BAN % "v9.0" + fix_body(body83)
for name, t in (("v8.4", v84), ("v9.0", v90)):
    assert all(ord(ch) < 128 for ch in t), name
    open(R + "SMC_Structure_Strategy_%s_NOTES.txt" % name, "w").write(t.rstrip("\n") + "\n")
    print(name, len(t.split("\n")), "lines")
