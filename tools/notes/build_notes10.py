# SMC_Structure_Strategy_v10.0_NOTES.txt = new v10.0 part + the v9.1 notes (from "WHAT v9.1 CHANGES" on)
R = "/home/user/smc-work/"
v91 = open(R + "SMC_Structure_Strategy_v9.1_NOTES.txt").read()
k = v91.index("-" * 74 + "\nWHAT v9.1 CHANGES")
body91 = v91[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v10.0  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v10.0.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v10.0_HANDBOOK.pdf - every setting, with
examples and the value to use.

v10.0 in three lines:
  - Loss recovery has three rules - A: losses carried + your amount,
    B: 2 x losses carried, NEW C: losses carried. All three are never
    less than your base risk, and go back to it when the losses carried
    are paid off.
  - NEW "loss recovery counts from" (group 21): by default only trades
    that close after the strategy goes live count - the chart's past can
    no longer stop the strategy before it starts.
  - Everything else is v9.1: orders only fill on their own signal's
    leg, the hard cap stops trading until you raise it, and the v9.0
    ideas (group 34) are all OFF.

SETTINGS: 108 - the 106 of v9.1 in the same places, plus 2 at the very
  end (shown in group 21). Replace the code while you are FLAT (no open
  trade), then delete the alert and create it again.

HEDGE: add v10.0 to the chart twice - copy 1 "Longs only", copy 2 "Shorts
only" (group 33), close and reverse OFF in both, tags smcL / smcS, one
alert per copy. Each copy keeps its own losses carried.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v10.0 CHANGES", """
97. LOSS RECOVERY: RULE A, B AND C (group 21 "Loss-recovery sizing").

    LOSSES CARRIED - the same memory for all three rules:
      - every closed trade adds its real loss or takes off its real
        profit - the Net P&L after commission that the List of Trades
        shows. A small loss adds a little, a small profit takes off a
        little. Trades that close on the same candle are added together
        first.
      - never below zero; carried into the next days.

    THE RULES (base risk 50, Rule A amount 50):
      Rule A   next risk = losses carried + your Rule A amount
      Rule B   next risk = 2 x losses carried
      Rule C   next risk = losses carried                        (new)
      ALL      never less than the base risk (50); back to the base
               risk as soon as the losses carried reach 0 - profit
               beyond that is not saved.

    YOUR RULE B EXAMPLE
      trade  risk             result      carried after
        1     50              -50           50
        2    2 x 50  = 100    -100         150
        3    2 x 150 = 300    +50 (cut)    100
        4    2 x 100 = 200    -10          110
        5    2 x 110 = 220

    YOUR RULE C EXAMPLE
      trade  risk                   result      carried after
        1     50                    -10 (news)    10
        2     50 (10 is below 50)   -50           60
        3     60                    +20 (cut)     40
        4     50 (40 is below 50)

    YOUR RULE A EXAMPLE: 50, 100, 130, 160, 140, then 50 (see item 94).
    NEW IN RULE A: never less than the base - with a Rule A amount of 10
    and a loss of only 2, the next trade risks 50, not 12.

    WHY RULE B MAY HAVE LOOKED WRONG BEFORE. Rule B has used exactly this
    arithmetic since v2.3. What can make a trade's risk differ from the
    ladder:
      - the size is rounded to your lot step. On gold 0.01 lot = 1 ounce;
        with a 15-point stop that is about 15.60 of risk per step, so a
        risk of 100 becomes 93.60 or 109.20;
      - "Max leverage" (group 21, 30 by default) cuts a big size: at 30x
        and 10,000 equity no more than about 66 ounces of gold. A Rule B
        risk of 300 with a 3-point stop needs 83 ounces, so it is cut
        (table row "Trades cut by leverage cap"). Raise Max leverage if
        your broker allows it;
      - with "Stop for the rest of the day" (the old default) the losses
        carried were cleared the morning after the cap stopped trading;
      - up to v9.0, Rule A (not B) divided by R.

98. LOSS RECOVERY COUNTS FROM (group 21, new setting).
      WHEN THE STRATEGY GOES LIVE (automatic, default): only trades that
        close from the first live candle on count - the moment you create
        the alert, or open the chart. The past candles are ignored, so
        the strategy always starts live with 0 carried and not stopped.
        Nothing to type.
      A DATE I CHOOSE: only trades that close on or after the date below.
      THE WHOLE CHART HISTORY: every trade on the chart (v9.1). Use it to
        see a rule in the backtest.
    Good to know with the automatic choice:
      - the backtest shows every trade at the base risk - to see a rule
        in the backtest, choose "The whole chart history" for a while;
      - changing any setting (raising the cap too), or creating the alert
        again, starts from 0 again. Very rarely TradingView restarts an
        alert on its own, which also starts from 0.
    The table row "LOSS RECOVERY (A / B / C)" shows the rule and where it
    counts from, for example "B - 2 x losses | from live 30 Sep 09:15".

99. THE CAP, AS IN v9.1: when the next risk would be above the hard cap,
    no new trade opens - today and every day after - until you raise the
    cap ("Stop permanently", the default). With the automatic choice the
    chart's past can no longer do this before you go live.

    IN THE TEST (real gold, counting from Apr 1 2026, base 50, cap 500):
    the cap stopped Rule B after its trade of Apr 6, Rule A after Apr 10
    and Rule C after Apr 14 - and nothing traded after that.
    On 1-minute gold a run of losses comes quickly. Keep the cap, and
    decide in advance what you will do when it stops.""")

S += sec("HOW v10.0 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v10.0 without a
    syntax error.
  - The settings: the 106 of v9.1 are in the same order and places; the
    2 new ones are at the very end. Every new name is declared before it
    is used; ASCII only; no tabs; no strategy.close_all.
  - Your three examples, worked by the same arithmetic as the code:
    Rule B 50, 100, 300, 200, 220; Rule C 50, 50, 60, 50; Rule A 50, 100,
    130, 160, 140, 50; Rule A with amount 10 after a loss of 2: 50.
  - The simulator (the strategy's logic on real gold 1-minute data):
    every order was sized for exactly the rule's risk, with the losses
    carried worked out again independently from the closed trades - Rule
    A, B and C, counting from the whole history and from Apr 1: 0
    differences in 1,165 orders. Counting from Apr 1, all 266 orders
    before Apr 1 were at the base risk and nothing stopped before it.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v9.1 NOTES - still true for v10.0, EXCEPT that\n"
       "Rule A, B and C are now never below the base risk, and which trades\n"
       "count is set by 'loss recovery counts from' (items 97 to 99 above).\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body91
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v10.0_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v10.0 notes", len(t.split("\n")), "lines")
