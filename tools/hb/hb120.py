# v12.0 handbook front part
import sys
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb112.py").read()
exec(src[:src.index("\nv111 = was(ch_v111(), ")])      # helpers + ch_v112() + ch_tests112() + older chapters
CHECK5 = "<b>identical</b> in 10 of 10 settings"          # the v11.2 result (its tests chapter is reused)
CHK = sys.argv[1] if len(sys.argv) > 1 else "CHK"


def ch_v120():
    h = chap("WHAT IS NEW IN v12.0", "Rule 3: enter at the close of the signal candle",
             "A new group 39 (4 settings) at the end of the settings. Everything is OFF by default - with it OFF v12.0 trades exactly like v11.2.", True)
    h += card("RULE 3 - enter at the close of the signal candle", "OFF", "your choice", [
        ("OFF", "Rules 1 and 2 as before: the strategy waits for the pullback (rule 1) or the broken pivot (rule 2)."),
        ("ON", "When a candle CLOSES and confirms the signal (your CHOCH), the strategy enters at market - wherever the candle closes. It fills at the OPEN of the next candle - practically the close. No pullback. Rules 1 and 2 are not used (except by the fall back at the end of the group)."),
        ("STOP / TARGET", "As always: stop = the CHOCH* level + your stop buffer; target = your R multiple from the entry; the size comes from your risk and that distance."),
        ("FILTERS", "Rule 3 does not need the higher timeframe to agree (like rule 1). Filter b, the favourable / against / auto modes, entry hours, news, weekend and the loss pause all still apply.")])
    h += card("- RULE 3: only if the close is near the broken level", "OFF", "your choice", [
        ("OFF", "Rule 3 enters wherever the signal candle closes."),
        ("ON", "Rule 3 enters only when the close is at most the distance set in the next setting (default 3) beyond the level the candle broke (the broken high of a bullish CHOCH, the broken low of a bearish one). A huge candle that closes far beyond it is skipped - or, with the fall back ON, gets the normal rule 1 / 2 setup.")])
    h += card("- the most the close may be beyond the broken level", "3", "3", [
        ("UNIT", "The unit of group 38, like group 24: Price = dollars on gold (3 = 3.00); Pips (3 pips = 0.30 on gold!); % of the price."),
        ("USED", "Only with the switch above ON. 3.00 exactly is allowed.")])
    h += card("- if the close is too far: fall back to RULE 1 / 2", "OFF", "your choice", [
        ("OFF", "A signal candle that closes too far beyond the broken level is skipped - no trade."),
        ("ON", "That signal gets the normal setup instead, exactly as with rule 3 OFF: rule 2 (a limit at the broken pivot) when the higher timeframe agrees, otherwise rule 1 (a limit at your pullback %), by your RULE 1 / RULE 2 switches. The limit may never be reached - then there is no trade."),
        ("USED", "Only with 'RULE 3: only if the close is near the broken level' ON. With RULE 1 and RULE 2 both OFF a close too far is still skipped.")])
    h += "<div style='break-inside: avoid'><h3>Example - a bullish CHOCH, the broken high at 4,100.00, the option ON with 3</h3>"
    h += table(["The CHOCH candle closes at", "Beyond the broken high", "Rule 3 alone", "+ 'near the broken level' 3", "+ fall back ON"], [
        ["4,102.50", "2.50", "buys at the next open", "<b>buys</b>", "<b>buys</b>"],
        ["4,103.00", "3.00", "buys at the next open", "<b>buys</b> (3.00 is allowed)", "<b>buys</b>"],
        ["4,108.00 (a huge candle)", "8.00", "buys at the next open", "<b>skipped</b>", "<b>buy limit</b> at 4,100 (rule 2) or 4,105 (rule 1)"]], num=(1,)) + "</div>"
    h += "<p>The rule 1 level in the last row: CHOCH* level 4,090, candle high 4,110, pullback 25%: 4,110 - 25% of 20 = 4,105. Rule 2 (the broken pivot 4,100) is used when the higher timeframe agrees.</p>"
    h += "<div style='break-inside: avoid'><h3>Which rule trades - 'near the broken level' ON and the fall back ON</h3>"
    h += table(["RULE 1", "RULE 2", "RULE 3", "Close near the level", "Close too far"], [
        ["on", "on", "on", "rule 3 at the close", "rule 2 (agrees) or rule 1"],
        ["on", "off", "on", "rule 3 at the close", "rule 1"],
        ["off", "on", "on", "rule 3 at the close", "rule 2 (only if the higher timeframe agrees)"],
        ["off", "off", "on", "rule 3 at the close", "skipped"]]) + "<p class='small'>With the fall back OFF, a close too far is always skipped.</p></div>"
    h += "<p>With the stop at 4,089.00 (CHOCH* level 4,090.00 + buffer 1.00) and a close of 4,101.00: distance 12.00, target 4,101 + 3 x 12 = 4,137 (+ the commission push), size 50 / (12 + 0.76) = 3.9, so 4 oz = 0.04 lot.</p>"
    h += box("Skip if the stop is closer / further than - for ALL entry rules", "These are the group 24 settings you already have: 'Skip the setup if the stop is CLOSER than this (price)' and "
             "'... FURTHER than this (price)', 0 = off (default). They work for rule 1, rule 2 and now rule 3 (for rule 3 the distance is from the close to the stop). "
             "Example with CLOSER 5 and FURTHER 30: a stop 12.00 away trades; 3.00 or 36.00 away is skipped.")
    h += box("One chance - no late entry", "The market order is sent on the signal candle only. A signal outside the entry hours, or while trading is blocked, opens nothing. "
             "With 'close and reverse' ON, a signal that reverses an open trade enters one candle later (after the old trade is closed). "
             "The broker message is unchanged: the alert fires when the order fills and TheConnector opens the trade at market with the stop and target.")
    h += box("The table and the audit labels", "A new last row 'RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)', e.g. 'on - 12 entered at the close | close within 3 of the break: 4 skipped, 7 fell back to rule 1 / 2'. "
             "The audit labels say 'R3 ARMED - entry at the close', 'SKIP - RULE 3: close 8.00 beyond the broken level', or 'RULE 3: close 8.00 beyond the broken level - fall back to RULE 1 / 2' above the rule 1 / 2 label.")
    h += box("Honest", "NOT tested for profit - you asked for the build without the 5.75-year test; it was tested only for correctness. Entering at the close puts the stop further away than "
             "rule 1's 25% pullback (about one third), so the same risk buys a smaller size, and every entry pays the full spread at once. The 5.75-year study found no 1-minute entry setting "
             "that made money in both 2021-23 and 2024-26. Run it in TradingView on the same dates as before, then on a demo account, before real money.", "warn")
    h += box("The MT5 EA v12.0", "The same group 39 at the end of the EA settings. Both 'touch' and 'pending' modes send a market order at once on the first tick of the next candle; "
             "if it does not fill on that candle the setup is dropped, like TradingView. A fall-back setup uses normal rule 1 / 2 orders.")
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
          "Part 1: rule 3 of v12.0 (entry at the close of the signal candle), the stop buffer unit of v11.2, the 'against' and 'auto' modes of v11.1, the three features of v11.0, what is new back to v8.4, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v12.0.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("ALSO", "SMC_Structure_EA_v12.0.mq5 - the same rules as an MT5 EA")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v120() + ch_tests120() + v112 + ch_tests112() + v111 + ch_tests111() + v110 + ch_together110() + ch_tests110() + v104 + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + \
    "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v12.0 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1), the v11.0 features, the v11.1 modes, the v11.2 stop buffer unit, the v12.0 rule 3, and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v12.0'.</p></div>"
assert all(ord(c) < 128 for c in h)
open(HB + "hb_v12.0.html", "w").write(page("SMC Structure Strategy v12.0 Handbook", h))
print("ok")
