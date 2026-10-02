# SMC_Structure_Strategy_v11.1_NOTES.txt = new v11.1 part + the v11.0 notes (from "WHAT v11.0 CHANGES" on)
R = "/home/user/smc-work/"
v110 = open(R + "SMC_Structure_Strategy_v11.0_NOTES.txt").read()
k = v110.index("-" * 74 + "\nWHAT v11.0 CHANGES")
body = v110[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v11.1  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v11.1.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v11.1_HANDBOOK.pdf - every setting, with
examples and the value to use.

v11.1 - six more choices in "Take trades on" (group 20), both optional:
  - "... - against the higher timeframe"  (CHOCH / BOS / both)
  - "... - auto: against HTF to equilibrium, then with HTF"  (CHOCH /
    BOS / both)
  The 9 choices of v11.0 are unchanged, so your saved settings stay as
  they are, and with one of them picked v11.1 trades exactly like v11.0.

SETTINGS: 118 - the same as v11.0, in the same places. Replace the code
  while you are FLAT (no open trade), then delete the alert and create it
  again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v11.1 CHANGES", """
116. "AGAINST THE HIGHER TIMEFRAME" MODES (group 20, "Take trades on")
       CHOCH only - against the higher timeframe
       BOS only - against the higher timeframe
       CHOCH and BOS - against the higher timeframe

     WHY: in 3 months of real gold data, the trades AGAINST the 15m won
     more than the trades WITH it - also with the same entry for both:
       rule 1 only (25%)   with the 15m     51 trades  35% wins    +26
                           against the 15m  61 trades  43% wins   +612
     That is a short period - see item 118.

     HOW IT WORKS - the mirror of the favourable modes (item 112):
       - Higher timeframe bullish -> only SELLS; bearish -> only BUYS;
         not clear yet -> no trades.
       - Entry: always RULE 1 (your pullback %). Rule 2 needs the higher
         timeframe to agree, so it is never used here - with rule 1 OFF
         these modes take no trades (the table says so).
       - A WAITING order is cancelled when the higher timeframe turns to
         agree with it. An OPEN trade keeps running to its stop or target.
       - Filter b (group 34) is not used in these modes.

     EXAMPLE (1m chart, CHOCH only - against the higher timeframe)
       15m trend   1m signal          result
       bullish     bearish CHOCH      SELL at 25%
       bullish     bullish CHOCH      skipped
       bearish     bullish CHOCH      BUY at 25%
       bearish     bearish CHOCH      skipped

117. "AUTO" MODES (group 20, "Take trades on")
       CHOCH only - auto: against HTF to equilibrium, then with HTF
       BOS only - auto: against HTF to equilibrium, then with HTF
       CHOCH and BOS - auto: against HTF to equilibrium, then with HTF

     HOW IT WORKS
       Every CHOCH or BOS on the higher timeframe starts a new leg.
       PART 1 - until the price touches the equilibrium of that leg (the
         % in group 37): only signals AGAINST the higher timeframe,
         entered by rule 1 - trading the pullback.
       PART 2 - from the touch on: only signals WITH the higher
         timeframe, entered like the favourable modes (rule 2 on = the
         broken pivot, else rule 1) - trading the move back.
       The next higher-timeframe CHOCH or BOS starts part 1 again.
       - A WAITING order on the wrong side after a switch is cancelled;
         an OPEN trade keeps running.
       - The % comes from group 37 ("the equilibrium, % pullback"), even
         with the group 37 switch off. The group 37 switch itself does not
         block these modes.
       - Higher timeframe not clear yet -> no trades. With rule 1 off,
         part 1 takes no trades.

     EXAMPLE (1m chart, 15m higher timeframe, 50%)
       10:00  15m bullish BOS, leg 3,950 -> 4,050, level 4,000  PART 1
       10:20  1m bearish CHOCH -> SELL at 25% (rule 1)          against
       10:40  1m bullish CHOCH -> skipped                       against
       11:40  price touches 4,000                                PART 2
              (a waiting sell order is cancelled now)
       11:50  1m bullish CHOCH -> BUY (rule 2 / rule 1)          with
       13:00  new 15m BOS -> a new leg                           PART 1
     The table row "HTF EQUILIBRIUM FIRST (group 37)" shows "AUTO part 1 -
     AGAINST the HTF until 4,000.00" or "AUTO part 2 - WITH the HTF".

118. WHAT 3 MONTHS OF REAL GOLD DATA SHOWED (your settings: CHOCH only,
     rule 1 + 2, 25%, reverse OFF; Feb 25 - May 26, 2026)
       setting                               trades  wins    net  lowest
       everything off                          112    38%   +793    -274
       favourable                               93    32%    -82    -182
       AGAINST the 15m                          90    42%   +767    -193
       equilibrium 50% (group 37 on)            84    43% +1,410    -128
       AUTO 50%                                100    29%   -511    -739
         part 1 (against)  26 trades -229 / part 2 (with) 74 trades -282
       AUTO 61.8%                               94    32%    -21    -249
       AUTO 50% + pause 3 losses / 2 days       61    31%   +120    -109
     In these 3 months the trades WITH the 15m after its pullback lost -
     the opposite of what the auto mode bets on. Only 3 months: test the
     modes in the long backtests (one year or more) before using one
     live, and compare each with everything off.""")

S += sec("HOW v11.1 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v11.1 without a
    syntax error. Every new name is declared before it is used and clashes
    with no old one. ASCII only; no tabs; no strategy.close_all.
  - The settings: the same 118 as v11.0; "Take trades on" keeps its 9
    old choices in the same order and adds 6 at the end.
  - The simulator on real gold 1-minute data (Feb 25 - May 26, 2026):
      the old choices: every order and trade the same as v11.0;
      AGAINST modes, 3 modes x 3 rule settings x reverse on / off: 0
        trades with the higher timeframe, always rule 1, 0 filled after
        the higher timeframe turned to agree; rule 2 only = no trades;
        with a test higher timeframe that flips often, 25 to 91 waiting
        orders were cancelled - none filled after it;
      AUTO modes, 50% and 61.8% x 3 modes x 3 rule settings x reverse
        on / off (36 runs): the side allowed was worked out separately
        from the higher-timeframe legs - 0 trades on the wrong side, 0
        with the wrong entry rule, 0 filled after a switch, 160 waiting
        orders cancelled at a switch;
      AUTO together with the group 37 switch and the pause: 0 errors.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v11.0 NOTES - still true for v11.1. The new\n"
       "choices (items 116-117) are optional; the old ones work exactly like v11.0.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v11.1_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v11.1 notes", len(t.split("\n")), "lines")
