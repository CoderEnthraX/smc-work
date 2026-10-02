# SMC_Structure_Strategy_v10.2_NOTES.txt = new v10.2 part + the v10.1 notes (from "WHAT v10.1 CHANGES" on)
R = "/home/user/smc-work/"
v101 = open(R + "SMC_Structure_Strategy_v10.1_NOTES.txt").read()
k = v101.index("-" * 74 + "\nWHAT v10.1 CHANGES")
body = v101[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v10.2  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v10.2.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v10.2_HANDBOOK.pdf - every setting, with
examples and the value to use.

v10.2 in two lines:
  - "Loss recovery counts from" is back (group 21), with THE WHOLE CHART
    HISTORY as the default - so the backtest looks exactly like v10.1.
  - Everything else is v10.1: Rule A / B / C and A+ / B+ / C+.

SETTINGS: 108 - the 106 of v10.1 in the same places, plus 2 at the very
  end (shown in group 21). They sit in the same places as in v10.0, so
  settings saved in v10.0 line up too. Replace the code while you are
  FLAT (no open trade), then delete the alert and create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v10.2 CHANGES", """
103. LOSS RECOVERY COUNTS FROM (group 21, back from v10.0).
       THE WHOLE CHART HISTORY (default): every closed trade on the chart
         counts - as in v10.1. Use it to see a rule in the backtest.
       WHEN THE STRATEGY GOES LIVE (automatic): only trades that OPEN
         from the first live candle on - the moment you create the alert
         or open the chart. A trade still open from the replayed past
         never reached your broker, so it does not count either. Nothing
         to type.
       A DATE I CHOOSE: only trades that open on or after the date in
         the next setting.
     It works the same way for Rule A / B / C and A+ / B+ / C+, and for
     the hard cap. The table row "LOSS RECOVERY" shows where it counts
     from, for example "C+ - total below 0 | from live 02 Oct 09:15".""")

S += sec("WHY IT HELPS  -  in simple English", """
A strategy on TradingView never starts "today". When you create the
alert it first replays every candle on your chart as if it had traded
them (that is the backtest), and then it goes on live FROM WHERE THE
REPLAY ENDED - with everything it remembers: the loss carried, the total
P&L and whether the cap has stopped it. "Counts from" decides whether that
replayed past is allowed to decide your live sizes.

1. YOUR FIRST LIVE TRADE IS NOT SIZED BY THE PAST.
   Your Rule C file: on Sep 22 at 09:35 the replayed past was carrying
   1,989.24 of losses. An alert created at that moment with the whole
   history would have sized its first live trade (09:41) at 1,989.24 -
   for losses that never happened in your account. With "when the
   strategy goes live" it starts at the base 50.

2. A CAP REACHED IN THE PAST CANNOT STOP YOU LIVE.
   With "Stop permanently", a cap reached anywhere in the replay leaves
   the strategy stopped before it starts - the alert would send nothing.
   Counted from live, only live trades can reach the cap.

3. A+ / B+ / C+ GET AN HONEST CUSHION.
   They use the total P&L. With the whole history the total includes
   backtest profit: your Rule A file was +3,983.34 on Sep 18, so A+ would
   have stayed at the base risk until 3,983 of LIVE losses. Counted from
   live, the cushion is only what you really made live.

4. THE SAME PLAN AS YOUR ACCOUNT.
   "A date I choose" lets the rules count from the day you went live, a
   new month, or a new deposit - and in a backtest it shows how a rule
   would have run from that day.

HOW TO USE IT
  - Testing: keep "The whole chart history" (the default) and read the
    backtest.
  - Going live: switch to "When the strategy goes live (automatic)", then
    create the alert. The backtest on the chart will then show every
    trade at the base risk - that is expected.
  - Changing any setting (raising the cap too) or creating the alert
    again starts the live count from zero again. Very rarely TradingView
    restarts an alert on its own, which also starts from zero.""")

S += sec("HOW v10.2 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v10.2 without a
    syntax error.
  - The settings: the 106 of v10.1 in the same order and places, the 2
    new ones at the very end - the same places as in v10.0. Every new
    name is declared before it is used; ASCII only; no tabs; no
    strategy.close_all.
  - The simulator on real gold 1-minute data, all six rules, counted from
    the whole history and from Apr 1 ("live"): every order was sized
    exactly by its rule, with the loss worked out again independently -
    8,172 orders, 0 differences. Counted from Apr 1, all 266 orders
    before that day were at the base risk. Trades count by the time they
    OPEN, so a trade from the replayed past that closes live does not
    count.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v10.1 NOTES - still true for v10.2, EXCEPT that\n"
       "'loss recovery counts from' is back (item 103 above, default: the whole\nchart history).\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v10.2_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v10.2 notes", len(t.split("\n")), "lines")
