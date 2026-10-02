# SMC_Structure_Strategy_v9.1_NOTES.txt = new v9.1 part + the v9.0 notes (from "WHAT v9.0 ADDS" on)
R = "/home/user/smc-work/"
v90 = open(R + "SMC_Structure_Strategy_v9.0_NOTES.txt").read()
k = v90.index("-" * 74 + "\nWHAT v9.0 ADDS")
body90 = v90[k:]
H = "-" * 74


def sec(title, text):
    return "\n\n" + H + "\n" + title + "\n" + H + "\n" + text.strip("\n")


HEAD = """SMC STRUCTURE STRATEGY  -  v9.1  -  HOW EVERYTHING WORKS
========================================================

Plain English. One heading per feature, then what it does and why.
File: SMC_Structure_Strategy_v9.1.txt      Pine Script v6      ASCII only.
Handbook: SMC_Structure_Strategy_v9.1_HANDBOOK.pdf - every setting, with
examples and the value to use.
Test report: SMC_Strategy_TEST_REPORT_v9.0.pdf.

v9.1 in three lines:
  - A waiting order only fills on the leg of the signal that armed it. A
    new BOS before the fill cancels it - "CHOCH only" now means CHOCH
    trades only (group 24, ON).
  - RULE A = losses carried + your Rule A amount (group 21, 50 by
    default). Nothing is divided by R any more.
  - When the hard cap is reached, trading stops until you raise the cap
    ("Stop permanently" is the new default). READ ITEM 95 before you use
    Rule A live.
Everything else is v9.0, and the v9.0 ideas (group 34) are still all OFF.

SETTINGS: 106 - the 104 of v9.0 in the same places, plus 2 at the very
  end. They are shown in group 21 (Rule A amount) and group 24 (cancel on
  a new BOS). Replace the code while you are FLAT (no open trade), then
  delete the alert and create it again. After updating, check group 21
  "when the cap is reached": the default is now "Stop permanently".

ONE FILE FOR THE HEDGE TOO. Add v9.1 to the chart twice - no separate
LONG / SHORT files are needed (see HEDGE WITH v9.1 below).

THE ALERT MESSAGE is still ONLY {{strategy.order.alert_message}}, and the
condition is still "Order fills only". The strategy never sends closeall.
Your TheConnector access key goes ONLY into the webhook URL inside
TradingView:  https://webhook.theconnector.fr/YOUR_ACCESS_KEY"""

S = sec("WHAT v9.1 CHANGES", """
93. A WAITING ORDER ONLY FILLS ON ITS OWN SIGNAL'S LEG (group 24, new
    setting "Cancel a waiting order when a new BOS prints before it
    fills", ON).

    WHAT YOU SAW (v8.3, "CHOCH only"). A CHOCH armed a rule 1 order at the
    25% pullback (the higher timeframe did not agree, so rule 1). The
    price did not come back to it. Then a BOS printed. In "Continuous"
    entry mode the waiting order follows the leg - and after the BOS the
    leg is the BOS leg: its high starts again at the BOS candle and the
    CHOCH* level (your stop) moves up to the new higher low. So the SAME
    CHOCH order (same id, same tag) moved to 25% of the BOS leg and filled
    there. It was never a BOS signal - in "CHOCH only" a BOS cannot arm,
    cancel or reverse anything - but the trade sat on the BOS leg.

    NOW. When a new BOS the same way prints before the order fills, the
    order is cancelled (audit label "CANCELLED - new BOS before the
    fill"). It never moves onto the new leg.
      CHOCH only      every trade is on its CHOCH leg; after the BOS
                      nothing opens until the next CHOCH.
      BOS only        the new BOS cancels the old order and arms its own,
                      as before. If the new BOS cannot be traded (max
                      trades open, outside the session), the old order is
                      still cancelled, not moved.
      CHOCH and BOS   a waiting CHOCH order is cancelled by the BOS, and
                      the BOS arms its own order. Every trade belongs to
                      the signal that armed it.
    Rule 2 orders (entry at the broken level) never moved, but they are
    cancelled by a new BOS too, so every mode follows one rule.
    An opposite CHOCH cancels a waiting order, as before.

    IN THE TEST (real gold, Feb 27 - May 25 2026, your CHOCH-only
    settings): 12 of 264 trades had filled after a BOS (net -64, 1 in 4
    won). With the cancel: +850 instead of +789. With "close and reverse"
    OFF those trades had made +179, and the total with the cancel was
    +1,021 instead of +1,442 - so it is about clean signals, not profit.
    OFF = the v9.0 behaviour.

94. RULE A = LOSSES CARRIED + YOUR RULE A AMOUNT (group 21, new setting
    "Rule A: amount added on top of the losses carried", 50).

    THE RULE
      - Base risk (group 21 "BASE risk per trade", for example 50): every
        trade while nothing is carried, and again after a series is paid
        off. While you keep winning, every trade is 50.
      - Losses carried: every closed trade adds its real loss or takes off
        its real profit - the Net P&L after commission that the List of
        Trades shows. Never below zero.
      - Next risk = losses carried + your Rule A amount.
      - A win bigger than what is carried: carried goes to 0, the extra
        profit is not saved, the next trade is the base risk again.
      - Losses carried continue into the next days.

    YOUR EXAMPLE (base 50, Rule A amount 50):
      trade  risk            result              carried after
        1     50             -50 (stop)            50
        2     50 + 50 = 100  -30 (news window)     80
        3     80 + 50 = 130  -30                  110
        4    110 + 50 = 160  +20 (cut short)       90
        5     90 + 50 = 140  wins at target        0
        6     back to 50
    With a Rule A amount of 10 the same results give 50, 60, 90, 120,
    100, then 50.

    WHAT CHANGED. Up to v9.0 Rule A was (losses carried + base) / R. At
    your R 3 that risked 33.33 after a loss of 50 instead of 100 - the
    "divided by R" is gone. The carrying of real losses and profits was
    already there since v2.3 and is unchanged.

    FULL LOSSES IN A ROW (amount 50): 50 -> 100 -> 200 -> 400 -> 800. The
    fifth trade is above a 500 cap, so the cap stops it (item 95).

95. THE HARD CAP: "STOP PERMANENTLY" IS THE NEW DEFAULT (group 21 "when
    the cap is reached").

    The cap is reached when the NEXT risk would be bigger than the hard
    cap - for example 470 carried + 50 = 520 with a cap of 500. Then no
    new trade is opened - today, tomorrow and every day after - and the
    losses carried are kept. Open trades keep their own stop and target.
    Trading starts again only when you raise the cap.

    RAISING THE CAP. Any change of a setting makes TradingView work the
    whole backtest out again from the first candle, with the new cap. An
    alert keeps the settings it was created with, so delete the alert and
    create it again after you change the cap.

    !!! IMPORTANT - READ BEFORE USING RULE A LIVE !!!
    A strategy on TradingView always runs over ALL the history on your
    chart first, then goes live. If the cap was reached ANYWHERE in that
    history, the strategy is already stopped when you create the alert -
    and it will never send a trade. In the test, Rule A with a 500 cap
    reached the cap on the second day (Feb 26: four losses in a row,
    841 carried) and never traded again in the three months.
    Until this is solved:
      - check the table row "Risk cap hit / HALT" before you create the
        alert - if it says HALTED, the alert will send nothing;
      - or use "Stop for the rest of the day" while you trade Rule A
        live (it clears the carried losses the next morning).
    The fix I propose (not built yet - it needs your OK): a setting
    "count Rule A from this date", so only trades after that date (the
    day you go live) are carried and can reach the cap.

96. THE TABLE. Row "LOSS RECOVERY (A / B)" shows "A - losses + 50" (your
    amount). New row "Cancelled - new BOS before the fill" counts item 93.""")

S += sec("HEDGE WITH v9.1  -  one file, added twice", """
Every version from v8.4 on has the "Trade direction" setting (group 33),
so v9.1 alone is enough:
  1. MT5: your FxPro account must be a HEDGING account, not netting.
  2. Add SMC_Structure_Strategy_v9.1.txt to the chart twice (Indicators
     -> your script, two times). Each copy has its own settings.
  3. Copy 1: group 33 "Longs only". Copy 2: "Shorts only".
  4. Both copies: group 20 "close and reverse" OFF, and a DIFFERENT
     TheConnector tag in group 30 - for example smcL and smcS.
  5. Type your other settings in both copies (the same values).
  6. One alert per copy: condition = that copy, "Order fills only",
     message ONLY {{strategy.order.alert_message}}, the same webhook URL.
  7. Each copy has its own report, daily limits, Rule A ladder and cap -
     your total is report 1 + report 2.""")

S += sec("HOW v9.1 WAS CHECKED", """
  - A Pine Script parser (the full Pine grammar) read v9.1 without a
    syntax error.
  - The settings: the 104 of v9.0 are in the same order and places; the 2
    new ones are at the very end. Every new name is declared before it is
    used; ASCII only; no tabs; no strategy.close_all.
  - Rule A arithmetic: your example gives exactly 50, 100, 130, 160, 140,
    then 50.
  - The simulator (the strategy's logic on real gold 1-minute data), with
    Rule A as in v9.1: every order sent was sized for exactly "losses
    carried + 50" (or 50 with nothing carried), with the carried amount
    worked out again independently from the closed trades - 34 orders, 0
    differences; the same with an amount of 10 and with a cap of 300.
  - The cancel on a new BOS: with it ON, 0 orders filled after a BOS in
    CHOCH only, BOS only and CHOCH and BOS (before: 13 in CHOCH only,
    over all the data).
  - This is not the TradingView compiler. If TradingView shows an error
    when you save, send me the line and the message.""")

BAN = ("\n\n" + "=" * 74 + "\nEVERYTHING BELOW IS FROM THE v9.0 NOTES - still true for v9.1, EXCEPT Rule A and\n"
       "the hard cap: where the text below says Rule A divides by R, or that the\ndefault is \"Stop for the rest of the day\", "
       "items 94 and 95 above replace it.\n" + "=" * 74 + "\n")
t = HEAD + S + BAN + body90
assert all(ord(c) < 128 for c in t)
long = [l for l in (HEAD + S).split("\n") if len(l) > 78]
assert not long, long
open(R + "SMC_Structure_Strategy_v9.1_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("v9.1 notes", len(t.split("\n")), "lines")
