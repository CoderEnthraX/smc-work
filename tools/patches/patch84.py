# v8.3 -> v8.4 : trade direction, symbol/tag without spaces, price settings with up to 8 decimals
# also writes the LONG and SHORT preset copies
import sys
R = "/home/user/smc-work/"
src = open(R + "SMC_Structure_Strategy_v8.3.txt").read()


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    return s.replace(old, new)


s = src
# ---- line 2
old2 = s.split("\n")[1]
assert old2.startswith("// SMC Structure Strategy  -  v8.3  -  ")
new2 = old2.replace("v8.3  -  ", "v8.4  -  ", 1).replace(
    "  -  ASCII only",
    ", trade direction (both / longs only / shorts only) so two copies can hedge, spaces taken out of the symbol and the tag, price settings take up to 8 decimals  -  ASCII only")
assert new2 != old2 and new2.endswith("ASCII only")
s = rep(s, old2, new2)

# ---- price / lot settings: up to 8 decimals
for name in ("stSlBuf  = input.float(0.0, \"Stop buffer beyond the CHOCH* level, in price\", minval = 0.0, step = 0.01",
             "stMinStop   = input.float(0.0, \"Skip the setup if the stop is CLOSER than this (price)\", minval = 0.0, step = 0.01",
             "stMaxStop   = input.float(0.0, \"Skip the setup if the stop is FURTHER than this (price)\", minval = 0.0, step = 0.01",
             "stSprd   = input.float(0.0, \"Broker spread, in price  (0 = not modelled)\", minval = 0.0, step = 0.01",
             "stLotStep = input.float(0.01, \"Round the size to the broker's lot step  (0 = off)\", minval = 0.0, step = 0.01",
             "stWhMinLot = input.float(0.0, \"Minimum lot your broker accepts  (0 = no check)\", minval = 0.0, step = 0.01"):
    s = rep(s, name, name[:-4] + "0.00000001")

# ---- symbol and tag without spaces (and without quotes)
s = rep(s, "var string stSymSend = str.replace_all(stWhSym != \"\" ? stWhSym : syminfo.ticker, '\"', \"\")",
        "// v8.4: spaces are taken out too - \"GOLD \" or \" XAUUSD\" typed with a space was refused by the broker\n"
        "var string stSymSend = str.replace_all(str.replace_all(stWhSym != \"\" ? stWhSym : syminfo.ticker, '\"', \"\"), \" \", \"\")\n"
        "var string stTagTx   = str.replace_all(str.replace_all(stTcTag, '\"', \"\"), \" \", \"\")")
s = rep(s, """    string _t = stTcTag
    if stTcTag != "" and str.length(tid) > 1""", """    string _t = stTagTx
    if stTagTx != "" and str.length(tid) > 1""")
s = rep(s, """        _t := (str.length(stTcTag) > _room ? str.substring(stTcTag, 0, _room) : stTcTag) + "-" + _n""",
        """        _t := (str.length(stTagTx) > _room ? str.substring(stTagTx, 0, _room) : stTagTx) + "-" + _n""")
s = rep(s, """            string _tg = stTcTag != "" ? ',"tag":"' + f_stTag(tid) + '"' : \"\"""",
        """            string _tg = stTagTx != "" ? ',"tag":"' + f_stTag(tid) + '"' : \"\"""")

# ---- the new setting, after the last one
TIP = ("BOTH (default): every signal is traded, exactly as before.\\n\\n"
       "LONGS ONLY: only buy signals open trades. A sell signal opens nothing (its audit label says SKIP - longs only).\\n"
       "SHORTS ONLY: only sell signals open trades.\\n\\n"
       "A sell signal still does everything else it did before: it cancels a waiting buy order, and with 'close and reverse' ON (group 20) it closes your open buys. "
       "Switch 'close and reverse' OFF if your buys must keep running until their own stop or target.\\n\\n"
       "HEDGE WITH TWO COPIES: a Pine strategy holds ONE net position, so one copy can never hold a buy and a sell together. "
       "Add the strategy to the chart twice: copy 1 LONGS ONLY, copy 2 SHORTS ONLY, 'close and reverse' OFF in both, a DIFFERENT TheConnector tag in each (group 30), "
       "and one alert per copy to the same webhook. Your broker account must be a HEDGING account (MT5: not netting). "
       "Each copy has its own report, daily limits, loss recovery and profit target.")
s = rep(s, """stMvBeOn   = input.bool(false, "Break-even only - once a candle CLOSES beyond 1R", group = gMv, tooltip = """,
        """stMvBeOn   = input.bool(false, "Break-even only - once a candle CLOSES beyond 1R", group = gMv, tooltip = """)
lines = s.split("\n")
ix = [i for i, l in enumerate(lines) if l.startswith("stMvBeOn   = input.bool(")]
assert len(ix) == 1
lines.insert(ix[0] + 1, "")
lines.insert(ix[0] + 2, "// v8.4 - appended after the last setting, so every setting saved on your chart keeps its place")
lines.insert(ix[0] + 3, 'gDr = "33. Trade direction"')
lines.insert(ix[0] + 4, 'stDirMode = input.string("Both", "Trade direction", options = ["Both", "Longs only", "Shorts only"], group = gDr, tooltip = "' + TIP + '")')
s = "\n".join(lines)

# ---- counter
s = rep(s, "var int    stCntRef = 0\n", "var int    stCntRef = 0\n// v8.4: signals not traded because of the trade direction (group 33)\nvar int    stCntDir = 0\n")

# ---- the signal block
s = rep(s, """    bool _take = stWin and (strategy.position_size == 0 or (stOpp and stRev) or _addB)
    if _take
""", """    bool _take = stWin and (strategy.position_size == 0 or (stOpp and stRev) or _addB)
    // v8.4: trade direction (group 33) - a signal the other way opens nothing
    bool _dirNo = stDirMode != "Both" and (stSigUp ? stDirMode == "Shorts only" : stDirMode == "Longs only")
    if _dirNo
        stCntDir += 1
    if _take and not _dirNo
""")
s = rep(s, """        _audS := "SKIP - " + (not stWin ? "outside session hours" : stOpp""",
        """        _audS := "SKIP - " + (_dirNo ? (stDirMode == "Longs only" ? "longs only" : "shorts only") : not stWin ? "outside session hours" : stOpp""")

# ---- table row
s = rep(s, "stTbl := table.new(f_stPos(stStatPos), 2, 40,", "stTbl := table.new(f_stPos(stStatPos), 2, 41,")
last = """    f_stCell(stTbl, 39, "BLOCKED NOW","""
i = s.index(last)
j = s.index("\n", i)
s = s[:j + 1] + """    f_stCell(stTbl, 40, "Trade direction (group 33)", stDirMode == "Both" ? "both" : (stDirMode + "  -  " + str.tostring(stCntDir) + " signals the other way not traded"), stDirMode == "Both" ? color.gray : color.aqua)
""" + s[j + 1:]
assert s.endswith("\n")
open(R + "SMC_Structure_Strategy_v8.4.txt", "w").write(s)

# ---- presets for the hedge: LONG and SHORT copies
for side, dm, tag in (("LONG", "Longs only", "smcL"), ("SHORT", "Shorts only", "smcS")):
    t = s
    t = rep(t, 'strategy("SMC Structure Strategy", "SMC STRAT", overlay = true,',
            'strategy("SMC Structure Strategy %s", "SMC %s", overlay = true,' % (side, side))
    l2 = t.split("\n")[1]
    t = rep(t, l2, l2.replace("// SMC Structure Strategy  -  v8.4  -  ",
                              "// SMC Structure Strategy %s  -  v8.4 %s preset (hedge copy: %s, close and reverse OFF, tag %s)  -  " % (side, side, dm.lower(), tag), 1))
    t = rep(t, 'stDirMode = input.string("Both", "Trade direction"', 'stDirMode = input.string("%s", "Trade direction"' % dm)
    t = rep(t, 'stRev    = input.bool(true, "Opposite signal while in a trade: close and reverse"',
            'stRev    = input.bool(false, "Opposite signal while in a trade: close and reverse"')
    t = rep(t, 'stTcTag  = input.string("smcgold", "TheConnector tag  (blank = none)"',
            'stTcTag  = input.string("%s", "TheConnector tag  (blank = none)"' % tag)
    open(R + "SMC_Structure_Strategy_v8.4_%s.txt" % side, "w").write(t)
print("ok")
