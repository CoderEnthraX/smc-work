# v10.0 handbook front part: "What is new in v10.0", then the v9.1 chapter, the v9.0 chapters, then (merged later) the v8.3 pages
HB = "/home/user/smc-work/tools/hb/"
src91 = open(HB + "hb91.py").read()
exec(src91[:src91.index("\nh = cover(")])          # docs.py helpers + ch_v91()


def ch_v10():
    h = chap("WHAT IS NEW IN v10.0", "Loss recovery: Rule A, B and C",
             "One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.", True)
    h += table(["Rule", "Next trade risk", "Never less than", "Back to the base risk"], [
        ["<b>A</b>", "losses carried + your Rule A amount", "the base risk", "when losses carried reach 0"],
        ["<b>B</b>", "2 &times; losses carried", "the base risk", "when losses carried reach 0"],
        ["<b>C</b> (new)", "losses carried", "the base risk", "when losses carried reach 0"]])
    h += "<p><b>Losses carried</b> (all three rules): every closed trade adds its real loss or takes off its real profit - the Net P&amp;L after commission in the List of Trades. " \
         "Small losses add a little, small profits take off a little. Trades closing on the same candle are added together first. Never below zero; carried into the next days.</p>"
    h += "<h3>Your examples (base risk 50)</h3>"
    h += table(["Trade", "Rule B risk", "Result", "Carried after"], [
        ["1", "50", money(-50), "50"], ["2", "2 &times; 50 = <b>100</b>", money(-100), "150"], ["3", "2 &times; 150 = <b>300</b>", money(50) + " cut short", "100"],
        ["4", "2 &times; 100 = <b>200</b>", money(-10), "110"], ["5", "2 &times; 110 = <b>220</b>", "", ""]], (1, 3))
    h += table(["Trade", "Rule C risk", "Result", "Carried after"], [
        ["1", "50", money(-10) + " news window", "10"], ["2", "<b>50</b> (10 is below 50)", money(-50), "60"],
        ["3", "<b>60</b>", money(20) + " cut short", "40"], ["4", "<b>50</b> (40 is below 50)", "", ""]], (1, 3))
    h += "<p class='small'>Rule A with amount 50: 50, 100, 130, 160, 140, then 50. New in Rule A: never less than the base - amount 10 and a loss of 2 gives 50, not 12.</p>"
    h += card("Loss recovery counts from (group 21)", "When the strategy goes live (automatic)", "automatic", [
        ("AUTOMATIC", "Only trades that close from the first live candle on count - the moment you create the alert or open the chart. The past candles are ignored, "
                      "so the strategy always starts live with 0 carried and not stopped. Nothing to type."),
        ("A DATE I CHOOSE", "Only trades that close on or after the date in the next setting."),
        ("WHOLE HISTORY", "Every trade on the chart - use it to see a rule in the backtest. With the automatic choice the backtest shows every trade at the base risk."),
        ("GOOD TO KNOW", "Changing any setting (raising the cap too), or creating the alert again, starts from 0 again. The table row 'LOSS RECOVERY (A / B / C)' shows the rule "
                         "and where it counts from, e.g. <code>B - 2 x losses | from live 30 Sep 09:15</code>.")])
    h += box("Why Rule B may have looked wrong before",
             "Its arithmetic has been 2 &times; losses carried since v2.3. A trade's real risk can still differ from the ladder: the size is rounded to your lot step "
             "(on gold with a 15-point stop one step is about 15.60 of risk); <b>Max leverage</b> (group 21, 30) cuts a big size - about 66 ounces at 10,000 equity, "
             "so a risk of 300 on a 3-point stop is cut (row 'Trades cut by leverage cap'); and with the old default 'Stop for the rest of the day' the losses carried were cleared the next morning.")
    h += box("The cap, as in v9.1",
             "When the next risk would be above the hard cap, no new trade opens until you raise it (Stop permanently). In the test, counting from Apr 1 2026 with a 500 cap, "
             "the cap stopped Rule B after Apr 6, Rule A after Apr 10 and Rule C after Apr 14. Decide in advance what you will do when it stops.", "warn")
    h += "<p class='small'>Settings: 108 - the 106 of v9.1 in the same places, plus 2 at the very end (shown in group 21). Hedge: add v10.0 twice (Longs only / Shorts only).</p>"
    return h


v91 = ch_v91()
i = v91.index("<div class='box bad'>")
j = v91.index("</div>", i) + 6
v91 = v91[:i] + box("Solved in v10.0", "The problem that the chart's history could stop the strategy before it goes live is solved by 'Loss recovery counts from' (previous page).", "good") + v91[j:]
v91 = v91.replace("<div class=''><div class='lab'>WHAT IS NEW IN v9.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v9.1</div>")
h = cover("HANDBOOK &middot; VERSION 10.0", "SMC Structure Strategy",
          "Part 1: what is new in v10.0, v9.1, v9.0 and v8.4, every new setting, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.0.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk"), ("HEDGE", "the same file added twice (Longs only / Shorts only)")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v10() + v91 + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v10.0 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C - " \
     "see 'What is new in v10.0'), the default when the cap is reached (now 'Stop permanently'), and which trades count for loss recovery (now from the moment the strategy goes live). " \
     "Where part 2 says 'v8.3', read 'v10.0'.</p></div>"
open(HB + "hb_v10.0.html", "w").write(page("SMC Structure Strategy v10.0 Handbook", h))
print("ok")
