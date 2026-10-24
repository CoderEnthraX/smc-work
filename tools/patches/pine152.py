# TradingView v15.2 = v15.1 (the complete file) +
#   1. section 9: 'Only take entries in kill zones' + Asian / London / New York / London close (New York times, so they follow
#      the US summer / winter time; the IST times are in the names) + 'when a kill zone ends: cancel the waiting order and close
#      the open trade' (OFF = a setup armed in a kill zone keeps waiting after it, open trades run on). The entry hours still
#      apply. Charts of 1 day and above: not used. The same rules as the MT5 EA v15.2.
#   2. section 4: 'C5 set' and 'C6 + RSI set' - each switches its settings ON as if typed in (the boxes keep what you set);
#      both ON = error
# usage: python3 pine152.py SMC_Structure_Strategy_v15.1.txt SMC_Structure_Strategy_v15.2.txt
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:160]))
    s = s.replace(old, new)


def after_line(start, add):
    """insert the lines 'add' after the one line that starts with 'start'"""
    global s
    L = s.split('\n')
    k = [i for i, l in enumerate(L) if l.startswith(start)]
    if len(k) != 1: raise SystemExit('line start %r found %d x' % (start, len(k)))
    L[k[0] + 1:k[0] + 1] = add.rstrip('\n').split('\n')
    s = '\n'.join(L)


def rename_input(old, new):
    """the raw input gets a new name (the effective value keeps the old one, see below)"""
    global s
    pat = re.compile(r'^' + re.escape(old) + r'(\s*)= input\.', re.M)
    m = pat.findall(s)
    if len(m) != 1: raise SystemExit('input %s found %d x' % (old, len(m)))
    s = pat.sub(lambda mm: new + ' ' * max(1, len(mm.group(1)) - (len(new) - len(old))) + '= input.', s)


# ---------------------------------------------------------------- the version (line 2), the settings title, the table title
rep('// SMC Structure Strategy  -  v15.1  -  main-tier CHOCH/BOS (v15.1: one box per zone',
    '// SMC Structure Strategy  -  v15.2  -  main-tier CHOCH/BOS (v15.2: kill zones - entries only in the Asian / London / New '
    'York / London close kill zones on the New York clock, optional close at their end - and the C5 / C6 + RSI sets that switch '
    'their section 4 settings on; v15.1: one box per zone')
rep('// ==== SETTINGS (v15.1) - 13 sections, the same order as the MT5 EA v15.1.',
    '// ==== SETTINGS (v15.2) - 13 sections, the same order as the MT5 EA v15.2.')
rep('"STRATEGY v15.1"', '"STRATEGY v15.2"')

# ---------------------------------------------------------------- section 4 end: the C5 / C6 + RSI sets
after_line('stBcMax2 = input.float(', '''stC5     = input.bool(false, "C5 set - switches ON: min stop 0.5% of the price, skip the first setup of the day, yesterday's high / low, move of 12+ candles", group = gx04, tooltip = "OFF (default): nothing changes - the settings above work as you set them.\\n\\nON: these section 4 settings are switched ON as if you typed them (the boxes above keep what you set and come back when C5 is OFF):\\n  skip the setup if the stop is closer than 0.5% of the price\\n  skip the first setup of the day\\n  no buy below yesterday's low, no sell above yesterday's high\\n  skip a CHOCH / BOS whose move took fewer than 12 candles\\nEverything else stays as you set it.\\n\\nOn charts ABOVE 1 minute the min stop % works only when 'Use skip closer / further, min stop % ... on the 1-minute chart only' above is OFF.\\n\\nC5 was the most even set in the gold 1-minute tests 2021-2026 - the best of many tries, so part of it can be luck. Not together with C6.")
stC6     = input.bool(false, "C6 + RSI set - switches ON: entries 13-21 (section 9), min stop 0.35%, yesterday's high / low, move of 12+ candles, RSI 1 hour (2) Pullback 50", group = gx04, tooltip = "OFF (default): nothing changes - the settings work as you set them.\\n\\nON: these settings are switched ON as if you typed them (the boxes keep what you set and come back when C6 is OFF):\\n  section 9: take entries from 13, stop taking entries at 21 (session timezone, IST by default)\\n  skip the setup if the stop is closer than 0.35% of the price\\n  no buy below yesterday's low, no sell above yesterday's high\\n  skip a CHOCH / BOS whose move took fewer than 12 candles\\n  RSI filter - HIGHER timeframe ON: 1 hour, length 2, Pullback, level 50\\nEverything else stays as you set it.\\n\\nOn charts ABOVE 1 minute the min stop % works only when 'Use skip closer / further, min stop % ... on the 1-minute chart only' above is OFF.\\n\\nC6 + RSI made the most in the gold 1-minute tests 2021-2026 - the best of many tries, so part of it can be luck. Not together with C5.")''')

# ---------------------------------------------------------------- section 9 end: the kill zones
after_line('stFl1m   = input.bool(', '''stKzOn   = input.bool(false, "Only take entries in kill zones (New York times - IST summer = mid-March to early November)", group = gx09, tooltip = "OFF (default): nothing changes.\\n\\nON: a NEW setup is armed only inside a kill zone you tick below. The times are New York times, so they move with the US summer / winter time by themselves - the IST times are in the names (summer = mid-March to early November).\\n\\nThe entry hours above (Take entries from / Stop taking entries at) still apply too - keep them wide (for example 6 to 23).\\n\\nA setup armed inside a kill zone keeps waiting after the kill zone ends, and open trades run on (stop, target, force close, weekend as usual) - unless 'when a kill zone ends' below is ON.\\n\\nNot used on charts of 1 day and above.")
stKzAs   = input.bool(false, "  - Asian 20:00-00:00 New York (IST 05:30-09:30 summer, 06:30-10:30 winter)", group = gx09)
stKzLo   = input.bool(true, "  - London 02:00-05:00 New York (IST 11:30-14:30 summer, 12:30-15:30 winter)", group = gx09)
stKzNy   = input.bool(true, "  - New York 07:00-10:00 New York (IST 16:30-19:30 summer, 17:30-20:30 winter)", group = gx09)
stKzLc   = input.bool(false, "  - London close 10:00-12:00 New York (IST 19:30-21:30 summer, 20:30-22:30 winter)", group = gx09)
stKzEnd  = input.bool(false, "  - when a kill zone ends: cancel the waiting order and close the open trade", group = gx09, tooltip = "OFF (default): when a kill zone ends nothing is cancelled or closed - only NEW setups wait for the next kill zone.\\n\\nON: outside the kill zones nothing is left - a waiting order is cancelled and an open trade is closed at the end of the kill zone (closed at the next candle's open, like the force-close hour).")''')

# ---------------------------------------------------------------- the C5 / C6 sets: the raw inputs get new names, the effective values keep the old ones
for a in ('stFstOn', 'stYdOn', 'stLegMin', 'stRsHOn', 'stRsHTf', 'stRsHLen', 'stRsHMode', 'stRsHLvl', 'stHrOn', 'stHrOff'):
    rename_input(a, a + 'I')
after_line('stZnCLb  = input.color(', '''
// v15.2 (section 4): the C5 / C6 + RSI sets switch their settings ON, as if typed in (the boxes keep what you set)
bool   stFstOn   = stC5 or stFstOnI
bool   stYdOn    = stC5 or stC6 or stYdOnI
int    stLegMin  = stC5 or stC6 ? 12 : stLegMinI
bool   stRsHOn   = stC6 or stRsHOnI
string stRsHTf   = stC6 ? "1 hour" : stRsHTfI
int    stRsHLen  = stC6 ? 2 : stRsHLenI
string stRsHMode = stC6 ? "Pullback" : stRsHModeI
float  stRsHLvl  = stC6 ? 50.0 : stRsHLvlI
int    stHrOn    = stC6 ? 13 : stHrOnI
int    stHrOff   = stC6 ? 21 : stHrOffI
if barstate.isfirst and stC5 and stC6
    runtime.error("Section 4: turn on the C5 set OR the C6 + RSI set, not both")
if barstate.isfirst and stKzOn and not (stKzAs or stKzLo or stKzNy or stKzLc)
    runtime.error("Only take entries in kill zones (section 9): turn on at least one kill zone")''')

# ---------------------------------------------------------------- the kill zone clock: New York time at the bar close, like the entry hours
after_line('string _nyTz = ', '''// v15.2: the kill zones on the New York clock (Asian 20-24, London 2-5, New York 7-10, London close 10-12), tested like the hours
// (a bar of 1 day or more always touches them)
int  _tMk = hour(time_close, _nyTz) * 60 + minute(time_close, _nyTz)
bool stKzIn = not stKzOn or (stKzAs and f_ovl(_tMk, _bMin, 1200, 1440)) or (stKzLo and f_ovl(_tMk, _bMin, 120, 300)) or (stKzNy and f_ovl(_tMk, _bMin, 420, 600)) or (stKzLc and f_ovl(_tMk, _bMin, 600, 720))''')

# ---------------------------------------------------------------- 'when a kill zone ends' ON: outside the kill zones a waiting order goes and an open trade is closed
rep('''if stFlatNow
    if strategy.position_size != 0
        stClsWhy := "Time flat"
        stCloseReq := bar_index
        stWhy := 2
    if stDir != 0
        stCntCanc += 1
        f_audEnd("CANCELLED - force-close hour", stAudCancC)
''', '''// v15.2: 'when a kill zone ends' ON - outside the kill zones a waiting order goes and an open trade is closed (like the force close)
if stFlatNow or (stKzEnd and not stKzIn)
    if strategy.position_size != 0
        stClsWhy := stFlatNow ? "Time flat" : "Kill zone end"
        stCloseReq := bar_index
        stWhy := 2
    if stDir != 0
        stCntCanc += 1
        f_audEnd(stFlatNow ? "CANCELLED - force-close hour" : "CANCELLED - kill zone ended", stAudCancC)
''')
# the min stop % of the C5 / C6 sets: straight into the value in use
rep('var float stMnP = stX1m ? 0.0 : stMnPct', 'var float stMnP = stX1m ? 0.0 : stC5 ? 0.5 : stC6 ? 0.35 : stMnPct')
# the table row of the section 4 filters: one helper for its parts (the same text)
rep('''    string _xT = (stFstOn ? ", first of the day " + str.tostring(stCntX0) : "") + (stYdOn ? ", yesterday's high / low " + str.tostring(stCntX1) : "") + (stLegMin > 0 ? ", move < " + str.tostring(stLegMin) + " candles " + str.tostring(stCntX2) : "") + (stTdOn ? ", today's move " + str.tostring(stCntX3) : "") + (stRsLOn ? ", RSI " + f_xTfTxt(stRsLTfS) + " " + str.tostring(stCntX4) : "") + (stRsHOn ? ", RSI " + f_xTfTxt(stRsHTfS) + " " + str.tostring(stCntX5) : "") + (stEmLOn ? ", EMA " + f_xTfTxt(stEmLTfS) + " " + str.tostring(stCntX6) : "") + (stEmHOn ? ", EMA " + f_xTfTxt(stEmHTfS) + " " + str.tostring(stCntX7) : "") + (stMnP > 0 ? ", stop < " + str.tostring(stMnP) + "% " + str.tostring(stCntX8) : "") + (stLzN > 0 ? ", leg < " + str.tostring(stLzN) + f_unTxt(stULz) + " " + str.tostring(stCntX9) : "") + (stLzX > 0 ? ", leg > " + str.tostring(stLzX) + f_unTxt(stULz) + " " + str.tostring(stCntX10) : "") + (stBcE > 0 ? ", candle > " + str.tostring(stBcE) + f_unTxt(stUBc) + " " + str.tostring(stCntX11) : "")
''', '''    string _xT = f_xc(stFstOn, "first of the day", stCntX0) + f_xc(stYdOn, "yesterday's high / low", stCntX1) + f_xc(stLegMin > 0, "move < " + str.tostring(stLegMin) + " candles", stCntX2) + f_xc(stTdOn, "today's move", stCntX3) + f_xc(stRsLOn, "RSI " + f_xTfTxt(stRsLTfS), stCntX4) + f_xc(stRsHOn, "RSI " + f_xTfTxt(stRsHTfS), stCntX5) + f_xc(stEmLOn, "EMA " + f_xTfTxt(stEmLTfS), stCntX6) + f_xc(stEmHOn, "EMA " + f_xTfTxt(stEmHTfS), stCntX7) + f_xc(stMnP > 0, "stop < " + str.tostring(stMnP) + "%", stCntX8) + f_xc(stLzN > 0, "leg < " + str.tostring(stLzN) + f_unTxt(stULz), stCntX9) + f_xc(stLzX > 0, "leg > " + str.tostring(stLzX) + f_unTxt(stULz), stCntX10) + f_xc(stBcE > 0, "candle > " + str.tostring(stBcE) + f_unTxt(stUBc), stCntX11)
''')
rep('''f_stTab4() =>
''', '''// v15.2: one part of the 'skipped: section 4 filters' row (the same text as before)
f_xc(bool on, string t, int n) =>
    on ? ", " + t + " " + str.tostring(n) : ""
f_stTab4() =>
''')
# a new setup only inside a kill zone
rep('    bool _take = stWin and (strategy.position_size == 0 or (stOpp and stRev) or _addB)',
    '    bool _take = stWin and stKzIn and (strategy.position_size == 0 or (stOpp and stRev) or _addB)')
rep(': not stWin ? "outside session hours" : stOpp ? "in a trade (reverse is off)"',
    ': not stWin ? "outside session hours" : not stKzIn ? "outside the kill zones" : stOpp ? "in a trade (reverse is off)"')

rep('f_stCell(15, "Exit - 02:00 flat / weekend", str.tostring(stCntFlat), color.silver)',
    'f_stCell(15, "Exit - 02:00 flat / weekend / kill zone end", str.tostring(stCntFlat), color.silver)')

open(dst, 'w').write(s)
print('written', dst)
