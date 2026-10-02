# v9.1 handbook front part: a new "What is new in v9.1" chapter, then the v9.0 chapters, then (merged later) the v8.3 pages
import sys
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "docs.py").read()
exec(src[:src.index("\nhandbook(False)")])


def ch_v91():
    h = chap("WHAT IS NEW IN v9.1", "Three changes you asked for",
             "Clean CHOCH-only trades, your own Rule A ladder, and a hard cap that stops until you raise it. Everything else is v9.0.", True)
    h += card("Cancel a waiting order when a new BOS prints before it fills (group 24)", "ON", "ON", [
        ("WHAT IT DOES", "A waiting order only fills on the leg of the signal that armed it. When a new BOS the same way prints before it fills, the order is "
                         "cancelled (<code>CANCELLED - new BOS before the fill</code>). It never moves onto the new leg."),
        ("WHY", "In 'Continuous' entry mode a waiting rule 1 order follows the leg. After a BOS the leg is the BOS leg, so a CHOCH order that had not "
                "filled moved to 25% of the BOS leg, with its stop at the new higher low, and filled there - a CHOCH-only strategy taking what looks like a BOS trade."),
        ("IN EACH MODE", "<b>CHOCH only</b>: every trade is on its CHOCH leg. <b>BOS only</b>: the new BOS cancels the old order and arms its own. "
                         "<b>CHOCH and BOS</b>: a waiting CHOCH order is cancelled by the BOS, which arms its own. If the new BOS cannot be traded, the old order is still cancelled."),
        ("TEST", "Your CHOCH-only settings, Feb 27 - May 25 2026: 12 of 264 trades had filled after a BOS (net -64). With the cancel: +850 instead of +789.")])
    h += card("Rule A: amount added on top of the losses carried (group 21)", "50", "your choice, e.g. 50 or 10", [
        ("THE RULE", "Next risk = <b>losses carried + this amount</b>. Nothing is divided by R. Losses carried: every closed trade adds its real loss or takes off "
                     "its real profit (Net P&amp;L after commission, as in the List of Trades), never below zero, carried into the next days. "
                     "A win bigger than what is carried: back to the base risk (group 21), the extra profit is not saved."),
        ("BEFORE v9.1", "Rule A was (losses carried + base) &divide; R: at R 3 it risked 33.33 after a loss of 50, not 100."),
        ("OFF", "Only used when 'Loss-recovery sizing' is Rule A.")])
    h += table(["Trade", "Risk", "Result", "Losses carried after"], [
        ["1", "50", money(-50) + " stop", "50"], ["2", "50 + 50 = <b>100</b>", money(-30) + " news window", "80"],
        ["3", "80 + 50 = <b>130</b>", money(-30), "110"], ["4", "110 + 50 = <b>160</b>", money(20) + " cut short", "90"],
        ["5", "90 + 50 = <b>140</b>", "wins at target", "0"], ["6", "back to <b>50</b>", "", ""]], (1, 3))
    h += "<p class='small'>Your example with base risk 50 and Rule A amount 50. With an amount of 10 the same results give 50, 60, 90, 120, 100, then 50. " \
         "Full losses in a row: 50, 100, 200, 400, 800 - the fifth is above a 500 cap.</p>"
    h += card("When the cap is reached (group 21)", "Stop permanently (new)", "Stop permanently, or Stop for the day - read below", [
        ("WHAT IT DOES", "The cap is reached when the <b>next</b> risk would be above the hard cap (470 carried + 50 = 520 against 500). No new trade is opened - today, "
                         "tomorrow and every day after - and the losses carried are kept. Open trades keep their own stop and target."),
        ("TO START AGAIN", "Raise the cap. TradingView then works the whole backtest out again with the new cap. Delete the alert and create it again - an alert keeps the settings it was made with.")], "warn")
    h += box("Important before you use Rule A live",
             "A TradingView strategy runs over <b>all the history on your chart</b> first, then goes live. If the cap was reached anywhere in that history, "
             "the strategy is already stopped when you create the alert, and it will never send a trade. In the test, Rule A with a 500 cap reached the cap "
             "on the second day (four losses in a row, 841 carried) and never traded again. Until this is solved: check the table row <b>'Risk cap hit / HALT'</b> "
             "before you create the alert (HALTED = nothing will be sent), or use <b>'Stop for the rest of the day'</b> while you trade Rule A live. "
             "The proposed fix - a 'count Rule A from this date' setting - is not built yet; it needs your OK.", "bad")
    h += "<h3>The hedge with v9.1 - one file, added twice</h3><ol>" \
         "<li>MT5: a <b>hedging</b> account, not netting.</li><li>Add <code>SMC_Structure_Strategy_v9.1.txt</code> to the chart twice.</li>" \
         "<li>Copy 1: group 33 <b>Longs only</b>; copy 2: <b>Shorts only</b>. Both: close and reverse <b>OFF</b>, and different tags in group 30 (<code>smcL</code>, <code>smcS</code>).</li>" \
         "<li>Type your other settings in both copies. One alert per copy, message only <code>{{strategy.order.alert_message}}</code>, the same webhook.</li></ol>"
    h += "<p class='small'>New table rows: 'LOSS RECOVERY (A / B)' shows <code>A - losses + 50</code>; row 43 'Cancelled - new BOS before the fill'. " \
         "Settings: 106 - the 104 of v9.0 in the same places, plus 2 at the very end (shown in groups 21 and 24).</p>"
    return h


h = cover("HANDBOOK &middot; VERSION 9.1", "SMC Structure Strategy",
          "Part 1: what is new in v9.1, v9.0 and v8.4, every new setting, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v9.1.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk"), ("HEDGE", "the same file added twice (Longs only / Shorts only)")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v91() + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v9.1 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Two exceptions:</b> Rule A (part 2 says it divides by R - in v9.1 it is losses carried + your Rule A amount) " \
     "and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v9.1'.</p></div>"
open(HB + "hb_v9.1.html", "w").write(page("SMC Structure Strategy v9.1 Handbook", h))
print("ok")
