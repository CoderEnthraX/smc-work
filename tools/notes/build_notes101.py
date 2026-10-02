# SMC_Structure_Strategy_v10.1_NOTES.txt = new v10.1 part + the v10.0 notes (from "WHAT v10.0 CHANGES" on)
R = "/home/user/smc-work/"
v10 = open(R + "SMC_Structure_Strategy_v10.0_NOTES.txt").read()
k = v10.index("-" * 74 + "\nWHAT v10.0 CHANGES")
body10 = v10[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v10.1  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v10.1.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v10.1_HANDBOOK.pdf - every setting, with
examples and the value to use.

v10.1 in three lines:
  - "Loss recovery counts from" is removed: every trade on the chart
    counts again, as in v9.1. To see a long backtest, raise the hard cap.
  - NEW Rule A+, B+ and C+: they work only with the loss of your TOTAL
    P&L below zero - profit already made is a cushion.
  - Rule A, B and C are unchanged (the loss since the high point).

SETTINGS: 106 - the same settings in the same places as v9.1 (v10.0's two
  "counts from" settings are gone). "Loss-recovery sizing" has three more
  choices. Replace the code while you are FLAT (no open trade), then
  delete the alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v10.1 CHANGES", """
100. "LOSS RECOVERY COUNTS FROM" REMOVED. Every closed trade on the chart
     counts for loss recovery again, as in v9.1. Rule A, B and C still
     never go below the base risk (v10.0), and trades that close on the
     same candle are still added together first.
     This brings back the v9.1 warning: with "Stop permanently", if the
     cap was reached anywhere in the chart's history the strategy is
     already stopped when you create the alert. Check the table row
     "Risk cap hit / HALT" before you create the alert, or raise the cap.

101. RULE A+, B+ AND C+ (group 21 "Loss-recovery sizing", three new
     choices - the hint in brackets says what each one does):
       Rule A+ (only when total P&L is below 0: that loss + amount)
       Rule B+ (only when total P&L is below 0: 2 x that loss)
       Rule C+ (only when total P&L is below 0: that loss)

     THE TWO WAYS TO MEASURE THE LOSS
       Rule A / B / C     the loss since the HIGH POINT. A loss adds, a
                          profit takes off, never below zero - profit
                          beyond what is owed is not saved.
       Rule A+ / B+ / C+  the TOTAL below zero: how far the total Net P&L
                          of all closed trades (the Cumulative P&L of the
                          List of Trades) is below zero. While the total
                          is above zero every trade is the base risk.
     Then the same formulas: A = loss + your Rule A amount, B = 2 x loss,
     C = loss - all never below the base risk.

     YOUR RULE C FILE (Sep 7-29), next risk after each trade:
       after trade  total P&L    Rule C (since the high)  Rule C+ (below 0)
            7        +665.67          50                     50
           12        +294.05         371.62                  50
           14        -790.93        1456.60                 790.93
           15        -494.53        1160.20                 494.53
           16       -1642.78        2308.45                1642.78
           17        +243.86         421.81                  50
           18        +741.34          50                     50
     So with C+, trade 16 risks about 494.53 and trade 18 is back to 50 -
     what you expected. With C they risk 1,160.20 and 421.81, because the
     account had been at +665.67 and C recovers every drop from a high.

     GOOD TO KNOW
       - "Total" means every closed trade on the chart. In a long backtest,
         once the account is well up, A+ / B+ / C+ do nothing until that
         profit is lost again.
       - "Stop for the rest of the day" clears the loss the next morning;
         for A+ / B+ / C+ the total starts again from zero.
       - The table row "LOSS RECOVERY" names the rule, for example
         "C+ - total below 0"; the row "Losses carried" shows the loss the
         rule is working with.

102. WHAT YOUR FOUR v10.0 FILES SHOWED (checked trade by trade)
       - Rule A, B and C: every trade was sized exactly by its rule
         (96 trades with a visible stop, 38 more checked against your
         "Off" file). Differences from the pure ladder came from "Max
         leverage" 30 (group 21), which cut 18 trades (Rule B: 12), and
         from "Stop for the rest of the day", which cleared Rule B's
         5,386 of losses on Sep 14.
       - Fewer trades: none of the 45 trades ended by "Opposite signal".
         "Opposite signal while in a trade: close and reverse" (group 20)
         was OFF on that chart - with it OFF every CHOCH that comes while
         a trade is open is skipped (in the 3-month test: 264 trades ON,
         109 OFF). Only 2 setup numbers were missing (S11, S46), so the
         cancel on a new BOS took out at most 2 setups.""")

S += sec("HOW v10.1 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v10.1 without a
    syntax error.
  - The settings are exactly v9.1's 106, in the same order; nothing of
    "counts from" is left. ASCII only; no tabs; no strategy.close_all.
  - Your Rule C file, worked with C and C+: C+ gives 494.53 for trade 16
    and 50 for trade 18.
  - The simulator on real gold 1-minute data, all six rules (A, B, C,
    A+, B+, C+): every order was sized exactly by its rule, with the loss
    worked out again independently from the closed trades - 4,091 orders,
    0 differences.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v10.0 NOTES - still true for v10.1, EXCEPT item\n"
       "98: 'loss recovery counts from' was removed in v10.1, every trade on the\nchart counts.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body10
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v10.1_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v10.1 notes", len(t.split("\n")), "lines")
