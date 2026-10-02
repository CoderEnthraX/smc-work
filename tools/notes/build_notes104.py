# SMC_Structure_Strategy_v10.4_NOTES.txt = new v10.4 part + the v10.3 notes (from "WHAT v10.3 CHANGES" on)
R = "/home/user/smc-work/"
v103 = open(R + "SMC_Structure_Strategy_v10.3_NOTES.txt").read()
k = v103.index("-" * 74 + "\nWHAT v10.3 CHANGES")
body = v103[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v10.4  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v10.4.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v10.4_HANDBOOK.pdf - every setting, with
examples and the value to use.
What to send me next: SMC_Strategy_DATA_REQUEST_v10.4.pdf

v10.4 in three lines:
  - NEW group 35 "Account floor + profit lock": the account can never fall
    more than an amount you choose, part of every new high is kept, and
    each trade risks a % of the cushion above the floor. Default Off =
    exactly v10.3.
  - NEW in these notes: what the statistics of your trade files say,
    with two corrections to what I told you in chat (items 108-110).
  - NEW: the data request PDF - everything to send for the next round.

SETTINGS: 113 - the 109 of v10.3 in the same places, plus 4 at the very
  end (their own group 35, at the end of the settings panel). Replace the
  code while you are FLAT (no open trade), then delete the alert and
  create it again.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v10.4 CHANGES", """
107. ACCOUNT FLOOR + PROFIT LOCK (group 35, the last 4 settings)
       Account floor                      Off (default) / On - size every
                                          trade from the cushion / On -
                                          only cap the risk
       the most the account may lose      2,000 (default)
       lock this % of every new high      50 (default)
       risk per trade, % of the cushion   2.5 (default)

     HOW IT WORKS
       THE FLOOR   = the most you may lose below the start, raised by the
                     lock % of every new profit high.
       THE CUSHION = your P&L since the start minus the floor.
       THE RISK    = risk % x the cushion.
     A loss takes only 2.5% of the cushion, so after 10 losses in a row
     97.5% x 97.5% x ... = 78% of it is left - the cushion shrinks but
     never reaches zero. The account cannot fall through the floor.

     THE TWO MODES
       SIZE EVERY TRADE FROM THE CUSHION: risk = % of the cushion. It
         grows when you are in profit and shrinks after losses. Loss
         recovery and its hard cap are not used (set loss recovery Off).
       ONLY CAP THE RISK: your base risk (and loss recovery, if on) work
         as before, but a trade never risks more than % of the cushion.
         Your normal trading with a safety net. Start with this one.

     EXAMPLE (the defaults, base 50)
       start:              floor -2,000, cushion 2,000, risk 50
       10 losses in a row: about 447 lost (cushion 1,553, risk 39)
       20 losses in a row: about 795 lost - never 2,000
       profit high +4,000: floor 0 - break-even is locked
       profit high +6,000: floor +1,000 - 1,000 of profit is kept

     WHERE IT STARTS: at the same moment as "loss recovery counts from"
     (group 21). Going live: set that to "When the strategy goes live
     (automatic)", so the floor starts from your live account and not
     from the backtest.

     HOW TO CHOOSE
       - The most to lose: what you can really afford to lose. Keep it AT
         LEAST 40 x your base risk (2,000 for base 50). Gold's smallest
         step, 0.01 lot = 1 oz, is already 20-25 of risk in 2026; with a
         small cushion many setups round to 0 oz and are skipped.
       - Risk %: base risk / the most to lose x 100 (50 / 2,000 = 2.5%),
         so the first trade risks your base.
       - Lock: 50% is a good middle.

     LIMITS - the floor cannot protect against:
       - slippage beyond the stop and price gaps (weekend, news);
       - several trades open at once (stacked BOS) - each takes its share
         of the cushion, the floor only sees closed trades;
       - the size is rounded to your lot step as usual (never more than
         'never let rounding raise the risk by more than' %, group 21).

     TABLE: the new row "ACCOUNT FLOOR (group 35)" shows the P&L, the
     floor, the cushion and the risk; "AT THE FLOOR" when nothing is left.""")

S += sec("WHAT THE STATISTICS OF YOUR FILES SAY", """
108. THE EDGE - does the average trade make money? (R = your base risk)
       test                         trades  avg/trade  verdict
       2021-22, reverse ON           1,628   -0.12 R   surely losing
       2023-24, reverse ON           1,530   -0.13 R   surely losing
       2025-26 CHOCH only, rev. ON   1,158   -0.04 R   probably losing
       Your settings (reverse OFF):    156   +0.13 R   positive, NOT
         Sep 2026 file + simulator                     proven yet
     156 trades are too few: the true average could be anywhere from
     -0.10 R to +0.38 R (95% range). About 480 trades (one year) are
     needed to know if it is really above zero.

     ONE TRADE DOES NOT PREDICT THE NEXT. In every file the result of a
     trade had no link to the result before it - like a coin toss. So a
     loss does not make a win "due", and no recovery rule (Rule A / B / C,
     A+ / B+ / C+) can make a losing strategy win. It only loses faster.

109. TWO CORRECTIONS TO WHAT I TOLD YOU IN CHAT
     a) THE FLOOR NUMBERS. My first year-long test let a trade have any
        size. With the real 1 oz step a tight floor (500 / 10%) skips many
        trades - in the simulator it skipped the big winners. Corrected
        test (2,000 one-year paths made of real trading days, 1 oz steps):

                           your 2026 edge   like 2025-26     like 2023-24
                           profit  median   median   worst   worst
        Fixed 50            99%   +4,038    -2,591  -9,011  -10,049
        Floor 2,000 / 2.5%  91%   +3,685    -1,432  -1,827   -1,929
        Floor 1,000 / 5%    80%   +3,207      -758    -939     -969
        Floor 500 / 10%     53%      +94      -371    -478     -485
        C+ split 3, cap 500 98%   +4,110    -3,178 -10,449  -10,473

        So the floor is INSURANCE: with a real edge it costs a little
        (99% -> 91% profitable years), without one it stops the loss at
        the amount you chose. 2,000 / 2.5% is the default for that reason.

     b) "PAUSE AFTER 2 LOSSES IN A ROW". Taking those trades out of your
        old files improved all 6 of them. But in the simulator, where the
        real strategy runs and a skipped trade changes the next ones, it
        MADE LESS in 2026: +536 instead of +793 (reverse OFF) and +519
        instead of +754 (reverse ON). It did raise the lowest point (-158
        instead of -274). So it is a safety rule, not a proven profit
        rule - the long backtests will decide (run C in the data request).

110. RECOMMENDED SETTINGS FOR NOW
       - Loss-recovery sizing: Off. No recovery rule helped in any test
         once the size steps were real.
       - Account floor: "On - only cap the risk", 2,000 / 50 / 2.5 - or
         your own amount (at least 40 x your base risk).
       - Pause after losses (group 34 g): your choice - safety, not
         proven profit.
       - Max leverage = your real FxPro gold leverage or lower;
         Properties margin 3 x that.
       - "Loss recovery counts from": "When the strategy goes live" before
         you create the alert (the floor starts there too).
       - Send me the data in SMC_Strategy_DATA_REQUEST_v10.4.pdf - most of
         all the long backtests. They decide everything else.""")

S += sec("HOW v10.4 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v10.4 without a
    syntax error.
  - The settings: the 109 of v10.3 in the same order and places, the 4
    new ones at the very end, declared before use. No new name clashes
    with an old one. ASCII only; no tabs; no strategy.close_all.
  - The simulator on real gold 1-minute data (Feb 25 - May 26, 2026):
      floor Off: every order and trade the same as v10.3;
      both modes, longs / shorts / both, reverse ON / OFF, the defaults
      and stress settings (300 to lose at 50% risk per trade): 5,852
      orders, the risk of each worked out again independently - 0
      differences; rounding never above the allowed 25%; the floor was
      never broken (closest: 4.30 above it, in the stress settings).
  - Your settings (CHOCH only, reverse OFF, Max leverage 100), 3 months:
       Fixed 50                          +793.31   lowest  -274.09
       Floor cap 2,000 / 50 / 2.5        +827.89   lowest  -268.34
       Floor size 2,000 / 50 / 2.5       +608.84   lowest  -268.34
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v10.3 NOTES - still true for v10.4. The account\n"
       "floor (item 107) is Off by default, which works exactly like v10.3.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v10.4_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v10.4 notes", len(t.split("\n")), "lines")
