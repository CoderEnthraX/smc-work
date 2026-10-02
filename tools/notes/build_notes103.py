# SMC_Structure_Strategy_v10.3_NOTES.txt = new v10.3 part + the v10.2 notes (from "WHAT v10.2 CHANGES" on)
R = "/home/user/smc-work/"
v102 = open(R + "SMC_Structure_Strategy_v10.2_NOTES.txt").read()
k = v102.index("-" * 74 + "\nWHAT v10.2 CHANGES")
body = v102[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v10.3  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v10.3.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v10.3_HANDBOOK.pdf - every setting, with
examples and the value to use.

v10.3 in two lines:
  - NEW "Split the loss over this many trades" (group 21, the last
    setting): what the loss-recovery rule asks for is divided by it.
  - Default 1 = exactly v10.2. Everything else is v10.2.

SETTINGS: 109 - the 108 of v10.2 in the same places, plus 1 at the very
  end (shown in group 21). Replace the code while you are FLAT (no open
  trade), then delete the alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v10.3 CHANGES", """
104. SPLIT THE LOSS OVER THIS MANY TRADES (group 21, the last setting).
     Default 1. From 1 to 20, in steps of 0.5.
     The loss-recovery rule works out its amount as before, and then
     that amount is DIVIDED by this number - never less than your BASE
     risk:
       A and A+   (loss + Rule A amount) / this number
       B and B+   2 x loss / this number
       C and C+   loss / this number
     1 = the next trade risks everything the rule asks for (as v10.2).

     WHY 3: your target is 1:3, so a full take-profit (TP) win pays 3 x
     the risk. Risk one third of the loss, and one TP win pays back
     3 x 1/3 = the whole loss. Set it to your risk:reward - 3 for a 1:3
     target, 2.5 for a 1:2.5 target.
     With 3 and a 1:3 target, one full TP win pays back:
       C / C+   the whole loss           -> the total is back at 0
       A / A+   the loss + your amount   -> the total is + your amount
       B / B+   2 x the loss             -> the total is + the loss

     EXAMPLE 1 - four losses, then one TP win (C+, base 50, 1:3 target)
       trade  result    split 1: risk   total    split 3: risk   total
         1    loss               50       -50               50     -50
         2    loss               50      -100               50    -100
         3    loss              100      -200               50    -150
         4    loss              200      -400               50    -200
         5    TP                400      +800            66.67       0
     With 3, trade 2 asks 50 / 3 = 16.67 - below the base, so it risks
     50. Trade 5 asks 200 / 3 = 66.67. The TP pays 200, the total is 0,
     and trade 6 is the base 50 again.

     EXAMPLE 2 - ten losses in a row (what happened on Feb 13-17, 2023)
       split 1: risks 50, 50, 100, 200, 400, 800, 1,600, 3,200, 6,400,
                12,800 -> total -25,600 (more than a 10,000 account)
       split 3: risks 50, 50, 50, 50, 66.67, 88.89, 118.52, 158.02,
                210.70, 280.93 -> total -1,123.73
       On split 3, trade 11 risks 374.58. A full TP win pays 1,123.73
       and the total is back at 0.

     EXAMPLE 3 - a win that is not a full TP (C+, split 3)
       Time flat, news window, weekend flat and opposite signal close a
       trade early, so it pays less than 3 x and only part of the loss
       comes back. The rest carries on:
       total -355.56 -> risk 118.52 -> closed at time flat at +118.52
       -> total -237.04 -> next risk 79.01 -> TP pays 237.04 -> total 0
       -> back to the base.

     EXAMPLE 4 - A+ and B+ with split 3
       A+ (amount 50): total -424.07 -> the rule asks 474.07 -> risk
         158.02 -> TP pays 474.07 -> total +50 (the loss + your amount).
         This is exactly what Rule A was meant to do.
       B+: total -771.60 -> the rule asks 1,543.20 -> risk 514.40 ->
         TP pays 1,543.20 -> total +771.60.

     HOW TO CHOOSE THE NUMBER (1:3 target)
       number     one full TP win pays back     in a losing streak
       1 (v10.2)  3 x the loss                  the loss doubles
       2          1.5 x the loss                the loss x 1.5 per loss
       3          exactly the loss              the loss x 1.33 per loss
       6          half the loss (2 TP wins)     the loss x 1.17 per loss

     GOOD TO KNOW
       - The hard cap is checked AFTER the split.
       - The size is still rounded to your lot step and cut by Max
         leverage.
       - The table row "LOSS RECOVERY" shows it, for example
         "C+ - total below 0 | split over 3 trades | whole history".
         "Risk NEXT trade" shows the risk after the split.
       - It does not turn losing trades into winners. A long losing
         streak still makes the risk grow, only much more slowly. Keep a
         real hard cap.

105. THE BASE RISK COMES FROM YOUR SETTINGS - NOTHING IS FIXED AT 50.
     Every rule (A / B / C and A+ / B+ / C+) and the split use "BASE
     risk per trade" (group 21) as the base, and "Rule A: amount added
     on top of the losses carried" as the Rule A amount. 50 is only the
     default of both. Change them and everything scales with them.
     Example - base 100, C+, split 3, 1:3 target: four losses = -400
     (risks 100, 100, 100, 100 - 100 / 3, 200 / 3 and 300 / 3 are all at
     or below the base). Trade 5 risks 400 / 3 = 133.33. A TP pays 400,
     the total is 0, and the next trade risks the base 100 again.
     Checked in the simulator with base 50 and with base 75 (Rule A
     amount 40).

106. YOUR RULE C+ FILE (2023, trades 1-123) - WHAT HAPPENED
     Your settings: account 10,000, base 50, Rule C+, hard cap 100,000,
     "Stop for the rest of the day", Max leverage 100, Properties 300x,
     CHOCH only, close and reverse OFF.
     - C+ sized every trade exactly by its rule. From trade 64 (Feb 13,
       total +28.54) to trade 73 there were 10 losses in a row. Each loss
       was as big as the whole hole, so the hole doubled each time:
       -2,018.03 after trade 72, -8,162.67 after trade 78 (Feb 17).
     - From trade 76 on, the rule asked for more than Max leverage 100
       allows (trade 76: about 587 oz asked, 359 given). A TP win still
       paid 3 x - but 3 x the REAL, cut risk: trade 87 risked 269.78
       against a loss of 8,722.46 and won 817.74.
     - The total never went back above 0, so C+ never went back to 50.
     - The cap (100,000) never fired: the biggest loss the rule worked
       with was 9,977.10. A cap bigger than the account cannot protect
       it.
     - After trade 123 (Mar 27) only 15.66 was left (-99.84%). One ounce
       cost about 1,955, so at 100x the biggest order was 0.8 oz, which
       rounds to 0. Every later setup had size 0: no trade for the rest
       of 2023. It is not a bug - the account was empty.
     - Properties 300x is right (3 x Max leverage): no margin call.
     With split 3, trades 64-78 would have ended near -1,100 instead of
     -8,162.67 (an estimate from each trade's own result in R).""")

S += sec("HOW TO USE LOSS RECOVERY  -  step by step", """
 1. BASE risk per trade (group 21): what one normal trade may lose -
    for example 50 on a 10,000 account (0.5%).
 2. Loss-recovery sizing: Rule C+ (or A+). The "+" rules work only while
    the total P&L is below 0 - profit already made is a cushion.
 3. Split the loss over this many trades: your risk:reward - 3 for a
    1:3 target.
 4. HARD CAP on risk per trade: a few % of the account - for example
    300 to 500 on 10,000. Never bigger than the account.
 5. When the cap is reached: "Stop for the rest of the day" (starts
    fresh the next day - the loss is forgotten by the rule, but the
    money is still gone) or "Stop permanently" (waits for you).
 6. Max leverage: the real leverage FxPro gives you on gold, or lower -
    otherwise FxPro rejects orders the backtest took, and live does not
    match the backtest. Properties (margin for long / short): 3 x that
    leverage or more, so TradingView never simulates a margin call.
 7. Loss recovery counts from: "The whole chart history" to test. Switch
    to "When the strategy goes live (automatic)" before you create the
    alert, so the replayed past does not size your first live trade.
 8. Read the table: LOSS RECOVERY (rule, split, counts from), Losses
    carried, Risk NEXT trade, Risk cap hit / HALT, Trades cut by
    leverage cap, Margin calls (Properties).
 9. Backtest the same period with "Off" and with your rule, and compare
    the net P&L AND the lowest point of the account. Then run it on a
    demo account.
10. Going live: replace the code while FLAT, delete the alert and create
    it again. Message ONLY {{strategy.order.alert_message}}, condition
    "Order fills only", your access key only in the webhook URL inside
    TradingView.""")

S += sec("HOW v10.3 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v10.3 without a
    syntax error.
  - The settings: the 108 of v10.2 in the same order and places, the new
    one at the very end. It is declared before it is used; ASCII only;
    no tabs; no strategy.close_all.
  - The simulator on real gold 1-minute data (Feb 25 - May 26, 2026):
    all six rules, split 1 / 2.5 / 3, base 50 (Rule A amount 50) and
    base 75 (Rule A amount 40), counted from the whole history and from
    Apr 1: 50,779 orders, each sized exactly by its rule with the loss
    worked out again independently - 0 differences. With split 1 every
    order and every trade result was the same as v10.2.
  - Your settings (CHOCH only, close and reverse OFF, Max leverage 100,
    Stop for the rest of the day) on the same data, 112 trades:
       rule           net P&L    lowest account   biggest risk
       Off            +793.31        9,725.91          50.00
       C+ split 1   +1,586.82        9,618.89         381.11
       C+ split 3     +944.05        9,779.90          73.37
       A+ split 3   +1,007.88        9,783.57          88.81
    These 3 months had no long losing streak while the total was below
    0, so split 1 earned the most here. Your 2023 file shows the other
    side: one bad week took split 1 to -8,162.67. Split 3 earns less
    when things go well and loses far less when they do not. (A cap of
    500 gave the same results - no risk reached 500.)
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v10.2 NOTES - still true for v10.3. The new\n"
       "setting 'split the loss over this many trades' (item 104) is 1 by default,\nwhich works exactly like v10.2.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v10.3_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v10.3 notes", len(t.split("\n")), "lines")
