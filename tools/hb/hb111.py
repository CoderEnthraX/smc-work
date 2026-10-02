# v11.1 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb110.py").read()
exec(src[:src.index("\nv104 = ch_v104()")])      # helpers + ch_v110() + ch_together110() + ch_tests110() + older chapters


def ch_v111():
    h = chap("WHAT IS NEW IN v11.1", "Six more choices in 'Take trades on'",
             "Both new sets are optional. The 9 choices of v11.0 are unchanged - with one of them picked, v11.1 trades exactly like v11.0.", True)
    h += "<h3>Against the higher timeframe</h3>"
    h += card("CHOCH only / BOS only / CHOCH and BOS - against the higher timeframe", "CHOCH only", "test it against your normal mode first", [
        ("RULE", "The mirror of the favourable modes: higher timeframe bullish &rarr; only <b>sells</b>; bearish &rarr; only <b>buys</b>; not clear &rarr; no trades."),
        ("ENTRY", "Always <b>rule 1</b> (your pullback %). Rule 2 needs the higher timeframe to agree, so it is never used - with rule 1 off these modes take no trades."),
        ("ORDERS", "A <b>waiting</b> order is cancelled when the higher timeframe turns to agree with it; an <b>open</b> trade keeps running."),
        ("WHY", "In 3 months of real gold data the trades against the 15m won more - with the same 25% entry: 43% wins / +612 against, 35% / +26 with.")])
    h += table(["15m trend", "1m signal", "Result"], [["bullish", "bearish CHOCH", "<b>SELL</b> at 25%"], ["bullish", "bullish CHOCH", "skipped"],
                                                  ["bearish", "bullish CHOCH", "<b>BUY</b> at 25%"], ["bearish", "bearish CHOCH", "skipped"]])
    h += "<h3>Auto: against the higher timeframe to its equilibrium, then with it</h3>"
    h += card("CHOCH only / BOS only / CHOCH and BOS - auto", "CHOCH only", "test it against your normal mode first", [
        ("PART 1", "A new higher-timeframe CHOCH or BOS starts a leg. Until the price touches its equilibrium: only signals <b>against</b> the higher timeframe, by rule 1 - trading the pullback."),
        ("PART 2", "From the touch on: only signals <b>with</b> the higher timeframe - rule 2 on = the broken pivot, else rule 1 - trading the move back."),
        ("AGAIN", "The next higher-timeframe CHOCH or BOS starts part 1 again."),
        ("ORDERS", "A waiting order on the wrong side after a switch is cancelled; an open trade keeps running."),
        ("THE %", "From group 37 ('the equilibrium, % pullback'), even with its switch off. The group 37 switch does not block these modes.")])
    h += table(["Time", "What happens", "Part", "Result"], [
        ["10:00", "15m bullish BOS - leg 3,950 &rarr; 4,050, level 50% = <b>4,000</b>", "1", "only sells"], ["10:20", "1m bearish CHOCH", "1", "<b>SELL</b> at 25%"],
        ["10:40", "1m bullish CHOCH", "1", "skipped"], ["11:40", "price touches 4,000 - a waiting sell order is cancelled", "2", "only buys"],
        ["11:50", "1m bullish CHOCH", "2", "<b>BUY</b> (rule 2 / rule 1)"], ["13:00", "new 15m BOS - a new leg", "1", "only sells again"]])
    h += "<h3>3 months of real gold data (Feb 25 - May 26, 2026)</h3><p class='small'>Your settings: CHOCH only, rule 1 + 2, 25%, close and reverse OFF.</p>"
    h += table(["Setting", "Trades", "Wins", "Net", "Lowest"], [
        ["everything off", "112", "38%", "+793", "-274"], ["favourable", "93", "32%", "-82", "-182"], ["<b>against the 15m</b>", "90", "42%", "+767", "-193"],
        ["equilibrium 50% (group 37 on)", "84", "43%", "<b>+1,410</b>", "-128"], ["auto 50%", "100", "29%", "-511", "-739"],
        ["auto 61.8%", "94", "32%", "-21", "-249"], ["auto 50% + pause 3 / 2", "61", "31%", "+120", "-109"]], num=(1, 2, 3, 4))
    h += box("Do not decide on 3 months", "In these months the trades WITH the 15m after its pullback lost - the opposite of what the auto mode bets on. "
             "Test each mode in the long backtests (one year or more) and compare it with everything off before using it live.", "warn")
    return h


def ch_tests111():
    h = chap("HOW v11.1 WAS CHECKED", "Parser, settings and the simulator", "")
    h += "<ul><li>A Pine Script parser (the full Pine grammar) read v11.1 without a syntax error. New names declared before use, no clashes, ASCII only, no tabs, no strategy.close_all.</li>" \
         "<li>Settings: the same 118 as v11.0. 'Take trades on' keeps its 9 old choices in the same order and adds 6 at the end.</li></ul>"
    h += table(["Check (real gold 1-minute data, Feb 25 - May 26, 2026)", "Result"], [
        ["The old choices", "every order and trade <b>the same as v11.0</b>"],
        ["Against modes - 3 modes &times; 3 rule settings &times; reverse on / off", "<b>0</b> trades with the higher timeframe, always rule 1, <b>0</b> filled after it turned to agree; rule 2 only = no trades"],
        ["Against modes - a test higher timeframe that flips often", "25 to 91 waiting orders cancelled - <b>none</b> filled after it"],
        ["Auto modes - 50% and 61.8% &times; 3 modes &times; 3 rule settings &times; reverse on / off (36 runs)", "the side allowed worked out separately: <b>0</b> on the wrong side, <b>0</b> wrong entry rule, <b>0</b> filled after a switch; 160 waiting orders cancelled at a switch"],
        ["Auto + the group 37 switch + the pause", "0 errors"]])
    return h


v110 = ch_v110().replace("<div class=''><div class='lab'>WHAT IS NEW IN v11.0</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v11.0</div>")
assert "WHAT WAS NEW IN v11.0" in v110
v104 = ch_v104().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.4</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.4</div>")
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
h = cover("HANDBOOK &middot; VERSION 11.1", "SMC Structure Strategy",
          "Part 1: the new 'against' and 'auto' modes of v11.1, the three features of v11.0, what is new back to v8.4, and the tests on real gold data. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v11.1.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk (your setting)"), ("NEXT STEP", "SMC_Strategy_DATA_REQUEST_v10.4.pdf - still valid")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v111() + ch_tests111() + v110 + ch_together110() + ch_tests110() + v104 + ch_stats104() + ch_tests104() + v103 + ch_file2023() + ch_tests103() + v102 + v101 + v10 + v91 + \
    "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v11.1 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+, 'counts from', 'split' or the account floor - " \
     "see part 1), the v11.0 features and the v11.1 modes, and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v11.1'.</p></div>"
open(HB + "hb_v11.1.html", "w").write(page("SMC Structure Strategy v11.1 Handbook", h))
print("ok")
