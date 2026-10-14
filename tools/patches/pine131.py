# TradingView v13.1 = v13.0 + the new setup filters at the END of section 4 (all OFF by default) - the same rules as the
# MT5 EA v13.1: minimum stop as % of the price (any unit), skip the first setup of the day, yesterday's high / low, the
# CHOCH / BOS move must take at least N candles, only with today's move, an RSI filter and an EMA filter for a LOWER and for
# a HIGHER timeframe (each: timeframe, length(s), rule).
# usage: python3 pine131.py SMC_Structure_Strategy_v13.0.txt SMC_Structure_Strategy_v13.1.txt
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


# ---- line 2 (version) and the settings banner
rep('// SMC Structure Strategy  -  v13.0  -  main-tier', '// SMC Structure Strategy  -  v13.1  -  main-tier')
rep('v12.2: Rule A / B / C split - the base risk grows in steps with the profit  -  ASCII only',
    'v12.2: Rule A / B / C split - the base risk grows in steps with the profit, v13.0: 13 sections, v13.1: new setup filters (min stop % of price, first setup of the day, yesterday\'s high / low, candles of the CHOCH / BOS move, today\'s move, RSI and EMA filters for a lower and a higher timeframe)  -  ASCII only')
rep('// ==== SETTINGS (v13.0) - 13 sections, the same order as the MT5 EA v13.0.', '// ==== SETTINGS (v13.1) - 13 sections, the same order as the MT5 EA v13.1.')

TFO = '["1 minute", "5 minutes", "15 minutes", "1 hour", "4 hours", "1 day", "1 week", "1 month"]'
RSO = '["Pullback: buy when RSI is BELOW the level, sell when ABOVE 100 minus it", "Momentum: buy when RSI is ABOVE the level, sell when BELOW 100 minus it"]'
EMO = '["Price above the EMA for buys, below it for sells", "Fast EMA above the slow EMA for buys, below it for sells"]'
TT_TF = ("The candles this filter reads: 1, 5 or 15 minutes, 1 or 4 hours, 1 day, 1 week or 1 month. A timeframe ABOVE the chart "
         "reads its last CLOSED candle (the one before the candle that holds the signal), so the backtest and live trading agree. "
         "A timeframe that is NOT above the chart (1 minute on a 1-minute or a 15-minute chart) uses the chart's own candles, including "
         "the signal candle.")
TT_RSL = ("OFF (default): nothing changes.\\n\\nON: a setup is taken only when the RSI agrees. PULLBACK rule, level 50: a buy needs RSI BELOW 50 "
          "(the price has just dipped), a sell needs RSI ABOVE 50. Level 30 = a buy only below 30, a sell only above 70. MOMENTUM rule, level 55: "
          "a buy needs RSI ABOVE 55, a sell BELOW 45.\\n\\nNote: on the chart's own timeframe a CHOCH up candle usually has RSI above 50, so the "
          "pullback rule there blocks most signals - use it on a higher timeframe, or use the momentum rule.\\n\\nThis one is meant for a LOWER "
          "timeframe (1, 5 or 15 minutes); the next one for a HIGHER timeframe (1 hour, 4 hours, 1 day, 1 week, 1 month). Both can be on together.")
TT_RSH = ("OFF (default): nothing changes.\\n\\nON: like the lower-timeframe RSI filter above, on a HIGHER timeframe. Tested setting: 1 hour, "
          "RSI length 2, pullback, level 50 - a buy only when the last closed 1-hour candle has RSI(2) below 50, a sell only above 50. "
          "Together with C6 (section 9 entries 13:00-21:00, yesterday's high / low, CHOCH move 12 candles, min stop 0.35% of price, 1R) it "
          "made +2,001 instead of +1,035 in 2021 - Oct 2026 at 50 risk (FxPro gold, real costs). That is a past result, not a promise.")
TT_EML = ("OFF (default): nothing changes.\\n\\nON: a setup is taken only when the EMA agrees. PRICE rule: a buy needs the signal candle's close "
          "ABOVE the EMA, a sell BELOW it (EMA 200 = the classic trend line; 9 / 20 = short term; 50 / 100 = medium). 2-EMA rule: a buy needs "
          "the FAST EMA above the SLOW one (for example 9 above 20, or 50 above 200), a sell below it.\\n\\nThis one is meant for a LOWER "
          "timeframe (1, 5 or 15 minutes); the next one for a HIGHER timeframe (1 hour, 4 hours, 1 day, 1 week, 1 month). Both can be on together.")
TT_EMH = ("OFF (default): nothing changes.\\n\\nON: like the lower-timeframe EMA filter above, on a HIGHER timeframe - for example 1 hour, EMA 200: "
          "buys only while the price is above the 1-hour EMA 200, sells only below it.\\n\\nTested on your settings (1-minute chart, 2021 - Oct "
          "2026): it cut the loss of your plain settings but did NOT help the C5 / C6 filter sets. Test it before you trade it.")
rep('stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg"',
    'stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg"', 1)
a = s.index('stEqPct = input.float(50.0, "  - the equilibrium, % pullback of the higher timeframe leg"')
e = s.index('\n', a) + 1
NEW = ('stMnPct  = input.float(0.0, "Skip the setup if the stop is closer than this % of the price (any unit; 0 = off)", minval = 0.0, maxval = 10.0, step = 0.05, group = gx04, '
       'tooltip = "0 (default) = off.\\n\\nA second minimum stop, always in % of the entry price, whatever unit section 1 uses - so your stop buffer can stay in price. '
       'Example 0.5: at gold 4,000 the stop must be at least 20.00 away; at 2,000 at least 10.00. A closer stop is skipped.\\n\\nTested (FxPro gold 2021 - Oct 2026, '
       'your settings, real costs): 0.5 alone took the result from -6,731 to about 0, and it cut the trades by two thirds.")\n'
       'stFstOn  = input.bool(false, "Skip the first setup of the day", group = gx04, tooltip = "OFF (default): nothing changes.\\n\\nON: the first setup of each day that would '
       'really be taken is skipped; the next ones are taken. The day is the calendar day of the session timezone (section 9). Example: setups at 07:10, 09:30 and 14:00 '
       '-> 07:10 is skipped, 09:30 and 14:00 are taken. A setup that another filter skips does not count as the first.\\n\\nIn the tests the first trade of the day '
       'was the worst one. Part of the C5 set. Use it on the 1, 5 and 15-minute charts - on a 1-hour or bigger chart there is rarely more than one setup a day, so it would skip almost all of them.")\n'
       'stYdOn   = input.bool(false, "No buy below yesterday\'s low, no sell above yesterday\'s high", group = gx04, tooltip = "OFF (default): nothing changes.\\n\\nON: a buy '
       'is skipped when the signal candle closes BELOW yesterday\'s low, a sell when it closes ABOVE yesterday\'s high - the price already broke out of yesterday\'s '
       'range the other way. Yesterday = the gold trading day that ended at 17:00 New York (02:30 IST in US summer time, 03:30 IST in winter). Example: yesterday '
       '4,080 - 4,120: a buy at 4,070 is skipped, a buy at 4,095 is taken.\\n\\nAlone it took your result from -6,731 to -1,777. Part of C5 and C6.")\n'
       'stLegMin = input.int(0, "Skip a CHOCH / BOS whose move took fewer than this many candles (0 = off)", minval = 0, maxval = 10000, group = gx04, '
       'tooltip = "0 (default) = off.\\n\\nCounts the candles from the swing point that becomes your stop level (the low for a buy, the high for a sell) to the '
       'candle that broke the structure. A faster move - a spike, often news - is skipped. Example 12 on the 1-minute chart: swing low at 10:00, break at 10:05 = 5 '
       'candles -> skipped; break at 10:20 -> taken.\\n\\n12 is the tested value (part of C5 and C6).")\n'
       'stTdOn   = input.bool(false, "Trade only with today\'s move (buy above today\'s open, sell below it)", group = gx04, tooltip = "OFF (default): nothing changes.\\n\\nON: '
       'a buy only when the signal candle closes ABOVE today\'s open by at least the part below of the average daily range (high - low of the last 14 complete days); '
       'a sell only BELOW it. Today starts at 17:00 New York, like yesterday above. Example 0.15: today\'s open 4,000, average day 40 -> buys only above 4,006, sells '
       'only below 3,994.\\n\\nNeeds 14 complete days of history first (until then it lets setups through).")\n'
       'stTdAtr  = input.float(0.15, "  - by at least this many x the average daily range of the last 14 days (0 = just past the open)", minval = 0.0, maxval = 5.0, step = 0.05, group = gx04)\n'
       'stRsLOn  = input.bool(false, "RSI filter - LOWER timeframe", group = gx04, tooltip = "' + TT_RSL + '")\n'
       'stRsLTf  = input.string("1 minute", "  - timeframe", options = ' + TFO + ', group = gx04, tooltip = "' + TT_TF + '")\n'
       'stRsLLen = input.int(14, "  - RSI length", minval = 1, maxval = 100, group = gx04)\n'
       'stRsLMode = input.string("Pullback: buy when RSI is BELOW the level, sell when ABOVE 100 minus it", "  - rule", options = ' + RSO + ', group = gx04)\n'
       'stRsLLvl = input.float(50.0, "  - level (the buy side; the sell side uses 100 minus it)", minval = 0.0, maxval = 100.0, step = 1.0, group = gx04)\n'
       'stRsHOn  = input.bool(false, "RSI filter - HIGHER timeframe", group = gx04, tooltip = "' + TT_RSH + '")\n'
       'stRsHTf  = input.string("1 hour", "  - timeframe", options = ' + TFO + ', group = gx04, tooltip = "' + TT_TF + '")\n'
       'stRsHLen = input.int(2, "  - RSI length", minval = 1, maxval = 100, group = gx04)\n'
       'stRsHMode = input.string("Pullback: buy when RSI is BELOW the level, sell when ABOVE 100 minus it", "  - rule", options = ' + RSO + ', group = gx04)\n'
       'stRsHLvl = input.float(50.0, "  - level (the buy side; the sell side uses 100 minus it)", minval = 0.0, maxval = 100.0, step = 1.0, group = gx04)\n'
       'stEmLOn  = input.bool(false, "EMA filter - LOWER timeframe", group = gx04, tooltip = "' + TT_EML + '")\n'
       'stEmLTf  = input.string("1 minute", "  - timeframe", options = ' + TFO + ', group = gx04, tooltip = "' + TT_TF + '")\n'
       'stEmLMode = input.string("Price above the EMA for buys, below it for sells", "  - rule", options = ' + EMO + ', group = gx04)\n'
       'stEmLLen = input.int(200, "  - EMA length (the SLOW one for the 2-EMA rule), e.g. 9, 20, 50, 100, 200", minval = 1, maxval = 500, group = gx04)\n'
       'stEmLFast = input.int(50, "  - FAST EMA length (2-EMA rule only)", minval = 1, maxval = 500, group = gx04)\n'
       'stEmHOn  = input.bool(false, "EMA filter - HIGHER timeframe", group = gx04, tooltip = "' + TT_EMH + '")\n'
       'stEmHTf  = input.string("1 hour", "  - timeframe", options = ' + TFO + ', group = gx04, tooltip = "' + TT_TF + '")\n'
       'stEmHMode = input.string("Price above the EMA for buys, below it for sells", "  - rule", options = ' + EMO + ', group = gx04)\n'
       'stEmHLen = input.int(200, "  - EMA length (the SLOW one for the 2-EMA rule), e.g. 9, 20, 50, 100, 200", minval = 1, maxval = 500, group = gx04)\n'
       'stEmHFast = input.int(50, "  - FAST EMA length (2-EMA rule only)", minval = 1, maxval = 500, group = gx04)\n')
s = s[:e] + NEW + s[e:]

# ---- the trading day + the RSI / EMA values (global, every bar) - before the signal block
rep('bool stUseCho = not str.startswith(stSigSrc, "BOS only")\n', r'''// ---- v13.1 (section 4): the New York trading day and the RSI / EMA filters - the same rules as the MT5 EA v13.1
// The day of a bar = the New York trading day of its OPEN: a new day starts at 17:00 New York (the gold daily close).
// Today's open / high / low, yesterday's high / low, the average range (high - low) of the last 14 complete days.
int _nyMs   = timestamp("UTC", year(time, _nyTz), month(time, _nyTz), dayofmonth(time, _nyTz), hour(time, _nyTz), minute(time, _nyTz), second(time, _nyTz))
int stDyKey = int(math.floor((_nyMs - 61200000) / 86400000.0))
var int   stDyPrev = na
var float stDyO = na
var float stDyH = na
var float stDyL = na
var float stYdH = na
var float stYdL = na
var float stDyAvg = 0.0
var array<float> stDyRng = array.new<float>()
if na(stDyPrev) or stDyKey != stDyPrev
    if not na(stDyPrev)
        stYdH := stDyH
        stYdL := stDyL
        array.push(stDyRng, stDyH - stDyL)
        if array.size(stDyRng) > 14
            array.shift(stDyRng)
        if array.size(stDyRng) == 14
            float _dSum = 0.0
            for _dv in stDyRng
                _dSum += _dv
            stDyAvg := _dSum / 14.0
    stDyPrev := stDyKey
    stDyO := open
    stDyH := high
    stDyL := low
else
    stDyH := math.max(stDyH, high)
    stDyL := math.min(stDyL, low)
// the timeframe of an RSI / EMA filter; a timeframe not above the chart = the chart's own candles
f_xTf(string s) =>
    s == "5 minutes" ? "5" : s == "15 minutes" ? "15" : s == "1 hour" ? "60" : s == "4 hours" ? "240" : s == "1 day" ? "D" : s == "1 week" ? "W" : s == "1 month" ? "M" : "1"
f_xUp(string tf) =>
    timeframe.in_seconds(tf) > timeframe.in_seconds(timeframe.period)
f_xTfTxt(string tf) =>
    not f_xUp(tf) ? "chart" : tf == "D" ? "1D" : tf == "W" ? "1W" : tf == "M" ? "1M" : tf == "60" ? "1h" : tf == "240" ? "4h" : tf + "m"
f_xRsOk(int d, float v, string md, float lv) =>
    str.startswith(md, "Pullback") ? (d == 1 ? v < lv : v > 100 - lv) : (d == 1 ? v > lv : v < 100 - lv)
string stRsLTfS = f_xTf(stRsLTf)
string stRsHTfS = f_xTf(stRsHTf)
string stEmLTfS = f_xTf(stEmLTf)
string stEmHTfS = f_xTf(stEmHTf)
bool _rsLUp = stRsLOn and f_xUp(stRsLTfS)
bool _rsHUp = stRsHOn and f_xUp(stRsHTfS)
bool _emLUp = stEmLOn and f_xUp(stEmLTfS)
bool _emHUp = stEmHOn and f_xUp(stEmHTfS)
// on the chart's own candles (computed on every bar), or the last CLOSED candle of the higher timeframe
float _rsLc = ta.rsi(close, stRsLLen)
float _rsHc = ta.rsi(close, stRsHLen)
float _emLsc = ta.ema(close, stEmLLen)
float _emLfc = ta.ema(close, stEmLFast)
float _emHsc = ta.ema(close, stEmHLen)
float _emHfc = ta.ema(close, stEmHFast)
float _rsLu = request.security(syminfo.tickerid, _rsLUp ? stRsLTfS : timeframe.period, ta.rsi(close, stRsLLen)[1], lookahead = barmerge.lookahead_on)
float _rsHu = request.security(syminfo.tickerid, _rsHUp ? stRsHTfS : timeframe.period, ta.rsi(close, stRsHLen)[1], lookahead = barmerge.lookahead_on)
float _emLsu = request.security(syminfo.tickerid, _emLUp ? stEmLTfS : timeframe.period, ta.ema(close, stEmLLen)[1], lookahead = barmerge.lookahead_on)
float _emLfu = request.security(syminfo.tickerid, _emLUp ? stEmLTfS : timeframe.period, ta.ema(close, stEmLFast)[1], lookahead = barmerge.lookahead_on)
float _emHsu = request.security(syminfo.tickerid, _emHUp ? stEmHTfS : timeframe.period, ta.ema(close, stEmHLen)[1], lookahead = barmerge.lookahead_on)
float _emHfu = request.security(syminfo.tickerid, _emHUp ? stEmHTfS : timeframe.period, ta.ema(close, stEmHFast)[1], lookahead = barmerge.lookahead_on)
float stRsLv = _rsLUp ? _rsLu : _rsLc
float stRsHv = _rsHUp ? _rsHu : _rsHc
float stEmLs = _emLUp ? _emLsu : _emLsc
float stEmHs = _emHUp ? _emHsu : _emHsc
// the 'fast' side of the EMA rule: the fast EMA (2-EMA rule) or the signal candle's close (price rule)
bool  _emL2 = str.startswith(stEmLMode, "Fast")
bool  _emH2 = str.startswith(stEmHMode, "Fast")
float stEmLf = _emL2 ? (_emLUp ? _emLfu : _emLfc) : close
float stEmHf = _emH2 ? (_emHUp ? _emHfu : _emHfc) : close
var int stFstDay = na
var int stCntX0 = 0
var int stCntX1 = 0
var int stCntX2 = 0
var int stCntX3 = 0
var int stCntX4 = 0
var int stCntX5 = 0
var int stCntX6 = 0
var int stCntX7 = 0
var int stCntX8 = 0
int _xDay = int(timestamp("UTC", year(time_close, stTz), month(time_close, stTz), dayofmonth(time_close, stTz), 0, 0) / 86400000)

bool stUseCho = not str.startswith(stSigSrc, "BOS only")
''')

# ---- the checks, right before a setup is armed (after the audit text of the older rules)
rep('''        if _use and not na(_opl)
            if stDir != 0
                stCntCanc += 1
                f_audEnd("CANCELLED - new signal", stAudCancC)
''', '''        // v13.1 (section 4): the new setup filters; the first setup of the day is checked LAST, so a setup that another
        // filter skips is never the day's first
        string _xs = ""
        if _use and not na(_opl)
            int _lb = _d == 1 ? bar_index - florS.x1 : bar_index - ceilS.x1
            if stTdOn and stDyAvg > 0 and not na(stDyO) and _d * (close - stDyO) < stTdAtr * stDyAvg
                _xs := "against today's move (open " + str.tostring(stDyO, format.mintick) + ", needs " + str.tostring(stTdAtr * stDyAvg, format.mintick) + (_d == 1 ? " above it)" : " below it)")
                stCntX3 += 1
            else if stYdOn and not na(stYdH) and (_d == 1 ? close < stYdL : close > stYdH)
                _xs := _d == 1 ? "below yesterday's low " + str.tostring(stYdL, format.mintick) : "above yesterday's high " + str.tostring(stYdH, format.mintick)
                stCntX1 += 1
            else if stLegMin > 0 and _lb < stLegMin
                _xs := "the move took " + str.tostring(_lb) + " candles (at least " + str.tostring(stLegMin) + ")"
                stCntX2 += 1
            else if stRsLOn and not na(stRsLv) and not f_xRsOk(_d, stRsLv, stRsLMode, stRsLLvl)
                _xs := "RSI(" + str.tostring(stRsLLen) + ") " + f_xTfTxt(stRsLTfS) + " = " + str.tostring(stRsLv, "#.#") + ", a " + (_d == 1 ? "buy" : "sell") + " needs " + (str.startswith(stRsLMode, "Pullback") == (_d == 1) ? "below " : "above ") + str.tostring(_d == 1 ? stRsLLvl : 100 - stRsLLvl, "#.#")
                stCntX4 += 1
            else if stRsHOn and not na(stRsHv) and not f_xRsOk(_d, stRsHv, stRsHMode, stRsHLvl)
                _xs := "RSI(" + str.tostring(stRsHLen) + ") " + f_xTfTxt(stRsHTfS) + " = " + str.tostring(stRsHv, "#.#") + ", a " + (_d == 1 ? "buy" : "sell") + " needs " + (str.startswith(stRsHMode, "Pullback") == (_d == 1) ? "below " : "above ") + str.tostring(_d == 1 ? stRsHLvl : 100 - stRsHLvl, "#.#")
                stCntX5 += 1
            else if stEmLOn and not na(stEmLs) and not na(stEmLf) and not (_d == 1 ? stEmLf > stEmLs : stEmLf < stEmLs)
                _xs := (_emL2 ? "EMA " + str.tostring(stEmLFast) : "price " + str.tostring(close, format.mintick)) + (_d == 1 ? " not above" : " not below") + " the EMA " + str.tostring(stEmLLen) + " " + f_xTfTxt(stEmLTfS) + " (" + str.tostring(stEmLs, format.mintick) + ")"
                stCntX6 += 1
            else if stEmHOn and not na(stEmHs) and not na(stEmHf) and not (_d == 1 ? stEmHf > stEmHs : stEmHf < stEmHs)
                _xs := (_emH2 ? "EMA " + str.tostring(stEmHFast) : "price " + str.tostring(close, format.mintick)) + (_d == 1 ? " not above" : " not below") + " the EMA " + str.tostring(stEmHLen) + " " + f_xTfTxt(stEmHTfS) + " (" + str.tostring(stEmHs, format.mintick) + ")"
                stCntX7 += 1
            else if stFstOn and (na(stFstDay) or stFstDay != _xDay)
                stFstDay := _xDay
                _xs := "first setup of the day"
                stCntX0 += 1
        if _xs != ""
            _use := false
            _audS := "SKIP - " + _xs
        if _use and not na(_opl)
            if stDir != 0
                stCntCanc += 1
                f_audEnd("CANCELLED - new signal", stAudCancC)
''')

# ---- the minimum stop as % of the entry price, at the placement
rep('''    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk
''', '''    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk
    // v13.1 (section 4): the stop at least this % of the entry price, whatever the unit of section 1
    bool _mpOk = stMnPct <= 0 or _r >= stEnt * stMnPct / 100.0
''')
rep('    bool _place = _sane and _dOk and _pdOk and _q /', '    bool _place = _sane and _dOk and _mpOk and _pdOk and _q /')
rep('    else if not _sane or not _dOk or not _pdOk or _q /', '    else if not _sane or not _dOk or not _mpOk or not _pdOk or _q /')
rep('''not _lotOk ? "CANCELLED - below the minimum lot" : not _dOk ? "CANCELLED - stop too close / too far" : "CANCELLED - size is zero", stAudCancC)''',
    '''not _lotOk ? "CANCELLED - below the minimum lot" : not _mpOk ? "CANCELLED - stop closer than " + str.tostring(stMnPct) + "% of the price" : not _dOk ? "CANCELLED - stop too close / too far" : "CANCELLED - size is zero", stAudCancC)''')
rep('''        if not _dOk
            stCntSkip += 1
        if not _pdOk
            stCntPd += 1
''', '''        if not _dOk or not _mpOk
            stCntSkip += 1
        if not _mpOk
            stCntX8 += 1
        if not _pdOk
            stCntPd += 1
''')

# ---- table: two more rows
rep('stTbl := table.new(f_stPos(stStatPos), 2, 52,', 'stTbl := table.new(f_stPos(stStatPos), 2, 54,')
rep('table.cell(stTbl, 0, 0, "STRATEGY v13.0",', 'table.cell(stTbl, 0, 0, "STRATEGY v13.1",')
rep('''    f_stCell(stTbl, 51, "PROFIT STEPS - A / B / C split (section 7)", _spT, stSplitM ? color.aqua : color.gray)
''', '''    f_stCell(stTbl, 51, "PROFIT STEPS - A / B / C split (section 7)", _spT, stSplitM ? color.aqua : color.gray)
    // v13.1: the new section 4 filters - how many setups each one skipped, and what they read now
    string _xT = (stFstOn ? ", first of the day " + str.tostring(stCntX0) : "") + (stYdOn ? ", yesterday's high / low " + str.tostring(stCntX1) : "") + (stLegMin > 0 ? ", move < " + str.tostring(stLegMin) + " candles " + str.tostring(stCntX2) : "") + (stTdOn ? ", today's move " + str.tostring(stCntX3) : "") + (stRsLOn ? ", RSI " + f_xTfTxt(stRsLTfS) + " " + str.tostring(stCntX4) : "") + (stRsHOn ? ", RSI " + f_xTfTxt(stRsHTfS) + " " + str.tostring(stCntX5) : "") + (stEmLOn ? ", EMA " + f_xTfTxt(stEmLTfS) + " " + str.tostring(stCntX6) : "") + (stEmHOn ? ", EMA " + f_xTfTxt(stEmHTfS) + " " + str.tostring(stCntX7) : "") + (stMnPct > 0 ? ", stop < " + str.tostring(stMnPct) + "% " + str.tostring(stCntX8) : "")
    f_stCell(stTbl, 52, "  - skipped: section 4 filters (v13.1)", _xT == "" ? "off" : str.substring(_xT, 2), _xT == "" ? color.gray : color.orange)
    string _xN = (stYdOn ? "  |  yesterday " + (na(stYdH) ? "-" : str.tostring(stYdL, format.mintick) + " - " + str.tostring(stYdH, format.mintick)) : "") + (stTdOn ? "  |  today's open " + (na(stDyO) ? "-" : str.tostring(stDyO, format.mintick)) + ", average day " + (stDyAvg > 0 ? str.tostring(stDyAvg, format.mintick) : "not ready") : "") + (stRsLOn ? "  |  RSI(" + str.tostring(stRsLLen) + ") " + f_xTfTxt(stRsLTfS) + " " + (na(stRsLv) ? "-" : str.tostring(stRsLv, "#.#")) : "") + (stRsHOn ? "  |  RSI(" + str.tostring(stRsHLen) + ") " + f_xTfTxt(stRsHTfS) + " " + (na(stRsHv) ? "-" : str.tostring(stRsHv, "#.#")) : "") + (stEmLOn ? "  |  EMA " + (_emL2 ? str.tostring(stEmLFast) + " / " : "") + str.tostring(stEmLLen) + " " + f_xTfTxt(stEmLTfS) + " " + (na(stEmLs) ? "-" : (_emL2 ? str.tostring(stEmLf, format.mintick) + " / " : "") + str.tostring(stEmLs, format.mintick)) : "") + (stEmHOn ? "  |  EMA " + (_emH2 ? str.tostring(stEmHFast) + " / " : "") + str.tostring(stEmHLen) + " " + f_xTfTxt(stEmHTfS) + " " + (na(stEmHs) ? "-" : (_emH2 ? str.tostring(stEmHf, format.mintick) + " / " : "") + str.tostring(stEmHs, format.mintick)) : "")
    f_stCell(stTbl, 53, "  - section 4 filters now", _xN == "" ? "off" : str.substring(_xN, 5), _xN == "" ? color.gray : color.aqua)
''')

# ---- v13.1 fix (14 Oct 2026): TradingView refused v13.1 with CE10295 "The main body of the script is too long. Try
# wrapping code in functions". Three display-only blocks move into functions - nothing that trades changes:
# (A) the statistics table, (B) the last-candle structure / equilibrium lines, (C) the structure alert queue.
s = s.replace('main-tier CHOCH/BOS,', 'main-tier CHOCH/BOS (v13.1 fix: table, last-candle lines and alert queue drawn in functions),', 1)
FX = '// v13.1 fix: drawn inside a function - TradingView limits the size of the main body of a script (CE10295)\n'
# (A) the table: the table is still made in the old block, its 54 rows are written by 4 functions f_stTab1..4 (one
# function for all rows used 357 'external elements' - TradingView allows 254 per function: every global value a function
# reads counts, int / float / bool twice). Each part keeps its own local values; the table is passed in as _t.
ha = 'var table stTbl = na\nif stStatOn and bar_index == last_bar_index\n'
i = s.index(ha); body = s[i + len(ha):]
assert body.startswith('    if na(stTbl)\n        stTbl := table.new(') and s.endswith('\n')
bl = body.rstrip('\n').split('\n'); mk = bl[:2]; rest = bl[2:]
cuts = [next(k for k, l in enumerate(rest) if l.startswith(c)) for c in
        ('    f_stCell(stTbl, 18,', '    int ny0 = year(timenow', '    // v10.4: the account floor')]
parts = [rest[a:b] for a, b in zip([0] + cuts, cuts + [len(rest)])]
assert sum(len(x) for x in parts) == len(rest) and all(x[0].startswith('    ') and not x[0].startswith('     ') for x in parts)
fn = ''
for n, pt in enumerate(parts, 1):
    fn += FX + 'f_stTab%d(table _t) =>\n' % n + re.sub(r'\bstTbl\b', '_t', '\n'.join(pt)) + '\n    true\n\n'
s = s[:i] + fn + ha + '\n'.join(mk) + '\n' + ''.join('    f_stTab%d(stTbl)\n' % n for n in range(1, len(parts) + 1))
# (B) the last-candle lines: the block's work goes into f_lastDraw(); the 14 lines / labels it keeps come back as a tuple
hb = 'if bar_index == last_bar_index\n    [_icLc, _icTc,'
i = s.index(hb); j = s.index('\nint _capMain', i)
blk = s[i:j].rstrip('\n').split('\n')[1:]
keep, back = [], []
for l in blk:
    m = re.match(r'^    (ipCeilLn|ipCeilLb|ipFlorLn|ipFlorLb|npCeilLn|npCeilLb|npFlorLn|npFlorLb|eqMLn|eqMLb|eqILn|eqILb|eqNLn|eqNLb) := (_\w+)$', l)
    if m: back.append((m.group(1), m.group(2)))
    else: keep.append(l)
assert len(back) == 14
tup = '[' + ', '.join(b for a, b in back) + ']'
s = s[:i] + FX + 'f_lastDraw() =>\n' + '\n'.join(keep) + '\n    ' + tup + '\n\n' + 'if bar_index == last_bar_index\n    ' + tup + ' = f_lastDraw()\n' + \
    ''.join('    %s := %s\n' % (a, b) for a, b in back) + s[j:]
# (C) the structure alert queue: both 'if almOk and ...' blocks go into f_almQueue(), called once on every bar
hc = 'if almOk and (evBosUp or evBosDn or evChoUp or evChoDn'
i = s.index(hc); j = s.index('\nf_armTag(', i)
blk = s[i:j].rstrip('\n')
assert blk.count('\nif almOk and ((rtMainRet and aMainRet)') == 1
s = s[:i] + FX + 'f_almQueue() =>\n' + '\n'.join(('    ' + l) if l.strip() else l for l in blk.split('\n')) + '\n    true\n\nf_almQueue()\n' + s[j:]

open(dst, 'w').write(s)
print('written', dst)
