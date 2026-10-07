# tools/ea - checks of the MT5 Expert Advisor (SMC_Structure_EA_v12.3.mq5)

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
| build | `python3 extract.py ../../SMC_Structure_EA_v12.3.mq5 core_x.inc && g++ -O2 -std=c++17 -o harness harness.cpp` | (the v12.3 core = the v12.2 core: same binary) |
| build | `python3 mql2cpp.py ../../SMC_Structure_EA_v12.3.mq5 ea_x.cpp && g++ -O2 -std=c++17 -o simmain simmain.cpp` | compiles with no warning from the EA |
| core vs simulator | `python3 tests1.py`, `tests2.py`, `tests3.py`, `tests4.py` | 105 runs: 104 identical, 1 float tie (a target exactly on a candle low) |
| shared hedge money | `python3 shared_chk2.py` | separate replay: 0 risk mismatches, 0 orders while halted or paused |
| whole EA, 1 year | `python3 fulltests.py` | 11 settings: same trades, same money to the cent (pending); prices within 0.01 (touch) |
| whole EA, restarts | `python3 restarts.py` | 10 settings x 484 restarts: identical to no restarts |
| table + drawings on vs off | `python3 onoff.py` | 4 settings, display ON with 249 restarts = OFF, identical trades |
| whole EA, 5.75 years | `python3 fulllong.py` | 1m: 2,817 trades, 15m best: 185 trades - same as the core, to the cent |
| group 41 OFF | all the rows above again | every output file byte-identical to the build before group 41 |
| group 41 calendars | `python3 calgen.py` | made-up MT5 calendars 2020-2026 (group 29 releases as high impact + medium / low / no-exact-time / EUR news, holidays; forecast / actual numbers) |
| group 41 file | `python3 calexport.py` | the EA saves the calendar (live, both clock kinds, USD / EUR / both): every line as expected |
| group 41 rules | `python3 caltests.py py` | Python simulator with the news rules worked out separately (`calflags.py`) = core |
| group 41 whole EA | `python3 caltests.py ea` | whole EA = core: tester (file), live (both clocks), hedge, restarts, EUR |
| group 41 effect | `python3 preeffect.py` | your 1m settings, group 29 releases, no new trades 1 / 2 / 4 h before: all about -0.13R per trade |
| v11.2 OFF | all the rows above again | unit Price: every output file byte-identical to v11.1 |
| v11.2 units | `python3 butests.py` | Python simulator (`buf_at` / `lim_at` in porthp.py) = core in 10 of 10 pips / % settings over 5.75 years; 10 pips = 1.0, 50 pips = 5.0; whole EA = core in 5 of 5 |
| v11.2 restarts | `python3 burestart.py` | pips / % with forced restarts = no restarts |
| v11.2 pip | `g++ -O2 -std=c++17 -o piptest piptest.cpp && ./piptest`, `python3 pinepip.py` | the automatic pip for 21 MT5 names and 14 TradingView symbols |
| v11.2 effect | `python3 bueffect.py` | your 1m settings, buffer 1.0 / 10 pips / 0.02-0.5% / 50 pips: all lose (wider loses less per trade) |
| v12.0 OFF | `python3 cctests.py off <folder with the v11.2 harness + simmain>` | group 39 Off: core 5 settings x 5.75 years and whole EA 2 settings x 1 year byte-identical to v11.2 |
| v12.0 rule 3 | `python3 cctests.py py` | Python simulator = core in 26 of 26 settings (rule 3, near the broken level 1 / 3 / 8, pips / %, group 24 with rule 3 and rules 1 + 2, reverse, BOS stacks, partial, filters, Rule C; 12 with the fall back to rule 1 / 2: rules 1 + 2, 1, 2, none), 2021-2026; 54,348 entries at the close and 762 fall-back trades checked separately (next open, near the broken level, group 24, size, target; fall back at the broken pivot or the pullback level); fall back with rules 1 / 2 off = no fall back, identical |
| v12.0 whole EA | `python3 cctests.py ea` | whole EA = core in 8 of 8 (touch, near the level pending, near the level + group 24, hedge, Rule C, fall back pending / touch / hedge + Rule C), 484 restarts = no restarts (3 settings) |
| v12.1 OFF | `python3 rbtests.py off <folder with the v12.0 harness + simmain>` | cap choice / loss mark off: core 5 settings x 5.75 years and whole EA 2 settings x 1 year byte-identical to v12.0 |
| v12.1 recovery | `python3 rbtests.py py` | (the profit-mark settings were taken out when v12.2 removed it) Python simulator = core in 28 of 28 settings (cap 'start again from the base' with A / B / B+ / C / C+, split, base above the cap; loss mark and profit mark (won back from the deepest point) with A / B / C / C+, with the cap, the floor, 'stop for the day', your 10k account); every order's risk replayed separately from the closed trades in 20 of 20 |
| v12.1 Pine pre-news | `python3 rbtests.py pine` | the TradingView group 41 test written out from the Pine = calflags.py: 1m 0.5 / 1 / 2 / 24 h, 15m 1 / 2 h |
| v12.1 whole EA | `python3 rbtests.py ea` | whole EA = core in 8 of 8 (pending, touch, hedge per side, hedge shared without the loss pause; cap reset, loss mark, profit mark), 484 restarts = no restarts (3 settings) |
| v12.2 OFF | `python3 sptests.py off <folder with the v12.1 harness + simmain>` | split rules not chosen: core 7 settings (also the v12.1 cap reset + loss mark ON) x 5.75 years and whole EA 2 settings x 1 year byte-identical to v12.1 (whose profit mark is off) |
| v12.2 split rules | `python3 sptests.py py` | Python simulator = core in 18 of 18 settings (A / B / C split: default and low steps, longs only, counts from 2025, cap clamp / start again / stop for the day / step base above the cap, loss mark, floor, your 10k account, 15m); every order's risk replayed separately from the closed trades in 12 of 12 (each with 121-611 orders on a profit step); steps with plain Rule C = Rule C, Rule C split with no steps = Rule C |
| v12.2 whole EA | `python3 sptests.py ea` | whole EA = core in 5 of 5 (pending, touch, default steps, hedge per side, hedge shared without the loss pause), 484 restarts = no restarts (2 settings) |
| v12.3 sleep / wake | `python3 sleeptests.py <simmain of v12.2> <simmain of v12.3>` (v12.2 built with this simmain.cpp) | 19 settings (sleeps of 1-600 candles every ~2-50 hours; touch, pending, reverse, rule 3, rule 3 fall back, hedge, hedge shared Rule C split, 15m, the terminal restarted at the wake-up - 595 times in 2 of them): no sleep = v12.2 byte-identical in all 19; v12.2 made 5-140 entries at the wake-up tick and had a buy and a sell open together up to 54 times, v12.3 0 and 0; every catch-up worked out separately (candles read = candles missed, each high / low, every drop) with 0 differences; the 02:00 force close never skipped |
| v12.3 restarts | `python3 sleeptests.py <v12.2> <v12.3> restarts` | 238 restarts in 3 settings (touch, pending, hedge): every deal (time, price, lots, setup number) = no restarts in v12.3 (453 / 453, 453 / 453, 780 / 780); v12.2 had the same trades but only 227 / 453, 227 / 453, 391 / 780 setup numbers right (lost when a restart kept a waiting setup) |

Notes
- `porthp.py` = the simulator with TradingView's exact session test for bars longer than 1 minute (f_ovl);
  on 1-minute bars it is identical to `port111.py` + news + "never apply" time rules.
- The harness option `grid 1` rounds order prices to 0.01 like MT5 (buy entry / stop down, target up);
  `fixTies 1` closes every trade whose stop is at the same price (the simulator closed only the first - a
  simulator bug found by the EA, it only matters for idea e / stacked trades with equal stops).
- Group 41: `mt5sim.h` has a fake MT5 calendar (`CalendarValueHistory` / `CalendarEventById`; `calMode 0` = times on the
  broker clock rule, `1` = with the broker offset of the moment) and files (`fileDir`); the harness option `simCal` puts
  the same list straight into the core. `porthp.py` takes `pre` flags (block new entries only).
- `simmain` option `dump 1` prints the counter table as it is at the end of the run (e.g. `to` = a bar just after a release).
- v12.3 sleeps in `simmain`: `sleepEvery N` (a sleep every 1..2N bars), `sleepMin` / `sleepMax` (its length in bars, from a
  random tick to a random tick), `sleepSeed`, `sleepRestart 1` (the EA is loaded again at the wake-up); while asleep the
  broker goes on (pending orders fill, stops / targets hit) and the EA hears nothing. `wakeLog` (one line per wake-up),
  `dealsOut` (every deal with its exact time and comment), `dropLog` (the order book at every catch-up check, through the
  test hook `sim::onDrop` that `mql2cpp.py` puts at the start of `DropReached`, and the EA's Print lines in between).
  `mt5sim.h` has `iHigh` / `iLow` (shift 0 = the forming candle only up to this tick).
- `htfSrv 1` makes the harness build 4h candles on the broker clock (17:00 New York), like TradingView and MT5.
  The earlier 15-minute search used 00:00 UTC 4h candles: +2,747 there, +1,069 with the real candles.
