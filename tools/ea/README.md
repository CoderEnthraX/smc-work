# tools/ea - checks of the MT5 Expert Advisor (SMC_Structure_EA_v11.1.mq5)

MetaEditor (the MQL5 compiler) only runs on Windows, so the EA is checked here in two ways:

1. **The core** (everything between `//==CORE-BEGIN==` and `//==CORE-END==` in the .mq5: structure engine,
   higher timeframe, entries, risk, loss recovery, pauses, news, hedge) is plain code. `extract.py` copies it out
   and `harness.cpp` compiles it as C++ with a TradingView-style order emulator (the rules of `tools/sim2/port111.py`).
   `cmp.py` runs the Python simulator and the harness with the same settings and compares every trade.
2. **The whole EA**: `mql2cpp.py` turns the .mq5 into C++ that compiles against `mt5sim.h`, a small fake
   MetaTrader 5 (ticks every 0.01 along TradingView's path, limit / market orders, SL / TP, hedging positions,
   deal history, global variables). `simmain.cpp` runs it tick by tick, optionally with forced restarts.

| Step | Command | Result when written (Oct 2026) |
|---|---|---|
| price files | `python3 mkdata.py` | fx.pkl, fx15.pkl, m1.bin, m15.bin from `../data/gold_m1_utc.npz` |
| build | `python3 extract.py ../../SMC_Structure_EA_v11.1.mq5 core_x.inc && g++ -O2 -std=c++17 -o harness harness.cpp` | |
| build | `python3 mql2cpp.py ../../SMC_Structure_EA_v11.1.mq5 ea_x.cpp && g++ -O2 -std=c++17 -o simmain simmain.cpp` | compiles with no warning from the EA |
| core vs simulator | `python3 tests1.py`, `tests2.py`, `tests3.py`, `tests4.py` | 105 runs: 104 identical, 1 float tie (a target exactly on a candle low) |
| shared hedge money | `python3 shared_chk2.py` | separate replay: 0 risk mismatches, 0 orders while halted or paused |
| whole EA, 1 year | `python3 fulltests.py` | 11 settings: same trades, same money to the cent (pending); prices within 0.01 (touch) |
| whole EA, restarts | `python3 restarts.py` | 10 settings x 484 restarts: identical to no restarts |
| table + drawings on vs off | `python3 onoff.py` | 4 settings, display ON with 249 restarts = OFF, identical trades |
| whole EA, 5.75 years | `python3 fulllong.py` | 1m: 2,817 trades, 15m best: 185 trades - same as the core, to the cent |
| group 41 OFF | all the rows above again | every output file byte-identical to the build before group 41 |
| group 41 calendars | `python3 calgen.py` | made-up MT5 calendars 2020-2026 (group 29 releases as high impact + medium / low / no-exact-time / EUR news, holidays) |
| group 41 file | `python3 calexport.py` | the EA saves the calendar (live, both clock kinds, USD / EUR / both): every line as expected |
| group 41 rules | `python3 caltests.py py` | Python simulator with the news rules worked out separately (`calflags.py`) = core |
| group 41 whole EA | `python3 caltests.py ea` | whole EA = core: tester (file), live (both clocks), hedge, restarts, EUR |
| group 41 effect | `python3 preeffect.py` | your 1m settings, group 29 releases, no new trades 1 / 2 / 4 h before: all about -0.13R per trade |

Notes
- `porthp.py` = the simulator with TradingView's exact session test for bars longer than 1 minute (f_ovl);
  on 1-minute bars it is identical to `port111.py` + news + "never apply" time rules.
- The harness option `grid 1` rounds order prices to 0.01 like MT5 (buy entry / stop down, target up);
  `fixTies 1` closes every trade whose stop is at the same price (the simulator closed only the first - a
  simulator bug found by the EA, it only matters for idea e / stacked trades with equal stops).
- Group 41: `mt5sim.h` has a fake MT5 calendar (`CalendarValueHistory` / `CalendarEventById`; `calMode 0` = times on the
  broker clock rule, `1` = with the broker offset of the moment) and files (`fileDir`); the harness option `simCal` puts
  the same list straight into the core. `porthp.py` takes `pre` flags (block new entries only).
- `htfSrv 1` makes the harness build 4h candles on the broker clock (17:00 New York), like TradingView and MT5.
  The earlier 15-minute search used 00:00 UTC 4h candles: +2,747 there, +1,069 with the real candles.
