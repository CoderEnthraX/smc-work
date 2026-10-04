# v11.2 handbook front part
import sys
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb111.py").read()
exec(src[:src.index("\nv110 = ch_v110()")])      # helpers + ch_v111() + ch_tests111() + older chapters
CHECK5 = sys.argv[1] if len(sys.argv) > 1 else "CHECK5"


def ch_v112():
    h = chap("WHAT IS NEW IN v11.2", "The stop buffer in price, pips or % of price",
             "A new group 38 at the end of the settings. Default 'Price (as now)' - with it v11.2 trades exactly like v11.1.", True)
    h += card("Stop buffer unit (group 38)", "Price (as now)", "keep Price on gold, or 10 pips = the same", [
        ("PRICE", "The group 20 'Stop buffer beyond the CHOCH* level, in price' - exactly as v11.1."),
        ("PIPS", "The pips below &times; the pip of the market on the chart (table). The strategy knows the pip from the ticker."),
        ("% OF PRICE", "This % of the CHOCH* level, worked out again for every setup - so it grows with the price."),
        ("ROUNDING", "The buffer is rounded to the smallest price step of the market."),
        ("ALSO", "Group 24 'Skip the setup if the stop is CLOSER / FURTHER than' is read in the same unit (pips, or % of the entry price). The trailing stop (34 c) uses the same buffer.")])
    h += card("- stop buffer in pips", "10", "10 on gold = your 1.0", [("USED", "Only when the unit is Pips."), ("EXAMPLE", "10 pips = 1.00 on gold, 0.10 on silver, 10 on Bitcoin, 0.0010 on EURUSD, 0.10 on USDJPY.")])
    h += card("- stop buffer in % of price", "0.02", "0.02 = 0.83 on gold now", [("USED", "Only when the unit is % of price."), ("EXAMPLE", "0.02% = 0.83 on gold at 4,140, 0.40 at 2,000; 20 on Bitcoin at 100,000; 0.00022 on EURUSD at 1.10.")])
    h += card("- pip size (0 = automatic)", "0", "0", [("USED", "0 = the automatic pip from the table. Type a number only if your broker counts pips differently, e.g. 0.01 for gold.")])
    h += "<h3>The automatic pip</h3>"
    h += table(["Market", "1 pip", "10 pips", "50 pips"], [
        ["Gold (XAUUSD, GOLD)", "0.10", "<b>1.00</b>", "5.00"], ["Silver (XAGUSD)", "0.01", "0.10", "0.50"], ["Bitcoin", "1", "10", "50"],
        ["Ethereum", "0.10", "1.00", "5.00"], ["EURUSD, GBPUSD, ...", "0.0001", "0.0010", "0.0050"], ["USDJPY, EURJPY, ...", "0.01", "0.10", "0.50"],
        ["Anything else", "10 &times; the price step", "", ""]], num=(1, 2, 3))
    h += "<div style='break-inside: avoid'><h3>Example - gold 1m, a bullish CHOCH*, the level at 4,100.00</h3>"
    h += table(["Unit", "Setting", "Buffer", "Stop at"], [
        ["Price", "1.0", "1.00", "4,099.00 (as v11.1)"], ["Pips", "10", "10 &times; 0.10 = 1.00", "4,099.00"], ["Pips", "50", "50 &times; 0.10 = 5.00", "4,095.00"],
        ["%", "0.02", "0.02% of 4,100 = 0.82", "4,099.18"], ["%", "0.1", "0.1% of 4,100 = 4.10", "4,095.90"]]) + "</div>"
    h += box("Group 24 follows the unit", "Switching to Pips: 'skip closer than' 30 = 30 pips = 3.00 on gold. Switching to %: 0.05 = 0.05% of the entry price = 2.07 on gold at 4,140. "
             "Set these two again when you switch the unit (0 = off stays off). The table's new last row 'STOP BUFFER (group 38)' shows the buffer in price.", "warn")
    h += "<h3>Will it change your results? Your settings, FxPro gold 1m, 2021 - Oct 2026, risk 50</h3>"
    h += table(["Buffer", "Trades", "Total", "Per trade", "Losing years"], [
        ["1.0 (now) = 10 pips", "2,839", "-18,514", "-0.13R", "5 of 6"], ["0.02%", "3,061", "-22,350", "-0.15R", "5 of 6"], ["0.05%", "2,799", "-19,840", "-0.14R", "6 of 6"],
        ["0.1%", "2,486", "-17,216", "-0.14R", "6 of 6"], ["0.2%", "2,114", "-12,519", "-0.12R", "6 of 6"], ["0.5%", "1,654", "-6,768", "-0.08R", "6 of 6"],
        ["5.0 = 50 pips", "2,101", "-10,583", "-0.10R", "6 of 6"]], num=(1, 2, 3))
    h += box("Honest", "The unit only changes how you type the buffer - 10 pips on gold is exactly your 1.0. A wider buffer loses less per trade, but no size made money over 5.75 years. "
             "In 3 months (Feb - May 2026) the order was the opposite (1.0: +793, 0.1%: -277) - 3 months is not enough to choose. "
             "Silver, crypto and forex have not been tested at all: test there before trading them.", "warn")
    return h


def ch_tests112():
    h = chap("HOW v11.2 WAS CHECKED", "Parser, settings, the simulator and the MT5 EA's own code", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v11.2 without a syntax error. New names declared before use, no clashes, ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Settings: the 118 of v11.1 unchanged in the same places + 4 new at the end = 122.</li></ul>"
    h += table(["Check", "Result"], [
        ["Unit 'Price' vs v11.1 - 6 settings, 3 months of real gold 1m", "every trade <b>the same</b>"],
        ["10 / 25 / 50 pips vs 1.0 / 2.5 / 5.0 in price", "every trade <b>the same</b>"],
        ["Group 24 limits 30 / 400 pips vs 3 / 40 in price", "every trade <b>the same</b>"],
        ["Pips and % settings, 2021 - Oct 2026: the simulator vs the MT5 EA's own code (a separate program)", CHECK5],
        ["The automatic pip: 14 TradingView symbols, 21 MT5 symbol names", "all as in the table"]])
    h += "<p class='small'>This is not the TradingView compiler. If TradingView shows an error when you save, send the line and the message.</p>"
    return h


def was(x, v):
    y = x.replace("<div class=''><div class='lab'>WHAT IS NEW IN " + v + "</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN " + v + "</div>")
    assert "WHAT WAS NEW IN " + v in y
    return y


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
h = cover("HANDBOOK &middot; VERSION 11.2", "SMC Structure Strategy",
          "Part 1: the stop buffer unit of v11.2, the 'against' and 'auto' modes of v11.1, the three features of v11.0, what is new back to v8.4, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v11.2.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("ALSO", "SMC_Structure_EA_v11.2.mq5 - the same rules as an MT5 EA")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v112() + ch_tests112() + v111 + ch_tests111() + v110 + ch_together110() + ch_tests110() + v104 + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + \
    "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v11.2 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1), the v11.0 features, the v11.1 modes, the v11.2 stop buffer unit, and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v11.2'.</p></div>"
assert all(ord(c) < 128 for c in h)
open(HB + "hb_v11.2.html", "w").write(page("SMC Structure Strategy v11.2 Handbook", h))
print("ok")
