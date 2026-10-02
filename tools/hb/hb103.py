# v10.3 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb102.py").read()
exec(src[:src.index("\nv101 = ch_v101()")])      # helpers + ch_v101() + ch_v10() + ch_v91() + ch_v102()


def ch_v103():
    h = chap("WHAT IS NEW IN v10.3", "Split the loss over this many trades",
             "One new setting at the end of group 21. Whatever the loss-recovery rule asks for is divided by it - never below your base risk. Default 1 = exactly v10.2.", True)
    h += card("Split the loss over this many trades (group 21, the last setting)", "1", "your risk:reward - 3 for a 1:3 target", [
        ("WHAT", "The rule works out its amount as before, then it is <b>divided by this number</b>, never less than your BASE risk. From 1 to 20, steps of 0.5."),
        ("A and A+", "(loss + Rule A amount) / this number"),
        ("B and B+", "2 &times; loss / this number"),
        ("C and C+", "loss / this number"),
        ("TABLE", "The row 'LOSS RECOVERY' shows it, e.g. <code>C+ - total below 0 | split over 3 trades | whole history</code>. 'Risk NEXT trade' shows the risk after the split.")])
    h += "<h3>Why 3</h3><p>Your target is <b>1:3</b>, so a full take-profit win pays 3 &times; the risk. Risk <b>one third</b> of the loss, and one TP win pays back 3 &times; &#8531; = " \
         "<b>the whole loss</b>. The total is back at 0 and the next trade is your base risk again. Set it to your risk:reward - 3 for 1:3, 2.5 for 1:2.5.</p>"
    h += table(["With 3 and a 1:3 target", "One full TP win pays back", "Total after the win"], [
        ["C / C+", "the whole loss", "0"], ["A / A+", "the loss + your Rule A amount", "+ your amount"], ["B / B+", "2 &times; the loss", "+ the loss"]])
    h += "<h3>Example 1 - four losses, then one TP win</h3><p class='small'>C+, base 50, 1:3 target.</p>"
    h += table(["Trade", "Result", "Split 1: risk", "Split 1: total", "Split 3: risk", "Split 3: total"], [
        ["1", "loss", "50", "-50", "50", "-50"], ["2", "loss", "50", "-100", "50 <span class='small'>(50/3 = 16.67 &rarr; base)</span>", "-100"],
        ["3", "loss", "100", "-200", "50 <span class='small'>(100/3 = 33.33 &rarr; base)</span>", "-150"], ["4", "loss", "200", "-400", "50 <span class='small'>(150/3)</span>", "-200"],
        ["5", "<b>TP</b>", "400", "<b>+800</b>", "66.67 <span class='small'>(200/3)</span>", "<b>0</b> &rarr; next trade 50"]], num=(2, 3, 4, 5), hl=(4,))
    h += "<h3>Example 2 - ten losses in a row</h3><p>This is what happened in your Rule C+ file on Feb 13-17, 2023.</p>"
    h += table(["", "Split 1 (v10.2)", "Split 3"], [
        ["Risks, trades 1-10", "50, 50, 100, 200, 400, 800, 1,600, 3,200, 6,400, 12,800", "50, 50, 50, 50, 66.67, 88.89, 118.52, 158.02, 210.70, 280.93"],
        ["Total after 10 losses", "<b>-25,600</b> - more than a 10,000 account", "<b>-1,123.73</b>"],
        ["Trade 11", "would need 25,600 - impossible", "risks 374.58; a TP pays 1,123.73 &rarr; total 0"]])
    h += "<h3>Example 3 - a win that is not a full TP</h3><p>Time flat, news window, weekend flat and opposite signal close a trade early, so it pays less than 3 &times; and only part of the loss comes back. " \
         "The rest carries on: total -355.56 &rarr; risk 118.52 &rarr; time flat at +118.52 &rarr; total -237.04 &rarr; next risk 79.01 &rarr; TP pays 237.04 &rarr; <b>total 0</b> &rarr; back to the base.</p>"
    h += "<h3>Example 4 - A+ and B+ with split 3</h3>"
    h += table(["Rule", "Loss", "Rule asks", "Risk (/3)", "TP pays", "Total after"], [
        ["A+ (amount 50)", "424.07", "474.07", "158.02", "474.07", "<b>+50</b>"], ["B+", "771.60", "1,543.20", "514.40", "1,543.20", "<b>+771.60</b>"]], num=(1, 2, 3, 4, 5))
    h += "<p>With split 3, <b>Rule A+ does exactly what its name says</b>: one TP win recovers the losses plus your amount.</p>"
    h += "<h3>How to choose the number</h3>"
    h += table(["Number", "One full TP win pays back (1:3)", "In a losing streak"], [
        ["1 (v10.2)", "3 &times; the loss", "the loss doubles every loss"], ["2", "1.5 &times; the loss", "&times; 1.5 per loss"],
        ["<b>3</b>", "<b>exactly the loss</b>", "<b>&times; 1.33 per loss</b>"], ["6", "half the loss - 2 TP wins", "&times; 1.17 per loss"]], hl=(2,))
    h += box("The base risk is your setting - nothing is fixed at 50",
             "Every rule and the split use <b>'BASE risk per trade'</b> (group 21) as the base, and <b>'Rule A: amount added on top of the losses carried'</b> as the Rule A amount. "
             "50 is only the default of both. Example with base 100, C+, split 3: four losses = -400 (risks 100, 100, 100, 100); trade 5 risks 400/3 = 133.33; a TP pays 400, "
             "the total is 0 and the next trade risks 100 again. Checked in the simulator with base 50 and base 75.")
    h += box("Good to know", "The hard cap is checked <b>after</b> the split. The size is still rounded to your lot step and cut by Max leverage. "
             "It does not turn losing trades into winners: a long streak still makes the risk grow, only much more slowly. Keep a real hard cap.", "warn")
    return h


def ch_file2023():
    h = chap("YOUR RULE C+ FILE", "Why the 2023 test emptied the account",
             "Account 10,000, base 50, Rule C+, hard cap 100,000, 'Stop for the rest of the day', Max leverage 100, Properties 300x, CHOCH only, close and reverse OFF.")
    h += table(["Trade", "Day", "C+ risk (= loss)", "Result", "Total after"], [
        ["64-66", "Feb 13-14", "50 (base)", "three losses", "-70.50"], ["67", "Feb 14", "70.50", "-70.20", "-140.70"], ["68", "Feb 14", "140.70", "-134.50", "-275.21"],
        ["69", "Feb 14", "275.21", "-68.95 (time flat)", "-344.16"], ["70", "Feb 15", "344.16", "-336.03", "-680.19"], ["71", "Feb 15", "680.19", "-346.50 (time flat)", "-1,026.69"],
        ["72", "Feb 16", "1,026.69", "-991.34", "-2,018.03"], ["73", "Feb 16", "2,018.03", "-96.72 (news)", "-2,114.75"], ["74", "Feb 16", "2,114.75", "+373.32 (time flat)", "-1,741.43"],
        ["75", "Feb 17", "1,741.43", "-1,688.44", "-3,429.87"], ["76", "Feb 17", "3,429.87 (cut)", "-2,055.27", "-5,485.15"], ["77", "Feb 17", "5,485.15 (cut)", "-1,753.70", "-7,238.85"],
        ["78", "Feb 17", "7,238.85 (cut)", "-923.82", "<b>-8,162.67</b>"]], num=(2, 3, 4))
    h += "<ul><li><b>The losses grew</b> because C+ risks the whole loss: every full loss doubles it. Trades 64-73 were 10 losses in a row.</li>" \
         "<li><b>The TP wins were small</b> because from trade 76 the rule asked for more than Max leverage 100 allows (trade 76: about 587 oz asked, 359 given). " \
         "A TP still paid 3 &times; - but 3 &times; the <b>real, cut</b> risk: trade 87 risked 269.78 against a loss of 8,722.46 and won 817.74.</li>" \
         "<li><b>It never went back to 50</b> because the total never got back above 0 after Feb 13.</li>" \
         "<li><b>The cap never fired</b>: the biggest loss the rule worked with was 9,977.10, far below 100,000. A cap bigger than the account cannot protect it.</li>" \
         "<li><b>It stopped after Mar 27</b> because only 15.66 was left (-99.84%). One ounce cost about 1,955, so at 100x the biggest order was 0.8 oz, which rounds to 0. " \
         "Every later setup had size 0. Not a bug - the account was empty.</li>" \
         "<li>Properties 300x is right (3 &times; Max leverage): no margin call.</li></ul>"
    h += box("With split 3", "Trades 64-78 would have ended near <b>-1,100</b> instead of -8,162.67, and the next full TP win would have paid that back. "
             "(An estimate from each trade's own result in R.)")
    return h


def ch_howto():
    h = chap("HOW TO USE IT", "Loss recovery - step by step", "The same order as the settings panel. Test first, then go live.")
    h += table(["Step", "Setting", "What to set"], [
        ["1", "BASE risk per trade (group 21)", "What one normal trade may lose - e.g. 50 on 10,000 (0.5%)"],
        ["2", "Loss-recovery sizing", "Rule C+ (or A+) - works only while the total P&amp;L is below 0"],
        ["3", "Split the loss over this many trades", "Your risk:reward - <b>3</b> for a 1:3 target"],
        ["4", "HARD CAP on risk per trade", "A few % of the account - e.g. <b>300-500</b> on 10,000. Never bigger than the account"],
        ["5", "When the cap is reached", "'Stop for the rest of the day' (fresh next day - the rule forgets the loss, the money is still gone) or 'Stop permanently'"],
        ["6", "Max leverage / Properties", "Max leverage = your real FxPro gold leverage or lower; Properties margin 3 &times; that or more"],
        ["7", "Loss recovery counts from", "'Whole chart history' to test; 'When the strategy goes live' before you create the alert"],
        ["8", "The table", "LOSS RECOVERY, Losses carried, Risk NEXT trade, Risk cap hit / HALT, Trades cut by leverage cap, Margin calls"],
        ["9", "Backtest", "The same period with 'Off' and with your rule: compare the net P&amp;L <b>and</b> the lowest point of the account. Then demo"],
        ["10", "Going live", "Replace the code while FLAT, delete and create the alert again - message only <code>{{strategy.order.alert_message}}</code>, 'Order fills only'"]])
    return h


def ch_tests103():
    h = chap("HOW v10.3 WAS CHECKED", "Parser, settings and the simulator on real gold data", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v10.3 without a syntax error.</li>" \
         "<li>Settings: the 108 of v10.2 in the same order and places, the new one at the very end, declared before use. ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Simulator on real gold 1-minute data (Feb 25 - May 26, 2026): all six rules, split 1 / 2.5 / 3, base 50 and base 75, counted from the whole history and from Apr 1 - " \
         "<b>50,779 orders, each sized exactly by its rule, 0 differences</b>. With split 1 every order and trade result was the same as v10.2.</li></ul>"
    h += "<p>Your settings (CHOCH only, close and reverse OFF, Max leverage 100, Stop for the rest of the day) on the same data, 112 trades:</p>"
    h += table(["Rule", "Net P&amp;L", "Lowest account", "Biggest risk"], [
        ["Off", "+793.31", "9,725.91", "50.00"], ["C+ split 1", "+1,586.82", "9,618.89", "381.11"],
        ["C+ split 3", "+944.05", "9,779.90", "73.37"], ["A+ split 3", "+1,007.88", "9,783.57", "88.81"]], num=(1, 2, 3))
    h += "<p>These 3 months had no long losing streak while the total was below 0, so split 1 earned the most here. Your 2023 file shows the other side: one bad week took split 1 to -8,162.67. " \
         "<b>Split 3 earns less when things go well and loses far less when they do not.</b></p>"
    return h


v102 = ch_v102().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.2</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.2</div>")
assert "WHAT WAS NEW IN v10.2" in v102
v101 = ch_v101().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.1</div>")
v10 = ch_v10()
i = v10.index("<div class='card'><div class='ch'><div class='ct'>Loss recovery counts from")
j = v10.index("<div class='box", i)
v10 = v10[:i] + v10[j:]
v10 = v10.replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.0</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.0</div>")
v10 = v10.replace("One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.",
                  "One memory of the losses carried for all three rules, never below your base risk. ('Counts from' is explained in 'What was new in v10.2'.)")
v91 = ch_v91().replace("<div class=''><div class='lab'>WHAT IS NEW IN v9.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v9.1</div>")
h = cover("HANDBOOK &middot; VERSION 10.3", "SMC Structure Strategy",
          "Part 1: what is new in v10.3 back to v8.4, every new setting, how to use loss recovery, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.3.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("HEDGE", "the same file added twice (Longs only / Shorts only)")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v103() + ch_file2023() + ch_howto() + ch_tests103() + v102 + v101 + v10 + v91 + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v10.3 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from' or 'split' - " \
     "see part 1) and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v10.3'.</p></div>"
open(HB + "hb_v10.3.html", "w").write(page("SMC Structure Strategy v10.3 Handbook", h))
print("ok")
