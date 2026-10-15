# TradingView v14.0 = v13.1 + (all OFF by default, old behaviour unchanged) - the same rules as the MT5 EA v14.0:
#   section 1: a 4th unit choice 'Separate unit for each setting' - then the stop buffer (section 5), skip closer /
#     further (section 4, one unit for both), the rule 3 distance (section 3) and the spread for sizing (section 11) each
#     have their OWN unit (price / pips / %) and box, at the end of their section; the old boxes are not used then
#   section 4: the LEG SIZE filter - the leg = from the broken level (the pivot the signal candle closed beyond) to the
#     CHOCH* level; skip the setup if it is shorter / longer than (own unit, any section 1 unit)
#   section 4: the BIG SIGNAL CANDLE filter - skip the setup if the CHOCH / BOS candle (high - low) is bigger than (own unit)
# Patched on the FINAL v13.1 file (after its size fixes), so nothing of the old indicator parts comes back.
# usage: python3 pine140.py SMC_Structure_Strategy_v13.1.txt SMC_Structure_Strategy_v14.0.txt
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


def after_line(start, text):
    """insert text after the (one) line that starts with start"""
    global s
    assert s.count('\n' + start) == 1, start
    a = s.index('\n' + start) + 1
    e = s.index('\n', a) + 1
    s = s[:e] + text + s[e:]


UNO = '["Price", "Pips (auto per market)", "% of price"]'
SEPN = "Used ONLY when section 1 is 'Separate unit for each setting' (otherwise the old box above, in the section 1 unit, is used)."

# ---- line 2 (version) and the settings banner
rep('// SMC Structure Strategy  -  v13.1  -  main-tier CHOCH/BOS (v13.1 fix: TradingView size limits - table and last-candle lines in functions, switched-off indicator extras removed),',
    '// SMC Structure Strategy  -  v14.0  -  main-tier CHOCH/BOS (v14.0: own unit for each distance, leg size and big signal candle filters),')
rep("today's move, RSI and EMA filters for a lower and a higher timeframe)  -  ASCII only",
    "today's move, RSI and EMA filters for a lower and a higher timeframe), v14.0: section 1 'Separate unit for each setting' (stop buffer, skip closer / further, rule 3 distance, spread - each its own unit and box), leg size (broken level to the CHOCH* level) and big signal candle filters  -  ASCII only")
rep('''// ==== SETTINGS (v13.1) - 13 sections, the same order as the MT5 EA v13.1. Every price DISTANCE (stop buffer, skip
// closer / further, rule 3 distance, spread for sizing) is read in the unit chosen in section 1: price, pips or % of price.''',
    '''// ==== SETTINGS (v14.0) - 13 sections, the same order as the MT5 EA v14.0. Every price DISTANCE (stop buffer, skip
// closer / further, rule 3 distance, spread for sizing) is read in the unit chosen in section 1: price, pips or % of price.
// v14.0: section 1 'Separate unit for each setting' = each of them has its OWN unit and box instead, at the END of its
// section (skip closer / further share one unit). The leg size and big candle filters (end of section 4) always have
// their own unit.''')

# ---- section 1: the 4th choice
rep('options = ["Price", "Pips (auto per market)", "% of price"], group = gx01, tooltip = "PRICE (default):',
    'options = ["Price", "Pips (auto per market)", "% of price", "Separate unit for each setting"], group = gx01, tooltip = "PRICE (default):')
rep(" When you change the unit, type those numbers again. The table row 'UNIT + STOP BUFFER' shows them in price.\")",
    " When you change the unit, type those numbers again. The table row 'UNIT + STOP BUFFER' shows them in price.\\n\\n"
    "SEPARATE UNIT FOR EACH SETTING (v14.0): each of those four has its OWN unit (price, pips or %) and its OWN box, at the END of its "
    "section: stop buffer (section 5), skip closer / further (section 4 - one unit for both boxes), rule 3 distance (section 3), spread "
    "(section 11). The old boxes are then not used. Example: stop buffer 1.0 in price, skip closer / further 0.2 / 0.5 in % of the entry "
    "(at gold 4,000: 8.00 / 20.00), rule 3 30 pips (3.00 on gold), spread 0.20 in price.\")")

# ---- the new settings: at the END of sections 3, 4, 5, 11
after_line('stExpBars   = input.int(0, "Cancel an unfilled order after N bars',
    'stR3U = input.string("Price", "RULE 3 near the broken level - unit (used when section 1 = Separate unit for each setting)", options = ' + UNO + ', group = gx03, '
    'tooltip = "' + SEPN + '\\n\\nThe unit of the box below: PRICE (3 = 3.00 on gold), PIPS (30 pips = 3.00 on gold) or % OF THE CLOSE '
    '(0.075 = 3.00 at 4,000). It works only with \'RULE 3: only if the close is near the broken level\' ON.")\n'
    'stR3V = input.float(3.0, "  - the most the close may be beyond the broken level", minval = 0.0, step = 0.00000001, group = gx03, '
    'tooltip = "' + SEPN + ' 3 (default).")\n')
after_line('stEmHFast = input.int(50, "  - FAST EMA length (2-EMA rule only)"',
    'stSkU = input.string("Price", "Skip closer / further - unit for both (used when section 1 = Separate unit for each setting)", options = ' + UNO + ', group = gx04, '
    'tooltip = "' + SEPN + '\\n\\nONE unit for the two boxes below: PRICE (8 = 8.00), PIPS (80 pips = 8.00 on gold) or % OF THE ENTRY price '
    '(0.2 = 8.00 at 4,000, 10.00 at 5,000). Both boxes measure the distance from the entry to the stop.")\n'
    'stSkMin = input.float(0.0, "  - skip the setup if the stop is CLOSER than this (0 = off)", minval = 0.0, step = 0.00000001, group = gx04, '
    'tooltip = "' + SEPN + ' Example: unit %, 0.2 -> at gold 4,000 a stop closer than 8.00 is skipped.")\n'
    'stSkMax = input.float(0.0, "  - skip the setup if the stop is FURTHER than this (0 = off)", minval = 0.0, step = 0.00000001, group = gx04, '
    'tooltip = "' + SEPN + ' Example: unit %, 0.5 -> at gold 4,000 a stop further than 20.00 is skipped.")\n'
    'stLzU = input.string("Price", "Leg size (from the broken level to the CHOCH* level) - unit", options = ' + UNO + ', group = gx04, '
    'tooltip = "Works with ANY section 1 unit - it has its own.\\n\\nTHE LEG = from the level the signal candle broke (not its close) to '
    'the CHOCH* level (your stop level). Example, a buy: CHOCH* low 4,000; the candle breaks the high at 4,006 and closes at 4,009 -> the leg is '
    '6.00 (the 3 to the close do not count) = 60 pips on gold = 0.15% of 4,000.\\n\\nUnit: PRICE, PIPS, or % OF THE CHOCH* LEVEL.\\n\\nIt is '
    'checked on its own: the skip closer / further boxes are checked too, so a setup must pass both.")\n'
    'stLzMin = input.float(0.0, "  - skip the setup if the leg is SHORTER than this (0 = off)", minval = 0.0, step = 0.00000001, group = gx04, '
    'tooltip = "0 (default) = off. Example 8 in price: a 6.00 leg is skipped, a 10.00 leg is taken.")\n'
    'stLzMax = input.float(0.0, "  - skip the setup if the leg is LONGER than this (0 = off)", minval = 0.0, step = 0.00000001, group = gx04, '
    'tooltip = "0 (default) = off. Example 30 in price: a 35.00 leg is skipped. When both boxes are used this one must be the bigger.")\n'
    'stBcU = input.string("Price", "Big signal candle - unit", options = ' + UNO + ', group = gx04, '
    'tooltip = "Works with ANY section 1 unit - it has its own.\\n\\nThe size of the candle that makes the CHOCH / BOS = its high - low '
    '(wicks included). Unit: PRICE, PIPS, or % OF ITS CLOSE.")\n'
    'stBcMax = input.float(0.0, "  - skip the setup if the CHOCH / BOS candle (high - low) is BIGGER than this (0 = off)", minval = 0.0, step = 0.00000001, group = gx04, '
    'tooltip = "0 (default) = off.\\n\\nA very big candle that breaks the structure is often news or something unusual - that setup is '
    'skipped, no trade on that leg. Only the signal candle counts; the next CHOCH / BOS is judged again. Example 10 in price: the signal '
    'candle goes from 4,004 to 4,018 = 14.00 -> skipped; a 7.00 candle -> taken.")\n')
after_line('stTrMode = input.string("Behind the CHOCH* level (slower)", "  - the stop follows"',
    'stBfU = input.string("Price", "Stop buffer - unit (used when section 1 = Separate unit for each setting)", options = ' + UNO + ', group = gx05, '
    'tooltip = "' + SEPN + '\\n\\nThe unit of the box below: PRICE (1.0 = 1.00 on gold), PIPS (10 pips = 1.00 on gold) or % OF THE CHOCH* '
    'LEVEL (0.025 = 1.00 at 4,000). Pips and % are rounded to the smallest price step.")\n'
    'stBfV = input.float(0.0, "  - stop buffer beyond the CHOCH* level", minval = 0.0, step = 0.00000001, group = gx05, '
    'tooltip = "' + SEPN + ' In % of price it must be 10 or less.")\n')
after_line('stSprd   = input.float(0.0, "Broker spread for SIZING (unit: section 1; 0 = not modelled)"',
    'stSpdU = input.string("Price", "Spread for sizing - unit (used when section 1 = Separate unit for each setting)", options = ' + UNO + ', group = gx11, '
    'tooltip = "' + SEPN + '\\n\\nThe unit of the box below: PRICE (0.20 = 0.20 on gold), PIPS (2 pips = 0.20 on gold) or % OF THE PRICE '
    '(0.005 = 0.20 at 4,000).")\n'
    'stSpdV = input.float(0.0, "  - broker spread for SIZING (0 = not modelled)", minval = 0.0, step = 0.00000001, group = gx11, '
    'tooltip = "' + SEPN + ' Read the box above (the one in the section 1 unit) for what the spread does. In % of price it must be 10 or less.")\n')

# ---- the units in use
rep('''var bool  stBuPipM  = stBuMode == "Pips (auto per market)"
var bool  stBuPctM  = stBuMode == "% of price"
// v11.2 / v13.0: the stop buffer beyond the level _lv, in price - the ONE stop buffer box (stSlBuf, section 5) read in the
// section 1 unit: pips x pip, or % of the level (both rounded to the price step), or the price as it is
f_stBuf(float _lv) =>
    stBuPipM ? math.round_to_mintick(stSlBuf * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stSlBuf / 100.0) : stSlBuf
// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is
f_stSprd(float _px) =>
    stBuPipM ? stSprd * stPipSz : stBuPctM ? math.max(nz(_px), 0.0) * stSprd / 100.0 : stSprd
// v13.0: a % of price above 10 is a typing mistake (1.0 typed in price, then the unit changed?) - stop with a clear message
if barstate.isfirst and stBuPctM and (stSlBuf > 10 or stSprd > 10)
    runtime.error("Section 1 unit is % of price: the stop buffer (section 5) and the spread (section 11) must be 10 or less")
// v12.0: the rule 3 'near the broken level' distance in price (the unit of section 1: price, pips, or % of the close)
f_stR3Lim(float _v, float _px) =>
    stBuPipM ? _v * stPipSz : stBuPctM ? _px * _v / 100.0 : _v
''', '''var bool  stBuPipM  = stBuMode == "Pips (auto per market)"
var bool  stBuPctM  = stBuMode == "% of price"
// v14.0: section 1 'Separate unit for each setting' - the stop buffer, skip closer / further, the rule 3 distance and the
// spread each use their own unit (0 price, 1 pips, 2 %) and box (end of sections 5, 4, 3, 11); otherwise the section 1
// unit and the old boxes, exactly as before
var bool  stBuSepM  = stBuMode == "Separate unit for each setting"
f_unN(string _u) =>
    _u == "Pips (auto per market)" ? 1 : _u == "% of price" ? 2 : 0
var int   stBuN = stBuPipM ? 1 : stBuPctM ? 2 : 0
var int   stUBf = stBuSepM ? f_unN(stBfU) : stBuN
var int   stUSk = stBuSepM ? f_unN(stSkU) : stBuN
var int   stUR3 = stBuSepM ? f_unN(stR3U) : stBuN
var int   stUSp = stBuSepM ? f_unN(stSpdU) : stBuN
var int   stULz = f_unN(stLzU)
var int   stUBc = f_unN(stBcU)
var float stBfX = stBuSepM ? stBfV : stSlBuf
var float stMnX = stBuSepM ? stSkMin : stMinStop
var float stMxX = stBuSepM ? stSkMax : stMaxStop
var float stR3X = stBuSepM ? stR3V : stR3Brk
var float stSpX = stBuSepM ? stSpdV : stSprd
// v14.0: a distance _v in the unit _u, in price: pips x pip, or % of _ref, or the price as it is
f_unPx(int _u, float _v, float _ref) =>
    _u == 1 ? _v * stPipSz : _u == 2 ? _ref * _v / 100.0 : _v
f_unTxt(int _u) =>
    _u == 1 ? " pips" : _u == 2 ? " %" : ""
// v11.2 / v13.0: the stop buffer beyond the level _lv, in price - the stop buffer box (section 5) read in its unit: pips x
// pip, or % of the level (both rounded to the price step), or the price as it is
f_stBuf(float _lv) =>
    stUBf == 1 ? math.round_to_mintick(stBfX * stPipSz) : stUBf == 2 ? math.round_to_mintick(_lv * stBfX / 100.0) : stBfX
// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is
f_stSprd(float _px) =>
    stUSp == 1 ? stSpX * stPipSz : stUSp == 2 ? math.max(nz(_px), 0.0) * stSpX / 100.0 : stSpX
// v13.0: a % of price above 10 is a typing mistake (1.0 typed in price, then the unit changed?) - stop with a clear message
if barstate.isfirst and ((stUBf == 2 and stBfX > 10) or (stUSp == 2 and stSpX > 10))
    runtime.error("The stop buffer (section 5) and the spread (section 11) in % of price must be 10 or less")
if barstate.isfirst and stLzMin > 0 and stLzMax > 0 and stLzMax < stLzMin
    runtime.error("Leg size (section 4): 'LONGER than' must be bigger than 'SHORTER than'")
// v12.0: the rule 3 'near the broken level' distance in price (its unit: price, pips, or % of the close)
f_stR3Lim(float _v, float _px) =>
    f_unPx(stUR3, _v, _px)
// v14.0 (section 4): the leg from the broken level _piv to the CHOCH* level _opl: 0 = fine (or no broken level), 1 = shorter
// than the minimum, 2 = longer than the maximum
f_xLeg(int _d, float _piv, float _opl) =>
    float _lg = _d * (_piv - _opl)
    na(_piv) ? 0 : stLzMin > 0 and _lg < f_unPx(stULz, stLzMin, _opl) - syminfo.mintick / 2 ? 1 : stLzMax > 0 and _lg > f_unPx(stULz, stLzMax, _opl) + syminfo.mintick / 2 ? 2 : 0
f_xLegTxt(int _d, float _piv, float _opl, int _k) =>
    "leg " + str.tostring(_d * (_piv - _opl), format.mintick) + " (broken level " + str.tostring(_piv, format.mintick) + " to the CHOCH* level " + str.tostring(_opl, format.mintick) + ") " + (_k == 1 ? "shorter than " + str.tostring(f_unPx(stULz, stLzMin, _opl), format.mintick) : "longer than " + str.tostring(f_unPx(stULz, stLzMax, _opl), format.mintick))
''')
rep('    c + (stSprd > 0 ? strategy.convert_to_account(f_stSprd(ent) * f_stPv()) : 0.0)',
    '    c + (stSpX > 0 ? strategy.convert_to_account(f_stSprd(ent) * f_stPv()) : 0.0)')
rep('bool  _r3Far = stR3On and stR3BrkOn and (na(_r3B) or _r3B > f_stR3Lim(stR3Brk, close))',
    'bool  _r3Far = stR3On and stR3BrkOn and (na(_r3B) or _r3B > f_stR3Lim(stR3X, close))')
rep('''    // v11.2: the group 24 limits in the unit of group 38 (pips, or % of the entry price)
    float _mnS = stBuPipM ? stMinStop * stPipSz : stBuPctM ? stEnt * stMinStop / 100.0 : stMinStop
    float _mxS = stBuPipM ? stMaxStop * stPipSz : stBuPctM ? stEnt * stMaxStop / 100.0 : stMaxStop
    bool _dOk = (stMinStop <= 0 or _r >= _mnS) and (stMaxStop <= 0 or _r <= _mxS) and _lotOk''',
    '''    // v11.2 / v14.0: skip closer / further in their unit (price, pips, or % of the entry price)
    float _mnS = f_unPx(stUSk, stMnX, stEnt)
    float _mxS = f_unPx(stUSk, stMxX, stEnt)
    bool _dOk = (stMnX <= 0 or _r >= _mnS) and (stMxX <= 0 or _r <= _mxS) and _lotOk''')

# ---- the filters (before the first setup of the day, which stays the last)
rep('var int stCntX8 = 0\n', 'var int stCntX8 = 0\nvar int stCntX9 = 0\nvar int stCntX10 = 0\nvar int stCntX11 = 0\n')
rep('''            else if stFstOn and (na(stFstDay) or stFstDay != _xDay)''',
    '''            else if f_xLeg(_d, _piv, _opl) > 0
                int _lgK = f_xLeg(_d, _piv, _opl)
                _xs := f_xLegTxt(_d, _piv, _opl, _lgK)
                stCntX9 += _lgK == 1 ? 1 : 0
                stCntX10 += _lgK == 2 ? 1 : 0
            else if stBcMax > 0 and high - low > f_unPx(stUBc, stBcMax, close) + syminfo.mintick / 2
                _xs := "big signal candle " + str.tostring(high - low, format.mintick) + " (most " + str.tostring(f_unPx(stUBc, stBcMax, close), format.mintick) + ")"
                stCntX11 += 1
            else if stFstOn and (na(stFstDay) or stFstDay != _xDay)''')

# ---- table
rep('(stCmMode == "Off" and stSprd <= 0) or na(stCmLast) ? "-"', '(stCmMode == "Off" and stSpX <= 0) or na(stCmLast) ? "-"')
rep('(stCmMode == "Off" and stSprd <= 0) or na(stCmLast) ? color.gray', '(stCmMode == "Off" and stSpX <= 0) or na(stCmLast) ? color.gray')
rep('(stCmMode == "Off" and stSprd <= 0) ? "off"', '(stCmMode == "Off" and stSpX <= 0) ? "off"')
rep('''    string _buU = stBuPipM ? " pips" : stBuPctM ? " %" : ""
    string _buT = stBuPipM ? (str.tostring(stSlBuf) + " pips x " + str.tostring(stPipSz) + " = " + str.tostring(f_stBuf(close), format.mintick)) : stBuPctM ? (str.tostring(stSlBuf) + "% of the level = " + str.tostring(f_stBuf(close), format.mintick) + " now") : ("price " + str.tostring(stSlBuf))
    if stSprd > 0
        _buT := _buT + "  |  spread for sizing " + str.tostring(f_stSprd(close), format.mintick)
    if stMinStop > 0 or stMaxStop > 0
        _buT := _buT + "  |  skip closer " + (stMinStop > 0 ? str.tostring(stMinStop) + _buU : "off") + " / further " + (stMaxStop > 0 ? str.tostring(stMaxStop) + _buU : "off")
    f_stCell(_t, 47, "UNIT + STOP BUFFER (sections 1, 5)", _buT, stBuPipM or stBuPctM ? color.aqua : color.gray)''',
    '''    string _buU = f_unTxt(stUSk)
    string _buT = (stBuSepM ? "separate units  |  buffer " : "") + (stUBf == 1 ? (str.tostring(stBfX) + " pips x " + str.tostring(stPipSz) + " = " + str.tostring(f_stBuf(close), format.mintick)) : stUBf == 2 ? (str.tostring(stBfX) + "% of the level = " + str.tostring(f_stBuf(close), format.mintick) + " now") : ("price " + str.tostring(stBfX)))
    if stSpX > 0
        _buT := _buT + "  |  spread for sizing " + str.tostring(f_stSprd(close), format.mintick)
    if stMnX > 0 or stMxX > 0
        _buT := _buT + "  |  skip closer " + (stMnX > 0 ? str.tostring(stMnX) + _buU : "off") + " / further " + (stMxX > 0 ? str.tostring(stMxX) + _buU : "off")
    f_stCell(_t, 47, "UNIT + STOP BUFFER (sections 1, 5)", _buT, stBuMode != "Price" ? color.aqua : color.gray)''')
rep('''    string _r3U = stBuPipM ? " pips" : stBuPctM ? " %" : ""
    string _r3T = not stR3On ? "off - rules 1 / 2" : "on  -  " + str.tostring(stCntR3) + " entered at the close" + (stR3BrkOn ? "  |  close within " + str.tostring(stR3Brk) + _r3U''',
    '''    string _r3U = f_unTxt(stUR3)
    string _r3T = not stR3On ? "off - rules 1 / 2" : "on  -  " + str.tostring(stCntR3) + " entered at the close" + (stR3BrkOn ? "  |  close within " + str.tostring(stR3X) + _r3U''')
rep('''(stMnPct > 0 ? ", stop < " + str.tostring(stMnPct) + "% " + str.tostring(stCntX8) : "")''',
    '''(stMnPct > 0 ? ", stop < " + str.tostring(stMnPct) + "% " + str.tostring(stCntX8) : "") + (stLzMin > 0 ? ", leg < " + str.tostring(stLzMin) + f_unTxt(stULz) + " " + str.tostring(stCntX9) : "") + (stLzMax > 0 ? ", leg > " + str.tostring(stLzMax) + f_unTxt(stULz) + " " + str.tostring(stCntX10) : "") + (stBcMax > 0 ? ", candle > " + str.tostring(stBcMax) + f_unTxt(stUBc) + " " + str.tostring(stCntX11) : "")''')
rep('f_stCell(_t, 52, "  - skipped: section 4 filters (v13.1)"', 'f_stCell(_t, 52, "  - skipped: section 4 filters (v13.1 / v14.0)"')

assert all(ord(c) < 128 for c in s), 'not ASCII'
open(dst, 'w').write(s)
print('written', dst)
