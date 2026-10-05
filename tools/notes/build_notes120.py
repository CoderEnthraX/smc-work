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

v12.0 - a new entry rule. RULE 3 enters at the CLOSE of the candle that
  confirms the signal (your CHOCH), wherever it closes. An optional switch
  lets it enter only when the close is near the level the candle broke
  (default 3); another one sends a close that is too far to the normal
  rule 1 / 2 setup instead of skipping it. A new group 39 at the end of
  the settings, everything OFF: with it OFF v12.0 trades exactly like
  v11.2.

SETTINGS: 126 - the 122 of v11.2 in the same places + 4 new at the end.
  Replace the code while you are FLAT (no open trade), then delete the
  alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v12.0 CHANGES", """
121. RULE 3 - ENTER AT THE CLOSE OF THE SIGNAL CANDLE (group 39, last 4)
       RULE 3 - enter at the close of the signal candle          OFF
       - RULE 3: only if the close is near the broken level      OFF
       - the most the close may be beyond the broken level       3
       - if the close is too far: fall back to RULE 1 / 2        OFF

     RULE 3 (OFF by default): the moment a candle CLOSES and confirms the
     signal (your CHOCH; a BOS too if you trade BOS), the strategy buys or
     sells at market. It does not matter where the candle closes.
     TradingView and MT5 cannot fill on a candle that has already closed,
     so the order fills at the OPEN of the next candle - a second later,
     practically the close price. No pullback is waited for. Rules 1 and 2
     are not used while rule 3 is on (except by the fall back below).

     The stop and target are the usual ones:
       stop   = the CHOCH* level + your stop buffer (group 20 / 38)
       target = your R multiple from the entry (+ the commission push)
       size   = from your risk and the entry-to-stop distance

     EXAMPLE (gold 1m, a bullish CHOCH, buffer 1.00, target 3R, risk 50)
       CHOCH* level 4,090.00   ->  stop 4,089.00
       the CHOCH candle closes at 4,101.00  ->  BUY at the next open
       distance 12.00   target 4,101 + 36 = 4,137 (+ the commission push)
       size 50 / (12 + 0.76) = 3.9  ->  4 oz = 0.04 lot

     "ONLY IF THE CLOSE IS NEAR THE BROKEN LEVEL" (OFF by default): rule 3
     enters only when the close is at most the distance (default 3) beyond
     the level the candle broke - the broken high of a bullish CHOCH, the
     broken low of a bearish one. A huge candle that closes far beyond it
     is skipped (no trade, no pullback order) - unless the fall back below
     is ON.
       broken high   candle closes at   beyond   with 3
       4,100.00      4,102.50           2.50     enters
       4,100.00      4,103.00           3.00     enters (3.00 is allowed)
       4,100.00      4,108.00           8.00     skipped
     The distance is in the unit of group 38 like group 24: Price = dollars
     on gold (3 = 3.00); Pips (3 pips = 0.30 on gold!); % of the price.

     "IF THE CLOSE IS TOO FAR: FALL BACK TO RULE 1 / 2" (OFF by default):
     works with the switch above. OFF: a close too far is skipped. ON:
     that signal gets the normal rule 1 / 2 setup instead, exactly as with
     rule 3 OFF, by your RULE 1 / RULE 2 switches - rule 2 at the broken
     pivot when the higher timeframe agrees, otherwise rule 1 at your
     pullback %.
       Broken high 4,100, CHOCH* level 4,090 (stop 4,089), candle high
       4,110, pullback 25%, the candle closes at 4,108 (8 beyond):
         fall back OFF  ->  skipped, no trade
         fall back ON   ->  buy limit at 4,100 (rule 2, the higher
                            timeframe agrees) or at 4,105 (rule 1:
                            4,110 - 25% of the 20 leg)
     The limit may never be reached - then there is no trade, as always
     with rules 1 and 2.

     WHICH RULE TRADES (near-the-level switch ON, fall back ON):
       RULE 1  RULE 2  RULE 3   close near the level   close too far
       on      on      on       rule 3 at the close    rule 2 or rule 1
       on      off     on       rule 3 at the close    rule 1
       off     on      on       rule 3 at the close    rule 2 (if agree)
       off     off     on       rule 3 at the close    skipped
     With the fall back OFF, a close too far is always skipped.

     SKIP IF THE STOP IS CLOSER / FURTHER THAN: these are the group 24
     settings you already have - "Skip the setup if the stop is CLOSER than
     this (price)" and "... FURTHER than this (price)", 0 = off (default).
     They work for ALL entry rules: rule 1, rule 2 and now rule 3 (for
     rule 3 the distance is from the close to the stop). Example with
     CLOSER 5 and FURTHER 30: a stop 12.00 away trades; 3.00 or 36.00 away
     is skipped.

     WHAT STAYS THE SAME: entry hours (06:00 - 23:00 for you), the 02:00
     force close, the weekend, news windows, US holidays, the loss pause,
     loss recovery, the floor, the daily limits, the higher-timeframe
     filters (b, favourable / against / auto). Rule 3 does NOT need the
     higher timeframe to agree (like rule 1).

     ONE CHANCE: the market order is sent on the signal candle only. A
     signal outside the entry hours, or while trading is blocked, opens
     nothing - there is no late entry. With "close and reverse" ON, a
     signal that reverses an open trade enters one candle later (after the
     old trade is closed).

     THE BROKER MESSAGE: unchanged. The alert fires when the order fills
     ("Order fills only") and TheConnector opens the trade at market with
     the stop and target, exactly as for rules 1 and 2.

     THE TABLE: a new last row "RULE 3 - ENTRY AT THE SIGNAL CLOSE (group
     39)", e.g. "on - 12 entered at the close | close within 3 of the
     break: 4 skipped, 7 fell back to rule 1 / 2". The audit labels (group
     20) say "R3 ARMED - entry at the close", "SKIP - RULE 3: close 8.00
     beyond the broken level", or "RULE 3: close 8.00 beyond the broken
     level - fall back to RULE 1 / 2:" and the rule 1 / 2 label.

122. IS IT BETTER? (honest)
     NOT TESTED for profit - you asked me to build it without the test.
     It was tested only for CORRECTNESS (below). Things to know:
     - Entering at the close puts the stop further away than rule 1's
       25% pullback (about one third further), so the SAME risk buys a
       SMALLER size, and the target is further away too.
     - Every entry is a market order: you pay the full spread at once.
     - 5.75 years of tests found no 1-minute entry setting that made money
       in both 2021-23 and 2024-26. Run v12.0 in TradingView (rule 3, then
       rule 3 with the broken-level option, then with the fall back) on the
       same dates as before and compare, and use a demo account before real
       money. I can run the
       5.75-year test whenever you want it.""")

S += sec("HOW v12.0 WAS CHECKED", CHECK + """
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v11.2 NOTES - still true for v12.0. The new\n"
       "entry rule (item 121) is optional; with it OFF v12.0 works exactly like\nv11.2.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S + BAN).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v12.0_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v12.0 notes", len(t.split("\n")), "lines")
