# builds the front part of the v8.4 and v9.0 handbooks and the test report (HTML), rendered by render.js
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import *

SP = "/home/user/smc-work/tools/"
res = {r["key"]: r for r in json.load(open(SP + "sim2/final.json"))}
csv = json.load(open(SP + "ana/csvstats.json"))
OUT = SP + "hb/"
B = res["base"]


def resrow(k, label=None):
    r = res[k]
    return [label or esc(r["name"]), str(r["n"]), money(r["net"]), "%.2f" % r["pf"], "{:,}".format(r["dd"]),
            money(r["m"][0]), money(r["m"][1]), money(r["m"][2])]


RH = ["Test (one change at a time)", "Trades", "Net", "PF", "Max DD", "Month 1", "Month 2", "Month 3"]
NUM = (1, 2, 3, 4, 5, 6, 7)

# ------------------------------------------------------------------ shared chapters
def ch_whatsnew(v9):
    files = [["SMC_Structure_Strategy_v9.0.txt", "The strategy: v8.4 plus the seven idea switches (group 34), all OFF."]] if v9 else []
    files += [["SMC_Structure_Strategy_v8.4.txt", "v8.3 plus trade direction, symbol without spaces, 8 decimals."],
              ["SMC_Structure_Strategy_v8.4_LONG.txt", "Hedge copy: longs only, close and reverse OFF, tag smcL."],
              ["SMC_Structure_Strategy_v8.4_SHORT.txt", "Hedge copy: shorts only, close and reverse OFF, tag smcS."],
              ["..._NOTES.txt", "The full notes: every feature in plain English, and how it was checked."],
              ["SMC_Strategy_TEST_REPORT_v9.0.pdf", "Your three trade files and every idea, tested on real gold data."]]
    h = chap("CHAPTER A", "What is new" + (" in v8.4 and v9.0" if v9 else " in v8.4"),
             "Everything in this part is new. Part 2 is the v8.3 handbook, unchanged - every setting in it works the same way here.", True)
    h += "<h3>v8.4</h3><ul>"
    h += "<li><b>Trade direction</b> (group 33): Both / Longs only / Shorts only. Both = exactly v8.3. Two copies make a hedge (chapter C).</li>"
    h += "<li><b>Symbol and tag without spaces.</b> <code>GOLD </code> typed with a space is sent as <code>GOLD</code>.</li>"
    h += "<li><b>Up to 8 decimals</b> in the price and lot settings, so <code>0.0001</code> for forex is kept.</li></ul>"
    if v9:
        h += "<h3>v9.0</h3><ul><li>The seven <b>ideas to make it more profitable</b>, each a switch in group 34: smaller risk for stacked BOS trades, " \
             "higher-timeframe filter, structure trailing stop, target at the next liquidity, partial profit, premium / discount filter, " \
             "pause after losses in a row.</li><li><b>Every switch is OFF by default.</b> With all of them OFF, v9.0 trades exactly like v8.4.</li>" \
             "<li>Every idea was tested on real gold data first - chapter B shows which ones helped and which lost.</li></ul>"
    h += "<h3>The files</h3>" + table(["File", "What it is"], [["<code>%s</code>" % a, b] for a, b in files])
    h += "<h3>How to update</h3><ol><li>Wait until you are <b>flat</b> (no open trade).</li>" \
         "<li>Pine Editor: replace the code, save. Your saved settings keep their places: the new settings are at the very end (%s).</li>" \
         "<li>Delete the alert and create it again: condition = the strategy, <b>Order fills only</b>, message <b>only</b> <code>{{strategy.order.alert_message}}</code>.</li>" \
         "<li>Your TheConnector access key goes only into the webhook URL inside TradingView: <code>https://webhook.theconnector.fr/YOUR_ACCESS_KEY</code>.</li></ol>" % (
             "89 in v8.4, 104 in v9.0" if v9 else "89 settings: the 88 of v8.3 plus 1")
    h += box("What did NOT change", "The structure engine, rule 1 and rule 2, the stop, the target, the sizing, v8.3's order handling and the messages "
             "(apart from the spaces). The strategy never sends closeall.")
    return h


def ch_tests(v9):
    h = chap("CHAPTER B", "What the tests showed",
             "Your three one-year trade files, and every idea tested on real gold 1-minute data. The full detail is in the test report.")
    h += "<p>The strategy's logic was copied into a simulator and run on real gold 1-minute data from Feb 27 to May 25 2026 with your settings " \
         "(CHOCH only, rule 1 + 2, pullback 25, stop buffer 1, R 3, risk 50, costs 0.6 per ounce). It reproduces your own file for that period: " \
         "187 of about 265 trades start in the same minute on the same side, and those trades net 1,081 against 1,077 in your file. " \
         "Then one setting was changed at a time. Months: 1 = Feb 27-Mar 25, 2 = Mar 26-Apr 24, 3 = Apr 25-May 25.</p>"
    keys = ["base", "rev", "r2", "ln", "ny", "r2only", "mo2", "be", "step", "min6"]
    if v9:
        keys += ["a", "b", "c1", "c2", "d", "e", "f0", "f", "g", "hedge", "C"]
    else:
        keys += ["hedge"]
    h += table(RH, [resrow(k) for k in keys], NUM, hl=(0,))
    h += "<p class='small'>PF = profit factor (money won / money lost). Max DD = the largest fall from a high point of the account.</p>"
    return h


def ch_reco(v9):
    h = "<div style='page-break-inside:avoid'><h3>Which ones helped</h3><ul>"
    h += "<li><span class='tag g'>BETTER</span> <b>Close and reverse OFF</b> - the clearest gain. 'Opposite signal' exits lost money in all three of your yearly files - by far the most in 2021-22 and 2023-24.</li>"
    h += "<li><span class='tag g'>BETTER</span> <b>New York hours only</b> (entries 17-23) - the best hours in all three files too. Fewer trades.</li>"
    h += "<li><span class='tag g'>BETTER</span> <b>Step stop</b> and <b>minimum stop 6</b> - small stops lost most in 2021-22 and 2023-24.</li>"
    if v9:
        h += "<li><span class='tag g'>BETTER</span> <b>f. premium / discount filter with pullback 50</b> - half the drawdown of pullback 50 alone.</li>"
        h += "<li><span class='tag y'>SAME</span> break-even, c. trailing behind the CHOCH* level, d. liquidity target, e. partial profit, g. pause after losses.</li>"
        h += "<li><span class='tag r'>WORSE</span> rule 2 only, stacked BOS trades (a. helps only a little), b. higher-timeframe filter, c. trailing behind every swing, f. with your 25% pullback.</li></ul></div>"
    else:
        h += "<li><span class='tag y'>SAME</span> break-even; the hedge (about the same as one copy).</li><li><span class='tag r'>WORSE</span> rule 2 only, stacked BOS trades.</li></ul></div>"
    h += box("Try in this order, one step at a time", "<ol><li>Group 20 <b>close and reverse OFF</b>.</li><li>Group 24 <b>minimum stop 6</b> (gold at today's prices).</li>" +
             ("<li>v9.0 <b>f. premium / discount filter ON</b>, line 50, with the group 20 <b>rule 1 pullback 50</b>.</li>" if v9 else "") +
             "<li>Group 32 <b>step stop ON</b>.</li><li>Optional: <b>entries from 17:00</b> (group 20).</li>"
             "<li>Check your real broker cost: you model 0.6 per ounce per round trip. At 0.3 your own settings made %s instead of %s.</li></ol>"
             "Backtest each step over a full year on your chart first, then on a different year without changing anything, then on a demo account." % (
                 "{:+,}".format(res["cost3"]["net"]), "{:+,}".format(B["net"])))
    h += box("Be careful with these numbers", "Three months, 100 to 270 trades, one kind of market (gold falling from 5,200 to 4,550). "
             "One trade is worth 50 to 150, so a difference of a few hundred can be luck. Trust only what is better in several months and in your yearly files.", "warn")
    return h


def ch_direction():
    h = chap("CHAPTER C", "Group 33 - Trade direction and the hedge",
             "One copy of the strategy holds one net position. Two copies - one for buys, one for sells - can hold a buy and a sell at the same time.")
    h += card("Trade direction", "Both", "Both (one copy)", [
        ("WHAT IT DOES", "<b>Both</b>: every signal is traded, exactly as v8.3. <b>Longs only</b>: only buy signals open trades. <b>Shorts only</b>: only sell signals. "
                         "A signal the other way opens nothing - its audit label says <code>SKIP - longs only</code> and the table row 'Trade direction' counts it. "
                         "It still does everything else: it cancels a waiting order the other way, and with close and reverse ON it closes your open trades."),
        ("EXAMPLE", "Longs only, a bearish CHOCH prints while a buy is open. Close and reverse OFF: the buy keeps running to its own stop or target, no sell is opened. "
                    "Close and reverse ON: the buy is closed at the next open, still no sell."),
        ("WHY THIS VALUE", "One copy: Both. The two hedge copies are already preset: LONG = Longs only, SHORT = Shorts only.")])
    h += "<h3>The hedge, step by step</h3><ol>" \
         "<li><b>MT5:</b> your FxPro account must be a <b>hedging</b> account, not netting. On a netting account a sell closes your buy at the broker.</li>" \
         "<li><b>Pine Editor:</b> new script, paste <code>SMC_Structure_Strategy_v8.4_LONG.txt</code>, save (for example 'SMC LONG'), add to chart. The same with the SHORT file.</li>" \
         "<li><b>Type your own settings in each copy</b> - a new script starts at the defaults. Check at least: take trades on, rule 1 pullback, target R, stop buffer, " \
         "session hours, force-close hour, weekend cutoff, risk, lot step, commission, spread, symbol, news.</li>" \
         "<li><b>Keep the presets</b>: direction, close and reverse OFF, tags <code>smcL</code> and <code>smcS</code>.</li>" \
         "<li><b>One alert per copy</b>: condition = that copy, Order fills only, message only <code>{{strategy.order.alert_message}}</code>, " \
         "webhook <code>https://webhook.theconnector.fr/YOUR_ACCESS_KEY</code>. Both alerts go to the same webhook.</li>" \
         "<li><b>Each copy has its own report</b>, daily limits, loss recovery and profit target. Your total = report 1 + report 2.</li></ol>"
    h += table(RH, [resrow("base", "One copy, Both, reverse ON (yours)"), resrow("hedge", "LONG copy + SHORT copy, reverse OFF"),
                    resrow("rev", "One copy, Both, reverse OFF")], NUM, hl=(0,))
    h += box("Honestly", "The hedge made about the same as one copy, with less drawdown. One copy with close and reverse OFF did better. Gold fell in these months, "
             "so the SHORT copy made the money and the LONG copy lost. A buy and a sell on the same symbol partly cancel out, and you pay costs on both. Test it on a demo account first.", "warn")
    return h


def ch_small():
    h = chap("CHAPTER E", "Symbol, tag, decimals and the table", "Three small changes in v8.4, and the new table rows.")
    h += card("Symbol to send (group 30) and TheConnector tag", "blank / smcgold", "your broker's symbol, or blank", [
        ("WHAT IT DOES", "Spaces and quotes are taken out before they are sent. <code>GOLD </code> is sent as <code>GOLD</code>; a tag <code>smc gold</code> as <code>smcgold</code>."),
        ("WHY", "A space typed by accident made the broker refuse the order ('instrument name is wrong'). The table row 'Ticker - type / 1 lot / symbol sent' shows exactly what is sent."),
        ("FOREX", "Leave the symbol blank for EURUSD, AUDUSD, GBPUSD...: the chart's ticker is sent.")])
    h += card("Up to 8 decimals", "-", "type the number", [
        ("WHICH", "Stop buffer (group 20), lot step (21), minimum lot (22), minimum / maximum stop distance (24), broker spread (26)."),
        ("EXAMPLE", "EURUSD: spread <code>0.00012</code>, stop buffer <code>0.0001</code>, minimum stop <code>0.0005</code>. Before v8.4 TradingView rounded these to 2 decimals (0.00)."),
        ("GOOD TO KNOW", "The small arrows now move by 0.00000001 - type the number instead.")])
    h += "<h3>New rows in the counter table</h3>" + table(["Row", "What it shows"], [
        ["40  Trade direction (group 33)", "both, or the direction and how many signals the other way were not traded"],
        ["41  v9.0 ideas switched ON (group 34)", "the letters of the ideas that are ON, or none (v9.0 only)"],
        ["42  skipped: HTF filter / premium-discount / paused days", "setups skipped by b and f, and days paused by g (v9.0 only)"]])
    h += "<p class='small'>Row 13 is now 'Exit - moved stop (BE / step / trail)': in v9.0 it also counts the trailing stop and the break-even after the early profit.</p>"
    return h


def ch_ideas():
    h = chap("CHAPTER D", "Group 34 - the seven ideas",
             "Each one is a switch, OFF by default. The 'Set' value is what the test on real gold data suggests.")
    r = res
    h += card("a. Smaller risk for stacked BOS trades", "OFF / 50%", "OFF (CHOCH only)", [
        ("WHAT IT DOES", "With BOS in 'Take trades on', every same-side BOS adds a trade (group 31). ON: each <b>added</b> trade risks only this % of the normal risk. The first trade keeps the full risk."),
        ("EXAMPLE", "Risk 50, 50%: the CHOCH trade risks 50, each stacked BOS trade 25. Three stacked trades stopped together lose 75 instead of 150."),
        ("TEST", "Stacking lost in every form: %s with 50%% risk, %s at full risk (max 3 open), against %s for CHOCH only." % (money(r["a"]["net"]), money(r["mo3"]["net"]), money(B["net"])))], "bad")
    h += card("b. Higher-timeframe filter", "OFF", "OFF", [
        ("WHAT IT DOES", "ON: a signal is taken only when the higher timeframe (group 20, 15m on a 1m chart) trends the same way. With rule 2 ON this is 'rule 2 only'. "
                         "With rule 2 OFF and rule 1 ON, the agreeing signals use rule 1 - rule 1 only in the higher-timeframe direction."),
        ("TEST", "Rule 1 with the filter %s, rule 2 only %s, against %s. The 15-minute trend was a poor guide." % (money(r["b"]["net"]), money(r["r2only"]["net"]), money(B["net"])))], "bad")
    h += card("c. Structure trailing stop", "OFF / CHOCH* level", "OFF, or test the CHOCH* level", [
        ("WHAT IT DOES", "At every candle close the stop follows the structure, never backwards. <b>CHOCH* level</b>: for a buy the protected low of the up-trend, which moves up after every BOS. "
                         "<b>Every new swing</b>: behind each new swing low (high for a sell). The stop goes the group 20 stop buffer beyond the level."),
        ("EXAMPLE", "Buy at 4,500, stop 4,488. A BOS moves the CHOCH* low to 4,496: the stop moves to 4,495 (buffer 1). If the price falls back, the trade closes at 4,495."),
        ("AT THE BROKER", "Like a group 32 move: TradingView's moved stop fills and the close message closes the trade by its tag. The broker keeps the original stop as a safety net."),
        ("TEST", "CHOCH* level %s (about the same as %s); every swing %s - too tight for 1-minute noise." % (money(r["c1"]["net"]), money(B["net"]), money(r["c2"]["net"])))], "warn")
    h += card("d. Target at the next liquidity", "OFF / 1.5 R", "test it", [
        ("WHAT IT DOES", "ON: the target is the nearest swing high (low for a sell) the price has <b>not</b> traded through yet - where other traders' stops sit - "
                         "but only one at least this many R from the entry. None: the normal R target. The target follows new swings while the order waits, then stays."),
        ("EXAMPLE", "Buy at 4,500, stop 4,490 (R = 10). Untaken swing highs at 4,508 and 4,521. With 1.5 R the first one allowed is 4,515 or more: target 4,521."),
        ("TEST", "At least 1.5 R: %s against %s, better in 2 of 3 months; 1 R and 2 R were worse. A small, uncertain gain." % (money(r["d"]["net"]), money(B["net"])))], "warn")
    h += card("e. Partial profit", "OFF / 50% / 1.0 R / BE ON", "OFF", [
        ("WHAT IT DOES", "ON: every setup is sent as <b>two trades</b> at the same price and stop: the early part (this % of the size, target at this R, pushed out to cover its costs) "
                         "and the rest (the normal target). When the early part hits its target, the rest moves its stop to break-even."),
        ("AT THE BROKER", "Each part is an ordinary trade with its own order id (<code>L12</code>, <code>L12p</code>) and its own tag (<code>smcgold-k3f9</code>, <code>smcgold-k3f_</code>). "
                          "No partial-close command is needed, so TheConnector and the MetaApi receiver both work as they are."),
        ("GOOD TO KNOW", "The size is split on the lot step. With 50 risk and a wide gold stop the size is often only 0.01 lot - then it is sent as one trade. 'Max trades open' counts each part."),
        ("TEST", "%s against %s - about the same, a smoother curve." % (money(r["e"]["net"]), money(B["net"])))], "warn")
    h += card("f. Premium / discount filter", "OFF / 50", "test ON, with pullback 50", [
        ("WHAT IT DOES", "ON: a buy only at a <b>discount</b> - at or below this line of the leg, measured down from its high. A sell only at a <b>premium</b>. "
                         "The leg is the one rule 1 uses. A setup on the wrong side is cancelled."),
        ("IMPORTANT", "Your rule 1 pullback of 25% is always above the 50% line, so every rule 1 setup would be cancelled (1 trade in the test). Set the group 20 rule 1 pullback to 50 with it."),
        ("TEST", "Line 50 + pullback 50: %s, PF %.2f, max drawdown %s. Pullback 50 alone: %s but drawdown %s. Yours: %s, drawdown %s." % (
            money(r["f"]["net"]), r["f"]["pf"], "{:,}".format(r["f"]["dd"]), money(r["pb50"]["net"]), "{:,}".format(r["pb50"]["dd"]), money(B["net"]), "{:,}".format(B["dd"])))], "good")
    h += card("g. Pause after losses in a row", "OFF / 3", "OFF", [
        ("WHAT IT DOES", "ON: after this many losing trades in a row (after costs) no new trade for the rest of the day. Open trades are not touched. A win or a new day starts the count again."),
        ("TEST", "After 3 losses: %s against %s. In your yearly files it lost less only because it traded less - a brake, not an edge." % (money(r["g"]["net"]), money(B["net"])))], "warn")
    return h


def divider(v):
    return "<div class='divider'><div class='lab' style='color:#1d5b8c;font-weight:700;letter-spacing:2px'>PART 2</div><h2>The v8.3 handbook</h2>" \
           "<p class='lead'>The next pages are the v8.3 handbook, unchanged. Every setting it describes works exactly the same way in %s - " \
           "the new settings (groups 33%s) are at the end of the settings panel and are explained in part 1.</p>" \
           "<p class='lead'>Where part 2 says 'v8.3', read '%s'. Where it says the strategy will not hold a buy and a sell together: one copy will not - two copies can (chapter C).</p></div>" % (
               v, " and 34" if v == "v9.0" else "", v)


def handbook(v9):
    v = "v9.0" if v9 else "v8.4"
    h = cover("HANDBOOK &middot; VERSION %s" % v[1:], "SMC Structure Strategy",
              "Part 1: what is new, every new setting, and what the tests on real gold data showed. Part 2: the v8.3 handbook with every other setting.",
              [("SCRIPT", "SMC_Structure_Strategy_%s.txt" % v), ("PLATFORM", "TradingView, Pine Script v6"),
               ("BUILT FOR", "XAUUSD, 1-minute chart, OANDA feed"), ("EXECUTED AT", "FxPro MT5 via TheConnector"),
               ("EXAMPLE ACCOUNT", "10,000 USD, 50 base risk"), ("HEDGE COPIES", "..._v8.4_LONG.txt and ..._v8.4_SHORT.txt")],
              "This handbook describes what the code does, checked line by line and in a simulator. It is not financial advice, and no backtest guarantees future results. Run it on a demo account first.")
    h += ch_whatsnew(v9) + ch_tests(v9) + ch_reco(v9) + ch_direction()
    if v9:
        h += ch_ideas()
    h += ch_small() + divider(v)
    open(OUT + "hb_%s.html" % v, "w").write(page("SMC Structure Strategy %s Handbook" % v, h))


handbook(False)
handbook(True)


# ------------------------------------------------------------------ test report
def bars_svg(items, w=520, h=150, title=""):
    vals = [x[1] for x in items]
    mx = max(1, max(abs(v) for v in vals))
    bw = (w - 60) / len(items)
    s = "<svg width='%d' height='%d' viewBox='0 0 %d %d'>" % (w, h + 30, w, h + 30)
    y0 = h / 2 + 5
    s += "<line x1='50' x2='%d' y1='%.1f' y2='%.1f' stroke='#9aa4b2' stroke-width='1'/>" % (w - 5, y0, y0)
    for i, (lab, v) in enumerate(items):
        x = 55 + i * bw
        hh = abs(v) / mx * (h / 2 - 10)
        y = y0 - hh if v >= 0 else y0
        s += "<rect x='%.1f' y='%.1f' width='%.1f' height='%.1f' fill='%s'/>" % (x, y, bw * 0.7, hh, "#0b6b3a" if v >= 0 else "#a01515")
        s += "<text x='%.1f' y='%.1f' font-size='8' text-anchor='middle' fill='#1f2733'>%s</text>" % (x + bw * 0.35, (y - 3) if v >= 0 else (y + hh + 10), "{:+,}".format(int(v)))
        s += "<text x='%.1f' y='%d' font-size='8' text-anchor='middle' fill='#4a5566'>%s</text>" % (x + bw * 0.35, h + 24, lab)
    s += "<text x='0' y='12' font-size='9' font-weight='700' fill='#1f2733'>%s</text></svg>" % title
    return s


def eq_svg(series, w=520, h=190):
    import math
    allv = [v for _, _, ys in series for v in ys] + [0]
    lo, hi = min(allv), max(allv)
    n = max(len(ys) for _, _, ys in series)
    top = 14 * len(series) + 8
    s = "<svg width='%d' height='%d' viewBox='0 0 %d %d'>" % (w, h + top, w, h + top)
    X = lambda i, m: 45 + (w - 55) * i / max(1, m - 1)
    Y = lambda v: top + 10 + (h - 30) * (hi - v) / max(1, hi - lo)
    for g in range(int(lo // 500) * 500, int(hi) + 1, 500):
        s += "<line x1='45' x2='%d' y1='%.1f' y2='%.1f' stroke='#e3e7ec'/><text x='40' y='%.1f' font-size='8' text-anchor='end' fill='#6b7686'>%s</text>" % (w - 10, Y(g), Y(g), Y(g) + 3, "{:,}".format(g))
    ly = 10
    for name, col, ys in series:
        pts = " ".join("%.1f,%.1f" % (X(i, len(ys)), Y(v)) for i, v in enumerate(ys))
        s += "<polyline fill='none' stroke='%s' stroke-width='1.6' points='%s'/>" % (col, pts)
        s += "<rect x='55' y='%d' width='10' height='3' fill='%s'/><text x='70' y='%d' font-size='8.5' fill='#1f2733'>%s</text>" % (ly - 3, col, ly + 1, esc(name))
        ly += 12
    s += "<text x='45' y='%d' font-size='8' fill='#6b7686'>trade by trade, Feb 27 - May 25 2026 (net after costs, USD)</text></svg>" % (h + top - 4)
    return s


eqs = json.load(open(SP + "sim2/equity.json"))
names = {"A 2021-22": "2021-22", "B 2023-24": "2023-24", "C 2025-26 CHOCH only": "2025-26"}
R = cover("TEST REPORT &middot; v9.0", "What your trades say",
          "Your three one-year trade files, the settings you asked about, and the seven new ideas - tested on real gold data before they were built.",
          [("YOUR FILES", "2021-22, 2023-24, 2025-26 (CHOCH only)"), ("SIMULATOR", "the strategy's logic in Python, real gold 1m data"),
           ("TEST PERIOD", "Feb 27 - May 25 2026 (3 months)"), ("YOUR SETTINGS", "CHOCH only, R 3, pullback 25, buffer 1, risk 50"),
           ("COSTS", "0.6 per ounce per round trip (your files)"), ("STRATEGY", "SMC_Structure_Strategy_v9.0.txt")],
          "Backtests and simulations describe the past. They are not financial advice and do not guarantee future results. Test every change on a demo account first.")
R += chap("SUMMARY", "The short answer", "What to change first, and why.", True)
R += "<ol><li><b>Costs are the biggest problem.</b> In 2021-22 and 2023-24 commission was 85-93%% of the loss; before costs those years were almost flat. Check your real FxPro cost and type it exactly.</li>" \
     "<li><b>Switch 'close and reverse' OFF.</b> 'Opposite signal' exits lost money in all three files (13,754 and 15,192 in 2021-22 and 2023-24), and OFF was clearly better in the test (%s against %s, drawdown %s against %s).</li>" \
     "<li><b>Skip small stops.</b> Stops under 4 to 8 in price lost most of the money in 2021-22 and 2023-24. A minimum stop of 6 helped in the test too.</li>" \
     "<li><b>New York hours were the best</b> in every file and in the test; 06:00-17:00 the worst.</li>" \
     "<li><b>Of the seven ideas</b>, the premium / discount filter (with a 50%% pullback) helped; liquidity target and partial profit changed little; the higher-timeframe filter, stacking BOS trades and trailing behind every swing lost.</li>" \
     "<li><b>The hedge</b> (a LONG and a SHORT copy) made about the same as one copy - it is possible, but it did not add profit.</li></ol>" % (
         money(res["rev"]["net"]), money(B["net"]), "{:,}".format(res["rev"]["dd"]), "{:,}".format(B["dd"]))
R += box("How far to trust it", "Your files cover three years but can only answer some questions. The simulator answers all of them, but on three months of data (100 to 270 trades, gold falling). "
         "Where both agree - close and reverse OFF, small stops, New York hours - the result is solid. Everything else: backtest it on your chart over a full year before you trade it.", "warn")

R += chap("PART 1", "Your three trade files", "One year (or more) each, as exported from TradingView's List of Trades.")
rows = []
for k, o in csv.items():
    a = o["all"]
    rows.append([names[k], o["period"], str(a["n"]), money(a["net"]), "{:,}".format(a["comm"]), money(a["gross"]), "%.1f%%" % a["win"], "%.2f" % a["pf"], "{:,}".format(a["dd"])])
R += table(["File", "Period", "Trades", "Net", "Costs", "Before costs", "Win", "PF", "Max DD"], rows, (2, 3, 4, 5, 6, 7, 8))
R += "<p>2021-22 and 2023-24 almost used up the 10,000 account; 2025-26 lost 2,133. In every file the costs are about as large as the whole loss.</p>"
R += "<h3>How the trades ended</h3>"
ex_rows = []
for why in ("Opposite signal", "Own stop / target", "Time flat", "Weekend flat"):
    ex_rows.append([why] + ["%d / %s" % (csv[k]["exits"][why]["n"], money(csv[k]["exits"][why]["net"])) for k in csv])
R += table(["Exit", "2021-22 (trades / net)", "2023-24", "2025-26"], ex_rows, (1, 2, 3))
R += "<p>'Opposite signal' - a trade closed by the next CHOCH against it - is where most of the money went in 2021-22 and 2023-24, and it lost in 2025-26 too. Trades held to 02:00 or the weekend made money in every file.</p>"
R += "<h3>Stop size decides a lot</h3><p>The stop distance is worked out from the size (risk 50 / size - costs). Small stops mean big sizes, big costs and more noise.</p>"
for k in csv:
    R += bars_svg([(x[0], x[1]["net"]) for x in csv[k]["stops"]], title="Net by stop distance in price - " + names[k])
R += "<h3>Hours (entry time, your chart's time)</h3>"
hr_rows = []
for i in range(6):
    hr_rows.append([csv["A 2021-22"]["hours"][i][0]] + ["%d / %s" % (csv[k]["hours"][i][1]["n"], money(csv[k]["hours"][i][1]["net"])) for k in csv])
R += table(["Entries", "2021-22", "2023-24", "2025-26"], hr_rows, (1, 2, 3))
R += "<h3>What-ifs the files can answer</h3><p>Removing trades from a file is exact when the strategy holds one trade at a time (CHOCH only): the other trades do not change.</p>"
wi = json.load(open(SP + "ana/whatif.json"))
R += table(["What-if", "2021-22", "2023-24", "2025-26"], [[esc(k)] + [money(v) for v in vals] for k, vals in wi], (1, 2, 3), hl=(0,))
R += "<p class='small'>Target R rows are estimated from each trade's best price (favourable excursion): a trade that reached the smaller target is counted as a win at that target.</p>"

R += chap("PART 2", "The simulator and every setting you asked about", "Real gold 1-minute data, your settings, one change at a time.")
R += "<p><b>How it works.</b> The strategy's structure engine (CHOCH / BOS, the 3-candle pullback, sweeps), the 15-minute trend for rule 2, the entry rules, the stop and target, the sizing with your costs, " \
     "the session, 02:00 and weekend rules, and TradingView's way of filling orders inside a candle were written again in Python and run on real gold 1-minute data (Feb 25 - May 26 2026, 86,839 candles).</p>" \
     "<p><b>Checked against your own file.</b> For that period your 2025-26 file has about 265 trades. 187 of them start in the same minute on the same side in the simulator (181 also with the same size), " \
     "and those 187 trades net <b>1,081</b> in the simulator against <b>1,077</b> in your file. The others differ because this data is not OANDA's feed (prices are 0.3 to 0.6 apart). " \
     "Totals: simulator %s, your file for the same days %s.</p>" % (money(B["net"]), money(812))
R += "<h3>Settings that already exist</h3>" + table(RH, [resrow(k) for k in ["base", "rev", "r2", "ln", "ny", "r2only", "mo2", "mo3", "be", "step", "min6", "cost3"]], NUM, hl=(0,))
R += eq_svg([("Your settings", "#6b7686", eqs["base"]), ("Close and reverse OFF", "#1d5b8c", eqs["rev"]),
             ("Combination: reverse OFF + pullback 50 + filter f + step stop", "#0b6b3a", eqs["C"])])
R += chap("PART 3", "The seven new ideas", "Each built into the simulator exactly as in v9.0, then switched on alone.")
R += table(RH, [resrow(k) for k in ["base", "a", "mo3", "b", "c1", "c2", "d", "e", "f0", "f", "pb50", "g", "hedge", "C", "Cny"]], NUM, hl=(0,))
R += table(["Idea", "Verdict", "Why"], [
    ["a. Smaller risk for stacked BOS", "<span class='tag r'>WORSE</span>", "Stacking loses; smaller stacks only lose less. Keep CHOCH only."],
    ["b. Higher-timeframe filter", "<span class='tag r'>WORSE</span>", "The 15-minute trend was a poor guide on 1-minute gold."],
    ["c. Trailing - CHOCH* level", "<span class='tag y'>SAME</span>", "About the same result; worth a test on your chart."],
    ["c. Trailing - every swing", "<span class='tag r'>WORSE</span>", "Too tight: normal 1-minute noise stops the trade."],
    ["d. Target at next liquidity", "<span class='tag y'>SMALL GAIN</span>", "Better in 2 of 3 months at 1.5 R; worse at 1 R and 2 R."],
    ["e. Partial profit", "<span class='tag y'>SAME</span>", "Smoother, not more profitable. Often too small to split on gold."],
    ["f. Premium / discount", "<span class='tag g'>BETTER</span>", "Only with a 50% pullback: half the drawdown of pullback 50 alone."],
    ["g. Pause after losses", "<span class='tag y'>SAME</span>", "Loses less only by trading less."],
    ["Hedge (two copies)", "<span class='tag y'>SAME</span>", "About the same as one copy; one copy with reverse OFF did better."]])
R += box("The combination", "Close and reverse OFF + rule 1 pullback 50 + premium / discount filter 50 + step stop made %s with profit factor %.2f and a maximum drawdown of %s, "
         "better than your settings in all three months. Adding New York hours (entries from 17:00) kept %s with only %d trades. "
         "These combinations were chosen after seeing the results, so they will look better here than they will be in the future - backtest them on a full year on your chart." % (
             money(res["C"]["net"]), res["C"]["pf"], "{:,}".format(res["C"]["dd"]), money(res["Cny"]["net"]), res["Cny"]["n"]), "good")
R += chap("PART 4", "How to test it yourself", "So the backtest does not fool you.")
R += "<ol><li>Change <b>one</b> setting at a time and write down trades, net profit, profit factor and max drawdown.</li>" \
     "<li>Use a full year. Then check the same settings on a <b>different</b> year without changing anything. Keep a change only if it is better in both.</li>" \
     "<li>Type your <b>real</b> costs: commission per lot and spread (group 23 and 26), and the Properties commission.</li>" \
     "<li>Use Bar Magnifier if your TradingView plan has it.</li>" \
     "<li>Run it on a demo account for two weeks and compare the demo trades with the backtest every week.</li></ol>"
open(OUT + "report.html", "w").write(page("SMC Strategy test report v9.0", R))
print("html ok")
