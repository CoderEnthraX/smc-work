# EA v15.2 = EA v15.1 +
#   1. section 9: 'Only take entries in kill zones' + Asian / London / New York / London close (New York times, so they follow
#      the US summer / winter time; the IST times are in the names) + 'when a kill zone ends: cancel the waiting order and close
#      the open trade' (OFF = a setup armed in a kill zone keeps waiting after it, open trades run on). The entry hours above
#      still apply. Charts of 1 day and above: not used.
#   2. section 4: 'C5 set' and 'C6 + RSI set' - each switches its settings ON as if typed in (the settings themselves are not
#      changed; with the set OFF they work as set by hand); both ON = error
# usage: python3 ea152.py SMC_Structure_EA_v15.1.mq5 SMC_Structure_EA_v15.2.mq5
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: raise SystemExit('expected %d x, found %d x: %r' % (n, c, old[:160]))
    s = s.replace(old, new)


def box(t):
    return '//| ' + t.ljust(66) + ' |'


# ---------------------------------------------------------------- header (version on line 2)
rep('//| SMC Structure EA v15.1 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v15.1, same      |\n',
    '//| SMC Structure EA v15.2 (+ hedge) - MetaTrader 5 Expert Advisor     |\n'
    '//| The TradingView strategy "SMC Structure Strategy" v15.2, same      |\n')
rep(box('Owner: Punit. v15.1: zone boxes, last zone, OB 2, MSS, pauses.'),
    box('Owner: Punit. v15.2: kill zones, the C5 / C6 + RSI sets.'))
rep('#property version     "15.10"', '#property version     "15.20"')
rep('#property description "SMC Structure EA v15.1 - the TradingView strategy v15.1 rules in MetaTrader 5, plus a hedge mode."',
    '#property description "SMC Structure EA v15.2 - the TradingView strategy v15.2 rules in MetaTrader 5, plus a hedge mode."')
rep('   Print("SMC EA v15.1 ready: ", n,', '   Print("SMC EA v15.2 ready: ", n,')

# ---------------------------------------------------------------- inputs (new ones at the END of their section)
rep('''input double   InBcMax2    = 0.0;     // Big signal candle on charts ABOVE 1 minute - skip if BIGGER than this (unit above; 0 = off)
''', '''input double   InBcMax2    = 0.0;     // Big signal candle on charts ABOVE 1 minute - skip if BIGGER than this (unit above; 0 = off)
input bool     InC5        = false;   // C5 set - switches ON: min stop 0.5% of the price, skip the first setup of the day, yesterday's high / low, move of 12+ candles
input bool     InC6        = false;   // C6 + RSI set - switches ON: entries 13-21 (section 9), min stop 0.35%, yesterday's high / low, move of 12+ candles, RSI 1 hour (2) Pullback 50
''')
rep('''input bool     InFl1m      = true;    // Force-close hour on the 1-minute chart only (above 1 minute: no force close)
''', '''input bool     InFl1m      = true;    // Force-close hour on the 1-minute chart only (above 1 minute: no force close)
input bool     InKzOn      = false;   // Only take entries in kill zones (New York times - IST summer = mid-March to early November)
input bool     InKzAs      = false;   //   - Asian 20:00-00:00 New York (IST 05:30-09:30 summer, 06:30-10:30 winter)
input bool     InKzLo      = true;    //   - London 02:00-05:00 New York (IST 11:30-14:30 summer, 12:30-15:30 winter)
input bool     InKzNy      = true;    //   - New York 07:00-10:00 New York (IST 16:30-19:30 summer, 17:30-20:30 winter)
input bool     InKzLc      = false;   //   - London close 10:00-12:00 New York (IST 19:30-21:30 summer, 20:30-22:30 winter)
input bool     InKzEnd     = false;   //   - when a kill zone ends: cancel the waiting order and close the open trade
''')

# ---------------------------------------------------------------- core: settings
rep('''   int    mssN, mssSt, ldN2, ldSkip;   //   MSS swing size, confirmation stop; section 8: losses after the pause, days skipped
''', '''   int    mssN, mssSt, ldN2, ldSkip;   //   MSS swing size, confirmation stop; section 8: losses after the pause, days skipped
   bool   c5, c6;                      // v15.2 section 4: the C5 / C6 + RSI sets (switch their settings ON)
   bool   kzOn, kzAs, kzLo, kzNy, kzLc, kzEnd;   // v15.2 section 9: entries only in the chosen kill zones; at their end: flat
''')
rep('''            mssN = 2; mssSt = 0; ldN2 = 0; ldSkip = 1;
''', '''            mssN = 2; mssSt = 0; ldN2 = 0; ldSkip = 1;
            c5 = false; c6 = false; kzOn = false; kzAs = false; kzLo = true; kzNy = true; kzLc = false; kzEnd = false;
''')
rep('''      if (pxOff) { slBuf = 0;''', '''      // v15.2: section 4 - the C5 / C6 + RSI sets switch their settings ON, as if typed in (everything else stays as set)
      if (c5) { mnPct = 0.5; fstOn = true; ydOn = true; legMin = 12; }
      if (c6) { hrOn = 13; hrOff = 21; mnPct = 0.35; ydOn = true; legMin = 12; rsOn[1] = true; rsTf[1] = 3600; rsLen[1] = 2; rsMode[1] = 0; rsLvl[1] = 50; }
      if (pxOff) { slBuf = 0;''')

# ---------------------------------------------------------------- core: the kill zone clock (New York time at the bar close, like the entry hours)
rep('''bool   g_win = true, g_flatNow = false,''', '''bool   g_kzIn = true;   // v15.2: this bar may arm a setup - inside a chosen kill zone (or the kill zones are off)
bool   g_win = true, g_flatNow = false,''')
rep('''   g_win = !S.timeOn || S.cs >= 86400 || S.hrOn == S.hrOff || Ovl(g_tM, S.bMin, S.hrOn * 60, S.hrOff * 60);
''', '''   g_win = !S.timeOn || S.cs >= 86400 || S.hrOn == S.hrOff || Ovl(g_tM, S.bMin, S.hrOn * 60, S.hrOff * 60);
   // v15.2: the kill zones in New York time (Asian 20-24, London 2-5, New York 7-10, London close 10-12), tested like the hours
   // (a bar of 1 day or more always touches them)
   int nyM = MinOfDay(NyLoc(tc));
   g_kzIn = !S.kzOn || (S.kzAs && Ovl(nyM, S.bMin, 1200, 1440)) || (S.kzLo && Ovl(nyM, S.bMin, 120, 300)) ||
            (S.kzNy && Ovl(nyM, S.bMin, 420, 600)) || (S.kzLc && Ovl(nyM, S.bMin, 600, 720));
''')

# ---------------------------------------------------------------- core: the side - the end of a kill zone (switch ON), arming only inside one
rep('''      if (g_flatNow)
      {
         if (pos != 0) closeWhy = "Time flat";
         if (dir != 0) { cntCanc++; Note("CANCELLED - force-close hour"); }
         CancelSent();
         dir = 0;
      }
''', '''      // v15.2: 'when a kill zone ends' ON - outside the kill zones a waiting order goes and an open trade is closed (like the force close)
      if (g_flatNow || (S.kzEnd && !g_kzIn))
      {
         if (pos != 0) closeWhy = g_flatNow ? "Time flat" : "Kill zone end";
         if (dir != 0) { cntCanc++; Note(g_flatNow ? "CANCELLED - force-close hour" : "CANCELLED - kill zone ended"); }
         CancelSent();
         dir = 0;
      }
''')
rep('''         bool take  = g_win && (pos == 0 || (opp && S.rev) || addB);''',
    '''         bool take  = g_win && g_kzIn && (pos == 0 || (opp && S.rev) || addB);''')
rep('''(!g_win ? "outside session hours" : (opp ? "in a trade (reverse is off)" : (full ? "max trades open" : "already in a trade the same way")))));''',
    '''(!g_win ? "outside session hours" : (!g_kzIn ? "outside the kill zones" : (opp ? "in a trade (reverse is off)" : (full ? "max trades open" : "already in a trade the same way"))))));''')

# ---------------------------------------------------------------- adapter
rep('''   S.mssOn = InMssOn; S.mssN = InMssN; S.mssCf = InMssCf; S.mssSt = (int)InMssSt; S.ldN2 = InLdN2; S.ldSkip = InLdSkip;
''', '''   S.mssOn = InMssOn; S.mssN = InMssN; S.mssCf = InMssCf; S.mssSt = (int)InMssSt; S.ldN2 = InLdN2; S.ldSkip = InLdSkip;
   S.c5 = InC5; S.c6 = InC6;   // v15.2
   S.kzOn = InKzOn; S.kzAs = InKzAs; S.kzLo = InKzLo; S.kzNy = InKzNy; S.kzLc = InKzLc; S.kzEnd = InKzEnd;
''')
rep('''   if (InLzMin > 0 && InLzMax > 0 && InLzMax < InLzMin) return "Leg size (section 4): 'LONGER than' must be bigger than 'SHORTER than'";
   return "";
''', '''   if (InLzMin > 0 && InLzMax > 0 && InLzMax < InLzMin) return "Leg size (section 4): 'LONGER than' must be bigger than 'SHORTER than'";
   // v15.2
   if (InC5 && InC6) return "Section 4: turn on the C5 set OR the C6 + RSI set, not both";
   if (InKzOn && !InKzAs && !InKzLo && !InKzNy && !InKzLc) return "Only take entries in kill zones (section 9): turn on at least one kill zone";
   return "";
''')
# the C6 set uses the 1-hour candles for the higher-timeframe RSI
rep('''   tf[0] = InRsLTf; tf[1] = InRsHTf; tf[2] = InEmLTf; tf[3] = InEmHTf;''',
    '''   tf[0] = InRsLTf; tf[1] = InC6 ? TFF_H1 : InRsHTf; tf[2] = InEmLTf; tf[3] = InEmHTf;   // v15.2: the C6 set = 1 hour''')
# the table's exit counts: a kill zone end is a time close
rep('''   else if (cw == "Weekend flat" || cw == "Time flat") g_exFlat++;''',
    '''   else if (cw == "Weekend flat" || cw == "Time flat" || cw == "Kill zone end") g_exFlat++;''')

rep('''   Row("Exit - " + Two(S.hrFlat) + ":00 flat / weekend", I2(g_exFlat), clrSilver);''',
    '''   Row("Exit - " + Two(S.hrFlat) + ":00 flat / weekend" + (S.kzOn && S.kzEnd ? " / kill zone end" : ""), I2(g_exFlat), clrSilver);''')

open(dst, 'w').write(s)
print('written', dst)
