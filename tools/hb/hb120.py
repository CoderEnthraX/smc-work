# v12.0 handbook front part
import sys
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb112.py").read()
exec(src[:src.index("\nv111 = was(ch_v111(), ")])      # helpers + ch_v112() + ch_tests112() + older chapters
CHECK5 = "<b>identical</b> in 10 of 10 settings"          # the v11.2 result (its tests chapter is reused)
CHK = sys.argv[1] if len(sys.argv) > 1 else "CHK"


def ch_v120():
    h = chap("WHAT IS NEW IN v12.0", "Rule 3 and rule 4: enter at the close of the signal candle",
             "A new group 39 at the end of the settings. Default 'Off (rules 1 / 2 as now)' - with it v12.0 trades exactly like v11.2.", True)
    h += card("Entry at the close of the signal candle", "Off (rules 1 / 2 as now)", "your choice: RULE 3 or RULE 4", [
        ("OFF", "Rules 1 and 2 as before: the strategy waits for the pullback (rule 1) or the broken pivot (rule 2)."),
        ("RULE 3", "When a candle CLOSES and confirms the signal (your CHOCH), the strategy enters at market. It fills at the OPEN of the next candle - practically the close. No pullback. Rules 1 and 2 are not used."),
        ("RULE 4", "The same, but only when the distance from the close to the stop is within the two limits below. A huge signal candle means a far stop: the setup is skipped, or falls back to rule 1 / 2."),
        ("STOP / TARGET", "As always: stop = the CHOCH* level + your stop buffer; target = your R multiple from the entry; the size comes from your risk and that distance."),
        ("FILTERS", "Rule 3 / 4 do not need the higher timeframe to agree (like rule 1). Filter b, the favourable / against / auto modes, entry hours, news, weekend, loss pause and group 24 all still apply.")])
    h += card("- RULE 4: skip if the stop is FURTHER than (0 = off)", "30", "30", [
        ("UNIT", "The unit of group 38, like group 24: Price = dollars on gold (30 = 30.00); Pips (30 pips = 3.00 on gold!); % of the entry price."),
        ("0", "No upper limit.")])
    h += card("- RULE 4: skip if the stop is CLOSER than (0 = off)", "3", "3", [
        ("WHY", "A very tight stop is mostly noise - the 5.75-year study found the tightest stops lost the most."),
        ("ALWAYS SKIPPED", "A stop this close is skipped even with 'fall back' (a pullback entry would be even closer).")])
    h += card("- RULE 4: when the stop is too far", "Skip the setup", "Skip the setup (or Fall back)", [
        ("SKIP THE SETUP", "The signal opens nothing."),
        ("FALL BACK TO RULE 1 / 2", "The setup is armed the normal way instead: a limit order at the pullback (rule 1) or the broken pivot (rule 2), with your rule 1 / 2 switches. That pullback entry must keep the SAME limits - if its stop distance is outside them, it is cancelled too.")])
    h += "<div style='break-inside: avoid'><h3>Example - gold 1m, a bullish CHOCH, buffer 1.00, target 3R, risk 50</h3>"
    h += table(["The CHOCH candle closes at", "Stop", "Distance", "RULE 3", "RULE 4 (3 - 30)"], [
        ["4,101.00", "4,089.00", "12.00", "buys at the next open", "<b>buys</b>"],
        ["4,125.00 (a huge candle)", "4,089.00", "36.00", "buys at the next open", "<b>too far</b> - skipped (or falls back)"],
        ["4,091.50", "4,089.00", "2.50", "buys at the next open", "<b>too close</b> - skipped"]], num=(1, 2)) + "</div>"
    h += "<p>The 12.00 trade: target 4,101 + 3 x 12 = 4,137 (+ the commission push); size 50 / (12 + 0.76) = 3.9, so 4 oz = 0.04 lot.</p>"
    h += box("One chance - no late entry", "The market order is sent on the signal candle only. A signal outside the entry hours, or while trading is blocked, opens nothing. "
             "With 'close and reverse' ON, a signal that reverses an open trade enters one candle later (after the old trade is closed) and rule 4 checks that candle's close. "
             "The broker message is unchanged: the alert fires when the order fills and TheConnector opens the trade at market with the stop and target.")
    h += box("The table and the audit labels", "A new last row 'ENTRY AT THE SIGNAL CLOSE (group 39)', e.g. 'RULE 4 (3 - 30) - 12 entered at the close | skipped: too far 4 / too close 1'. "
             "The audit labels say 'R3 ARMED - entry at the close, stop 12.00', 'SKIP - RULE 4: stop too far (36.00)', and so on.")
    h += box("Honest", "NOT tested for profit - you asked for the build without the 5.75-year test; it was tested only for correctness. Entering at the close puts the stop further away than "
             "rule 1's 25% pullback (about one third), so the same risk buys a smaller size, and every entry pays the full spread at once. The 5.75-year study found no 1-minute entry setting "
             "that made money in both 2021-23 and 2024-26. Run it in TradingView on the same dates as before, then on a demo account, before real money.", "warn")
    h += box("The MT5 EA v12.0", "The same group 39 at the end of the EA settings. Both 'touch' and 'pending' modes send a market order at once on the first tick of the next candle; "
             "if it does not fill on that candle the setup is dropped, like TradingView.")
    return h


def ch_tests120():
    h = chap("HOW v12.0 WAS CHECKED", "Parser, settings, the simulator and the MT5 EA's own code", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v12.0 without a syntax error. New names declared before use, no clashes, ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Settings: the 122 of v11.2 unchanged in the same places + 4 new at the end = 126.</li></ul>"
    h += CHK
    h += "<p class='small'>This is not the TradingView compiler. If TradingView shows an error when you save, send the line and the message.</p>"
    return h


v112 = was(ch_v112(), "v11.2")
v111 = was(ch_v111(), "v11.1")
v110 = was(ch_v110(), "v11.0")
v104 = was(ch_v104(), "v10.4")
v103 = was(ch_v103(), "v10.3")
v102 = was(ch_v102(), "v10.2")
v101 = was(ch_v101(), "v10.1")
v10 = ch_v10()
i = v10.index("<div class='card'><div class='ch'><div class='ct'>Loss recovery counts from")
j = v10.index("<div class='box", i)
v10 = v10[:i] + v10[j:]
v10 = was(v10, "v10.0")
v10 = v10.replace("One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.",
                  "One memory of the losses carried for all three rules, never below your base risk. ('Counts from' is explained in 'What was new in v10.2'.)")
v91 = was(ch_v91(), "v9.1")
h = cover("HANDBOOK &middot; VERSION 12.0", "SMC Structure Strategy",
          "Part 1: rule 3 and rule 4 of v12.0 (entry at the close of the signal candle), the stop buffer unit of v11.2, the 'against' and 'auto' modes of v11.1, the three features of v11.0, what is new back to v8.4, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v12.0.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("ALSO", "SMC_Structure_EA_v12.0.mq5 - the same rules as an MT5 EA")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v120() + ch_tests120() + v112 + ch_tests112() + v111 + ch_tests111() + v110 + ch_together110() + ch_tests110() + v104 + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + \
    "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v12.0 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1), the v11.0 features, the v11.1 modes, the v11.2 stop buffer unit, the v12.0 rules 3 / 4, and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v12.0'.</p></div>"
assert all(ord(c) < 128 for c in h)
open(HB + "hb_v12.0.html", "w").write(page("SMC Structure Strategy v12.0 Handbook", h))
print("ok")
