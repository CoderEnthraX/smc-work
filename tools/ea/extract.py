import sys
s = open(sys.argv[1]).read()
a = s.index('//==CORE-BEGIN=='); b = s.index('//==CORE-END==')
core = s[a:b]
# v13.0: the one stop buffer box (no buPips / buPct) + the hedge 'base' option - the harness sets them its own way
if 'buPips' not in core: core = '#define CORE_V13 1\n' + core
# v13.1: the new section 4 filters (min stop %, first of the day, yesterday, move candles, today, RSI / EMA)
if 'rsOn[2]' in core: core = '#define CORE_V131 1\n' + core
# v14.0: separate unit per distance (buMode 3), leg size, big signal candle
if 'ZnCandle' in core:
    core = '#define CORE_V15 1\nstatic FILE *g_znLog = nullptr;\n' + core   # v15.0: zone modes, 1m-only rules, no loss mark
    # test hook (harness copy only): every bar's higher timeframe state + signals, and every zone decision (v14tests / v15sep.py)
    h = '   if (!S.obM) return;\n   int d = g_T15;\n'
    assert core.count(h) == 1
    core = core.replace(h, h + '   if (g_znLog) fprintf(g_znLog, "B,%d,%d,%.10f,%.10f,%d,%d,%d,%d,%d\\n", EN.bi, g_T15, g_htO, g_htX, g_htE, (int)EN.evCU, (int)EN.evCD, (int)EN.evBU, (int)EN.evBD);\n')
    h = '   if (best == 0 && S.znLine && g_zl.dir == d && g_zl.tch && !g_zl.spent) best = -1;\n   return best;\n'
    assert core.count(h) == 1
    core = core.replace(h, '   if (best == 0 && S.znLine && g_zl.dir == d && g_zl.tch && !g_zl.spent) best = -1;\n'
        '   if (g_znLog) { if (best > 0) fprintf(g_znLog, "A,%d,%d,%d,%d,%.10f,%.10f\\n", EN.bi, d, g_zn[best - 1].tf, g_zn[best - 1].kind, g_zn[best - 1].top, g_zn[best - 1].bot); '
        'else fprintf(g_znLog, "A,%d,%d,%d,-1,0,0\\n", EN.bi, d, best == -1 ? 9 : -1); }\n   return best;\n')
    # the zone box (the zone a with-HTF chart signal came from): Z,bar,d,tf,kind,top,bottom,left time,right time
    h = '   else       { g_zbTf = 9; g_zbK = 2; g_zbTop = g_htO; g_zbBot = g_htO; g_zbT0 = g_zl.tt; }\n'
    if h in core:
        core = core.replace(h, h + '   if (g_znLog) fprintf(g_znLog, "Z,%d,%d,%d,%d,%.10f,%.10f,%lld,%lld\\n", EN.bi, d, g_zbTf, g_zbK, g_zbTop, g_zbBot, (long long)g_zbT0, (long long)g_zbT1);\n')
if 'lzMin' in core:
    core = '#define CORE_V14 1\n' + core
    # test hook (harness copy only, the .mq5 is not changed): every call of the section 4 filters with the two levels it reads
    h = 'string XSkip(int d, double piv, double opl)\n   {\n'
    assert core.count(h) == 1
    core = core.replace(h, h + '      if (g_xsLog) fprintf(g_xsLog, "%d,%lld,%d,%d,%.10f,%.10f\\n", EN.bi, (long long)g_t, k, d, piv, opl);\n')
    core = core.replace('#define CORE_V14 1\n', '#define CORE_V14 1\nstatic FILE *g_xsLog = nullptr;\n', 1)
open(sys.argv[2], 'w').write(core)
