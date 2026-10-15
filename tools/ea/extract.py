import sys
s = open(sys.argv[1]).read()
a = s.index('//==CORE-BEGIN=='); b = s.index('//==CORE-END==')
core = s[a:b]
# v13.0: the one stop buffer box (no buPips / buPct) + the hedge 'base' option - the harness sets them its own way
if 'buPips' not in core: core = '#define CORE_V13 1\n' + core
# v13.1: the new section 4 filters (min stop %, first of the day, yesterday, move candles, today, RSI / EMA)
if 'rsOn[2]' in core: core = '#define CORE_V131 1\n' + core
# v14.0: separate unit per distance (buMode 3), leg size, big signal candle
if 'lzMin' in core:
    core = '#define CORE_V14 1\n' + core
    # test hook (harness copy only, the .mq5 is not changed): every call of the section 4 filters with the two levels it reads
    h = 'string XSkip(int d, double piv, double opl)\n   {\n'
    assert core.count(h) == 1
    core = core.replace(h, h + '      if (g_xsLog) fprintf(g_xsLog, "%d,%lld,%d,%d,%.10f,%.10f\\n", EN.bi, (long long)g_t, k, d, piv, opl);\n')
    core = core.replace('#define CORE_V14 1\n', '#define CORE_V14 1\nstatic FILE *g_xsLog = nullptr;\n', 1)
open(sys.argv[2], 'w').write(core)
