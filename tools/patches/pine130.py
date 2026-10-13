# TradingView v13.0 = v12.2 + the settings in 13 sections (the same order as EA v13.0) + ONE stop buffer box read in the
# section 1 unit (stBuPips / stBuPct gone) + the spread for sizing read in that unit too + every 'group N' in the tooltips
# and the table -> the new section (or 'above' / 'below' inside a section) + the ideas a-g lost their letters.
# The input statements are moved to the top of the script (they only use their group names), nothing else moves.
# usage: python3 pine130.py SMC_Structure_Strategy_v12.2.txt SMC_Structure_Strategy_v13.0.txt
import sys, re
src, dst = sys.argv[1], sys.argv[2]
L = open(src).read().split('\n')

ORDER = [
    ('gx01', '1. MARKET & UNITS - price, pips or % for every distance below', ['stBuMode', 'stBuPip']),
    ('gx02', '2. SIGNALS - market structure (CHOCH / BOS)', ['stSigSrc', 'stHtf', 'altMode', 'pbBodyOn', 'pbBodyRef', 'pbSwp2']),
    ('gx03', '3. ENTRIES - entry rules, direction, order handling',
     ['stOn', 'stR1On', 'stPbPct', 'stR2On', 'stR3On', 'stR3BrkOn', 'stR3Brk', 'stR3Fb', 'stEntMode', 'stDirMode', 'stRev', 'stMaxOpen', 'stCancelSig', 'stBosCnl', 'stExpBars']),
    ('gx04', '4. SETUP FILTERS - which setups are taken', ['stMinStop', 'stMaxStop', 'stHfOn', 'stPdOn', 'stPdPct', 'stEqOn', 'stEqPct']),
    ('gx05', '5. STOP & TARGET - stop buffer, target, managing open trades',
     ['stSlBuf', 'stRR', 'stLqOn', 'stLqMin', 'stPpOn', 'stPpPct', 'stPpR', 'stPpBe', 'stMvStepOn', 'stMvBeOn', 'stTrOn', 'stTrMode']),
    ('gx06', '6. POSITION SIZE', ['stSize', 'stRisk', 'stQty', 'stCash', 'stLotStep', 'stRndMax', 'stLev', 'stBkOn', 'stBkPct']),
    ('gx07', '7. LOSS RECOVERY - Rule A / B / C, cap, split, profit steps',
     ['stSeqMode', 'stSeqMax', 'stSeqCapAct', 'stSeqAdd', 'stSeqSplit', 'stSeqFrom', 'stSeqFromT', 'stLmOn', 'stLmAmt',
      'stSp1', 'stSpN1', 'stSp2', 'stSpN2', 'stSp3', 'stSpN3', 'stSpInc', 'stSpAdd']),
    ('gx08', '8. ACCOUNT PROTECTION - daily limits, floor, profit target, pauses',
     ['stDayLoss', 'stMaxTrades', 'stDD', 'stFlMode', 'stFlAmt', 'stFlLock', 'stFlPct', 'stPtOn', 'stPtAmt', 'stPtPer', 'stPtFrom',
      'stLsOn', 'stLsN', 'stLdOn', 'stLdN', 'stLdD']),
    ('gx09', '9. TRADING HOURS & WEEKEND', ['stSessMode', 'stTz', 'stHrOn', 'stHrOff', 'stHrFlat', 'stWkFlat', 'stWkDay', 'stWkHr', 'stWk247']),
    ('gx10', '10. NEWS - windows, US news, holidays',
     ['stNewsOn', 'stNwExit', 'stNw1On', 'stNw1', 'stNw2On', 'stNw2', 'stNw3On', 'stNw3', 'stNwNy', 'stNdOn', 'stNdList', 'stNdScope',
      'stAuOn', 'stAuNfp', 'stAuJc', 'stAuIsmM', 'stAuIsmS', 'stAuPre', 'stAuPost', 'stUsClk', 'stHolTrade', 'stPreOn', 'stPreHrs']),
    ('gx11', '11. COSTS - commission and spread (used to SIZE trades and to count losses)', ['stCmMode', 'stCmLot', 'stCmUnit', 'stCmPct', 'stCmFix', 'stCmTgt', 'stSprd']),
    ('gx12', '12. BROKER - webhook message and TheConnector', ['stWhOn', 'stWhMode', 'stWhMinLot', 'stWhQty', 'stWhId', 'stWhSym', 'stTcTag', 'stTcSl']),
    ('gx13', '13. DISPLAY - levels, table, audit labels', ['stShow', 'stStatOn', 'stStatPos', 'stAudit', 'stAudSz']),
]
GONE = {'stBuPips', 'stBuPct'}

# per input: (old text, new text) - every one must be found exactly once in that input's line
ED = {
    'stBuMode': [('input.string("Price (as now)", "Stop buffer unit", options = ["Price (as now)", ',
                  'input.string("Price", "Unit for every price distance (stop buffer, skip closer / further, rule 3, spread)", options = ["Price", ')],
    'stBuPip': [('"  - pip size (0 = automatic)"', '"  - pip size (0 = automatic: gold 0.10, silver 0.01, forex 0.0001, JPY 0.01)"')],
    'stSlBuf': [('"Stop buffer beyond the CHOCH* level, in price", minval = 0.0, step = 0.00000001, group = gStg)',
                 '"Stop buffer beyond the CHOCH* level (unit: section 1)", minval = 0.0, step = 0.00000001, group = gStg, tooltip = '
                 '"How far beyond the CHOCH* level the stop is placed, in the unit chosen in section 1:\\n\\nPRICE (default): in price - '
                 '1.0 = 1.00 on gold.\\nPIPS: in pips of this market - 10 pips = 1.00 on gold, 0.0010 on EURUSD.\\n% OF PRICE: % of the '
                 'CHOCH* level - 0.025 = 1.00 on gold at 4,000, 25 on Bitcoin at 100,000.\\n\\nPips and % are rounded to the smallest price '
                 'step. When you change the unit, type this number again (1.0 in price is not 1.0 pips or 1.0 %). The table row '
                 '\'UNIT + STOP BUFFER\' shows the buffer in price.")')],
    'stMinStop': [('"Skip the setup if the stop is CLOSER than this (price)"', '"Skip the setup if the stop is CLOSER than this (unit: section 1; 0 = off)"'),
                  ('Try 3 on gold. 0 = off."', 'Try 3 on gold. 0 = off.\\n\\nRead in the unit of section 1: price (8 = 8.00), pips (80 pips = 8.00 on gold) or % of the entry price (0.5 = 20.00 at 4,000)."')],
    'stMaxStop': [('"Skip the setup if the stop is FURTHER than this (price)"', '"Skip the setup if the stop is FURTHER than this (unit: section 1; 0 = off)"'),
                  ('in the time you have. 0 = off."', 'in the time you have. 0 = off.\\n\\nRead in the unit of section 1, like the box above."')],
    'stSprd': [('"Broker spread, in price  (0 = not modelled)"', '"Broker spread for SIZING (unit: section 1; 0 = not modelled)"'),
               ('in PRICE (not ticks, not points).', 'in the unit of section 1 (price, pips, or % of the price - not ticks, not points).')],
    'stR3Brk': [('"  - the most the close may be beyond the broken level"', '"  - the most the close may be beyond the broken level (unit: section 1)"'),
                ('In the unit of group 38 like group 24:', 'In the unit of section 1, like the skip limits of section 4:')],
    'stHtf': [('"Higher timeframe for RULE 2"', '"Higher timeframe (RULE 2, higher-timeframe choices and filters)"')],
    'stSessMode': [('"Time-of-day filters"', '"Time-of-day filters (hours, force close, weekend)"')],
    'stMaxOpen': [('"Max trades open at the same time  (0 = no limit)"', '"Max trades open at the same time  (0 = no limit; stacked BOS trades)"')],
    'stAudSz': [('"Audit label size"', '"  - audit label size"'), ('(switch them on in group 20)', '(switch them on above)')],
    'stNewsOn': [('the windows in group 25, the dates in group 28, and the automatic US news and US holidays in group 29.',
                  'the windows 1 / 2 / 3, the chosen dates, the automatic US news and the US holidays (all in this section).'),
                 ('inside your session hours (group 20, for example', 'inside your session hours (section 9, for example')],
    'stSigSrc': [('(the % in group 37)', '(the % in section 4)'), ('The group 37 switch is not used', 'The section 4 equilibrium switch is not used'),
                 ('Filter b (group 34) is not used', 'The higher-timeframe filter (section 4) is not used')],
    'stAudit': [('(size and colours: group 31)', '(size: below)')],
    'stSeqMode': [('reaches a step of group 43', 'reaches a profit step (below)')],
    'stWhMode': [('and see group 30.', 'and see the TheConnector settings below.')],
    'stWk247': [('The session hours in group 20 still apply', 'The session hours above still apply'),
                ("'Time-of-day filters' in group 20", "'Time-of-day filters' above")],
    'stNw1On': [('from group 20 (Asia/Kolkata', 'from section 9 (Asia/Kolkata')],
    'stPtPer': [('(group 20)', '(section 9)')],
    'stNdOn': [('"News windows work ONLY on the dates below"', '"Windows 1 / 2 / 3 work ONLY on the dates below"'),
               ('the news windows in group 25 work', 'windows 1 / 2 / 3 work'), ('(group 20)', '(section 9)')],
    'stAuOn': [("'When a window starts' in group 25.", "'When a window starts' above."),
               ('Your group 25 windows and group 28 dates keep working', 'Your windows 1 / 2 / 3 and the chosen dates keep working')],
    'stAuNfp': [('add the real date in group 28', 'add the real date to the chosen dates above')],
    'stUsClk': [('your group 25 windows', 'your windows 1 / 2 / 3')],
    'stNwNy': [('"Read the group 25 window times in New York time"', '"Read the window 1 / 2 / 3 times in New York time"'),
               ('the group 25 window times are read in your session timezone (group 20)', 'the window 1 / 2 / 3 times are read in your session timezone (section 9)'),
               ('The group 28 dates are still read', 'The chosen dates are still read')],
    'stHolTrade': [("'When a window starts' in group 25.", "'When a window starts' above.")],
    'stDirMode': [("'close and reverse' ON (group 20)", "'close and reverse' ON (section 3)"), ('(group 30)', '(section 12)')],
    'stBkOn': [('"a. Smaller risk for stacked BOS trades"', '"Smaller risk for stacked BOS trades"'), ('(group 31 stacking - ', '(stacking, section 3 - ')],
    'stHfOn': [('"b. Higher-timeframe filter', '"Higher-timeframe filter'), ("(group 20 'Higher timeframe for RULE 2')", "(section 2 'Higher timeframe')")],
    'stTrOn': [('"c. Structure trailing stop"', '"Structure trailing stop"'), ('(group 32 can still move it)', '(the step stop / break-even above can still move it)'),
               ('the group 20 stop buffer', 'the stop buffer (section 5)'), ('like a group 32 move', 'like a step-stop move'),
               ('Works together with group 32', 'Works together with the step stop / break-even')],
    'stLqOn': [('"d. Target at the next liquidity', '"Target at the next liquidity'), ('the R multiple of group 20', 'the R multiple above')],
    'stPpOn': [('"e. Partial profit', '"Partial profit'), ('(group 21)', '(section 6)')],
    'stPdOn': [('"f. Premium / discount filter', '"Premium / discount filter'), ('(group 20)', '(section 3)')],
    'stLsOn': [('"g. Pause for the rest of the day', '"Pause for the rest of the day')],
    'stFlMode': [("'loss recovery counts from' in group 21", "'loss recovery counts from' in section 7"), ('(group 21)', '(section 7)')],
    'stLdOn': [('(group 34 e)', '(partial profit, section 5)'), ('(group 21)', '(section 7)')],
    'stLdD': [('(group 20)', '(section 9)')],
    'stEqOn': [('(the one set in group 20 - Auto', '(the one set in section 2 - Auto')],
    'stEqPct': [('(group 20)', '(section 2)')],
    'stPreOn': [('"No NEW trades in the hours before news (group 29 US releases)"', '"No NEW trades in the hours before news (the automatic US news)"'),
                ('that group 29 works out', 'that the automatic US news works out'),
                ("(group 25 'When a window starts', and the minutes before / after of group 29)", "('When a window starts' and the minutes before / after above)"),
                ("The same rule as the MT5 EA's group 41", "The same rule as the MT5 EA's"),
                ("Needs group 29 'Automatic US news windows' ON", "Needs 'Automatic US news windows' ON")],
    'stLmOn': [('(A, B, C, A+, B+, C+ - group 21)', '(A, B, C, A+, B+, C+ - above)'), ('The hard cap (group 21)', 'The hard cap (above)')],
    'stSp1': [('"Step 1 - total profit of at least"', '"Rule A / B / C split - step 1: total profit of at least"'),
              ('(group 21). 0 = this step is off.', '(above). 0 = this step is off.'), ("('loss recovery counts from', group 21)", "('loss recovery counts from', above)")],
    'stSp2': [('"Step 2 - total profit of at least"', '"Rule A / B / C split - step 2: total profit of at least"')],
    'stSp3': [('"Step 3 - total profit of at least"', '"Rule A / B / C split - step 3: total profit of at least"')],
    'stSpInc': [('"Then a new step every this much more profit  (0 = no more steps)"', '"Rule A / B / C split - then a new step every this much more profit  (0 = no more)"')],
}
# the stBuMode tooltip is written again (it described the three buffer boxes)
BU_TIP = ('"PRICE (default): every price distance is typed in price, exactly as before - 1.0 = 1.00 on gold.\\n\\n'
          'PIPS: typed in pips, and the strategy knows the pip of the market on the chart: gold 0.10, silver 0.01, Bitcoin 1, '
          'Ethereum 0.10, forex 0.0001 (JPY pairs 0.01), anything else 10 x the smallest price step. 10 pips on gold = 1.00, on EURUSD = 0.0010.\\n\\n'
          '% OF PRICE: typed in % of the price, worked out again for every setup - the stop buffer is % of the CHOCH* level, the skip '
          'limits are % of the entry, the rule 3 distance % of the close, the spread % of the price. 0.025% of gold at 4,000 = 1.00, '
          'of EURUSD at 1.10 = 0.000275, of Bitcoin at 100,000 = 25. One setting for gold, silver, forex and crypto.\\n\\n'
          'It is used by: the stop buffer (section 5), skip the setup if the stop is CLOSER / FURTHER than (section 4), the rule 3 '
          "'near the broken level' distance (section 3) and the spread for sizing (section 11). When you change the unit, type those "
          "numbers again. The table row 'UNIT + STOP BUFFER' shows them in price.\"")

idx = {}
for i, l in enumerate(L):
    m = re.match(r'^(\w+)\s*=\s*input\.\w+\(', l)
    if m: idx[m.group(1)] = i
names = [n for _, _, ns in ORDER for n in ns]
if set(idx) - GONE != set(names) or len(names) != len(set(names)):
    raise SystemExit('inputs: missing %s, unknown %s' % (set(idx) - GONE - set(names), set(names) - set(idx)))
gconst = {}
for i, l in enumerate(L):
    m = re.match(r'^(g\w+)\s*=\s*"[^"]*"\s*$', l)
    if m: gconst[m.group(1)] = i
used_g = set()
newl = {}
for n in names:
    t = L[idx[n]]
    g = re.search(r'group = (\w+)', t)
    used_g.add(g.group(1))
    for a, b in ED.get(n, []):
        if t.count(a) != 1: raise SystemExit('%s: %d x %r' % (n, t.count(a), a[:80]))
        t = t.replace(a, b)
    if n == 'stBuMode':
        k = t.index('tooltip = ') + len('tooltip = ')
        t = t[:k] + BU_TIP + ')'
    t = re.sub(r'group = \w+', 'group = ' + [gv for gv, _, ns in ORDER if n in ns][0], t, count=1)
    newl[n] = t
# the old group names used only by the inputs go too
drop = set(idx.values())
for g in used_g:
    other = [j for j, l in enumerate(L) if re.search(r'\b%s\b' % g, l) and j not in idx.values() and j != gconst.get(g)]
    if other: raise SystemExit('%s still used at %s' % (g, other))
    drop.add(gconst[g])
blk = ['// ==== SETTINGS (v13.0) - 13 sections, the same order as the MT5 EA v13.0. Every price DISTANCE (stop buffer, skip',
       '// closer / further, rule 3 distance, spread for sizing) is read in the unit chosen in section 1: price, pips or % of price.']
for gv, title, ns in ORDER:
    blk.append('')
    blk.append('%s = "%s"' % (gv, title))
    for n in ns: blk.append(newl[n])
blk.append('')
# insert after the strategy(...) declaration (its last line ends with 'calc_on_every_tick = false)')
ins = next(i for i, l in enumerate(L) if l.rstrip().endswith('calc_on_every_tick = false)')) + 1
out = []
for i, l in enumerate(L):
    if i == ins: out.extend([''] + blk)
    if i in drop: continue
    out.append(l)
s = '\n'.join(out)


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:120]))
    s = s.replace(old, new)


# version line 2
s = re.sub(r'^(// SMC Structure Strategy  -  )v12\.2(  -  )', r'\1v13.0\2', s, count=1, flags=re.M)
if '// SMC Structure Strategy  -  v13.0  -  ' not in s.split('\n')[1]: raise SystemExit('line 2')
# option names used in comparisons
for x in 'ABC':
    rep('Rule %s split (%s, the base grows with the profit - group 43)' % (x, x), 'Rule %s split (%s, the base grows with the profit - section 7)' % (x, x), {'A': 4, 'B': 4, 'C': 3}[x])
# the one stop buffer box, the spread in the unit
rep('// v11.2: the stop buffer beyond the level _lv, in price (pips x pip, or % of the level, rounded to the price step; else the group 20 buffer)\n'
    'f_stBuf(float _lv) =>\n'
    '    stBuPipM ? math.round_to_mintick(stBuPips * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stBuPct / 100.0) : stSlBuf\n',
    '// v11.2 / v13.0: the stop buffer beyond the level _lv, in price - the ONE stop buffer box (stSlBuf, section 5) read in the\n'
    '// section 1 unit: pips x pip, or % of the level (both rounded to the price step), or the price as it is\n'
    'f_stBuf(float _lv) =>\n'
    '    stBuPipM ? math.round_to_mintick(stSlBuf * stPipSz) : stBuPctM ? math.round_to_mintick(_lv * stSlBuf / 100.0) : stSlBuf\n'
    '// v13.0: the spread for sizing (section 11) in price: pips x pip, or % of the price, or the price as it is\n'
    'f_stSprd(float _px) =>\n'
    '    stBuPipM ? stSprd * stPipSz : stBuPctM ? math.max(nz(_px), 0.0) * stSprd / 100.0 : stSprd\n'
    '// v13.0: a % of price above 10 is a typing mistake (1.0 typed in price, then the unit changed?) - stop with a clear message\n'
    'if barstate.isfirst and stBuPctM and (stSlBuf > 10 or stSprd > 10)\n'
    '    runtime.error("Section 1 unit is % of price: the stop buffer (section 5) and the spread (section 11) must be 10 or less")\n')
rep('// v12.0: the rule 3 \'near the broken level\' distance in price (the unit of group 38: price, pips, or % of the close)',
    '// v12.0: the rule 3 \'near the broken level\' distance in price (the unit of section 1: price, pips, or % of the close)')
rep('    c + (stSprd > 0 ? strategy.convert_to_account(stSprd * f_stPv()) : 0.0)', '    c + (stSprd > 0 ? strategy.convert_to_account(f_stSprd(ent) * f_stPv()) : 0.0)')
# the table
rep('table.cell(stTbl, 0, 0, "STRATEGY", ', 'table.cell(stTbl, 0, 0, "STRATEGY v13.0", ')
rep('"0 - type yours in group 23, lot="', '"0 - type yours in section 11, lot="')
rep('f_stCell(stTbl, 40, "Trade direction (group 33)"', 'f_stCell(stTbl, 40, "Trade direction (section 3)"')
rep('    string _v9 = (stBkOn ? "a " : "") + (stHfOn ? "b " : "") + (stTrOn ? "c " : "") + (stLqOn ? "d " : "") + (stPpOn ? "e " : "") + (stPdOn ? "f " : "") + (stLsOn ? "g " : "")\n'
    '    f_stCell(stTbl, 41, "v9.0 ideas switched ON (group 34)", _v9 == "" ? "none" : _v9, _v9 == "" ? color.gray : color.aqua)\n',
    '    string _v9 = (stBkOn ? ", stacked BOS risk" : "") + (stHfOn ? ", HTF filter" : "") + (stTrOn ? ", trailing stop" : "") + (stLqOn ? ", liquidity target" : "") + (stPpOn ? ", partial profit" : "") + (stPdOn ? ", premium / discount" : "") + (stLsOn ? ", day pause" : "")\n'
    '    f_stCell(stTbl, 41, "Extra options switched ON", _v9 == "" ? "none" : str.substring(_v9, 2), _v9 == "" ? color.gray : color.aqua)\n')
rep('"ACCOUNT FLOOR (group 35)"', '"ACCOUNT FLOOR (section 8)"')
rep('"PAUSE AFTER LOSSES (group 36)"', '"PAUSE AFTER LOSSES (section 8)"')
rep('"HTF EQUILIBRIUM FIRST (group 37)"', '"HTF EQUILIBRIUM FIRST (section 4)"')
rep('"STOP BUFFER (group 38)", _buT, stBuPipM or stBuPctM ? color.aqua : color.gray)', '"UNIT + STOP BUFFER (sections 1, 5)", _buT, stBuPipM or stBuPctM ? color.aqua : color.gray)')
rep('"RULE 3 - ENTRY AT THE SIGNAL CLOSE (group 39)"', '"RULE 3 - ENTRY AT THE SIGNAL CLOSE (section 3)"')
rep('"on - but group 29 is OFF (no releases)"', '"on - but the automatic US news is OFF (no releases)"')
rep('" h before the group 29 releases"', '" h before the automatic US releases"')
rep('"NO NEW TRADES BEFORE NEWS (group 41)"', '"NO NEW TRADES BEFORE NEWS (section 10)"')
rep('"LOSS MARK - BACK TO THE BASE (group 42)"', '"LOSS MARK - BACK TO THE BASE (section 7)"')
rep('"PROFIT STEPS - A / B / C split (group 43)"', '"PROFIT STEPS - A / B / C split (section 7)"')
a = s.index('    string _buT = ')
b = s.index('\n', a)
old = s[a:b]
for x, y in (('str.tostring(stBuPips) + " pips x "', 'str.tostring(stSlBuf) + " pips x "'), ('str.tostring(stBuPct) + "% of the l', 'str.tostring(stSlBuf) + "% of the l')):
    if old.count(x) != 1: raise SystemExit('_buT: %r' % x)
    old = old.replace(x, y)
s = s[:a] + old + s[b:]
rep('    if stMinStop > 0 or stMaxStop > 0\n        _buT := _buT + ',
    '    if stSprd > 0\n        _buT := _buT + "  |  spread for sizing " + str.tostring(f_stSprd(close), format.mintick)\n'
    '    if stMinStop > 0 or stMaxStop > 0\n        _buT := _buT + ')

left = [m.group(0) for m in re.finditer(r'"[^"\n]*\bgroups? \d+[^"\n]*"', s)]
if left: raise SystemExit('group numbers left in texts: %s' % left[:5])
for v in ('stBuPips', 'stBuPct'):
    if re.search(r'\b%s\b' % v, s): raise SystemExit(v + ' still used')
for ch in s:
    if ord(ch) > 126 or (ord(ch) < 32 and ch not in '\n\t'): raise SystemExit('not ASCII: %r' % ch)
open(dst, 'w').write(s)
print('written', dst, len(s.split('\n')), 'lines,', len(names), 'inputs')
