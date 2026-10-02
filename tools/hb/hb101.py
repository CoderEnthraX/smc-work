# v10.1 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src10 = open(HB + "hb10.py").read()
exec(src10[:src10.index("\nv91 = ch_v91()")])      # docs.py helpers + ch_v91() + ch_v10()


def ch_v101():
    h = chap("WHAT IS NEW IN v10.1", "Rule A+, B+ and C+",
             "'Loss recovery counts from' is removed - every trade on the chart counts again. Three new rules measure the loss from your total P&L instead of from the high point.", True)
    h += table(["Rule", "The loss it works with", "Next trade risk"], [
        ["<b>A / B / C</b>", "the loss <b>since the high point</b>: a loss adds, a profit takes off, never below 0 - extra profit is not saved", "A: loss + amount &nbsp; B: 2 &times; loss &nbsp; C: loss"],
        ["<b>A+ / B+ / C+</b> (new)", "the <b>total P&amp;L below 0</b> (the Cumulative P&amp;L of the List of Trades) - while the total is above 0 every trade is the base risk", "A+: loss + amount &nbsp; B+: 2 &times; loss &nbsp; C+: loss"]])
    h += "<p>All six are never less than the base risk. The names in the settings carry a hint: <code>Rule C+ (only when total P&amp;L is below 0: that loss)</code>.</p>"
    h += "<h3>Your Rule C file - next risk after each trade</h3>"
    rows = [("7", 665.67, "50", "50"), ("12", 294.05, "371.62", "50"), ("14", -790.93, "1,456.60", "790.93"), ("15", -494.53, "<b>1,160.20</b>", "<b>494.53</b>"),
            ("16", -1642.78, "2,308.45", "1,642.78"), ("17", 243.86, "<b>421.81</b>", "<b>50</b>"), ("18", 741.34, "50", "50")]
    h += table(["After trade", "Total P&amp;L", "Rule C (since the high)", "Rule C+ (below 0)"], [[a, "<span class='%s'>%s</span>" % ("pos" if b > 0 else "neg", "{:+,.2f}".format(b)), c, d] for a, b, c, d in rows], (1, 2, 3))
    h += "<p class='small'>With C+ trade 16 risks about 494.53 and trade 18 is back to 50. With C they risk 1,160.20 and 421.81, because the account had been at +665.67 and C recovers every drop from a high.</p>"
    h += box("Good to know",
             "<b>Total</b> means every closed trade on the chart: once the account is well up, A+ / B+ / C+ do nothing until that profit is lost again. "
             "'Stop for the rest of the day' clears the loss the next morning (for A+ / B+ / C+ the total starts again from 0). "
             "With 'Stop permanently', a cap reached anywhere in the chart's history keeps the strategy stopped when you create the alert - check the row 'Risk cap hit / HALT' first, or raise the cap.", "warn")
    h += box("What your four v10.0 files showed",
             "Every trade was sized exactly by its rule. Differences from the pure ladder came from <b>Max leverage 30</b> (18 trades cut, 12 of them in Rule B) and from "
             "'Stop for the rest of the day', which cleared Rule B's 5,386 of losses on Sep 14. None of the 45 trades ended by 'Opposite signal': <b>close and reverse was OFF</b> on that chart, "
             "which is why there were fewer trades (3-month test: 264 trades ON, 109 OFF).")
    h += "<p class='small'>Settings: 106 - the same settings in the same places as v9.1; 'Loss-recovery sizing' has three more choices.</p>"
    return h


v10 = ch_v10()
i = v10.index("<div class='card'><div class='ch'><div class='ct'>Loss recovery counts from")
j = v10.index("<div class='box", i)
v10 = v10[:i] + v10[j:]
v10 = v10.replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.0</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.0</div>")
v10 = v10.replace("One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.",
                  "One memory of the losses carried for all three rules, never below your base risk. (The 'counts from' setting of v10.0 was removed in v10.1.)")
v91 = ch_v91().replace("<div class=''><div class='lab'>WHAT IS NEW IN v9.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v9.1</div>")
h = cover("HANDBOOK &middot; VERSION 10.1", "SMC Structure Strategy",
          "Part 1: what is new in v10.1, v10.0, v9.1, v9.0 and v8.4, every new setting, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.1.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk"), ("HEDGE", "the same file added twice (Longs only / Shorts only)")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v101() + v10 + v91 + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v10.1 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C or A+ / B+ / C+ - " \
     "see part 1) and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v10.1'.</p></div>"
open(HB + "hb_v10.1.html", "w").write(page("SMC Structure Strategy v10.1 Handbook", h))
print("ok")
