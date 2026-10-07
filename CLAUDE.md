# SMC Structure Strategy - project memory (read this first)

## The project
- Pine Script v6 strategy for TradingView: **SMC Structure Strategy**, traded on **XAUUSD 1-minute,
  OANDA feed**, executed at **FxPro MT5** through **TheConnector** (webhook). Alternative bridges:
  `metaapi_receiver/` (Cloudflare Worker -> MetaApi, about $0.039/hour = ~$29/month per account, the
  receiver only uses the free "MetaApi API") and the MQL5 VPS guide (`SMC_Strategy_v8.3_MQL5_VPS_GUIDE.pdf`).
- Owner: **Punit** (punit7870@gmail.com). Works from a phone. Wants **simple English, short examples with
  numbers, tables**. Times are **IST** (Asia/Kolkata).
- **Latest version: TradingView v12.2 + MT5 EA v12.3** = `SMC_Structure_Strategy_v12.2.txt` + `SMC_Structure_EA_v12.3.mq5`
  (EA v12.3 = the v12.2 rules + a safe catch-up after sleep / no connection / restart; the user asked for the EA file ONLY).
  No notes / handbook for v12.1 / v12.2 / v12.3, as the user asked - the v12.0 notes + handbook still describe everything
  else; see Versions. EA v12.2 kept; v12.1 files kept (they hold the profit mark that v12.2 removed). Before them:
  **v12.0** = `SMC_Structure_Strategy_v12.0.txt` + `_NOTES.txt` + `_HANDBOOK.pdf` (v11.2 + group 39
  "RULE 3 - enter at the close of the signal candle", all OFF; option "only if the close is near the broken level",
  default 3; option "if the close is too far: fall back to RULE 1 / 2"; see Versions). v11.2 files kept.
- **MT5 EA: `SMC_Structure_EA_v12.3.mq5`** (v12.2 + safe catch-up after a gap, always on, no setting; MT5 part only, core
  unchanged: CatchUp / DropReached / FilledReal; RestoreSides now restores the setup number) / `SMC_Structure_EA_v12.2.mq5` (v12.1 without the profit mark + ESeq SEQ_AS / SEQ_BS / SEQ_CS = 7 / 8 / 9 + group
  43 InSp1..InSpAdd at the very END; core StepBase(flPnl), money basNow) / `SMC_Structure_EA_v12.1.mq5` (v12.0 + ECap CAP_BASE
  = 3 + group 42 InLmOn / InLmAmt / InPmOn / InPmAmt at the very END; notes = the v12.0 EA notes) / `SMC_Structure_EA_v12.0.mq5` + `_NOTES.txt` (v11.1 / v11.2 files kept) = v12.0 rules in MQL5 (group 39 at the
  very END, after group 38; core r3Far / r3Fb / r3Use + side mktBar / cntR3 / cntR3Far / cntR3Fb; BkPlace(..., mkt): a rule 3 entry is a MARKET
  order at the next candle's first tick in touch AND pending mode, dropped if not filled on that candle; group 38 after
  group 41; core BufAt / LimAt / RoundTick; adapter PipAuto from symbol name, base / profit
  currency, SYMBOL_TRADE_CALC_MODE forex) + HEDGE mode (group 33 4th
  choice; money per side or shared) + group 40 (magic, touch / pending entries, broker clock FxPro UTC+2 EU
  DST, 20,000 warm-up bars, restart resume <= 5 bars via MT5 global variables, drawing). Same inputs /
  defaults as TradingView (groups 22 / 30 dropped). Core between `//==CORE-BEGIN==` / `//==CORE-END==` is
  plain code; checked in `tools/ea` (see its README): core vs simulator 105 runs identical (1 float tie),
  whole EA in a fake MT5 (tick per 0.01) = core to the cent over 5.75 years, 484 restarts identical. NOT
  compiled by MetaEditor yet (Windows only) - the user compiles (F7) and reports errors.
  Display (only draws, never changes a trade - checked on vs off + restarts): TradingView-style counter table
  (group 20: on/off, 8 positions, Small/Normal/Large, Full ~50 rows / Short ~15; MT5 rows on top: structure,
  HTF now, waiting setup, last signal, open P&L) and the higher timeframe drawn in purple (group 40: HTF
  BOS* / CHOCH* levels, EQ line, last 50 HTF CHOCH / BOS marks; 0 = none). Table counts start at EA start.
  **Group 41 (EA only, both OFF by default)**: news windows from MT5's built-in economic calendar (currencies
  "USD", High / High+Medium, 10 min before / 20 after, closes per group 25 "When a window starts", calendar
  holidays added when group 29 "Trade on US holidays" is OFF; master group 25 ON; intraday only) and
  "No NEW trades N hours before news" (default 1 h; calendar + group 29 releases; cancels the waiting order,
  skips signals, open trades run on). Live: reads now-3d..+35d every hour; calendar times -> UTC by the clock
  rule or today's offset, picked by US 08:30 NY releases. Tester has no calendar: user saves
  Common\Files\SMC_calendar.csv once live ("save the calendar to a file" ON; 2020-01-01 .. +60 days, UTC;
  columns utc,text,cur,imp,type,name); without the file a tester run with the calendar ON fails at init.
  Checked (tools/ea: calgen.py, calflags.py, calexport.py, caltests.py): OFF = byte-identical outputs; export
  exact; whole EA (file / live both clocks / hedge / restarts / EUR / calendar not answering) = core; Python
  separate calc (calflags.py + porthp.py `pre` flags) = core, 1m and 15m.
  Table "TODAY'S NEWS" rows (input "Show today's news in the table", default High+Medium, display only, works
  with the windows OFF): IST time, HIGH/MEDIUM, name, countdown, F forecast, after release A actual + MT5's
  "good / bad for USD" (impact_type); live re-read every 10 min (1 min after a release until the actual is in);
  the file has 3 more columns (result, forecast, actual).
  Forex Factory not used (WebRequest + this week only). Real MT5 calendar NOT tested yet.
- Work branch: `claude/tradingview-alerts-market-structure-53wugf` (push there; no PRs unless asked).
- Build / test tools: `tools/` (see `tools/README.md`).

## The user's working rules - always follow
1. **Before creating any new file, confirm with the user first** - say what the problem is and how you
   will solve it.
2. **New versions:** the user describes features one by one. For each: restate it in simple English,
   give a numeric example, ask the open questions (with your suggestion). At the end list every
   confirmed feature and **ask for WRITTEN permission** before building.
3. Every version:
   - ASCII only; the version comment on **line 2**;
   - new settings appended at the **END** (saved settings keep their places); new features **OFF by
     default** so the old behaviour is unchanged; extra dropdown choices go at the end of the list;
   - a **notes file** (plain English, one heading per feature, new part first with lines <= 78
     chars, then "EVERYTHING BELOW IS FROM THE vX NOTES" + the previous notes);
   - a **handbook PDF** (part 1 = what is new, part 2 = the v8.3 handbook pages 2..end);
   - **live must match the backtest** (higher timeframe from the last CLOSED candle, counts by entry
     time, etc.).
4. Checks before delivering: parser (`tools/parsechk.py`), settings count / order, declared-before-use,
   no name clashes, simulator "feature OFF = identical to the previous version", and each feature's
   rule checked against a SEPARATE calculation. Say clearly that the parser is not the TradingView
   compiler.
5. Git: `git -c user.email=punit7870@gmail.com -c user.name=Punit commit ...`; end commit messages with
   the Co-Authored-By / Claude-Session lines from the system prompt; no model names in commits.
   **Keep `main` updated with every new version** (the user's wish): after pushing the work branch,
   also run `git push origin HEAD:main` (a fast-forward of the same commit). `main` is meant to be the
   repository's default branch - the user switches it in GitHub Settings (this session's proxy cannot
   change repository settings). The other branch `claude/pine-script-smc-review-tdosam` is a
   different project (Market Structure indicator v15.x) - never merge it into `main`.
6. Be honest: correct earlier mistakes openly; 3 months of data is not enough - say so; never promise
   profit.

## Security rules - keep them exactly
- The **TheConnector access key** stays private: never ask for it or post it; it goes only into
  TradingView's webhook URL `https://webhook.theconnector.fr/YOUR_ACCESS_KEY`.
- Never paste TheConnector dashboard's static sample message.
- Alert message is ONLY `{{strategy.order.alert_message}}`, condition **"Order fills only"**.
- The strategy **never sends closeall**.
- Never put the MetaApi token, SECRET, MT5 password or a Telegram bot token into files, chat or
  screenshots.

## The user's current settings (as told in chat)
CHOCH only, RULE 1 + RULE 2, pullback 25%, target 3R, close and reverse OFF, entries 06:00-23:00 IST,
force close 02:00, weekend flat, account 10,000, base risk 50, Max leverage 100, Properties
leverage 300x. Loss recovery: used Rule C+ with cap 100,000 (emptied a 2023 backtest) - advised **Off**.
Recommended floor: "On - only cap the risk", 2,000 / 50% / 2.5%.

## Versions (short)
- v8.3 base; v8.4 trade direction (LONG / SHORT copies); v9.0 ideas a-g (group 34); v9.1 cancel a waiting
  order on a new same-side BOS, new Rule A, "Stop permanently" default.
- v10.0 Rule A / B / C never below base; v10.1 A+ / B+ / C+ (total below 0); v10.2 "loss recovery counts
  from" (whole history / when live / a date); v10.3 split the loss over N trades; v10.4 account floor +
  profit lock (group 35).
- v11.0: group 36 pause D days after N losses in a row (Mon-Fri, every day for crypto / 24-7); "higher
  timeframe favourable" choices; group 37 higher-timeframe equilibrium first (each HTF CHOCH / BOS closes
  the gate, a touch of the % opens it).
- v11.1: "against the higher timeframe" choices (rule 1 only); "auto" choices (against the HTF until the
  equilibrium touch, then with it).
- v11.2: group 38 "Stop buffer unit" (4 inputs at the end, 122 total): Price (as now) / Pips / % of price; pips 10, %
  0.02, pip size 0 = auto (gold 0.10, silver 0.01, BTC 1, ETH 0.10, forex 0.0001, JPY 0.01, else 10 x mintick); %
  = of the CHOCH* level; rounded to mintick; group 24 min / max stop read in the same unit (pips, or % of entry);
  trailing stop uses it; table row 47. Pine f_stBuf / stPipSz; sim port112 buf_at / lim_at (tools/patches/sim112.py).
- v12.0 (user asked, permission "just build it", NO profit test - user declined to spend tokens). REDONE once: the first
  build (4 inputs: RULE 3 / RULE 4 = entry-to-stop limits 3 - 30, skip / fall back) misread the user. What they meant:
  group 39 (4 inputs at the end, 126 total, all OFF): stR3On "RULE 3 - enter at the close of the signal candle"
  (market at the signal close = fills next open, wherever it closes; rules 1 / 2 unused; HTF filters apply, no
  agreement needed); stR3BrkOn "only if the close is near the broken level" + stR3Brk 3.0 = the most the close may be
  beyond the pivot the candle broke (_piv: stCeilPrev long / stFlorPrev short; unit of group 38 like group 24,
  f_stR3Lim); too far = skip, or with stR3Fb "if the close is too far: fall back to RULE 1 / 2" (asked after the
  redo) the normal rule 1 / 2 setup (_r3Fb = _r3Far and stR3Fb and (stR1On or stR2On); _r3Use = stR3On and not _r3Fb
  -> keeps the v11.2 _use / stRule). R1+R2+R3 = rule 3 then 1 / 2; only R3 = rule 3 or skip.
  "Skip if the stop is CLOSER / FURTHER than" = the EXISTING group 24
  inputs (0 = off), already for rules 1 / 2 / 3 - nothing new. stRule 3 = market; one chance (stMktBar; cancelled if
  not filled the next bar, or 2 bars when reverse closes an opposite trade first); stEnt = close; strategy.entry
  limit = na; table row 48; audit "R3 ARMED" / "SKIP - RULE 3: close X beyond the broken level".
  Sim: port120.py / porthp.py r3On / r3BrkOn / r3Brk / r3Fb + pbSwp2 (tools/patches/sim120.py). Checks (cctests.py): OFF
  byte-identical (sim 4, core 5 x 5.75 y, whole EA 2 x 1 y); Python = core 26/26 settings 2021-26 (12 with the fall
  back); 54,348 market entries + 762 fall-back trades (rule 2 pivot / rule 1 pullback level from the engine) checked
  separately; fall back with R1 = R2 = off = no fall back, identical; whole EA = core 8/8; 484 restarts identical (3).
  Parser PARSED OK. Side numbers (recovery off, user settings, 2021-26, NOT a profit study): r3 -11,312 (1,943 tr),
  r3 + near 3 -11,572 (1,857), + fall back -11,693 (1,909; 74 fell back); v11.2 -11,253 (1,844).
- v12.1 (user asked; ONLY the two strategy files, no notes / handbook; NO profit test). First built "without the profit rule"
  (I misheard: the user had said WITH it) - the profit mark (4.) was then added to the same v12.1 files:
  1. HARD CAP 4th choice (end of the list) "Start again from the base risk (forget the losses)" (EA CAP_BASE = 3): next risk >
  cap (the old test, after split) -> if carried > 0.005: seqLoss = seqTot = 0, capOn false; risk = min(base, cap); never halts.
  2. group 42 (Pine + EA, end): stLmOn "Start again from the base risk when the losses carried reach" + stLmAmt 300: after the
  closes are counted, carried >= amt - 0.005 -> seqLoss = seqTot = 0 (stCntLm); all six rules; recovery Off = nothing.
  3. Pine only, group 41 (before 42): stPreOn "No NEW trades in the hours before news (group 29 US releases)" + stPreHrs 1.0
  (0.1-24) = the EA's PreHit: today + tomorrow f_auDay (stAuN1..4), time_close < T and time_close + bar > T - hours; needs
  news master + group 29 ON + intraday; in stGo (cancels waiting orders, skips signals, open trades run on); audit / BLOCKED
  NOW "news soon - no new trades". Table rows 49 / 50 (51 rows). Pine 130 inputs, EA 145.
  4. group 42 (after the loss mark): stPmOn "Start again from the base risk once this much is won back" + stPmAmt 200 (EA
  InPmOn / InPmAmt): stCarPk = the most carried in the current losing run (0 when nothing carried; cleared by every reset:
  cap Base, Day reset, loss mark); after the closes (after the loss mark): carried > 0.005 and stCarPk - carried >= amt -
  0.005 -> seqLoss = seqTot = 0 (stCntPm); then stCarPk = carried <= 0.005 ? 0 : max(stCarPk, carried). Pine 132 inputs,
  EA 147; table row 50 = "BACK TO THE BASE - loss / profit mark (group 42)".
  (Why "won back": Rule C is already at base at a new high, so "the account made $200" would change nothing.)
  Tools: patches/patch121.py, ea121.py, sim121.py (port121.py; porthp capAct "Base", lmOn / lmAmt); ea/rbtests.py. Checks:
  OFF byte-identical to v12.0 (core 5 x 5.75 y, whole EA 2 x 1 y; porthp 2 + port121 3 months); Python = core 28/28;
  separate risk replay from the closed trades 20/20 (every order's risk; 18-1,216 cap resets, 16-250 loss-mark resets,
  23-91 profit-mark resets);
  Pine pre-news written out from the Pine = calflags.py 6/6 (1m 0.5 / 1 / 2 / 24 h, 15m 1 / 2 h); whole EA = core 8/8
  (shared hedge WITHOUT the loss pause - with it, same-candle closes of the two sides are ordered by tick in the EA and
  by candle in the core -> pause can differ; pre-existing, also v12.0; big Rule C sizes in shared hedge also differ via the
  leverage cap on live equity); restarts 484 identical (3). Parser PARSED OK. Side numbers (one 10k account from Jan 2021,
  user settings, Rule C split 3, lev 100): cap 200 'start again' emptied 19 Aug 2022 (482 trades); loss mark 300 emptied
  13 Apr 2023; profit mark 200 alone emptied 10 May 2022 (440 trades, risk up to 1,356 - it does not limit the risk).
- v12.2 (user asked + answered 7 questions; ONLY the two strategy files; NO profit test): built from v12.1 as it was BEFORE
  the profit mark (git ec60510 files, so the profit mark is gone: Pine 132 -> 130 + 8 = 138 inputs, EA 147 -> 145 + 8 = 153).
  'Loss-recovery sizing' + 3 choices at the end: "Rule A split / Rule B split / Rule C split (X, the base grows with the profit
  - group 43)" = Rule A / B / C (loss since the high, split, cap, loss mark all as before) but the BASE = max(base risk,
  min(step base, hard cap)); step base = OPTION 2 (the user's choice): the step AMOUNT / its parts, not the actual profit, so
  a loss never makes the next base bigger; profit = stFlPnl (counted closed trades, never reset). Group 43 (8 inputs, user
  left the steps after 1,000 to me): step 1 200 / 3, step 2 500 / 5, step 3 1,000 / 8, then every 500 more (stSpInc) one more
  part (stSpAdd 1): 66.67, 100, 125, 166.67 (1,500 / 9), 200 (2,000 / 10), 227.27, 250, 269.23, 285.71, ... 312.50 (5,000 / 16),
  384.62 (10,000 / 26); always rising, never reaches 500 (500 / 1). Next risk = max(step base, Rule A / B / C ask). The step
  base is clamped to the cap so it never triggers the cap action itself; the cap's 'start again' gives min(step base, cap).
  Pine f_stStep / stSplitM / stBaseNow, table row 51 "PROFIT STEPS"; EA StepBase / basNow / SpTxt; seqPlus = 4..6 only.
  Tools: patches/patch122.py, ea122.py, sim122.py (port122.py; porthp seqMode As / Bs / Cs, sp1..spAdd, step_base);
  ea/sptests.py (rbtests.py lost its profit-mark settings). Checks: OFF byte-identical to v12.1 (core 7 incl. cap reset +
  loss mark, whole EA 2; porthp 2 + port122 3 months); Python = core 18/18; every order's risk replayed separately 12/12 (121-611
  orders on profit steps each); steps with Rule C = C, C split with no steps = C; whole EA = core 5/5; restarts identical (2).
  Parser PARSED OK. Side number: user 1m settings, Rule C split, one 10k account from Jan 2021 = empty 3 Mar 2021 (profit
  never reached 200 - the steps never started).
- v12.3 (MT5 EA ONLY, user asked after a real case: the laptop slept; at the wake-up MT5 opened a buy AND a sell at once, and a
  CHOCH right after was not traded). Cause: up to v12.2 every missed candle was handled as live (ProcessBar + ExecuteAll each):
  entries of old candles went out at today's price, and a trade opened during the catch-up was invisible to the next missed
  candles (GatherIO(tEnd) ignores positions opened after tEnd) -> buy + sell; those open trades then blocked the new CHOCH.
  v12.3 (always on, no setting, core unchanged = same harness binary): OnTick with 2+ missed candles -> CatchUp: the missed
  candles are processed WITHOUT trading; before each, DropReached drops a side whose waiting entry was reached in that candle
  (a rule 3 market entry always) unless the broker filled it (FilledReal: open position, or an IN deal with that comment in
  the last 10 days); then the forming candle so far (iHigh / iLow(0); only when TimeCurrent() > t0 or high > low, so a wake at
  a candle's first price fills like TradingView's open); then ONE ExecuteAll (exits, stop moves, setups still waiting) +
  SaveState. One missed candle (the normal new bar) = the old path, unchanged. The TryInit restart tail uses the same CatchUp.
  Live only: waits up to 60 s for SERIES_SYNCHRONIZED after a gap (missed candles still downloading). Old slip found and fixed:
  RestoreSides did not restore g_side.seq when a restart kept a waiting setup (seq back to 0 -> comments reused; FilledReal
  could match an old deal). Log lines: "SMC EA: setup L12 dropped - its entry 4105.00 was reached while the EA was offline
  (candle ...)", "N candle(s) missed ... - read without opening trades". Entries reached while asleep are LOST (no late entry):
  the EA cannot copy TradingView's fill then - so the EA and TradingView differ after every sleep; sleep Never / a VPS.
  Tools: patches/ea123.py; mt5sim.h iHigh / iLow (forming candle so far), sim::onDrop hook, sim::printTo; mql2cpp.py array
  parameters + the hook; simmain sleepEvery / sleepMin / sleepMax / sleepSeed / sleepRestart / wakeLog / dealsOut / dropLog /
  verbose; ea/sleeptests.py. Checks: no sleep = v12.2 byte-identical (19 settings + 8 earlier; 484 restarts, 8 settings);
  sleeps 1-600 candles in 19 settings (touch, pending, reverse, rule 3, fall back, hedge, shared Rule C split, 15m, restart at
  the wake-up): v12.2 2-140 entries at the wake tick and buy + sell together up to 54 times; v12.3 0 / 0; every catch-up worked
  out separately (candles, high / low, drops) - 0 differences; the 02:00 force close never skipped. Restarts (238, 3
  settings): every deal incl. the setup number = no restarts (v12.2 only 227 of 453 numbers right). NOT compiled in MetaEditor.

## How the v11.1 code works (key points)
- 118 inputs (v11.2: 122, + group 38 stop buffer unit). Groups: 20 strategy, 21 risk / loss recovery, 24 safety, 25 daily blocking windows,
  33 direction, 34 v9 ideas, 35 floor, 36 loss pause, 37 equilibrium.
- One higher-timeframe request: `f_tfTrC` returns `[trend, leg start, leg extreme, CHOCH/BOS count]`
  of the last CLOSED HTF candle. Auto HTF: 1m->15m, 5m->1h, 15m->4h, 1h->1D, 4h->1W, 1D->1M.
- RULE 1 = limit at the pullback % of the leg (follows new extremes); RULE 2 = limit at the broken pivot,
  only when the HTF agrees; both ON: agree -> rule 2, otherwise rule 1. Same stop (CHOCH level +
  buffer) and target (R) for both.
- `stGo` = every block (news, weekend, daily limit, cap, profit target, floor, loss pause, equilibrium
  gate); when it is false a waiting order is cancelled ("CANCELLED - blocked"), open trades run on.

## What the data showed so far
- Edge per trade: old one-year files (reverse ON): 2021-22 -0.12R, 2023-24 -0.13R, 2025-26 -0.04R.
  Current settings (reverse OFF, 156 trades in 2026): +0.14R but NOT proven (95% range -0.10..+0.38R;
  about 480 trades needed).
- One trade does not predict the next (no streaks) -> no recovery / martingale rule can help.
- Floor with real 1-oz steps: 2,000 / 2.5% = good insurance (profitable years 91% vs 99%, worst year
  -1,929 vs -10,049); 500 / 10% is too tight (skips trades).
- 3 months (Feb 25 - May 26 2026, simulator, user settings): everything off +793; equilibrium 50%
  +1,410; pause 3 losses / 2 days +1,244; favourable -82; against +767; against + equilibrium +941;
  auto 50% -511. Trades against the 15m won more than trades with it (same entry too) in that period.
- Hours (old files): 09:00-12:59 IST worse in all 3 years, 17:00-20:59 better - NOT seen with the current
  settings (09-13 was profitable in 2026). Day of month: no consistent pattern.
- Stop size: the tightest 20% of stops were worse in all 4 data sets (-0.14..-0.17R vs average), the
  widest 20% better.
- Targets (3 months): 3R best profit, 2R smaller drops; break-even / partial / step / trailing all
  reduced profit. Kelly ~7.7% full - stay at 0.5% risk until the edge is proven.
- **5.75 YEARS (FxPro M1 2021-01-04 .. 2026-10-02, simulator port111, user settings, account 100,000 x
  leverage 10 = the 10,000 x 100 size cap): v11.1 LOSES.** 2,839 trades, 31% wins, -0.13R/trade (95%
  -0.18..-0.08), -18,514 at 50 risk. Per year R: 2021 -0.19, 2022 -0.24, 2023 -0.16, 2024 -0.17,
  2025 -0.04, 2026 +0.04. Costs (cmU 0.6/oz) = 0.09R/trade; before costs still -0.04R (2021-24 negative).
  Same 3 months OANDA vs FxPro: 85 of ~114 trades identical, +0.14R vs +0.20R -> the feed is fine.
- All 13 v11.1 choices lose over 2021-26 (against, favourable, equilibrium, against+eq, auto, pause,
  2R, reverse ON, pullback 50, rule 1 only, rule 2 only, CHOCH+BOS); none positive in 2021-23.
- ATR minimum stop (skip if stop < X x ATR14 of 1m, X 4..12): no X positive in 2021-23 (-0.17..-0.23R)
  -> NOT worth a version. The existing fixed "skip if stop closer than" $5 was better (-0.07R 2021-23,
  -0.015R 2024-26) but still not positive. Stops are 1.5..30x ATR14(1m); median stop 5 USD (2021) ->
  19 USD (2026).
- Scripts: scratchpad only (fx.pkl / atr14.pkl / port112x.py with atrX / modes.py) - rebuild from
  tools/data/gold_m1_utc.npz if needed.
- **Six recovery rules, 2021-26** (user settings + split 3 + pause 4 losses / 3 days + cap 100,000 'Day',
  account 10,000, lev 100). One account from Jan 2021: ALL empty - Off 27 Feb 2024, A / C / A+ / C+
  Mar-Apr 2022, B / B+ 19 Feb 2021. Fresh 10,000 each year (net): Off -3,283 / -3,569 / -2,530 / -1,583
  / -422 / +1,097 (sum -10,290, never empty); A sum -7,301 (2 empty); B +9,159 (4 empty, 2023 +35,991
  luck); C -10,717 (2); A+ -17,834 (1); B+ -15,888 (2); C+ -17,948 (1). Page with every month:
  https://claude.ai/artifact/9SNr14gQjCUEWiWBuTt9Cq (scripts: scratchpad rec6/).
- **15-minute chart** (same six-rule test): no account emptied; Off +665 (fresh yearly) / +568 one
  account; Rule C +926 / +1,238. Only 24-80 trades a year ($50 risk + 1-oz steps skip stops > ~$62);
  83% of trades closed by the 02:00 force close / weekend; 6 of 359 reached 3R.
- **Rule C search (~1,300 runs, pick on 2021-23, check on 2024-26)**: 1m 0/126 and 5m 0/126 entry
  settings profitable on 2021-23; 15m 20/120. Auto 50% mode = the one option that helped every entry
  setting in BOTH halves (hours 17-23 = in-sample only). BEST: 15m, CHOCH only - auto (eq 50), rule 1+2,
  pullback 50, target 2R, reverse off, stop buffer 1, cancel-on-new-BOS OFF, Rule C split 1, cap 300
  "Clamp to the cap and carry on", pause 4 losses / 3 days, hours / force close / weekend as now.
  One 10,000 account: +629 / +532 / +358 / +514 / +164 / +550 = +2,747, never below 10,000, worst drop
  765, biggest risk 321, 22 of 62 months losing (worst -413 Sep 2025), 197 trades. Recovery off same
  entries +1,232 (+0.13R/trade, 95% +0.01..+0.24, t 2.15) -> promising, NOT proven (search bias).
  Neighbours stable (23 of 28 one-value changes profitable all 6 years). Same setting on 1m: empty 2021;
  5m: -7,398. Next: user checks it in TradingView 15m OANDA, then demo 2-3 months. Page:
  https://claude.ai/artifact/Dr2foQNDBHDN2w552fswBc (scripts: scratchpad c15/, portx.py = port111 + barSec).
  **CORRECTION (found while checking the EA):** that search used 4h candles from 00:00 UTC. TradingView
  OANDA and FxPro MT5 4h candles start at 17:00 New York. With the real candles: 186 trades +1,069
  (2021 +420, 2022 -546, 2023 -472, 2024 -101, 2025 +1,217, 2026 +550); recovery off +61. NOT an
  every-year winner; told the user (EA notes section 12). 1m results unaffected (15m HTF aligned).
- **1-minute Rule C search (~1,240 runs + ~50,000 shuffled replays)**: NO 1m entry edge. Stop buffer:
  negative worst (-1 -> -0.28R), wider better (5 -> -0.03..-0.10R; 7-20 about 0). Hours 13-21 / 12-23
  help. Best 6-year entry: yours + buffer 20 + hours 13-21, recovery off = -116 (-0.007R, break-even).
  The 12 best on 2021-23 ALL lost on 2024-26. Rule C on these: past +9,513 (pick, all 6 years +) up to
  +95,137 (hindsight), and 20/20 start dates positive for some - BUT same trades shuffled by day: account
  emptied 44-93% on 10k; on 100k cap 1,000 average -1,703 (median +5,307, worst 5% -31,880), cap 10,000
  average -1,043 (worst 5% = whole 100k). Classic martingale illusion. 15m setting: 0% emptied, 1.9%
  loss when shuffled. Advice: no Rule C on 1m; negative buffer not worth building. Page:
  https://claude.ai/artifact/UPFGWtDYhMAsuHxD1g98Rv (scripts: scratchpad m1c/, replay = shuffle2.py).
- **1 Jan 2024 - 2 Oct 2026, 1m, user entries, Rule C / C+ split 3, pause 4/3, cap 100k Day**: one 10k
  account from Jan 2024 - ALL six (buffer 1.0 / 0.25 / 0) emptied (C: 30 Aug / 12 Jul / 26 Jul 2024;
  C+: 22 Jan 2025 / 5 Sep 2024 / 4 Apr 2025); buffer 2.5 also emptied (Aug 2024); Off -1,153. Fresh 10k
  each year: C buf 1.0 = empty 2024, +3,325 2025, +2,978 2026; buf 0.25 / 0 empty every year with C.
  Page (months + Jul-Sep 2026 weeks): https://claude.ai/artifact/SoKqievj1Aep7Fn2dGug8h (scratchpad p24/).
- **News windows**: v11.1 defaults block NOTHING (master ON, windows 1-3 OFF, automatic US news OFF). With
  "Automatic US news windows" ON (NFP, jobless claims, ISM M/S; -10/+20 min; close open trades) added to
  the simulator (scratchpad p24/portn.py + usnews.py, identical when off; 0.74% of minutes blocked):
  2024-26, 1m, user entries, split 3: pause 4/3 -> C every buffer EMPTY, C+ 0.25 / 0 EMPTY, C+ 1.0 +1,361,
  Off -720. Pause grid (N 2-8 x D 1-10, 37 settings): best C 1.0 = 4/2 (+8,996 one account), C 0 / 0.25
  = no pause (+13,200 / +12,206), C+ 1.0 = 4/2, C+ 0.25 = 4/2, C+ 0 = 4/1, Off = 2/5 (+1,010). BUT the
  shuffle test: Rule C 68-82% emptied, C+ 32-42%, average a loss for all -> luck, not an edge. Page:
  https://claude.ai/artifact/5TZMG1P6MunBcx9swjDyGy
- **1h and 4h charts** (scratchpad h14/: porth.py = portn + sessOff ('Time-of-day filters: Never apply' =
  no session, no force close, no weekend cutoff); 1h bars on the hour, 4h from 17:00 NY; HTF auto 1h->1D,
  4h->1W). Too few trades to prove anything: 1h ~11/yr, 4h ~21/yr. 1h your entries (time AUTO): +0.09R
  (95% -0.04..+0.22, 64 trades), 62 of 64 closed by the 02:00 force close / weekend; $50 = +148 in 6 yrs.
  4h time AUTO: almost no trades. 4h best (CHOCH+BOS, R1, 25%, 2R, reverse ON, time NEVER): +0.14R
  (95% -0.08..+0.37, 120 trades), +BE 1R +0.18R; mostly 2023; with $50 + 1-oz steps 38% of stops
  unsizable and NO trades 2025-26; $200 risk +2,172 (BE +2,955) with a -1,267 year. 4h against / auto =
  fit on 2021-23, failed 2024-26 (-0.6R); 4h longs only = gold's bull market, not an edge.
  Verdict: 15m still the best-supported; no new version for 1h / 4h.
- **15m best setting, close & reverse / hedge**: reverse ON +2,533 (Rule C) / +1,089 (off) vs OFF +2,747 /
  +1,232 -> keep OFF. Hedge (two copies Longs only + Shorts only, v8.4 method) +2,773 / +1,230 = no
  change: long and short trades never overlapped (0 of 92; auto mode allows one side at a time). Plain
  CHOCH 15m (no auto): hedge +825 vs one copy +1,037 (8 of 154 overlapped) -> no benefit.
- **1m hedge (two files Longs only + Shorts only, reverse OFF, $50, recovery off, 2021-Oct 2026)**: your
  hours -30,771 (vs one file -18,514; 4,762 trades, -0.13R; 1,801 of 2,264 buys overlapped a sell; 10k
  empty 28 Sep 2022). Stop/target only (Time-of-day filters Never apply): hedge -9,825; ONE file -1,554
  (-0.02R, about break-even - the time rules hurt the 1m); longs file +3,630 = gold's rise. Page:
  https://claude.ai/artifact/GtJJSsyexuxQt44RiPsi5F (scratchpad hg1/).
- **1m hedge with Rule C split 3, 3R** (each file its own Rule C memory, then both merged BY CLOSE TIME into
  one shared 10,000 account, stop when empty): ALL versions empty - two files: your hours no pause 5 Nov
  2021, pause 4/3 30 Dec 2021; no time rules no pause 15 Nov 2022, pause 4/3 1 Mar 2024. One file empty
  2022 in every version. A combined Rule C across two files is impossible in TradingView (a strategy cannot
  see another's trades). Page: https://claude.ai/artifact/1y7MdMJPDGu8D2UmTiDviQ (hg1/runC.py, repC.py).
- **1m SHARED Rule C (buys + sells at once on one account, one Rule C split 3 from the shared loss - what an
  MT5 EA could do; replay hg1/shared.py, checked vs simulator 24/24 empty-or-not)**: one account from Jan 2021
  empty in every version (your hours 14 Jul 2021; no time rules 5 Dec 2022). Fresh yearly best (no time
  rules, no pause): +4,732 / -1,834 / +3,668 / EMPTY Feb 2024 / +4,533 / +1,265. Flat $50 both sides lost
  every year. Not worth an MT5 EA. Page: https://claude.ai/artifact/6CZ9PWMAfb516YtBKwAcfs

- **Stop buffer size, 1m, user settings, 2021 - Oct 2026 (v11.2 rules, rounded)**: 1.0 = 10 pips -18,514 (-0.13R, 5 of 6
  years lose); 0.02% -22,350; 0.05% -19,840; 0.1% -17,216; 0.2% -12,519 (-0.12R); 0.5% -6,768 (-0.08R); 50 pips -10,583
  (-0.10R); all but 1.0 / 0.02% lose every year. Wider loses less per trade, none profitable. 3 months (OANDA, port112):
  1.0 +793, 0.02% +794, 0.05% +284, 0.1% -277, 0.2% -698, 50 pips -592 (opposite order). tools/ea/bueffect.py.
- **User's 10 TradingView screenshots (Oct 2026), 1m FxPro, 1 Jan 2023 - 2 Oct 2026**: CHOCH only, R1+R2, pb 25, 3R,
  buffer 1.0, reverse OFF, PULLBACK RULE 3 (pbSwp2) ON, hours 06-23 / 02:00 / weekend, 50 risk, lev 100, Rule C split 3
  cap 100,000 Day, pause 4/3, auto US news ON, commission 30/lot/side. Python (porthp + pbSwp2, scratchpad u23/portu.py)
  = core harness to the cent: 564 trades, -9,974.93 (one 10k account empty: <500 on 30 Sep 2024, last trade 5 Nov 2024;
  Aug 2024 -8,800, risk up to 4,082). Fresh 10k yearly: 2023 +37, 2024 empty, 2025 +4,203, 2026 +1,608. Recovery off:
  1,266 trades -3,843 (2023 -0.21R, 2024 -0.12R, 2025 +0.08R, 2026 -0.02R). User's TV screen showed PF 1.15 - asked for
  the TV Performance Summary + List of Trades. Page: https://claude.ai/artifact/FDhyjgQDQ4kCyWSZmwauDE
  **TV screen for these settings (Deep, OANDA): +10,408, 1,253 trades, 35.83% win, PF 1.15, largest win 4,812 / loss
  -1,180, top 5 +15,712, other 1,248 -5,304, max DD 29.81%.** Entries match ours (recovery off 1,266 trades, 35.78%).
  52 "noisy feeds" (every bar moved by N(0, 2-10 cents), 75-80% same trades like OANDA vs FxPro; scratchpad
  u23/feeds.py): Rule C 47 empty / 5 profit (best +9,579; set 42 = +9,510, PF 1.16, -1,277, top5 +15,269 = TV's
  shape) -> TV = a lucky path. Recovery off 0/52 profitable (-5,472..-1,345). Cap 10,000 = identical (max risk 4,082;
  4,474 in any set); caps 2,000 / 1,000 / 500 Day: 38 / 32 / 23 of 53 empty. The 30 Sep TV Rule C+ export (248f2)
  emptied by 27 Mar 2023 while FxPro same settings survived to Oct 2024 (75% same entries; one extra TV loss 5 Jan).
- **Win/loss pattern study (Oct 2026, PDF sent: scratchpad pat/SMC_win_loss_patterns_2021-2026.pdf, 12 pages)**: user's
  TV settings, recovery off, 2021-01 .. 2026-10: 1,844 trades, -0.12R, -11,253 (Python = core). Exits: SL 53%, TP 8%,
  02:00 close 23% / news 11% / weekend 6% (those +0.37R, 64% win = most winners). Before entry winners ~= losers (rule,
  wait, 1h trend); tight stops (<0.165% of price) -0.31R both halves; wide stops look better only because 42% end at
  02:00 (TP vs SL stops $6.02 vs $5.72). 10-14 IST worse, 18-20 better both halves; 1st trade of day worst. Losers median
  2h15, TP 6h. 23% of SL trades were +1R first but BE/step/partial/trail/smaller targets all worse (BE -15,222).
  One change alone (grid1): none positive 2021-23; lose less: no time rules -524 (but 39/40 noisy sets lose, swap not
  modelled ~2,100), 13-21 -5,679, buffer 10 -5,270, min stop $8 -1,295, rule 2 only -5,901. 720 combos (grid2): 32 +
  on 2021-23, 3 + in both; #1 on 2021-23 +0.14R -> 2024-26 -0.05R; rank corr A vs B -0.07. "Lucky island" = no time
  rules + buffer 3 + min stop $8 + 5R + eq 50: +2,141 (+0.07R, 40/40 noisy sets + recovery off) but 0 of 13 one-value
  neighbours + in both halves; Rule C empties it 9 Jun 2026. Rule C 40 sets emptied: yours 35, 13-21 15 (real +9,020),
  buffer 5 40, rule 2 only 40, min $8 21. Streaks 9-17 losses every year; split 3: 18 losses = 11,225 carried.
  Scripts: scratchpad pat/ (portf.py ARM signal log, features.py, explore.py, grid.py, grid2.py, rc.py, report.py).

## Open items / next steps
00. **Group 41**: ask the user to attach the EA once with "save the calendar to a file" ON and send
   SMC_calendar.csv -> test the REAL news list (CPI, FOMC ...) on 2021-2026. With group 29 releases only
   (1m, user settings): none -18,514 / windows -18,844 / +pre 1 h -18,708 / 2 h -18,302 / 4 h -18,070,
   all -0.13R per trade (tools/ea/preeffect.py) -> news blocking does not change the edge.
0. **MT5 EA**: user compiles `SMC_Structure_EA_v12.3.mq5` in MetaEditor (F7) and sends any error lines; then
   Strategy Tester (Every tick based on real ticks) and a demo account. Fix compile errors with a patch, re-run
   `tools/ea` checks before delivering.
1. **Waiting for the user's data**: v11.1 one-year backtests 2023, 2024, 2025, 2026 (loss recovery,
   floor, groups 36 / 37, daily limits all OFF, Properties initial capital 100,000), MT5 XAUUSD M1 bars
   2023 -> today [RECEIVED: tools/data/gold_m1_utc.npz, 2021-2026], optional 2025 runs (against mode; equilibrium ON). Then: edge per year, stop-size rule,
   target from each trade's best point (MFE), hours / days, with vs against the HTF, streaks. Choose
   rules on 2023-24, check them on 2025-26, report in plain English -> next version.
2. **ATR minimum stop: tested, NOT recommended** (v11.2 became the stop buffer unit) (see above). Edge monitor (pause when the win
   rate of the last N trades falls below X%) not tested. The 5.75-year loss is the real issue: confirm
   in TradingView (v11.1 one-year backtests), then test any new idea on the 5.75 years BEFORE building.
3. **Open question**: the auto mode's alternatives - (b) opposite trades from the HTF break until the
   equilibrium touch, then NOTHING; (c) the same, then BOTH directions. Not decided yet.
