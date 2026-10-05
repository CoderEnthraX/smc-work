# SMC_Structure_Strategy_v12.0_NOTES.txt = new v12.0 part + the v11.2 notes (from "WHAT v11.2 CHANGES" on)
import sys
R = "/home/user/smc-work/"
v112 = open(R + "SMC_Structure_Strategy_v11.2_NOTES.txt").read()
k = v112.index("-" * 74 + "\nWHAT v11.2 CHANGES")
body = v112[k:]
H = "-" * 74
CHECK = open(sys.argv[1]).read().rstrip("\n") if len(sys.argv) > 1 else "  CHECKS"


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v12.0  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v12.0.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v12.0_HANDBOOK.pdf - every setting, with
examples and the value to use.

v12.0 - two new entry rules. RULE 3 enters at the CLOSE of the candle
  that confirms the signal (your CHOCH). RULE 4 does the same, but only
  when the distance from the entry to the stop is within your limits
  (default 3 to 30); a bigger one is skipped, or falls back to rule 1 / 2.
  A new group 39 at the end of the settings. Default "Off (rules 1 / 2 as
  now)": with it v12.0 trades exactly like v11.2.

SETTINGS: 126 - the 122 of v11.2 in the same places + 4 new at the end.
  Replace the code while you are FLAT (no open trade), then delete the
  alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v12.0 CHANGES", """
121. ENTRY AT THE CLOSE OF THE SIGNAL CANDLE (group 39, the last 4)
       Entry at the close of the signal candle
                         Off (rules 1 / 2 as now)  /  RULE 3 - always
                         enter at the close  /  RULE 4 - enter at the
                         close only if the stop distance is within the
                         limits
       - RULE 4: skip if the stop is FURTHER than (0 = off)    30
       - RULE 4: skip if the stop is CLOSER than (0 = off)      3
       - RULE 4: when the stop is too far
                         Skip the setup  /  Fall back to RULE 1 / 2
                         (wait for the pullback)

     RULE 3: the moment a candle CLOSES and confirms the signal (your
     CHOCH; a BOS too if you trade BOS), the strategy buys or sells at
     market. TradingView and MT5 cannot fill on a candle that has already
     closed, so the order fills at the OPEN of the next candle - a second
     later, practically the close price. No pullback is waited for.
     Rules 1 and 2 are not used while rule 3 / 4 is on.

     The stop and target are the usual ones:
       stop   = the CHOCH* level + your stop buffer (group 20 / 38)
       target = your R multiple from the entry (+ the commission push)
       size   = from your risk and the entry-to-stop distance

     EXAMPLE (gold 1m, a bullish CHOCH, buffer 1.00, target 3R, risk 50)
       CHOCH* level 4,090.00   ->  stop 4,089.00
       the CHOCH candle closes at 4,101.00  ->  BUY at the next open
       distance 12.00   target 4,101 + 36 = 4,137 (+ the commission push)
       size 50 / (12 + 0.76) = 3.9  ->  4 oz = 0.04 lot

     RULE 4: the same, but first the distance from the close to the stop
     is checked against the two limits:
       candle closes at   stop       distance   rule 4 (3 - 30)
       4,101.00           4,089.00   12.00      enters
       4,125.00 (huge)    4,089.00   36.00      too far
       4,091.50           4,089.00    2.50      too close - skipped
     The limits are in the unit of group 38 like group 24: Price =
     dollars on gold (30 = 30.00); Pips (30 = 30 pips = 3.00 on gold!);
     % (of the entry price). 0 = that limit off.

     "WHEN THE STOP IS TOO FAR":
       Skip the setup (default)  the signal opens nothing.
       Fall back to RULE 1 / 2   the setup is armed the normal way
                                 instead: a limit order at the pullback
                                 (rule 1) or the broken pivot (rule 2),
                                 with your rule 1 / 2 switches and the
                                 higher-timeframe rule of rule 2. That
                                 pullback entry must keep the SAME
                                 limits (3 - 30): if its stop distance is
                                 outside them, it is cancelled too.
     A stop that is too CLOSE is always skipped (a pullback entry would be
     even closer).

     WHAT STAYS THE SAME: entry hours (06:00 - 23:00 for you), the 02:00
     force close, the weekend, news windows, US holidays, the loss pause,
     loss recovery, the floor, the daily limits, group 24, the higher-
     timeframe filters (b, favourable / against / auto). Rule 3 / 4 do NOT
     need the higher timeframe to agree (like rule 1).

     ONE CHANCE: the market order is sent on the signal candle only. A
     signal outside the entry hours, or while trading is blocked, opens
     nothing - there is no late entry. With "close and reverse" ON, a
     signal that reverses an open trade enters one candle later (after the
     old trade is closed), and rule 4 checks that candle's close.

     THE BROKER MESSAGE: unchanged. The alert fires when the order fills
     ("Order fills only") and TheConnector opens the trade at market with
     the stop and target, exactly as for rules 1 and 2.

     THE TABLE: a new last row "ENTRY AT THE SIGNAL CLOSE (group 39)", e.g.
       RULE 4 (3 - 30)  -  12 entered at the close  |  skipped: too far 4
       / too close 1
     The audit labels (group 20) say "R3 ARMED - entry at the close, stop
     12.00", "SKIP - RULE 4: stop too far (36.00)" and so on.

122. IS IT BETTER? (honest)
     NOT TESTED for profit - you asked me to build it without the test.
     It was tested only for CORRECTNESS (below). Three things to know:
     - Entering at the close puts the stop further away than rule 1's
       25% pullback (about one third further), so the SAME risk buys a
       SMALLER size, and the target is further away too.
     - Every entry is a market order: you pay the full spread at once.
     - 5.75 years of tests found no 1-minute entry setting that made money
       in both 2021-23 and 2024-26. Run v12.0 in TradingView (rule 3, then
       rule 4) on the same dates as before and compare, and use a demo
       account before real money. I can run the 5.75-year test whenever
       you want it.""")

S += sec("HOW v12.0 WAS CHECKED", CHECK + """
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v11.2 NOTES - still true for v12.0. The new\n"
       "entry rules (item 121) are optional; with \"Off\" v12.0 works exactly\nlike v11.2.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S + BAN).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v12.0_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v12.0 notes", len(t.split("\n")), "lines")
