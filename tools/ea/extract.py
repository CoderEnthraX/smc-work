import sys
s = open(sys.argv[1]).read()
a = s.index('//==CORE-BEGIN=='); b = s.index('//==CORE-END==')
core = s[a:b]
# v13.0: the one stop buffer box (no buPips / buPct) + the hedge 'base' option - the harness sets them its own way
if 'buPips' not in core: core = '#define CORE_V13 1\n' + core
# v13.1: the new section 4 filters (min stop %, first of the day, yesterday, move candles, today, RSI / EMA)
if 'rsOn[2]' in core: core = '#define CORE_V131 1\n' + core
open(sys.argv[2], 'w').write(core)
