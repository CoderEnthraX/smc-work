# SMC_Strategy_DATA_REQUEST_v10.4.pdf - everything to send for the next round of tests
import sys
HB = "/home/user/smc-work/tools/hb/"
sys.path.insert(0, HB)
import common
from common import page, cover, chap, table, box

common.CSS += """
.ck { display: inline-block; width: 3.4mm; height: 3.4mm; border: 1.3px solid #1d5b8c; border-radius: 1px; vertical-align: -0.6mm; }
.fill { display: block; border-bottom: 1px solid #9aa5b4; height: 7mm; }
.step { display: grid; grid-template-columns: 7mm 1fr; column-gap: 2mm; margin-bottom: 1.8mm; }
.step .n { background: #1d5b8c; color: #fff; border-radius: 50%; width: 5.2mm; height: 5.2mm; font-size: 7.6pt; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.tag { white-space: nowrap; }
.p1 { background: #a01515; } .p2 { background: #b86200; } .p3 { background: #1d5b8c; } .p4 { background: #0b6b3a; }
"""
CK = "<span class='ck'></span>"


def steps(items):
    return "".join("<div class='step'><div class='n'>%d</div><div>%s</div></div>" % (i + 1, t) for i, t in enumerate(items))


def pr(n):
    return "<span class='tag %s'>PRIORITY %s</span>" % ({"1": "r", "1b": "r", "2": "y", "3": "b", "4": "g"}[n], n.upper())


h = cover("DATA REQUEST &middot; FOR v10.4", "What to send me",
          "Everything I need to measure, test and improve the SMC Structure Strategy - step by step, the most important first. Start with Priority 1: I can begin as soon as the first year arrives.",
          [("SCRIPT", "SMC_Structure_Strategy_v10.4.txt"), ("CHART", "XAUUSD 1-minute, OANDA feed"),
           ("BROKER", "FxPro MT5 via TheConnector"), ("HOW TO SEND", "upload the files in our chat"),
           ("TIME NEEDED", "about 1-2 hours, in parts"), ("MOST IMPORTANT", "Priority 1 - the long backtests")],
          "<b>Never send</b> passwords, your TheConnector access key or the webhook URL with the key, a MetaApi token, SECRET or a Telegram bot token - in files, chat or screenshots. "
          "Your account number and name are optional - you can cover them.")

# ---------------------------------------------------------------- checklist
h += chap("AT A GLANCE", "The checklist", "Tick each line when it is sent. The file names help me match everything - any name is fine if you tell me what it is.", True)
h += table(["", "What", "Priority", "File name (suggested)"], [
    [CK, "Backtest of v10.4, List of Trades CSV - one file per year: 2023, 2024, 2025, 2026", pr("1"), "<code>v10.4_2023.csv</code> ... <code>v10.4_2026.csv</code>"],
    [CK, "Screenshots: every settings group, the Properties tab, the Performance Summary, the strategy table", pr("1"), "<code>settings_1.png</code>, <code>properties.png</code> ..."],
    [CK, "Your chart timezone and TradingView plan (Deep Backtesting? Bar Magnifier?) - just type it", pr("1"), "in chat"],
    [CK, "Comparison runs on 2025: A reverse ON, B CHOCH and BOS, C pause after 2 losses, D account floor", pr("1b"), "<code>v10.4_2025_A.csv</code> ... <code>_D.csv</code>"],
    [CK, "MT5: XAUUSD 1-minute bars from 1 Jan 2023 to today (one file per year is fine)", pr("2"), "<code>XAUUSD_M1_2023.csv</code> ..."],
    [CK, "MT5: trade history report of the demo account TheConnector trades", pr("3"), "<code>mt5_history.html</code>"],
    [CK, "MT5: XAUUSD specification + your account type, gold leverage, commission per lot", pr("3"), "<code>xauusd_spec.png</code>"],
    [CK, "TheConnector order log + TradingView alert log for the same days (hide the key)", pr("3"), "<code>connector_log.png</code>, <code>alerts_log.png</code>"],
    [CK, "Your numbers - the short form on the 'Your numbers' page", pr("4"), "in chat or a photo of the page"]])
h += box("Why this order", "Priority 1 answers the biggest question - does the strategy make money on average? Everything else (targets, filters, the floor, the risk %) is tuned on top of that answer. "
         "If you only have time for one thing, send <b>one year of Priority 1</b>.")

# ---------------------------------------------------------------- why
h += chap("WHY", "What we know so far - and what is missing", "In R = your base risk. From your own files and the simulator on real gold data.")
h += table(["Test", "Trades", "Avg per trade", "What it means"], [
    ["2021-22, close and reverse ON", "1,628", "-0.12 R", "surely losing"], ["2023-24, close and reverse ON", "1,530", "-0.13 R", "surely losing"],
    ["2025-26 CHOCH only, reverse ON", "1,158", "-0.04 R", "probably losing"],
    ["<b>Your settings now (reverse OFF)</b>", "156", "+0.13 R", "<b>positive, but not proven</b> - could be -0.10 R to +0.38 R"]], num=(1, 2))
h += "<p>Your current settings look good - but 156 trades are not enough to tell skill from luck. About <b>480 trades (one year)</b> are needed. That is why the long backtests come first.</p>"
h += table(["Data", "The question it answers"], [
    ["Long backtests (P1)", "Does the strategy win in every year, or only some? The best target (1.5 / 2 / 3 / 4 R), break-even, partial profit - from each trade's best and worst point. Hours, days, longs vs shorts, stop size, news days."],
    ["Comparison runs (P1b)", "Rules that change WHICH trades happen - close and reverse, BOS trades, the daily pause, the floor. These cannot be worked out from a list; TradingView must run them."],
    ["1-minute prices (P2)", "My simulator has only Feb 25 - May 26, 2026. With years of prices I can test any new rule exactly, in trending, choppy and news-heavy years."],
    ["Broker data (P3)", "Do live fills match the backtest? Slippage, spread, rejected orders, leverage - so the backtest costs and Max leverage match your real account."],
    ["Your numbers (P4)", "What 'better' means for you: the most you can lose (the floor), the profit you want, the hours you can trade."]])
h += box("How I keep it honest", "Rules are chosen on <b>2023-24</b>, then tested on <b>2025-26</b>, which they have never seen. Only rules that also work there go into the next version. "
         "This stops the strategy being fitted to the past.")

# ---------------------------------------------------------------- priority 1
h += chap("PRIORITY 1", "Long backtests of v10.4", "The most valuable data. One List of Trades CSV per year, with the settings below.")
h += "<h3>Step by step</h3>" + steps([
    "Add <b>SMC_Structure_Strategy_v10.4.txt</b> to an <b>XAUUSD 1-minute chart, OANDA feed</b> (<code>OANDA:XAUUSD</code>).",
    "Keep everything <b>exactly as you trade it</b>: CHOCH only, close and reverse OFF, rule 1 / rule 2, your target R, sessions, time flat, news and weekend rules, commission and spread.",
    "Change only the settings in the table below.",
    "In the Strategy Tester, if your plan has <b>Deep Backtesting</b>, switch it on, set the dates <b>1 Jan 2023 - 31 Dec 2023</b> and generate the report.",
    "Open the <b>List of Trades</b> tab and <b>export</b> it as CSV (the download button).",
    "Repeat for <b>2024</b>, <b>2025</b> and <b>2026</b> (to today). If TradingView cannot do a whole year, split it in halves.",
    "Take the screenshots: every settings group (scroll through all of them), the Properties tab, the Performance Summary of each year, and the strategy table on the chart. Once is enough if all years used the same settings.",
    "Tell me your <b>chart timezone</b> (bottom right of the chart) and whether <b>Bar Magnifier</b> was on."])
h += "<h3>Settings to change for this test</h3>"
h += table(["Group", "Setting", "Set to", "Why"], [
    ["21", "Loss-recovery sizing", "<b>Off</b>", "Measure the strategy itself, at one fixed risk"],
    ["35", "Account floor", "<b>Off</b>", "The same"],
    ["21", "BASE risk per trade", "50", "Any value works - I measure in R"],
    ["21", "Max leverage", "100", "As you trade"],
    ["24", "Max trades per day / Stop for the day after losing / Stop PERMANENTLY after drawdown", "<b>0 / 0 / 0</b>", "Keep every trade - I can apply limits afterwards, but never bring back a trade a limit removed"],
    ["27", "Stop taking new trades once the profit target is reached", "<b>OFF</b>", "The same"],
    ["34", "g. Pause for the rest of the day after losses in a row", "<b>OFF</b>", "Tested separately in run C"],
    ["Properties", "Initial capital", "<b>100,000</b>", "So the test never runs out of money - your 2021-22 and 2023-24 files stopped when the 10,000 ran out. The risk stays 50."],
    ["Properties", "Margin for long / short positions", "as you have it (300x)", "No margin calls"],
    ["Properties", "Bar Magnifier (if your plan has it)", "ON - and tell me", "More exact fills inside each candle"]])
h += box("Why the limits must be off", "From a full list of trades I can apply any daily limit, pause or cap afterwards with maths. A trade that a limit removed is gone for ever - I cannot bring it back.", "warn")

h += "<h3>Priority 1b - four comparison runs (2025 only is enough)</h3><p>The same settings as above, with <b>one</b> change each. These rules change which trades happen, so TradingView has to run them.</p>"
h += table(["Run", "The one change", "File name"], [
    ["A", "Group 20: Opposite signal while in a trade: close and reverse - <b>ON</b>", "<code>v10.4_2025_A_reverseON.csv</code>"],
    ["B", "Group 20: Take trades on - <b>CHOCH and BOS</b>", "<code>v10.4_2025_B_chochbos.csv</code>"],
    ["C", "Group 34: g. Pause for the rest of the day after losses in a row - <b>ON, 2</b>", "<code>v10.4_2025_C_pause2.csv</code>"],
    ["D", "Group 35: Account floor - <b>On - only cap the risk</b>, 2,000 / 50 / 2.5; Properties initial capital <b>10,000</b>", "<code>v10.4_2025_D_floor.csv</code>"]])

# ---------------------------------------------------------------- priority 2
h += chap("PRIORITY 2", "1-minute gold prices from MT5", "Years of prices let me test any new rule exactly - not just from a list of trades.")
h += steps([
    "Open <b>MT5</b> on your computer (FxPro).",
    "Menu <b>View &rarr; Symbols</b> (or Ctrl+U), then the <b>Bars</b> tab.",
    "Choose <b>XAUUSD</b>, timeframe <b>M1</b>, from <b>2023.01.01</b> to today, and press <b>Request</b>.",
    "Press <b>Export Bars</b> and save the CSV. About 20 MB per year - one file per year is fine if it is easier to upload.",
    "Tell me the <b>MT5 server time</b> shown in Market Watch, so I can line the prices up with TradingView.",
    "If FxPro's history does not go back to 2023, send what it has and tell me the first date."])
h += box("Optional - real spread", "In the same window, the <b>Ticks</b> tab: one normal week of XAUUSD ticks (Request, then Export). It shows the real spread through the day - one week is enough.")

# ---------------------------------------------------------------- priority 3
h += chap("PRIORITY 3", "What really happens at your broker", "So the backtest costs, leverage and fills match your real account.")
h += table(["What", "How", "What I look for"], [
    ["MT5 trade history (demo account TheConnector trades)", "History tab &rarr; right-click &rarr; choose the period &rarr; <b>Report</b> (HTML). Cover your name and account number if you like.", "Fill prices vs the backtest, slippage, missed or rejected orders"],
    ["XAUUSD specification", "Market Watch &rarr; right-click XAUUSD &rarr; <b>Specification</b> &rarr; screenshot", "Contract size, smallest lot, lot step, margin, stops level, swap"],
    ["Account conditions", "Account type, <b>leverage on gold</b>, commission per lot - from your FxPro account page", "Max leverage and the commission settings"],
    ["TheConnector order log", "Screenshots for the same days - <b>hide the access key and webhook URL</b>", "Orders rejected or late"],
    ["TradingView alert log", "Alerts panel &rarr; Log - screenshots for the same days", "Alerts that fired but did not reach the broker"]])

# ---------------------------------------------------------------- priority 4
h += chap("PRIORITY 4", "Your numbers", "Just type the answers in chat, or fill this page in and send a photo. They decide what 'better' means for you.")
q = ["The account size you will trade live (USD)", "The MOST you are willing to lose in total - this becomes the account floor",
     "The most you accept to lose in one day", "The monthly profit you would be happy with",
     "The hours you can trade (IST), and days you do not want to trade", "Will you run longs and shorts as two separate copies? (yes / no)",
     "Your TradingView plan - does it have Deep Backtesting and Bar Magnifier?", "Does MT5 run on a VPS or on your own PC - always on?",
     "Anything that went wrong live that I should know"]
h += "".join("<p style='margin-top:3.5mm'><b>%d.</b> %s</p><span class='fill'></span>" % (i + 1, t) for i, t in enumerate(q))

# ---------------------------------------------------------------- after
h += chap("AFTER YOU SEND IT", "What I will do with it", "Every step is measured on 2023-24 and checked on 2025-26 before it goes into the strategy.")
h += table(["Step", "What I work out", "From"], [
    ["1. The edge, year by year", "Does the average trade make money in every year? How sure can we be?", "P1"],
    ["2. Exits", "The best target (1.5 / 2 / 3 / 4 R), break-even after +1R, partial profit, time flat", "P1 (each trade's best and worst point), P2"],
    ["3. Filters", "Hours, days, longs vs shorts, stop size, news days, volatility", "P1, P2"],
    ["4. Day rules", "Pause after N losses, daily loss limit, max trades per day", "P1, P1b"],
    ["5. Sizing", "The right risk % (Kelly, cut for safety), the floor amount and lock, whether any recovery rule helps", "P1, P4"],
    ["6. Monte Carlo", "Chance of a profitable year, the likely worst year, the likely biggest drop", "all"],
    ["7. Live vs backtest", "Costs, slippage and leverage set so the backtest matches your account", "P3"]])
h += box("What you get back", "A report with the results in plain English, and <b>v10.5</b> with only the rules that also worked on the years they were not chosen on - plus the notes and handbook as usual.")
h += box("Never send", "Passwords (MT5, investor), your TheConnector access key, the webhook URL with the key, a MetaApi token, SECRET or a Telegram bot token - not in files, chat or screenshots. "
         "Check every screenshot before you send it.", "bad")

open(HB + "dr_v10.4.html", "w").write(page("SMC Strategy Data Request v10.4", h))
print("ok")
