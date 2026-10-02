# SMC_Structure_Strategy_v11.0_NOTES.txt = new v11.0 part + the v10.4 notes (from "WHAT v10.4 CHANGES" on)
R = "/home/user/smc-work/"
v104 = open(R + "SMC_Structure_Strategy_v10.4_NOTES.txt").read()
k = v104.index("-" * 74 + "\nWHAT v10.4 CHANGES")
body = v104[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v11.0  -  HOW EVERYTHING WORKS
=========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v11.0.txt     Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v11.0_HANDBOOK.pdf - every setting, with
examples and the value to use.

v11.0 - three new features, each one OPTIONAL and OFF by default. With all
three off, v11.0 trades exactly like v10.4.
  1. Pause for some days after losses in a row        (group 36)
  2. "Higher timeframe favourable" modes             (group 20, "Take
                                                       trades on")
  3. Trade only after the higher timeframe pulled
     back to its equilibrium                          (group 37)

SETTINGS: 118 - the 113 of v10.4 in the same places, plus 5 at the very
  end (their own groups 36 and 37). "Take trades on" has 3 more choices;
  the old 3 are unchanged, so your saved settings stay as they are.
  Replace the code while you are FLAT (no open trade), then delete the
  alert and create it again.

SPEED: the three features share the ONE higher-timeframe request the
  strategy already made (it now also brings the higher-timeframe leg).
  Each candle adds only a few comparisons; the day count of feature 1
  runs only at the moment a pause starts.

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v11.0 CHANGES", """
111. PAUSE FOR SOME DAYS AFTER LOSSES IN A ROW (group 36)
       Pause for some days after losses in a row   Off (default) / On
       - losses in a row                           3 (default)
       - days to pause (after the rest of that day) 2 (default)

     HOW IT WORKS
       - Every closed trade with Net P&L BELOW 0 after costs (as the List
         of Trades shows it) adds 1 to the count - a small loss at time
         flat counts the same as a full stop. A WINNING trade starts the
         count again at 0. A trade at exactly 0 changes nothing. The
         early-profit part of a setup (group 34 e) is not counted.
       - On the Nth loss in a row: no new trade for the REST OF THAT DAY
         plus the number of days. A trade still open keeps running to its
         stop or target; a waiting order is cancelled.
       - Gold, forex, silver, indices: only Monday to Friday count.
         Crypto (or "Trade 24/7" on, group 24): every day counts.
         A day starts at 00:00 in your session timezone (group 20).
       - After the pause trading starts again by itself and the count
         starts again at 0. Trades that close during the pause (the ones
         that were still open) are not counted.
       - Only the trades that "loss recovery counts from" (group 21)
         counts are counted. With "When the strategy goes live" the
         replayed backtest cannot start your alert already paused.

     EXAMPLES (3 losses, 2 days)
       market   3rd loss in a row    paused                 trading again
       gold     Monday 14:00         rest of Mon, Tue, Wed  Thursday
       gold     Thursday 14:00       rest of Thu, Fri, Mon  Tuesday
       crypto   Thursday 14:00       rest of Thu, Fri, Sat  Sunday
     The new table row "PAUSE AFTER LOSSES (group 36)" shows "2 of 3
     losses in a row" or "PAUSED until Thu 05 Mar 00:00".

112. "HIGHER TIMEFRAME FAVOURABLE" MODES (group 20, "Take trades on")
       CHOCH only - higher timeframe favourable
       BOS only - higher timeframe favourable
       CHOCH and BOS - higher timeframe favourable

     HOW IT WORKS
       - The same signals as the mode without "favourable", but ONLY in
         the direction of the higher timeframe: higher timeframe bullish
         -> only buys; bearish -> only sells; signals the other way are
         skipped. While the higher-timeframe trend is not clear yet, no
         trades.
       - The higher timeframe is the one in group 20 - Auto pairs it with
         the chart: 1m -> 15m, 5m -> 1h, 15m -> 4h, 1h -> 1D, 4h -> 1W,
         1D -> 1M. "Bullish / bearish" = the market structure of the last
         CLOSED higher-timeframe candle.
       - Entry, the same in all three modes:
           rule 1 only   -> the pullback %
           rule 2 only   -> the broken pivot
           rule 1 + 2    -> the broken pivot (rule 1 is never used: it
                            only takes the signals AGAINST the higher
                            timeframe, and there are none left)
       - A WAITING order is cancelled when the higher timeframe flips
         against it. An OPEN trade keeps running to its stop or target.
       - It works like filter "b" (group 34), plus the cancel on a flip.

     EXAMPLE (1m chart, CHOCH only - higher timeframe favourable)
       15m trend   1m signal          result
       bearish     bearish CHOCH      SELL
       bearish     bullish CHOCH      skipped
       bullish     bullish CHOCH      BUY
       bullish     bearish CHOCH      skipped

113. HIGHER TIMEFRAME EQUILIBRIUM FIRST (group 37)
       Trade only after the higher timeframe pulled back
         to its equilibrium                        Off (default) / On
       - the equilibrium, % pullback of the higher
         timeframe leg                             50 (default)

     HOW IT WORKS
       - Every CHOCH or BOS on the higher timeframe starts a new leg and
         CLOSES the gate: no trades at all (buys and sells) until the
         price TOUCHES the equilibrium of that leg - a wick is enough,
         deeper is fine.
       - The level is measured from the end of the leg back towards its
         start: 50% = the middle; 61.8 or 70.5 = a deeper pullback. If
         the leg runs further before the pullback, the level moves with
         it.
       - After the touch the gate stays OPEN, and the chart trades by
         "Take trades on", rule 1 and rule 2 - until the next
         higher-timeframe CHOCH or BOS closes it again.
       - When the gate closes, a waiting order is cancelled; an open
         trade keeps running.
       - The higher-timeframe CHOCH / BOS counts once its candle has
         closed, so the backtest and live trading see the same thing.
       - The higher timeframe must be ABOVE the chart, or the gate never
         opens (the table says so).

     EXAMPLE (1m chart, 15m higher timeframe, 50%)
       10:00  15m bullish BOS, leg 3,950 -> 4,050, level 4,000  closed
       10:30  price 4,020                                        closed
       11:40  price dips to 3,998 - touched                      OPEN
       11:50  1m bullish CHOCH -> buy (rule 1 / rule 2)          trades
       13:00  new 15m BOS - a new leg                            closed
     The new table row "HTF EQUILIBRIUM FIRST (group 37)" shows "OPEN" or
     "WAITING - needs 4,000.00".

114. HOW THE THREE WORK TOGETHER
     Every signal passes the checks in this order:
       1. the pause after losses (and every other stop - news, weekend,
          daily limit, floor, ...)
       2. the equilibrium gate
       3. "Take trades on" - with a favourable mode, only the higher
          timeframe's direction
       4. rule 1 / rule 2 - where the order waits
     Example, all three on: only buys while the 15m is bullish, only
     after the 15m pulled back to 50% of its leg, and never during a
     pause after 3 losses in a row.

115. WHAT 3 MONTHS OF REAL GOLD DATA SHOWED (your settings: CHOCH only,
     rule 1 + 2, 25%, reverse OFF; Feb 25 - May 26, 2026)
       setting                               trades    net    lowest
       v10.4 / everything off                  112    +793     -274
       2. favourable (rule 1 + 2)               93     -82     -182
       2. favourable, rule 1 only               92    -397     -458
       3. equilibrium 50%                       84  +1,410     -128
       1. pause 3 losses / 2 days               82  +1,244     -204
       2 + 3                                    77    -160     -260
       all three                                56    +221      -57
     Only 3 months - not enough to decide anything (see item 108). Test
     each one in the long backtests of the data request before you use
     it live.""")

S += sec("HOW v11.0 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v11.0 without a
    syntax error. Every new name is declared before it is used and clashes
    with no old one. ASCII only; no tabs; no strategy.close_all.
  - The settings: the 113 of v10.4 in the same order and places, the 5
    new ones at the very end; the 3 old "Take trades on" choices are
    unchanged.
  - The simulator on real gold 1-minute data (Feb 25 - May 26, 2026),
    each feature checked against its own rule worked out SEPARATELY:
      everything off: every order and trade the same as v10.4
        (CHOCH / BOS / both, reverse on / off, rule 2 off, filter b);
      2. favourable modes, all 3 modes x 3 rule settings x reverse on /
        off: 0 trades against the higher timeframe, 0 with the wrong
        entry rule, 0 filled after the higher timeframe flipped; with a
        test higher timeframe that flips often, 5 to 71 waiting orders
        were cancelled on a flip - and none filled after it;
      3. equilibrium gate, 50% and 61.8%: 0 trades armed or filled
        while the gate was closed; the gate opened exactly when the
        separate calculation said (32 and 30 times); the 15m leg's end
        was the highest high / lowest low since its CHOCH / BOS every
        time;
      1. pause, 6 settings (1 to 3 losses, 1 to 3 days, gold days and
        every day, whole history and from live) x reverse on / off:
        every pause started and ended exactly where a separate calendar
        calculation said, and 0 trades opened inside a pause;
      all three together: the same checks, 0 errors.
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v10.4 NOTES - still true for v11.0. The three\n"
       "new features (items 111-114) are OFF by default, which works exactly like\nv10.4.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v11.0_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v11.0 notes", len(t.split("\n")), "lines")
