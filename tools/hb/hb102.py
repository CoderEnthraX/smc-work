# v10.2 handbook front part
HB = "/home/user/smc-work/tools/hb/"
src = open(HB + "hb101.py").read()
exec(src[:src.index("\nv10 = ch_v10()")])      # helpers + ch_v101() + ch_v10() + ch_v91()


def ch_v102():
    h = chap("WHAT IS NEW IN v10.2", "Loss recovery counts from - back",
             "One setting in group 21 decides which trades the loss-recovery rules (A / B / C and A+ / B+ / C+) and the hard cap look at.", True)
    h += card("Loss recovery counts from (group 21)", "The whole chart history", "whole history to test - 'goes live' for live trading", [
        ("WHOLE HISTORY", "Every closed trade on the chart counts, as in v10.1. Use it to see a rule in the backtest."),
        ("GOES LIVE", "Only trades that <b>open</b> from the first live candle on count - the moment you create the alert or open the chart. A trade still open from the replayed past never reached your broker, so it does not count. Nothing to type."),
        ("A DATE", "Only trades that open on or after the date in the next setting - the day you went live, a new month, a new deposit."),
        ("TABLE", "The row 'LOSS RECOVERY' shows where it counts from, e.g. <code>C+ - total below 0 | from live 02 Oct 09:15</code>.")])
    h += "<h3>Why it helps</h3><p>A TradingView strategy never starts 'today'. When you create the alert it first <b>replays every candle on your chart</b> as if it had traded them, " \
         "then goes on live <b>from where the replay ended</b> - with the loss carried, the total P&amp;L and any cap stop it remembers. This setting decides whether that replayed past may size your live trades.</p>"
    h += table(["", "The whole chart history", "When the strategy goes live"], [
        ["First live trade", "Your Rule C file, alert at 09:35 on Sep 22: the replay carried <b>1,989.24</b>, so the 09:41 trade risks 1,989.24 - for losses your account never had", "Starts at the base <b>50</b>"],
        ["Hard cap", "A cap reached anywhere in the replay leaves the strategy stopped before it starts ('Stop permanently')", "Only live trades can reach the cap"],
        ["A+ / B+ / C+ cushion", "Backtest profit counts: your Rule A file was +3,983.34 on Sep 18, so A+ would wait for 3,983 of live losses", "Only the profit you really made live"],
        ["Backtest on the chart", "Shows the rules working", "Shows every trade at the base risk (expected)"]])
    h += box("How to use it", "<b>Testing:</b> keep 'The whole chart history' (the default) and read the backtest. <b>Going live:</b> switch to 'When the strategy goes live (automatic)', then create the alert. "
             "Changing any setting (raising the cap too) or creating the alert again starts the live count from zero again.")
    h += "<p class='small'>Settings: 108 - the 106 of v10.1 in the same places, plus 2 at the very end (shown in group 21), in the same places as in v10.0.</p>"
    return h


v101 = ch_v101().replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.1</div>")
v10 = ch_v10()
i = v10.index("<div class='card'><div class='ch'><div class='ct'>Loss recovery counts from")
j = v10.index("<div class='box", i)
v10 = v10[:i] + v10[j:]
v10 = v10.replace("<div class=''><div class='lab'>WHAT IS NEW IN v10.0</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v10.0</div>")
v10 = v10.replace("One memory of the losses carried for all three rules, never below your base risk, and counted only from the moment the strategy goes live.",
                  "One memory of the losses carried for all three rules, never below your base risk. ('Counts from' is explained in 'What is new in v10.2'.)")
v91 = ch_v91().replace("<div class=''><div class='lab'>WHAT IS NEW IN v9.1</div>", "<div class='chap'><div class='lab'>WHAT WAS NEW IN v9.1</div>")
h = cover("HANDBOOK &middot; VERSION 10.2", "SMC Structure Strategy",
          "Part 1: what is new in v10.2 back to v8.4, every new setting, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.2.txt"), ("PLATFORM", "TradingView, Pine Script v6"),
           ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
           ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk"), ("HEDGE", "the same file added twice (Longs only / Shorts only)")],
          "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
h += ch_v102() + v101 + v10 + v91 + "<div style='page-break-before:always'></div>" + ch_whatsnew(True) + ch_tests(True) + ch_reco(True) + ch_direction() + ch_ideas() + ch_small()
h += "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
     "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works the same way in v10.2 - the new settings are at the end of the " \
     "settings panel and are explained in part 1.</p><p class='lead'><b>Exceptions:</b> loss recovery (part 2 describes the old Rule A that divided by R, and has no Rule C, A+ / B+ / C+ or 'counts from' - " \
     "see part 1) and the default when the cap is reached (now 'Stop permanently'). Where part 2 says 'v8.3', read 'v10.2'.</p></div>"
open(HB + "hb_v10.2.html", "w").write(page("SMC Structure Strategy v10.2 Handbook", h))
print("ok")
