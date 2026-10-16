import sys
s = open(sys.argv[1]).read()
a = s.index('//==CORE-BEGIN=='); b = s.index('//==CORE-END==')
core = s[a:b]
# v13.0: the one stop buffer box (no buPips / buPct) + the hedge 'base' option - the harness sets them its own way
if 'buPips' not in core: core = '#define CORE_V13 1\n' + core
# v13.1: the new section 4 filters (min stop %, first of the day, yesterday, move candles, today, RSI / EMA)
if 'rsOn[2]' in core: core = '#define CORE_V131 1\n' + core
# v14.0: separate unit per distance (buMode 3), leg size, big signal candle


def hook(h, add, before=False):
    global core
    assert core.count(h) == 1, h[:80]
    core = core.replace(h, add + h if before else h + add)


if 'ZnCount' in core:
    # v15.1: one box per zone, last zone, order block type 2 / to the swing, the zones of an old leg go, MSS + its confirmation.
    # Test hooks (harness copy only, the .mq5 is not changed; key znLog), read by v151sep.py:
    #   B  every bar: the higher timeframe state + the chart's signals + the leg start time
    #   A  every zone count: bar, side, kind (1 CHOCH / BOS, 2 MSS), how many, the zones (tf:kind:top:bottom:candle time, L = the line)
    #   Z  every zone box: bar, side, tf, kind, top, bottom, left, right, signals counted, last zone, leg
    #   L  the last zone when it changes;  M  an MSS;  W / K / F  a side's MSS setup armed / confirmed / failed;  X  its zones all gone
    core = '#define CORE_V15 1\n#define CORE_V151 1\nstatic FILE *g_znLog = nullptr;\nstatic int g_lzLogId = -1;\n' + core
    hook('   if (!S.obM) return;\n   int d = g_T15;\n',
         '   if (g_znLog) fprintf(g_znLog, "B,%d,%d,%.10f,%.10f,%d,%d,%d,%d,%d,%lld\\n", EN.bi, g_T15, g_htO, g_htX, g_htE, (int)EN.evCU, (int)EN.evCD, (int)EN.evBU, (int)EN.evBD, (long long)g_htS);\n')
    hook('   if (g_zcN == 0 && S.znLine && g_zl.dir == d && g_zl.tch && !g_zl.spent && (kind == 1 ? g_zl.vs != 2 : g_zl.vs == 0)) g_zc[g_zcN++] = -1;\n',
         '   if (g_znLog)\n   {\n      fprintf(g_znLog, "A,%d,%d,%d,%d", EN.bi, d, kind, g_zcN);\n'
         '      for (int a = 0; a < g_zcN; a++) { int i = g_zc[a]; if (i < 0) fprintf(g_znLog, ",L"); else fprintf(g_znLog, ",%d:%d:%.10f:%.10f:%lld", g_zn[i].tf, g_zn[i].kind, g_zn[i].top, g_zn[i].bot, (long long)g_zn[i].t0); }\n'
         '      fprintf(g_znLog, "\\n");\n   }\n')
    hook('      g_zb[g_zbN].dir = d; g_zb[g_zbN].t1 = g_t;\n',
         '      if (g_znLog) fprintf(g_znLog, "Z,%d,%d,%d,%d,%.10f,%.10f,%lld,%lld,%d,%d,%d\\n", EN.bi, d, g_zb[g_zbN].tf, g_zb[g_zbN].kind, g_zb[g_zbN].top, g_zb[g_zbN].bot, (long long)g_zb[g_zbN].t0, (long long)g_t, g_zb[g_zbN].n, (int)g_zb[g_zbN].last, g_zb[g_zbN].leg);\n')
    h = '   g_lz = LastZn(d);\n}\n'
    assert core.count(h) == 1
    core = core.replace(h, '   g_lz = LastZn(d);\n'
        '   if (g_znLog && (g_lz >= 0 ? g_zn[g_lz].id : -1) != g_lzLogId)\n   {\n'
        '      if (g_lz >= 0) fprintf(g_znLog, "L,%d,%d,%d,%.10f,%.10f,%lld\\n", EN.bi, g_zn[g_lz].tf, g_zn[g_lz].kind, g_zn[g_lz].top, g_zn[g_lz].bot, (long long)g_zn[g_lz].t0);\n'
        '      else fprintf(g_znLog, "L,%d,-1\\n", EN.bi);\n      g_lzLogId = g_lz >= 0 ? g_zn[g_lz].id : -1;\n   }\n}\n')
    hook('      g_msPiv = piv; g_msLow = lp; g_msLowB = lb;\n',
         '      if (g_znLog) fprintf(g_znLog, "M,%d,%d,%.10f,%.10f,%d\\n", EN.bi, d, piv, lp, lb);\n')
    hook('                  if (S.mssCf) { rule = 4; cf = 1; cfTop = MfFirst(d == 1 ? 0 : 1, g_msLowB); cfTchB = NAI; cfPb = NAD; fix = NAD; }\n',
         '                  if (g_znLog) fprintf(g_znLog, "W,%d,%d,%d,%d,%d,%.10f,%.10f,%.10f,%.10f,%.10f\\n", EN.bi, k, seq, d, rule, opl, msAnch, cfTop, sl, fix);\n')
    hook('               cntMsCf++;\n', '               if (g_znLog) fprintf(g_znLog, "K,%d,%d,%d,%d,%.10f,%.10f\\n", EN.bi, k, seq, dir, sl, cfPb);\n')
    h = '{ cntMsF++; Cancel('
    assert core.count(h) == 1
    core = core.replace(h, '{ cntMsF++; if (g_znLog) fprintf(g_znLog, "F,%d,%d,%d,%d\\n", EN.bi, k, seq, dir); Cancel(')
    hook('         if (nSup == 0) Cancel(', '         if (nSup == 0 && g_znLog) fprintf(g_znLog, "X,%d,%d,%d,%d\\n", EN.bi, k, seq, dir);\n', before=True)
    # R = a setup armed (side, direction, kind, how many zones allow it); E = a waiting setup ended on this bar (filled, cancelled, replaced)
    hook('               src = isMs ? 1 : 0;\n', '               if (g_znLog) fprintf(g_znLog, "R,%d,%d,%d,%d,%d,%d\\n", EN.bi, k, seq, d, isMs ? 2 : 1, nSup);\n', before=True)
    hook('      if (dir != 0) Note(Id() + " FILLED");\n', '      if (g_znLog && dir != 0) fprintf(g_znLog, "E,%d,%d,%d,f\\n", EN.bi, k, seq);\n', before=True)
    hook('   void Decide()\n   {\n', '      int dir0 = dir, seq0 = seq;\n')
    hook('      if (closeWhy != "") BkCloseAll(k, closeWhy);\n   }\n};\nCSide g_side[2];\n', '      if (g_znLog && dir0 != 0 && (dir == 0 || seq != seq0)) fprintf(g_znLog, "E,%d,%d,%d,d\\n", EN.bi, k, seq0);\n      if (g_znLog && seq != seq0 && dir == 0) fprintf(g_znLog, "E,%d,%d,%d,d\\n", EN.bi, k, seq);\n', before=True)
elif 'ZnCandle' in core:
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
    if h not in core: h = 'string XSkip(int d, double piv, double opl, int lb)\n   {\n'   # v15.1
    assert core.count(h) == 1
    core = core.replace(h, h + '      if (g_xsLog) fprintf(g_xsLog, "%d,%lld,%d,%d,%.10f,%.10f\\n", EN.bi, (long long)g_t, k, d, piv, opl);\n')
    core = core.replace('#define CORE_V14 1\n', '#define CORE_V14 1\nstatic FILE *g_xsLog = nullptr;\n', 1)
open(sys.argv[2], 'w').write(core)
