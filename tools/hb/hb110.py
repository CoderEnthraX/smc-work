# v11.0 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb104.py").read()
exec(src[:src.index("\nv103 = ch_v103()")])      # helpers + ch_v104() + ch_stats104() + ch_tests104() + older chapters


def ch_v110():
    h = chap("WHAT IS NEW IN v11.0", "Three new features - each one optional",
             "All three are OFF by default. With all three off, v11.0 trades exactly like v10.4. They share the one higher-timeframe request the strategy already made, so the script stays as fast as before.", True)
    h += "<h3>1. Pause for some days after losses in a row (group 36)</h3>"
    h += card("Pause for some days after losses in a row", "Off", "your choice", [
        ("LOSSES", "<b>- losses in a row</b> (default 3). Any trade with Net P&amp;L below 0 after costs counts - a small loss at time flat too. A <b>win</b> starts the count again at 0; exactly 0 changes nothing."),
        ("DAYS", "<b>- days to pause</b> (default 2): the rest of that day <b>plus</b> this many days. Gold / forex / silver / indices: Monday-Friday only. Crypto or 'Trade 24/7': every day."),
        ("DURING", "No new trades. An open trade keeps running to its stop or target; a waiting order is cancelled. Trades that close during the pause are not counted."),
        ("AFTER", "Trading starts again by itself at 00:00 (session timezone) and the count starts again at 0."),
        ("LIVE", "Counts only the trades 'loss recovery counts from' (group 21) counts - with 'When the strategy goes live' the backtest cannot start your alert paused.")])
    h += table(["Market", "3rd loss in a row", "Paused", "Trading again"], [
        ["Gold", "Monday 14:00", "rest of Mon, Tue, Wed", "<b>Thursday</b>"], ["Gold", "Thursday 14:00", "rest of Thu, Fri, Mon", "<b>Tuesday</b>"],
        ["Crypto", "Thursday 14:00", "rest of Thu, Fri, Sat", "<b>Sunday</b>"]])
    h += "<h3>2. 'Higher timeframe favourable' modes (group 20, 'Take trades on')</h3>"
    h += card("Take trades on - three more choices", "CHOCH only", "test it against your normal mode first", [
        ("CHOICES", "<code>CHOCH only - higher timeframe favourable</code>, <code>BOS only - ...</code>, <code>CHOCH and BOS - ...</code>"),
        ("RULE", "The same signals, but <b>only in the higher timeframe's direction</b>: bullish &rarr; only buys, bearish &rarr; only sells. Not clear yet &rarr; no trades."),
        ("PAIRING", "Auto: 1m &rarr; 15m, 5m &rarr; 1h, 15m &rarr; 4h, 1h &rarr; 1D, 4h &rarr; 1W, 1D &rarr; 1M - the last <b>closed</b> higher-timeframe candle."),
        ("FLIP", "A <b>waiting</b> order is cancelled when the higher timeframe flips against it; an <b>open</b> trade keeps running.")])
    h += table(["Rule 1", "Rule 2", "Entry for every trade"], [["ON", "OFF", "the pullback %"], ["OFF", "ON", "the broken pivot"], ["ON", "ON", "the broken pivot (rule 1 is never used)"]])
    h += table(["15m trend", "1m signal", "Result"], [["bearish", "bearish CHOCH", "<b>SELL</b>"], ["bearish", "bullish CHOCH", "skipped"], ["bullish", "bullish CHOCH", "<b>BUY</b>"], ["bullish", "bearish CHOCH", "skipped"]])
    h += "<h3>3. Higher timeframe equilibrium first (group 37)</h3>"
    h += card("Trade only after the higher timeframe pulled back to its equilibrium", "Off", "your choice - 50, 61.8 or 70.5", [
        ("CLOSES", "Every CHOCH or BOS on the higher timeframe starts a new leg and <b>closes the gate</b>: no trades at all, buys and sells."),
        ("OPENS", "When the price <b>touches</b> the equilibrium of that leg (a wick is enough, deeper is fine). If the leg runs further first, the level moves with it."),
        ("THEN", "The chart trades by 'Take trades on', rule 1 and rule 2 until the next higher-timeframe CHOCH or BOS closes the gate again."),
        ("ORDERS", "A waiting order is cancelled when the gate closes; an open trade keeps running."),
        ("SAME LIVE", "The higher-timeframe CHOCH / BOS counts once its candle has closed - the backtest and live see the same thing.")])
    h += table(["Time", "What happens", "Gate"], [
        ["10:00", "15m bullish BOS - leg 3,950 &rarr; 4,050, level 50% = <b>4,000</b>", "closed"], ["10:30", "price 4,020", "closed"],
        ["11:40", "price dips to 3,998 - touched", "<b>OPEN</b>"], ["11:50", "1m bullish CHOCH &rarr; buy (rule 1 / rule 2)", "open"],
        ["13:00", "new 15m BOS - a new leg", "closed"]])
    return h


def ch_together110():
    h = chap("HOW THEY WORK TOGETHER", "The order every signal goes through", "And what 3 months of real gold data showed with your settings.")
    h += table(["Step", "Check", "If it fails"], [
        ["1", "Pause after losses - and every other stop (news, weekend, daily limit, floor ...)", "no trade"],
        ["2", "Higher timeframe equilibrium gate", "no trade"],
        ["3", "'Take trades on' - with a favourable mode, only the higher timeframe's direction", "skipped"],
        ["4", "Rule 1 / rule 2", "decides where the order waits"]])
    h += box("Example - all three on", "Only buys while the 15m is bullish, only after the 15m pulled back to 50% of its leg, and never during a pause after 3 losses in a row.")
    h += "<h3>3 months of real gold data (Feb 25 - May 26, 2026)</h3><p class='small'>Your settings: CHOCH only, rule 1 + 2, 25%, close and reverse OFF, Max leverage 100.</p>"
    h += table(["Setting", "Trades", "Net P&amp;L", "Lowest point"], [
        ["v10.4 / everything off", "112", "+793", "-274"], ["2. favourable (rule 1 + 2)", "93", "-82", "-182"], ["2. favourable, rule 1 only", "92", "-397", "-458"],
        ["3. equilibrium 50%", "84", "<b>+1,410</b>", "-128"], ["1. pause 3 losses / 2 days", "82", "<b>+1,244</b>", "-204"], ["2 + 3", "77", "-160", "-260"],
        ["all three", "56", "+221", "<b>-57</b>"]], num=(1, 2, 3))
    h += box("Do not decide on 3 months", "This is one short period. Test each feature in the long backtests of the data request (one year or more) before using it live - and compare with everything off.", "warn")
    return h


def ch_tests110():
    h = chap("HOW v11.0 WAS CHECKED", "Parser, settings and the simulator - each feature against its own rule", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v11.0 without a syntax error. Every new name is declared before use and clashes with no old one. ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Settings: the 113 of v10.4 in the same order and places, the 5 new ones at the very end; the 3 old 'Take trades on' choices unchanged.</li></ul>"
    h += table(["Check (real gold 1-minute data, Feb 25 - May 26, 2026)", "Result"], [
        ["Everything off - CHOCH / BOS / both, reverse on / off, rule 2 off, filter b", "every order and trade <b>the same as v10.4</b>"],
        ["2. Favourable modes - 3 modes &times; 3 rule settings &times; reverse on / off", "<b>0</b> trades against the higher timeframe, <b>0</b> wrong entry rule, <b>0</b> filled after a flip"],
        ["2. A test higher timeframe that flips often", "5 to 71 waiting orders cancelled on a flip - <b>none</b> filled after it"],
        ["3. Equilibrium gate - 50% and 61.8%", "<b>0</b> trades armed or filled while closed; opened exactly when the separate calculation said"],
        ["3. The 15m leg", "its end was the highest high / lowest low since its CHOCH / BOS every time"],
        ["1. Pause - 6 settings &times; reverse on / off (gold days, every day, from live)", "every pause started and ended exactly where a separate calendar said; <b>0</b> trades inside a pause"],
        ["All three together", "the same checks - 0 errors"]])
    return h


v104 = ch_v104().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.4</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.4</div>")
assert "WHAT WAS NEW IN v10.4" in v104
v103 = ch_v103().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.3</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.3</div>")
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
h = cover("HANDBOOK &middot; VERSION 11.0", "SMC Structure Strategy",
          "Part 1: the three new features of v11.0, how they work together, what is new back to v8.4, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v11.0.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("NEXT STEP", "SMC_Strategy_DATA_REQUEST_v10.4.pdf - still valid")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v110() + ch_together110() + ch_tests110() + v104 + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + \
    "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v11.0 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1), the three v11.0 features, and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v11.0'.</p></div>"
open(HB + "hb_v11.0.html", "w").write(page("SMC Structure Strategy v11.0 Handbook", h))
print("ok")
