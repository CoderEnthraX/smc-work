# v10.4 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb103.py").read()
exec(src[:src.index("\nv102 = ch_v102()")])      # helpers + ch_v103() + ch_file2023() + ch_howto() + ch_tests103() + older chapters


def ch_v104():
    h = chap("WHAT IS NEW IN v10.4", "Account floor + profit lock",
             "A new group 35 at the end of the settings. The account can never fall more than an amount you choose, part of every new high is kept, and each trade risks a % of the cushion above the floor. Default Off = exactly v10.3.", True)
    h += card("Account floor (group 35)", "Off", "On - only cap the risk", [
        ("OFF", "No floor - exactly as v10.3."),
        ("ONLY CAP", "Your base risk (and loss recovery, if on) work as before, but a trade never risks more than % of the cushion. <b>Your normal trading with a safety net - start with this one.</b>"),
        ("SIZE", "Risk = % of the cushion: it grows with profit and shrinks after losses. Loss recovery and its hard cap are not used.")])
    h += card("&nbsp;&nbsp;- the most the account may lose", "2,000", "what you can really afford - at least 40 &times; your base risk", [
        ("WHAT", "The floor starts this far below your P&amp;L at the start - the same start as 'loss recovery counts from' (group 21)."),
        ("WHY 40&times;", "Gold's smallest step (0.01 lot = 1 oz) is already 20-25 of risk in 2026. With a small cushion many setups round to 0 oz and are skipped.")])
    h += card("&nbsp;&nbsp;- lock this % of every new profit high", "50", "50", [
        ("WHAT", "The floor rises by this share of every new high. With 2,000 to lose: -1,000 at +2,000, <b>0 at +4,000</b> (break-even locked), +1,000 at +6,000."),
        ("0 / 100", "0 = the floor never moves. 100 = it follows every high, always 'the most to lose' below it.")])
    h += card("&nbsp;&nbsp;- risk per trade, % of the cushion", "2.5", "your base risk / the most to lose &times; 100", [
        ("WHAT", "Each trade risks this share of the cushion. 50 / 2,000 = 2.5%, so the first trade risks your base."),
        ("WHY SAFE", "A loss takes only 2.5% of the cushion - after 10 losses in a row 78% of it is left. It shrinks but never reaches zero.")])
    h += "<h3>Example - the defaults, base 50</h3>"
    h += table(["Moment", "Floor", "Cushion", "Risk"], [
        ["Start", "-2,000", "2,000", "50"], ["After 10 losses in a row (about -447)", "-2,000", "1,553", "39"],
        ["After 20 losses in a row (about -795)", "-2,000", "1,205", "30"], ["Profit high +4,000", "<b>0</b> - break-even locked", "4,000", "100 (size) / 50 (cap)"],
        ["Profit high +6,000", "<b>+1,000</b> kept", "5,000", "125 (size) / 50 (cap)"]], num=(1, 2, 3))
    h += box("What the floor cannot stop", "Slippage beyond the stop and price gaps (weekend, news); several trades open at once (stacked BOS) each take their share - the floor only sees closed trades; "
             "rounding to your lot step (never more than the 'rounding' % in group 21).", "warn")
    h += box("Going live", "Set 'loss recovery counts from' (group 21) to <b>'When the strategy goes live (automatic)'</b> before you create the alert, so the floor starts from your live account and not from the backtest. "
             "The table row 'ACCOUNT FLOOR (group 35)' shows the P&amp;L, the floor, the cushion and the risk.")
    return h


def ch_stats104():
    h = chap("WHAT THE STATISTICS SAY", "Your trade files, measured", "R = your base risk. Every number here comes from your own files and the simulator on real gold data.")
    h += "<h3>Does the average trade make money?</h3>"
    h += table(["Test", "Trades", "Avg per trade", "Verdict"], [
        ["2021-22, close and reverse ON", "1,628", "-0.12 R", "<span class='tag r'>surely losing</span>"],
        ["2023-24, close and reverse ON", "1,530", "-0.13 R", "<span class='tag r'>surely losing</span>"],
        ["2025-26 CHOCH only, reverse ON", "1,158", "-0.04 R", "<span class='tag y'>probably losing</span>"],
        ["<b>Your settings now (reverse OFF)</b> - Sep 2026 file + simulator", "156", "+0.13 R", "<span class='tag b'>positive, not proven</span>"]], num=(1, 2))
    h += "<p>156 trades are too few: the true average could be anywhere from <b>-0.10 R to +0.38 R</b>. About <b>480 trades (one year)</b> are needed to know if it is really above zero - that is the first thing the data request asks for.</p>"
    h += box("One trade does not predict the next", "In every file the result of a trade had no link to the result before it - like a coin toss. A loss does not make a win 'due', so no recovery rule "
             "(A / B / C, A+ / B+ / C+) can turn a losing strategy into a winning one. It only loses faster.")
    h += "<h3>Correction 1 - the floor numbers, with real 1 oz steps</h3><p>My first test in chat let a trade have any size. With the real 1 oz step a tight floor skips many trades. Corrected: 2,000 one-year paths made of your real trading days.</p>"
    nw = lambda x: "<span style='white-space:nowrap'>%s</span>" % x
    h += table(["Method", "2026 edge: years in profit", "2026 edge: median", "2025-26: median", "2025-26: worst", "2023-24: worst"], [
        [nw("Fixed 50"), "99%", "+4,038", "-2,591", "-9,011", "-10,049"], [nw("<b>Floor 2,000 / 2.5%</b>"), "91%", "+3,685", "-1,432", "-1,827", "<b>-1,929</b>"],
        [nw("Floor 1,000 / 5%"), "80%", "+3,207", "-758", "-939", "-969"], [nw("Floor 500 / 10%"), "53%", "+94", "-371", "-478", "-485"],
        [nw("C+ split 3, cap 500"), "98%", "+4,110", "-3,178", "-10,449", "-10,473"]], num=(1, 2, 3, 4, 5), hl=(1,))
    h += "<p>The floor is <b>insurance</b>: with a real edge it costs a little (99% &rarr; 91% profitable years); without one it stops the loss at the amount you chose.</p>"
    h += "<h3>Correction 2 - pause after 2 losses in a row</h3><p>Taking those trades out of your old files improved all 6 of them. But in the simulator, where the real strategy runs and a skipped trade changes the next ones, it made <b>less</b> in 2026: " \
         "+536 instead of +793 (reverse OFF), +519 instead of +754 (reverse ON). It did raise the lowest point (-158 instead of -274). A safety rule, not a proven profit rule - run C of the data request decides.</p>"
    h += "<h3>Recommended settings for now</h3>"
    h += table(["Setting", "Value", "Why"], [
        ["Loss-recovery sizing (21)", "Off", "No recovery rule helped in any test once the size steps were real"],
        ["Account floor (35)", "On - only cap the risk, 2,000 / 50 / 2.5", "Your normal trading with a hard limit on the total loss"],
        ["Pause after losses (34 g)", "your choice", "Safety, not proven profit"],
        ["Max leverage (21) / Properties", "your FxPro gold leverage / 3 &times; that", "So live orders match the backtest"],
        ["Loss recovery counts from (21)", "When the strategy goes live - before the alert", "The floor and the rules start from your live account"],
        ["Next step", "Send the data in SMC_Strategy_DATA_REQUEST_v10.4.pdf", "The long backtests decide everything else"]])
    return h


def ch_tests104():
    h = chap("HOW v10.4 WAS CHECKED", "Parser, settings and the simulator on real gold data", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v10.4 without a syntax error.</li>" \
         "<li>Settings: the 109 of v10.3 in the same order and places, the 4 new ones at the very end (group 35), declared before use; no new name clashes with an old one. ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Simulator on real gold 1-minute data (Feb 25 - May 26, 2026): with the floor Off every order and trade is the same as v10.3. Both modes, longs / shorts / both, reverse ON / OFF, the defaults and stress settings " \
         "(300 to lose at 50% per trade): <b>5,852 orders, each sized exactly - 0 differences; the floor was never broken</b> (closest: 4.30 above it, in the stress settings).</li></ul>"
    h += "<p>Your settings (CHOCH only, reverse OFF, Max leverage 100), the same 3 months:</p>"
    h += table(["Sizing", "Net P&amp;L", "Lowest point"], [["Fixed 50", "+793.31", "-274.09"], ["Floor, only cap, 2,000 / 50 / 2.5", "+827.89", "-268.34"],
                                                        ["Floor, size, 2,000 / 50 / 2.5", "+608.84", "-268.34"]], num=(1, 2))
    return h


v103 = ch_v103().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.3</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.3</div>")
assert "WHAT WAS NEW IN v10.3" in v103
v102 = ch_v102().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.2</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.2</div>")
v101 = ch_v101().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.1</div>")
v10 = ch_v10()
i = v10.index("<div class='card'><div class='ch'><div class='ct'>Loss recovery counts from")
j = v10.index("<div class='box", i)
v10 = v10[:i] + v10[j:]
v10 = v10.replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.0</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.0</div>")
v10 = v10.replace("One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.",
                  "One memory of the losses carried for all three rules, never below your base risk. ('Counts from' is explained in 'What was new in v10.2'.)")
v91 = ch_v91().replace("<div class=''><div class='lab'>WHAT IS NEW IN v9.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v9.1</div>")
h = cover("HANDBOOK &middot; VERSION 10.4", "SMC Structure Strategy",
          "Part 1: what is new in v10.4 back to v8.4, what the statistics of your files say, the recommended settings, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.4.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("NEXT STEP", "SMC_Strategy_DATA_REQUEST_v10.4.pdf")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v104() + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v10.4 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1) and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v10.4'.</p></div>"
open(HB + "hb_v10.4.html", "w").write(page("SMC Structure Strategy v10.4 Handbook", h))
print("ok")
