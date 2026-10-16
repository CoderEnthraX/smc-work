# SMC Structure Strategy - project memory (read this first)

## The project
- Pine Script v6 strategy for TradingView: **SMC Structure Strategy**, traded on **XAUUSD 1-minute,
  OANDA feed**, executed at **FxPro MT5** through **TheConnector** (webhook). Alternative bridges:
  `metaapi_receiver/` (Cloudflare Worker -> MetaApi, about $0.039/hour = ~$29/month per account, the
  receiver only uses the free "MetaApi API") and the MQL5 VPS guide (`SMC_Strategy_v8.3_MQL5_VPS_GUIDE.pdf`).
- Owner: **Punit** (punit7870@gmail.com). Works from a phone. Wants **simple English, short examples with
  numbers, tables**. Times are **IST** (Asia/Kolkata).
- **Latest version: v15.1 for BOTH** = `SMC_Structure_Strategy_v15.1.txt` (complete) + `SMC_Structure_Strategy_v15.1_noRSI_EMA.txt`
  + `SMC_Structure_EA_v15.1.mq5`; NO notes (user). v15.1 = v15.0 + one box per zone / show all zones, zones of an old HTF leg
  go, a setup goes only when ALL its zones are gone, last zone only, order block type 2 / to the swing, MSS + its
  confirmation, every-other-day mode after a pause, force close on 1m only, every price distance off - see Versions.
  Before it: **v15.0 for BOTH** = `SMC_Structure_Strategy_v15.0.txt` (complete) + `SMC_Structure_Strategy_v15.0_noRSI_EMA.txt`
  (the same without the 4 RSI / EMA filters - the user asked for two TradingView files) + `SMC_Structure_EA_v15.0.mq5`; NO notes
  (user). v15.0 = v14.0 + HTF order block zone modes + 1-minute-only section 4 rules + news on 1m only, loss mark and
  favourable / against / auto modes removed, TradingView code made smaller (v14.0 failed the token limit) - see Versions.
  Before it: **v14.0 for BOTH** = `SMC_Structure_Strategy_v14.0.txt` + `SMC_Structure_EA_v14.0.mq5` (NO notes file -
  the user said it is not needed; the v13.1 notes still describe everything else). v14.0 = v13.1 + section 1 'Separate unit
  for each setting' + section 4 leg size and big signal candle filters, all OFF (see Versions). Before it: **v13.1** =
  `SMC_Structure_Strategy_v13.1.txt` + `SMC_Structure_EA_v13.1.mq5` +
  `SMC_Structure_v13.1_NOTES.txt` (new part + the two recipes + how to use + the v13.0 notes). v13.1 = v13.0 + new setup
  filters at the END of section 4, all OFF (see Versions). Before it: **v13.0** = `SMC_Structure_Strategy_v13.0.txt` +
  `SMC_Structure_EA_v13.0.mq5` + `SMC_Structure_v13.0_NOTES.txt` (one notes file: what is new + the old -> new settings map +
  the v12.0 notes). v13.0 = the v12.2 / v12.3 rules with the settings in 13 SECTIONS, the same order in both files (see
  Versions). From v13.0 the TradingView and EA version numbers are the same. Before it:
  TradingView v12.2 + MT5 EA v12.3 = `SMC_Structure_Strategy_v12.2.txt` + `SMC_Structure_EA_v12.3.mq5`
  (EA v12.3 = the v12.2 rules + a safe catch-up after sleep / no connection / restart + the signal audit LABELS on the chart;
  the user asked for the EA file ONLY).
  No notes / handbook for v12.1 / v12.2 / v12.3, as the user asked - the v12.0 notes + handbook still describe everything
  else; see Versions. EA v12.2 kept; v12.1 files kept (they hold the profit mark that v12.2 removed). Before them:
  **v12.0** = `SMC_Structure_Strategy_v12.0.txt` + `_NOTES.txt` + `_HANDBOOK.pdf` (v11.2 + group 39
  "RULE 3 - enter at the close of the signal candle", all OFF; option "only if the close is near the broken level",
  default 3; option "if the close is too far: fall back to RULE 1 / 2"; see Versions). v11.2 files kept.
- **MT5 EA: `SMC_Structure_EA_v12.3.mq5`** (v12.2 + safe catch-up after a gap, always on, no setting; MT5 part only, core
  unchanged: CatchUp / DropReached / FilledReal; RestoreSides now restores the setup number; audit labels on the chart, group
  44 InAudSz / InAudMax at the very END, 155 inputs) / `SMC_Structure_EA_v12.2.mq5` (v12.1 without the profit mark + ESeq SEQ_AS / SEQ_BS / SEQ_CS = 7 / 8 / 9 + group
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
   - new settings go at the **END OF THEIR SECTION** (user's choice after v13.0 - keeps the 13 sections together;
     TradingView users add each version as a NEW script or reset the settings, the EA keeps names so .set files
     load); new features **OFF by default** so the old behaviour is unchanged; extra dropdown choices go at the
     end of the list;
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
  v12.3 also (user: "audit label ON in MT5 shows no labels"): up to v12.2 'Signal audit' (InAudit, group 20) only wrote the
  Experts journal - by design then, never drawn. Now (MT5 part, display only): BkNote -> AudNew (a CHOCH / BOS note "sg: ...")
  = an OBJ_TEXT at the signal candle (buy: its low, ANCHOR_LEFT_UPPER; sell: its high, ANCHOR_LEFT_LOWER), named g_AP + side
  + "_" + candle time (g_AP = "SMCA" + magic + "_" + symbol + "_", NOT deleted by a restart / parameter change, deleted on
  remove / account / chart change or when the audit is off); AudEnd adds FILLED / CANCELLED ... to the side's last ARMED label
  (g_audCur / g_audSeq; RestoreSides gives a kept setup its label back); AudRef = the broker side (SKIPPED - price past the
  stop or target, REFUSED BY THE BROKER). Tooltip = "sg  HTF up/dn/-/off" + one line per step (time, 2 spaces, text); chart
  text <= 63 characters (the MT5 limit): sg HTF | step > step, else sg | steps, else sg | last, else cut "...". Colours by the
  last step, dark / light chart (CHART_COLOR_BACKGROUND): armed DodgerBlue / MediumBlue, filled Lime / Green, cancelled or
  skipped Orange / DarkOrange, SKIP Silver / DimGray, refused Tomato / Red. Hedge: the long side labels buy signals, the short
  side sell signals. Group 44: InAudSz (Small 7 / Normal 9 / Large 11 default / Huge 14 pt), InAudMax 200 (newest kept, 0 = none).
  Live (and visual tester) only; history before the EA start has no labels (it is read dry). The journal line time is now the
  candle's (g_audT); a drop after a sleep says "CANCELLED - entry reached while the EA was offline" at the reached candle.
  Tools: mt5sim.h object store (ObjectGetString / ObjectsTotal / ObjectName, chartBg), simmain audit / audSz / audMax /
  chartBg / printLog / objDump / objPrefix (HAS_AUDLB from mql2cpp), ea/audtests.py. Checks: trades labels on = off (touch,
  pending, hedge); labels after 238 restarts = none; every label rebuilt separately from the journal + bars in 8 settings
  (dark / light, Small 50 kept, Huge rule 3, longs only, hedge, sleeps) - 0 differences.

- v13.0 (user asked: "reorganize both files, settings of a section together, better section names, % settings for every
  market, optimize, fix bugs"; answers: yes to all my suggestions = one box per distance, today's defaults + a settings
  map, the hedge option OFF, EA + TV + one notes file, no handbook). Rules that trade did NOT change.
  13 sections, same order in both files: 1 MARKET & UNITS (unit + pip size), 2 SIGNALS (take trades on, HTF, engine rules),
  3 ENTRIES (rules 1 / 2 / 3, entry handling, direction + hedge, reverse, max open, cancels), 4 SETUP FILTERS (closer /
  further, HTF filter, premium / discount, equilibrium), 5 STOP & TARGET (buffer, R, liquidity, partial, step / BE, trail),
  6 POSITION SIZE (+ stacked BOS risk), 7 LOSS RECOVERY (+ loss mark, profit steps), 8 ACCOUNT PROTECTION (daily loss,
  trades / day, drawdown, floor, profit target, day pause, days pause), 9 TRADING HOURS & WEEKEND, 10 NEWS (all of it; EA
  calendar), 11 COSTS (commission, spread), 12 BROKER (TV webhook + TheConnector / EA magic, exec, slippage, clock, history),
  13 DISPLAY. Pine group names gx01..gx13; inputs moved to the TOP of the script (after strategy()), nothing else moved.
  ONE stop buffer box (stSlBuf / InSlBuf) read in the section 1 unit (stBuPips / stBuPct, InBuPips / InBuPct gone): pips =
  RoundTick(slBuf x pip), % = RoundTick(level x slBuf / 100); the spread for sizing also in the unit (f_stSprd / SprdAt).
  TV 136 inputs, EA 154 (EA names unchanged -> .set files load; TradingView keys saved settings by POSITION -> add v13.0 as a
  NEW script or Defaults -> Reset settings). Pine runtime.error if unit % and buffer or spread > 10. Ideas a-g lost letters.
  EA only: InHgBase (section 3, OFF) "hedge + shared: a trade opened while the other side chases the loss risks only the base"
  (CSide chaseOrd / chasePos / hbSeen / cntHgB; SideChasing(); chaseOrd = !hb && riskNow > basNow; a fill makes chasePos;
  cleared when the side has no open trade; same candle: long side first; saved in GVs co / cp / hs). EA faster drawing: table
  cells cache (TblMem g_tm, slots) + lines / texts set style / width / ray / size / anchor once (display ON 32.9 -> 22.0 s CPU
  per year in the fake MT5; trades identical). Bugs fixed (EA CheckInputs): unreadable window time was ignored silently
  (WinOk), negative slippage = unlimited, negative magic, negative resume / marks. All 'group N' texts -> 'section N'.
  Tools: patches/pine130.py, ea130.py + ea130_inputs.txt; ea/v13tests.py (same <v12.3 folder> = every saved tools/ea setting
  v12.3 vs v13.0 byte-identical; hgb = OFF identical + separate replay of the order log, harness option ordLog; rs = restarts);
  extract.py / mql2cpp.py define CORE_V13 / EA_V13 (harness / simmain map old buPips / buPct keys into the one box);
  notes/build_notes130.py (+ v130_head / tail / checks). Checks: parser PARSED OK; TV structure + body diff = only intended;
  hgb 9 settings OFF = v12.3, replay 39,417 orders / 3,590 at base 0 wrong (2 half-lot ties), EA = core 4/4, 484 restarts =
  none; effect (1M test account, 1 y): deepest drop smaller in 5 of 7 (C 1:1 21,946 -> 12,218), bigger in 2 (rule 3, C+),
  profit a bit lower in 6 of 7. Same test: 222 of 222 saved tools/ea settings byte-identical v12.3 vs v13.0.
  Next versions: the user chose 'new settings at the END OF THEIR SECTION' (rule 3 updated).
- v13.1 (user: "build v13.1 with the C5 filters and RSI filter and all other suggestions that can be implemented"; then RSI /
  EMA filters for a lower AND a higher timeframe, all OFF; then "ONLY 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M timeframes"). No preset
  dropdown (recipes in the notes instead); dip-buyers NOT built (separate files, a later step if the user asks).
  26 new settings at the END of section 4 (TV 136 -> 162, EA 154 -> 180): stMnPct / InMnPct min stop % of the ENTRY (any unit,
  checked at placement with dOk -> cntSkip + cntX[8]); stFstOn / InFstOn skip the first setup of the day (session-tz day of the
  bar CLOSE; checked LAST in XSkip so a setup another filter skips is never 'first'; per side; EA keeps fstDay in GV 'fd' over
  restarts; the EA's start day does not know earlier setups); stYdOn / InYdOn (signal close below yesterday's low = no buy, above
  its high = no sell; day = New York trading day of the bar OPEN, new day 17:00 NY: DayNy = floor((NyLoc(t) - 61200) / 86400));
  stLegMin / InLegMin (bars from the CHOCH* pivot EN.flr.x1 / cel.x1 = Pine florS.x1 to the signal bar < N = skip); stTdOn +
  stTdAtr 0.15 (d * (close - today's open) < X * mean(H - L of the last 14 complete NY days) = skip; not ready = pass; EA
  WarmBars() = max(InWarm, 17 x 1440 min of bars) when ON); RSI L / H (tf, len 14 / 2, rule Pullback / Momentum, level 50) and
  EMA L / H (tf, rule price vs EMA / fast vs slow, len 200, fast 50): tf list ETfF = 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M (defaults L
  1m, H 1h); a tf not above the chart = the chart's own candles incl. the signal bar; above = the last CLOSED candle before the
  bar's own (Pine request.security(expr[1], lookahead_on); EA CInd fed by FeedInd from CopyRates like FeedHtf, 3,000 candles
  seeded at TryInit; harness IndKeyH on the broker clock: weeks from Sunday 00:00, months from the 1st). RSI = ta.rsi (Wilder,
  SMA seed); EMA starts at the first close. Not ready = pass. Order in XSkip: today, yday, leg, RSI L, RSI H, EMA L, EMA H, first.
  Audit 'SKIP - ...' texts; table rows 52 / 53 (TV, table 54 rows) / 2 EA rows (XTxt / XNowTxt). Tools: patches/pine131.py,
  ea131.py; ea/v131tests.py (sep / ea / rs), v131sep.py (separate copy of the v13.0 core + Python RSI / EMA flags); mt5sim.h
  PERIOD_M3 / M30 / H2 + W1 Sunday-aligned + MN1 calendar months (fix); extract.py CORE_V131 / mql2cpp.py EA_V131; m5.bin / h1.bin.
  Checks: parser PARSED OK; OFF = v13.0 (v13tests same: 222/222 byte-identical); separate 24/24 identical (1m / 5m / 15m / 1h charts, all tfs);
  whole EA = core 10/10; restarts 484 x 4 identical. Effect (real costs, 2021 - Oct 2026, 50 risk): C5 1R +933 (360 tr; 40/40
  noisy feeds, median +953); C6 1R +1,061; C6 + RSI H 1h(2) pullback 50 +2,006 (406 tr; 40/40 feeds, median +1,629, worst
  +1,147). No other RSI / EMA (1m .. 1M) beat these; EMA filters cut the plain-settings loss (15m EMA 50 -1,606, 1D 20/50 -2,109)
  but all still lost. Notes: tools/notes/build_notes131.py (+ v131_head / results / rsires / emares / checks).
  **v13.1 FIX (15 Oct 2026, same file names, 2 user reports)**: TradingView refused the first v13.1 with CE10295 "The main body
  of the script is too long. Try wrapping code in functions" (main body grew 22,085 -> 24,429 tokens; scratchpad ce/outline.py
  counts top-level statements incl. their blocks, functions excluded). Fix 1 (pine131.py step at the end): 3 display-only blocks
  into functions - the stats table, the last-candle structure / equilibrium lines (f_lastDraw() returns 14 lines / labels as a
  tuple, assigned to the globals in the old last-bar if), the structure alert queue (f_almQueue(), both 'if almOk' blocks,
  array.push to almQC / almQB, called every bar). Then TradingView: "The f_stTable function uses 357 external elements. The
  limit is 254. External elements are values returned by request.*() calls, inputs and parameters (int, float, bool count 2)"
  = TradingView compiles to the JVM (255 parameter slots per method; main body = one method, 64 KB). IN PRACTICE EVERY GLOBAL
  VARIABLE a function reads counts (directly + through the functions it calls), int / float / bool / untyped numeric 2, string /
  color / line / label / table / array 1, + its parameters: scratchpad ce/ext3.py gives exactly 357 for that f_stTable. Fix 2:
  the table is created in the old block and its rows are written by f_stTab1..4(table _t) (split before row 18, 'int ny0', the
  v10.4 floor comment): 65 / 100 / 74 / 164; f_lastDraw 180, f_almQueue 86, all old functions <= 76. Main body 19,909 tokens
  (v13.0 22,085). Script check: no global assigned inside the new functions; no ta. / request. / history inside; the table text
  is the old text (stTbl -> _t). Parser PARSED OK; 162 inputs same order; 7 request.security calls.
  Fix 3 (TradingView then: CE10117 "Compiled code contains too many tokens: 104405. The limit is 100256"): pine131.py final
  step = manual() + slim() + inline_consts() + slim() (code inside pine131.py, prototypes in scratchpad ce/: slim.py, manual.py,
  dangling.py): removes the old Market Structure indicator parts switched OFF by fixed values (structure alerts: queue, slots,
  sender, retracement-alert trackers mLvl / iLvl / nLvl + *RetFired; pivot / sweep / IDM marks; bgcolor; internal / inner
  equilibrium lines; f_innStrong; the HTF function's inner tier + evOut / inOut / nnOut - f_tfTrC reads 4 values), every 'if'
  false from constants alone, unread values / functions; then writes each fixed global value where it is used (137). Kept:
  mAnch / mOrig (rule 1), the internal tier of f_tfPack (iCe / iFl feed tkAH / tkAL when pbSwp2 is ON). Checks: no new
  dangling names (used-but-undeclared set unchanged); f_tfTrC to the end (1,576 lines: all trading code) identical except the
  4-value tuple; 162 inputs same order; parser PARSED OK. Estimated compiled tokens = 104,405 x source tokens / 34,058 (fix2):
  final 29,795 -> ~91,300 (v13.0 ~96,400, v12.2 ~96,400); main body 17,574; largest function 164 external elements.
  RULE FOR FUTURE VERSIONS: before delivering any Pine file check ALL THREE TradingView limits with these scripts (main body
  < ~20k tokens, every function < ~200 external elements, compiled tokens estimate < ~95k) - the parser cannot see them.
  (v15.0: + `python3 tools/ea/pineorder.py file` = every function / type / global declared before its first use.)
  EA: MetaEditor 0 errors / 2 warnings "declaration of 'k' hides member" (XSkip RSI / EMA loops vs CSide member k) -> loop index
  j (ea131.py); harness + simmain byte-identical. EA compiled by the user.
- v14.0 (user asked, answered every question, "give the version number 14.0 to both", "just give me the files", NO notes; NO
  profit test). Both files, 14 new settings each (TV 162 -> 176, EA 180 -> 194), all at the END of their section, OFF / 0:
  1. Section 1 unit: 4th choice "Separate unit for each setting" (EA BU_SEP = 3). Then the stop buffer, skip closer / further,
  rule 3 distance and spread each use their OWN unit dropdown (Price / Pips (auto per market) / % of price; EA enum EUnit) + ONE
  box, at the end of their section; skip closer / further share ONE dropdown with 2 boxes (the user's wish). The old 5 boxes are
  ignored in that mode. Inputs: section 3 stR3U / stR3V (InR3U / InR3V, % of the close, default 3.0); section 4 stSkU / stSkMin /
  stSkMax (InSkU / InSkMin / InSkMax, % of the entry); section 5 stBfU / stBfV (InBfU / InBfV, % of the CHOCH* level, rounded to
  the tick like before); section 11 stSpdU / stSpdV (InSpdU / InSpdV, % of the price). % buffer / spread > 10 = error.
  Core: CSet uBf / uSk / uR3 / uSp (Derive(): = buMode unless buMode 3; the adapter sets them + the values in mode 3);
  LimAt(int u, double v, double ref); BufAt / SprdAt read uBf / uSp. Pine: stBuSepM, f_unN, stUBf / stUSk / stUR3 / stUSp,
  stBfX / stMnX / stMxX / stR3X / stSpX (the box in use), f_unPx, f_unTxt.
  2. Section 4 LEG SIZE (always its own unit, any section 1 unit): leg = d x (broken level - CHOCH* level) = the pivot the signal
  candle closed beyond (EA piv = g_ceilPrev / g_florPrev, Pine _piv = stCeilPrev / stFlorPrev - the same level rule 2 / 3 use)
  to opl (flr / cel price = the stop level), NOT the candle's close (the user's definition). stLzU / stLzMin / stLzMax (InLzU /
  InLzMin / InLzMax; % = of the CHOCH* level); skip if leg < min - tick / 2 or > max + tick / 2; no broken level = pass; min >
  max = error. Checked separately from skip closer / further (both must pass - the user's example: leg 10, pullback 50%, stop
  under 8 -> skipped by 'closer').
  3. Section 4 BIG SIGNAL CANDLE: stBcU / stBcMax (InBcU / InBcMax; % = of its close): signal candle high - low > max + tick / 2 ->
  skip that setup (no trade on that leg); only the signal candle; the next CHOCH / BOS is judged again.
  Order in XSkip (EA) / the Pine chain: v13.1 filters, then leg, then candle, then 'first of the day' (still last). Counters
  cntX[9] leg short, [10] leg long, [11] candle (Pine stCntX9..11); table row 52 / EA row "(v13.1 / v14.0)"; audit "SKIP - leg
  6.00 (broken level 4006.00 to the CHOCH* level 4000.00) shorter than 8.00" / "SKIP - big signal candle 14.00 (most 10.00)".
  EA XSkip(d, piv, opl); TkS() = price text with the tick's decimals.
  Tools: patches/pine140.py (patched on the FINAL v13.1 file), ea140.py; harness / simmain keys buMode 3, bfU / bfV, skU / skMin /
  skMax, r3U / r3V, spdU / spdV, sprd (harness spread for sizing, 0 = before), lzU / lzMin / lzMax, bcU / bcMax (CORE_V14 /
  EA_V14); extract.py adds a test hook to the harness copy (xsLog: every XSkip call with bar, side, d, piv, opl); ea/v14tests.py.
  Checks: TV parser PARSED OK; TV limits main body 18,190 tokens, largest function f_stTab4 187 external elements, compiled
  tokens estimate ~94,200 (v13.1 ~91,300 compiled fine; limit 100,256); inputs old order kept, new ones at the end of their
  sections (both files); OFF = v13.1 byte-identical (222 saved settings, v13tests same); equiv 5/5 byte-identical (separate
  units in price / pips / % = the old unit; mixed = old way; old boxes set wrong to prove them unused); separate Python
  recalculation of every leg / candle / first-of-day decision from the logged levels + bars: 10 settings, ~65,600 decisions,
  all agree; whole EA = core 4/4 to the cent + 15m pending / touch same trades with one entry 0.31 better in the EA (1-minute
  jump over the limit inside a 15m candle - v13.1 identical, pre-existing); restarts 484 x 2 identical.
  OLD BUG FOUND + FIXED in v14.0 (MT5 part only, core unchanged): a restart or a settings change (both reload the EA) inside a
  candle right after a TOUCH fill sent the same entry again (duplicate trade) - the waiting order came back from the state saved
  at the last close; 1 case in the first v14.0 restart test (1m), 3 of 81 setups on 15m touch with ~2,450 restarts a year in
  v13.1 (since v11.1; earlier restart tests missed it by luck). SendMarket now sends only while the core still has that setup
  waiting (g_side dir != 0, same seq - else the book entry goes off) and not when FilledSince(comment, g_curOpen) finds an open
  position / IN deal of it in this candle. v14tests dup: v14.0 0 duplicates; 15m touch 2,453 restarts = no restarts. Also the
  journal line "SMC EA v12.3 ready" -> "v14.0 ready". NOT compiled by TradingView / MetaEditor yet (the user does).
  **v14.0 TradingView then FAILED CE10117 (100,771 tokens > 100,256) -> fixed in v15.0 (smaller code).**
- v15.0 (user: "build v15.0 with your suggestions ... both the meta ea and the tradingview file ... two tradingview files, one
  complete and one without the rsi and ema feature"; no notes; NO profit test). 3 files: SMC_Structure_EA_v15.0.mq5 (194 -> 202
  inputs), SMC_Structure_Strategy_v15.0.txt (176 -> 184), SMC_Structure_Strategy_v15.0_noRSI_EMA.txt (164 = minus the 20 RSI / EMA).
  ZONE BOX (user's last request, added before delivery; display only): the zone a with-HTF chart signal came from (the
  ZnAllow pick at the freeze point, BEFORE the visit is closed; any with-HTF signal, traded or not) is drawn as a box from the
  zone's candle (OB candle / first of the 3 FVG candles; the CHOCH* line: its first touch) to the signal candle, green = buy
  zone, red = sell zone, text '1h order block' / 'M15 FVG' / 'HTF CHOCH* line'; setting stZnBox / InZnBox (ON) at the END of
  section 13; TradingView keeps 50 (max_boxes_count default), the EA 50 (g_P + "Z" + n, + text n"t"; redrawn by the warm-up).
  Core: ZRec t0 / tt, ZnCandle(j, t, ...) with the candle open time (UTC; adapter SrvToUtc), g_znCt ring, ZnBox(d) -> g_zbOn /
  g_zbD / g_zbTf / g_zbK / g_zbTop / g_zbBot / g_zbT0 / g_zbT1; adapter DrawZnBox (OBJ_RECTANGLE, fill, back, tooltip + text).
  Pine: f_znReq + time[3], time[ku], time[kd] (13 values), Zn.t0, zL[3] = line first touch, f_znAllow 5 values (line: top =
  bottom = stHtO), box.new(xloc.bar_time) at the freeze block. Inputs: TV 185 (no RSI / EMA 165), EA 203.
  BUG CAUGHT before delivery: the box text used f_tfName above its declaration (TradingView would refuse it; the parser did not
  see it) -> f_tfName moved above f_znUp; NEW CHECK tools/ea/pineorder.py (declared-before-use; v13.1 / v14.0 clean).
  F1 section 4 end: stM1On / InM1On (ON) 'skip closer / further (old + separate boxes), min stop %, rule 3 distance, leg size on
  the 1-minute chart only' (chart > 60 s -> those 0 / off; rule 3 itself works, no fall back; seconds = 1m) + stBcMax2 / InBcMax2
  (0) big candle box for charts > 1m (old box = 1m) - EA Derive x1m / bcE, Pine stX1m, stMnX / stMxX / stMnP / stLzN / stLzX /
  stR3B / stBcE. F2 loss mark REMOVED (stLmOn / stLmAmt, InLmOn / InLmAmt, cntLm, row 50); CAP_BASE kept. F4 section 10 end:
  stNw1m / InNw1m (ON): chart > 1m -> windows 1-3, auto US news, EA calendar news, pre-news block off; US holidays (incl. EA
  calendar holidays) still work (Pine stNwX; EA NewsFlags). F5 'Take trades on' = 6 choices (CHOCH / BOS / both + the 3 zone
  modes); EA ESig SIG_CHOCH_OB / BOS_OB / BOTH_OB = 12 / 13 / 14; old .set 3-5 (favourable) -> hfOn + plain, 6-11 -> plain.
  F3 HTF ORDER BLOCK ZONE modes (section 2 end: stZnPct 50 / InZnPct, znBig, znOb, znFvg, znHalf, znTwo, znLine all ON): zone
  timeframes = HTF + 2 above (ladder 15m, 1h, 4h, 1D, 1W, 1M); zones from CLOSED candles: FVG = candle 1 / 3 gap, its OB = the
  last opposite candle among the 3 before the move (dedupe = same as the last OB of that tf / side); 10 per tf / side, 60 max;
  a zone dies on a close of ITS OWN tf beyond its far side (then a waiting order of it is cancelled); qualify per bar in the
  HTF leg's zone (OB touching / beyond the line, FVG touch line beyond it, both up to the leg start); touch = the bar's low
  (buy) reaches the touch line (OB near edge, FVG 50% or near edge); state 0 fresh / 1 visit open / 2 a with-HTF chart signal
  closed the visit / 3 stopped; beyond the visit's low (buy) after state 2 = liquidity taken: znTwo ON -> 1 again, OFF -> 3;
  new HTF leg (event count) = all states 0; biggest tf = max tf among qualified non-stopped zones; pick = first zone with
  the max tf among touched ones; else the CHOCH* line (leg start) if touched. Signal must be WITH the HTF; skipped = 'SKIP -
  zone mode: ...', cntOb / stCntOb, table row 'ORDER BLOCK ZONES (section 2)'; armed text gets '(HTF+1 order block)'.
  EA core: ZRec g_zn[60], ZnCandle / ZnBar / ZnAllow / ZnFreeze / ZnDead; adapter ZnSetup / FeedZn / ZnUp, GVs zf / zt / zb.
  Pine: type Zn + array zA, zL (line state), zO (last OBs), f_znReq / f_znGet (3 request.security, lookahead_on + [1] = last
  CLOSED candle; feed when its time changes, nz() for the first one), f_znCandle / f_znBar / f_znAllow / f_znFrz.
  EA fix found while checking the Pine: ZnDead looked at the last 32 broken zones (an old zone at the same prices could cancel
  a new setup); now only THIS bar's (ring cleared at the end of CoreBar) = TradingView.
  TV SIZE (no feature removed): pine150c.py = (1) values nobody reads (mnHiP / mnLoP, evSwp, iRun / nRun, evN, rqStr, stCapFlag,
  _eId / _eDir, f_tfPack iTr / iEvt), (2) fixed display choices written as values (styleOf, hAlignOf, lstyle / tsize /
  lblStyle, 12 black colour vars, eqLive / eqClose, caps 10), (3) internal (blue iBOS) + inner (yellow nBOS) tiers = ONE routine
  (type TLvl / Tier, f_tier / f_tSeed / f_tAdopt / f_tIdm / f_tBrk / f_tMark / f_tDraw; display only), (4) f_retExt(from, high,
  inc) = old f_retExtreme / f_retExtInc, (5) one global table stTbl (f_stCell(r, ...)), f_mt / f_r2 text helpers, f_hLine
  without setters that never change. Also table title 'STRATEGY v13.1' -> 'v15.0'. Tokens (ce/outline.py): v14.0 30,725 (=
  100,771 compiled), v15.0 complete 28,388, no RSI / EMA 26,748 -> estimate ~98,200 / ~96,400 (worst case ~99,000; the limit
  100,256). Main body 15,372; largest function f_stTab4 184 external elements.
  Checks: EA OFF = v14.0 (v13tests same old140): 184 of 222 byte-identical, the 38 others ALL use removed features (loss mark /
  against / auto; 4 loss-mark files identical - mark never fired) = 0 unexpected; equiv 6/6 byte-identical (switches = by hand; 1m unchanged); v15sep.py
  separate Python zone engine 10/10 settings ~32,000 decisions agree; whole EA = core 5/5 to the cent; restarts 484 x 2 identical.
  TradingView: tools/ea/pine2py.py (small Pine -> Python translator) + pinerun.py (OLD = NOCOMPACT=1 pine150.py output vs NEW
  compacted, the whole chart engine incl. every line / label, per bar): 5 x 60,000 bars (altMode, pbSwp2, pbBody, last-500 /
  every bar drawing) IDENTICAL; planted bugs caught (3 tried, 3 caught over 50k bars). pinezone.py: the Pine zone code run on
  the core's logged inputs = core 10/10 settings, 32,223 decisions (planted bugs caught). Parser PARSED OK (both files).

- v15.1 (user agreed to all my suggestions + added order block type 2, MSS, MSS confirmation, force close on 1m only, 'every price
  distance off'; then "build v15.1 ... perfect working file without any bugs ... check everything"; no notes; NO profit test).
  3 files: SMC_Structure_EA_v15.1.mq5 (203 -> 223 settings), SMC_Structure_Strategy_v15.1.txt (185 -> 205),
  SMC_Structure_Strategy_v15.1_noRSI_EMA.txt (165 -> 185). All new settings OFF (force close on 1m only ON, its old behaviour on
  1m), at the END of their section, the same order in both.
  1. BOXES (display): ONE box per zone (named by the zone; a later signal stretches it, text '1h OB x3'), every zone that
  counted for a with-HTF signal (OB + FVG, every tf), kept after the zone dies; green / red, darker when it was the last zone
  (EA SeaGreen / IndianRed, DarkGreen / Maroon; TV green / red, #006400 / #800000, 85 transparent); FVG with 'far half' drawn
  as its far half; newest 440 kept (TV max_boxes_count 500). Section 13 end: 'Show all zones' (InZnAll / stZnAll, OFF): every
  live zone in the leg's zone with no signal yet, to the last candle; visible % 50 / 30 / 15 (HTF / +1 / +2), border on HTF
  zones, labels of HTF+1 / +2 in the label colour (white), OB buy green / sell red, FVG teal / orange, last zone +25% (max 90),
  border 2, '(last)'. EA: colours mixed with the chart background (MT5 boxes cannot be see-through), redrawn every bar.
  2. A new HTF leg (CHOCH or BOS) kills zones MADE before the leg started (made = close of the 3rd FVG candle; te <= the open
  of the leg-start HTF candle -> dies) + the old leg's CHOCH* line; always on. Core: CHtf tRunLoT / tRunHiT / legT (strict
  < / >, = Pine tRLoT / tRHiT / tLegT in f_tfPack, 5th security value stHtS).
  3. A waiting order goes only when ALL its zones are gone (own-tf close beyond / killed); capacity drops are not deaths.
  EA: support tuples (supTf / supK / supD / supT / supB / supT0, up to 12 in GVs) checked against THIS bar's deaths (g_zd*);
  Pine: stSup = the array f_znCount returned, Zn.dead flags.
  4. Section 2 end: 'Only trade from the last zone' (znLast): last zone = among OBs in the leg's zone, not spent, HTF
  direction: highest tf, then the deepest (buy: lowest bottom); FVGs / the line never last; the line still counts alone when
  no zone counted; overrides 'biggest'; error if ON with OB OFF. 'OB box reaches the swing' (znSw): box to the min low / max
  high from the OB candle to candle 3. 'Order block type 2' (znOb2): OB = candle 1 of the FVG, any colour, one per burst (an
  FVG whose candle 1 is one of the last FVG's 3 candles = same burst). OB dedupe now by candle time.
  5. MSS (mssOn, mssN 2 = candles each side, 1-10): MSS up = first close above the newest strict swing high, WITH the HTF,
  not on a candle with a used chart CHOCH / BOS; MSS low = lowest low from the swing candle INCLUSIVE to this candle; needs a
  chart FVG with its OB (type 1: an opposite candle among candle 1 and the 2 before; type 2: always) with candle 1 >= the MSS
  low bar, and ZnCount(d, 2) > 0. One trade per visit: a visit that gave an MSS does not count for CHOCH / BOS, any signal
  blocks MSS. Entry rules 1 / 2 / 3 (rule 1 = pullback of the MSS move msAnch / msLow, rule 2 = the broken swing, rule 3 =
  close); stop = MSS low -/+ buffer; section 4 filters with the MSS low as the CHOCH* level, candles from the MSS low bar;
  premium / discount on the MSS move; exempt from trend-flip cancel, bosCnl and the rule-1 live stop; cancelled by an opposite
  chart CHOCH / BOS; a same-way chart signal no zone allows leaves it (keepMs). Confirmation (mssCf) + stop choice (mssSt:
  First MSS low / Newest swing low = the pullback extreme): wait for a touch of the first FVG's near edge (bar > MSS bar),
  then a NEW FVG with OB completing with candle 1 >= the touch bar -> enter at its close (market, rule 3, one chance); a
  wick beyond the MSS low = failed; rules 1 / 2 / 3 not used then (EA rule 4). Table / audit: 'MSS', counts.
  6. Section 8 end: ldN2 (0 = off) losses in a row AFTER a pause -> every-other-day mode: the rest of that day blocked, then
  only every (ldSkip + 1)-th trading day (Mon-Fri; every day with 24/7 / crypto in Pine) until ONE winning trade; no new
  pause in that mode. Blocked text 'loss pause (every other day)'.
  7. Section 9 end: 'Force close at 02:00 on the 1-minute chart only' (fl1m, ON): charts above 1m have no daily force close
  (entry hours / weekend unchanged; seconds = 1m). 8. Section 1 end: 'Switch OFF every price-distance setting' (pxOff, OFF):
  stop buffer, closer / further (old + separate boxes), min stop %, rule 3 distance (rule 3 still enters), leg size, big
  candle (both boxes), spread for sizing, 'push target out to cover commission'; the commission itself stays.
  Tools: patches/ea151.py, pine151.py (+ the pine150lite.py cut for the 3rd file); extract.py hooks B / A / Z / L / M / W / K /
  F / X / R / E (key znLog); harness / simmain keys pxOff, fl1m, znLast, znSw, znOb2, mssOn, mssN, mssCf, mssSt, ldN2, ldSkip,
  wk247, znAll (EA_V151 / CORE_V151); v151sep.py (separate zone + MSS + confirmation engine), v151tests.py (sep / equiv / fl1m /
  pause / ea / rs / box), pinezone151.py (the Pine zone + MSS code translated, fed the core's inputs), pinehtf151.py (the Pine
  f_tfPack translated: trend / leg / count / leg start time = core), pinedead.py; scratchpad
  b151/engrun.py (pinerun on the file before / after the engine merge).
  TV SIZE (no feature removed): f_tfPack's dead internal tracker (141 lines; pinedead.py), long / short orders in one call,
  the chart engine's ceiling / floor written once (for _k = 0 to 1), f_blk, f_xRsT / f_xEmT, f_stCancel(), seq-mode names by
  str.startswith / contains, SwingTracker defaults, the two order parts in one loop. Outline tokens: complete 29,514 (v15.0
  28,648 passed), no RSI / EMA 27,896; estimate ~99,450 / ~97,690 (limit 100,256 - the complete file is CLOSE: if CE10117,
  next room = the table texts f_stTab1..4 ~3,300 tokens). Main body 16,223; largest function f_stTab4 207 external elements.
  CHECKS: separate Python (v151sep) = core 12/12 settings (MSS 1m / confirmation first + newest / OB2 + last + both / hedge /
  rule 3 + whole FVG / BOS + no 2nd visit / 15m; up to 63,000 zone counts, 17,000 boxes, 3,214 MSS, 940 confirmations, 965
  failures per setting, zones-gone cancels); Pine zone + MSS code = core (pinezone151) on the same settings; chart engine
  merge = old bar by bar (5 x 60,000 bars, 3 planted bugs caught); equiv 5/5 byte-identical (pxOff = by hand 1m / zones+MSS /
  15m separate units; fl1m on 1m); fl1m 15m: 0 'Time flat' with ON (275 OFF), weekend close kept; pause replay 4/4 agree
  with every core note (65 / 58 / 38 / 76 every-other-day starts).
  EA vs TV differences known: a zone box deleted by the 440 ring and stretched again: EA recreates it, TV keeps it deleted.
  OLD BUG FOUND + FIXED (MT5 part only, core unchanged; there since v11.0): two trades of ONE side closing in the same second
  (stacked trades closed together) were counted for the loss pause / losses in a row in the broker's close order live, but in
  entry order after a restart (and in the core / TradingView) -> after a restart a pause could start that live did not (v15.1
  restart check: 244 vs 242 trades). Now GatherIO (ClsAfter) and ReplayMoney sort same-second closes by entry time, then
  main part before the early-profit part: live = restart = core (short range 11 = 11 = 11 trades).
  Effect on the saved settings: only the loss pause / day pause read that order -> the 50 saved whole-EA settings with ldOn /
  lsOn (restart twins = plain) re-run with the fix: 46 byte-identical, 3 lev1000 'OnInit failed' in every version, 1 changed
  (ocfg_off_bos_partial: a win + a loss closed in the same second; now counted win-then-loss like the core / TradingView ->
  a pause starts earlier; 6,392 -> 6,257 trades over 5.75 y). Whole EA = core 6/6 incl. the case that showed it (242 = 242).
  More checks: whole EA = core 5/5 to the cent; boxes: the 440 boxes the EA keeps over 3 years = the core's (place, prices,
  colour incl. darker last zone, 'x N'), 3 settings; Pine f_tfPack = core on 2,037,534 1m bars + 2 x 135,898 15m bars; the
  Pine MSS confirmation block = core on 6,370 setups (2,542 confirmed + stop, 2,427 failed; CF=1 pinezone151.py).
  Pine f_ldAlt = the EA's AltHalt on 96,000 cases (pinepause151.py, IST + New York). Parser PARSED OK (both files).

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

- **Rule C Ultra study (Oct 2026; user: "survive 5 more losses, small profit is enough")**, user 1m TV settings (u23 v_A
  from 2021), 10k, lev 100; exact EA core copies with experiments (scratchpad ultra/: hu = + 'slow split' ukS, hu2 = + 'edge
  gate' ugN / ugW, hu3 = + 'write off when the brake binds' ubReset; ulib.py, exp1-5). Entries 2021-26: 1,829 trades, 33.5%
  win, -0.118R, only 9% reach 3R, break-even win rate 39%, longest losing run per year 14/13/12/17/12/9. Maths: split 3
  empties after 18 losses in a row (x4/3 each), split 4 22, 6 29, 10 41; floor brake never. 58 start months, 12-month
  windows: C3 32 empty / 24 profit; BIGGER SPLIT IS WORSE (4: 39 empty, 6: 42) - the killer is the long slide, not one run;
  slow split k >= 0.5 = Off; loss mark 2,000 15 empty; write-off no better than the brake; edge gate 50 / 36% + brake looked
  best (0 empty, 31/58 profit to the end) BUT inside each half a high recent win rate predicts nothing (2021-23 -0.26 vs
  -0.23R, 2024-26 +0.004 vs -0.03R) = hindsight (2025). 40 noisy feeds (5 cents): from 2021 C3 40/40 empty (Off 39/40);
  from 2023 C3 36 empty / 4 profit (best +10,407 = TV), Off avg -3,727; C3 on 42k (= 5 more losses) 20/40 empty, on 100k
  11/40 empty (median +8,814). RECOMMENDED "Rule C Ultra" = Rule C split 3 + EXISTING group 35 'On - only cap the risk',
  most to lose 3,000, lock 50, 10% of the cushion: 58 starts 0 empty, worst -2,984, 13 in profit; 40 feeds from 2023 0 empty
  / 0 profit (about -2,866); from 2025 0 empty / 28 profit, median +4,337 (C3: 39 profit, +5,775, 1 empty; Off +648);
  biggest risk 289. It parks at the floor after a disaster (from Jul 2024: -2,904 to the end). No new code needed; told the
  user no money rule makes profit from losing entries.
  Follow-up (user uses TARGET 1R + Rule C SPLIT 1, "win rate 40-45%"): 1R entries 2021-26 = 2,467 trades, 43% win (38-50%
  by year) but break-even needs 49.9% (avg win +0.84R / loss -0.84R after costs) -> -0.114R, negative EVERY year (2025
  -0.001R); longest losing runs 10/10/11/9/9/8. Split 1 + 1R = doubling: 10k empty after 9 losses in a row. 58 start months:
  Off 1R 0 profitable 12-month windows; C1 1R 49/58 empty; every floor setting 0 empty AND 0 profit. 40 feeds from Jan
  2025 (best period): C1 1R 25 profit (median +8,482) but 15 EMPTY; Ultra on 1R (3k / 10% / lock 50) 1 profit, median
  -2,738; looser 3k / 50% 12 profit, median -1,576; 5k / 50% 14, median -3,167 - vs Ultra on 3R split 3: 28 profit, median
  +4,337 (Off 3R 37/40 profit, Off 1R 0/40). From 2021 / 2023 nothing profitable. Told the user: Ultra cannot fix 1:1
  (higher win rate but further below its break-even); 3R + Ultra is the better shape. Scripts: scratchpad ultra/exp6-8.
  Follow-up 2 (user: "stop not less than 8, not more than 15" = group 24 min / max stop 8 / 15, with 1R + split 1): 1R
  entries 894 trades, 45.5% win, break-even 48.5%, -0.048R (2024 +0.014, 2026 +0.055, others negative; runs 5-9); 3R + 8-15
  -0.082R. Neighbour grid (1R flat): a bigger MIN stop helps smoothly in both halves (min 0 / 8 / 10: 2021-23 -0.18 / -0.12 /
  -0.09R; 2024-26 -0.08 / -0.01 / 0.00) - real (commission per oz is a bigger share of small stops); the MAX 15 adds nothing.
  Real FxPro path, 58 starts: split 1 57/58 empty to the end; SPLIT 2 0 empty, 58/58 profit (median +2,676) - BUT 40 feeds:
  split 2 from 2021 34 empty / 6 profit, 2023 29 / 11, 2025 13 / 27 (median +1,809); split 1 30-38 empty; Off 0-2 profit;
  split 2 + floor 5k 25-50%: 0 empty, 2-4 profit (2021 / 2023), 16-19 (2025), median about -4,500. Feeds are fair (flat
  -0.033..-0.073R vs real -0.048R; real Off beats 25-30 of 40) but real split 2 beats 37 of 40 = a lucky order. Scripts:
  scratchpad ultra/exp9-10.
  Follow-up 3 (user: min stop 8, NO max, targets 1 / 1.3 / 1.5 / 2R + combinations): flat entries 2021-26 almost the same
  for every target: 1R 1,295 tr 47.7% win (need 49.4%) -0.025R; 1.3R -0.032; 1.5R -0.023; 2R -0.028; 2.5R -0.037; 3R -0.022;
  all about -0.12R in 2021-23 and +0.004..+0.025R in 2024-26 (t 0.1-0.56 = break-even, not proven). No max helped 1R
  (-0.025 vs -0.048 with max 15). Min-stop neighbours 6-12 similar shape. 40 feeds (min 8, no max): from 2021 every Rule C
  split 1/2/3 at every R empties 30-40/40; from 2023 19-32/40; from 2025 split 2/3 1 empty / 39 profit at 1 / 1.5 / 2R (1.5R
  C2 40/40, median +3,750; 2R C2 median +5,371); split 1 at 1.3-2R empties 25-34 even from 2025. Floors: 2R C2 + floor 5k /
  50% / lock 50 = from 2025 0 empty / 35 profit, median +5,269 (worst -4,506); from 2021 / 2023 median -4,849 / -4,961; real
  58 starts: 12-month windows 0 empty / 37 profit (Jul 2023+ starts 28/28, median +2,420), to the end from 2021-23 about
  -4,700..-4,960, from 2024+ +4,234..+7,121. 1R C2 + floor 3k / 50%: from 2025 31/40 profit, median +2,868; worst -3,000.
  Told the user: the target does not change the edge; results depend on whether the future looks like 2025-26 or 2021-23;
  a floor sets the worst case. Scripts: scratchpad ultra/qual.json, exp11-14 (v11.json, v13.json, v14.json).
  Follow-up 4 (user: "gold went from ~2,000 to 4,000-5,000 - optimise the stop to the price"): gold avg 1,793 / 1,799 /
  1,940 / 2,408 / 3,409 / 4,529 (2021..2026); median stop $5.25 -> $18.78 = 0.29% -> 0.43% of price; $8 = 0.45% of price in
  2021, 0.18% in 2026 -> $8 kept 22-25% of setups in 2021-23, 94% in 2026. Existing group 38 '% of price' (buffer = buPct % of
  the CHOCH level; group 24 min stop = % of the entry; LimAt / BufAt) tested, buffer 0.025%: EVERY min % still loses in
  2021-23 (-0.07..-0.24R) -> the price level is not the cause; buys and sells both lost 2021-23 (gold +8% sideways) and both
  ~0 in 2024-26 (+101% trend). Bigger min % better in both halves (smooth). Flat 0.4-0.7% min: -0.03..+0.01R, all 95% ranges
  include 0 (0.5%: 1R 105 trades/yr +0.009R, 2R 97/yr +0.008R). With C2 + floor (2R 5k / 1R 3k, 50%, lock 50), 40 feeds
  profit from 2021 / 2023 / 2025: $8 3/6/35, 0.3% 1/3/39, 0.35% 0/1/40, 0.4% 5/25/26, 0.45% 3/38/40, 0.5% 10/40/40 (1R:
  18/39/39), 0.6% 27/40/40 (median +1,732 2R / +850 1R from 2021), 0.7% 39/40/40 (+960 / +533; worst -4,909 / -2,931). Real
  58 starts, 0.5%: 0 empty, 58/58 profit to the end (2R +1,582..+2,616, 1R +1,179..+2,122); Off 0.5% from 2021 +235 / +303.
  Told the user: use % of price (consistent filter); 0.5-0.6% zone; entries still break-even, Rule C shape = many small wins,
  rare loss up to the floor. Scripts: scratchpad ultra/pct.json, exp15-18 (v15-v18.json).

- **Improvement study + high-win-rate strategies (Oct 2026, after v13.0; page https://claude.ai/artifact/2e5YMZQ6rBrPXdKN8b2fK9;
  scratchpad imp/ + hw2/)**. REAL FxPro costs from now on: spread at entry (npz sp, mean 0.19) + 0.07 commission per oz = about
  13 per lot per side (user's TV uses 30 -> TV looks worse than real; at 0.60/oz user settings -11,253, real -6,731).
  SMC, user settings 3R, real costs: 2021-23 -0.206R, 2024-26 +0.033R. Test copy of the EA core with filters (imp/mkcore.py:
  xFirst skip the first setup of the IST day, xYday no buy below yesterday's low / sell above yesterday's high (NY day),
  xLegMin CHOCH leg >= N bars, xToday with today's move in daily ATR, xMinPct min stop % of entry, hours). One at a time:
  min stop 0.5% -13 (feeds 21/40), 0.35% -573; others -1,777..-4,522; none positive in 2021-23. C5 = first + yday + leg12 +
  min 0.5%: 333 trades +847 (3R) / +933 (1R), A +0.027 B +0.060, 40/40 noisy feeds positive (median +773, worst +266),
  random entries beat it 6%. C4 (today 0.15 + hours 13-21 + first) +1,595, A +0.002, 40/40. C6 34/40. Rule 1+2 beats rule 3
  with filters (C5 1R +933 vs +207). No time rules (swap est.): real +1,746 but 5/40 feeds -> luck. Suggested now: TV
  commission ~13/side, rule 1+2, min stop 0.5% (unit %); possible v13.1 (NOT asked yet): first / yday / leg / today filters.
  High win rate (hw2/hw2.py, vectorised sim = old loop to the cent; swap est. long 4%/yr, short 1%/yr of price): textbook 5
  + 204-variant grid (RSI(2), buy the N-bar low, IBS; 15m/1h/4h/1D; pick on 2021-23). Wins 55-67% common, profit not: trend
  pullback 0.5R 67% win -6,122; London -1,878; soup -2,953; Bollinger -10,714. 1h dip-buyers: IBS +1,576, Double-10 longs
  +857, RSI(2) +530 (+0.007..+0.02R/trade); all 3 together +2,963 (2021 -443), 57% weeks up, worst week -270, drop -1,172;
  random same-exposure entries beat them 0.2-11%. Grid: 0 of 151 positive all 6 years; 15m 0/36; 1h 38/56. EURUSD: no data
  (Dukascopy blocked by the proxy) - needs the user's MT5 M1 export.

- **SMC + the high-win-rate strategies combined (Oct 2026, same page v2; scratchpad mix/)**. Side by side (one account,
  each $50; mix/combine.py): yours -6,731 -> -3,768; C5 +933 -> +3,896 (drop 444 -> 1,132); C6 +1,035 -> +3,999; weekly
  correlation SMC vs dips about 0; up to 4 trades open. As a filter (test core hj = core_i + per-minute flag file, last
  CLOSED 1h candle; flags all-buys / all-sells = the direction setting exactly; mix/flags.py T / R / RX / I / TR): yours best
  TR -2,273 (0/40 feeds); C5 none better; C6 + 1h RSI(2) < 50 buys / > 50 sells = +2,001 (399 tr, +0.105R, A +0.080 B +0.125,
  5/6 years, 40/40 feeds median +1,610, random 0/1,000). Best mix C6 + RSI filter + 3 dips +4,965 (-680 / +820 / +1,229 /
  +975 / +1,250 / +1,371), drop 1,264. 15 filter versions tried = some luck possible. Not built; needs written permission
  (v13.1 filters + a separate dip-buyer strategy / EA).

- **v13.1 RSI / EMA settings search (Oct 2026, after v13.1; scratchpad rsem/: lib.py, grid.py, stage2.py, an.py, an2.py,
  feeds.py, final.json; v13.1 core h131, real costs, $50, recovery off, 2021 - Oct 2026)**. 8,328 single runs: charts 1m / 15m
  x HTF off / favourable (sig 3) x bases yours / C5 / C6 x every RSI (tf 1m..1M, len 2/3/5/9/14/21, pullback / momentum, level
  20..80) and EMA (price vs 9/20/50/100/200, all 10 crosses); + 440 pairs of the A-picked tops; 16 finalists x 40 noisy feeds.
  'HTF favourable' (sig 3) and 'HTF filter' (hfOn) gave IDENTICAL trades in 9 of 9 settings -> reported as one.
  HTF fav alone, 1m yours: -6,731 -> -1,948 (0/40 feeds). Lower-tf RSI / EMA (1m / 5m / 15m) almost never help (yours fav: RSI-L
  3/252 + in both halves, EMA-L 0/45) -> leave the LOWER filter OFF. Picks on 2021-23 that held on 2024-26:
  1m yours + HTF fav + EMA 1M price vs EMA 20 +1,720 (941 tr, 74% buys, sells +662 too; 36/40 feeds, median +685; stable: 1W
  50/100/200 and 1M 20..200 all + in both halves) ; + RSI 4h(3) momentum 70 = +2,004 (448 tr, drop 692, 39/40, median +1,238)
  but RSI 4h(3) m70 is an ISLAND (neighbours mixed) -> trust the EMA part more. C5 + RSI 1h(3) pullback 80 +1,199 (drop 314,
  40/40 median +1,071; RSI 1h pullback zone all + in both halves). C6 + RSI 1h(2) pullback 50 (the recipe) +2,006 = the hindsight
  best, NOT the strict A-pick (RSI 1W(14) p50 A +1,166 B +192), but a stable zone (RSI 1h len 2-9, level 40-70 all +), 40/40
  median +1,514. C6 + HTF fav (no RSI / EMA) +1,252 (40/40, median +1,105); RSI / EMA add little on top (7/792 better both
  halves). 15m: yours plain +821 (331 tr, 40/40) is the best simple; filters beat its 2024-26 in 12/594 only; RSI 15m(14) p70 +
  RSI 1M(2) p20 +1,032 but 80 trades; HTF fav 15m +461, + RSI 1D(5) momentum 50 +764 (90 tr). 5-cent noise barely changes 15m.
- **1.5R + Rule C split 1.5 (Oct 2026; scratchpad ultra/exp19.py, v13.1 core h131, comm 0.13 = real, 10k, lev 100)**: split 1.5
  at 1.5R = one win pays all back, risk x5/3 per loss: 10k gone after 11 losses in a row (split 3: 18). Longest runs at 1.5R:
  yours 9-14 / yr, C5 up to 9, C6+RSI 11 (2024). No floor: yours EMPTY May 2021 / Jun 2023, C6+RSI EMPTY Jul 2024. With the
  Ultra floor (flMode 2, 3,000 / 50 / 10%): C6+RSI split 1.5 +3,161 from 2021 (40/40 feeds, median +2,240 vs split 3 +1,675,
  Off +1,380; worst drop median 2,376 vs 2,157); C5 split 1.5 31/40 (split 3 40/40, better); yours 0/40 from 2021 either split.
  Told the user: OK only with the floor ON and the C6 + RSI entries.
- **"Can Rule C carry less loss / survive longer streaks?" (Oct 2026; scratchpad rcmath/: R.json = real trade R lists, mc.py =
  4,000 reshuffled paths, 10k, base 50)**. Losses in a row to empty 10k (base 50 / 25 / 10): split 1 9/10/11, 1.5 11/13/15, 3
  18/20/24, 6 29/33/39, 10 41/49/58. Your entries 3R (-0.074R real costs), 3 years: Off 0.1% empty avg -3,518; split 3 75% empty
  avg -5,667; split 10 63% avg -6,247; base 25 57%; cap 300 81%; loss mark 1,000 16% avg -5,075; 'chase only after a win' (idea,
  not in code) 63%; Ultra floor 0% avg -2,243 worst5% -2,949. C6+RSI 1.5R (+0.092R) 3 y: Off avg +955; split 3 +1,222 (0.5% empty);
  split 1.5 +1,627 (3.8% empty); split 1.5 + floor +1,583 (0%, worst5% -863). Longest losing run in a year (shuffled): yours 3R
  median 11, P(>=12) 48%, P(>=18) 5%; C6+RSI 1.5R median 5, P(>=10) 2.6%, P(>=12) 0.7% (real 2024 had 11). Told the user: no money
  rule changes the average; levers = better entries (shorter streaks), floor (hard limit), split = target; nothing to build.

## Open items / next steps
00. **Group 41**: ask the user to attach the EA once with "save the calendar to a file" ON and send
   SMC_calendar.csv -> test the REAL news list (CPI, FOMC ...) on 2021-2026. With group 29 releases only
   (1m, user settings): none -18,514 / windows -18,844 / +pre 1 h -18,708 / 2 h -18,302 / 4 h -18,070,
   all -0.13R per trade (tools/ea/preeffect.py) -> news blocking does not change the edge.
0a. **v15.0 delivered (see Versions)**: the user compiles the 3 files (TradingView complete + no RSI / EMA, MetaEditor F7) and
   reports errors. If TradingView says CE10117 again: my token model is only 2 points (fix2 104,405 / 34,058 outline tokens;
   v14.0 100,771 / 30,725) -> compiled ~= 100,771 + 1.09 x (tokens - 30,725); more room = the zone engine / table texts.
   The F1-F5 list below is what v15.0 built (kept for reference).
   OLD: **v14.0 TradingView FAILED CE10117: 100,771 tokens (limit 100,256, over by 515)**; v13.1 passed -> my estimate (104,405 x
   tokens / 34,058 = ~94,200) was WRONG: the marginal cost is about 1 compiled token per outline.py token (fix 3 removed 4,263
   -> about 4,300; v14 added 930 -> about 1,000), with a big fixed part. Calibrate from now on: compiled ~= 100,771 + (my tokens
   - 30,725). Next version (number not given yet) - user features being collected, NO build before written permission:
   F1 (confirmed): new switch at the end of section 4 "Use closer / further, the rule 3 distance and the leg size on the
   1-minute chart only", ON by default (user's wish): on charts above 1 minute ignore skip closer / further (old boxes AND the
   separate-unit boxes), the v13.1 min stop % of the price (stMnPct / InMnPct, user said make it 1m-only too), the rule 3
   'near the broken level' distance (rule 3 itself still works; no fall back there), and the leg size min / max. Seconds
   charts count as 1 minute. Big signal candle: TWO boxes sharing the one unit dropdown - the old box = 1-minute (and seconds)
   charts, a new box (default 0 = off) = all charts above 1 minute; not tied to the switch. Make room in TV by compacting code
   (no feature removed - the user said so). F2 (CONFIRMED): REMOVE completely the loss mark "Start again from the base
   risk when the losses carried reach" (section 7: stLmOn / stLmAmt, EA InLmOn / InLmAmt, table row 50 / EA row, counters
   cntLm); KEEP the hard-cap choice "Start again from the base risk (forget the losses)" (CAP_BASE) - the user
   confirmed. F3 (mostly answered; my model of the zone life sent for confirmation): 3 new 'Take trades on' modes CHOCH /
   BOS / CHOCH+BOS "- HTF order block zone", ALL chart timeframes, always WITH the HTF direction. Zones searched on the HTF +
   the 2 timeframes above it (1m chart: 15m / 1h / 4h; 15m chart: 4h / 1D / 1W), inside the HTF leg's pullback zone (line
   setting, default 50%; at ~50% only OBs, FVGs only beyond the line). New settings: 'only the biggest timeframe's zones
   count' (ON = biggest present wins, OB + FVG together; OFF = all count); 'use order blocks'; 'use FVGs'; 'FVG: only its far
   half (touch at its 50% line)' (OFF = whole FVG, touch at its near edge); 'second visit counts if it takes the first
   visit's liquidity' (OFF = it does not). OB = last opposite candle before a move that leaves an FVG (zone = its high-low).
   A zone DIES only when a candle of ITS OWN timeframe closes beyond its far side (15m zone -> 15m close, 1h -> 1h, 4h -> 4h)
   or the HTF leg changes; a wick beyond (even above the 100% swing) is fine. After a touch, EVERY with-HTF chart CHOCH counts
   while the zone is alive and price has not closed beyond it (user's example: sell, buy CHOCH ignored, next sell CHOCH below
   the zone taken); a CHOCH after the zone died needs a NEW zone. Entry / stop / target as now. EXTRA setting (asked last):
   'the HTF CHOCH* line counts as a zone' - after an HTF BOS, the HTF CHOCH* line (100%, the leg start) works like a zone:
   chart price reaches it, no HTF candle closes beyond it, then the chart CHOCH back with the HTF -> trade (mirror for buys).
   FULL LIST + suggestions (zone line 50, biggest-tf ON, OB ON, FVG ON, far half ON, second visit ON, CHOCH* line ON, dead
   zone cancels a waiting order, both OB + FVG off = error, version v15.0 both files, no notes) SENT, asked WRITTEN permission. F4 news switch: answers =
   my suggestions (above 1m ignore windows 1-3, automatic US news, EA calendar news, 'no new trades before news'; US
   holidays keep working; default ON; end of section 10). F5 confirmed by the user's earlier message.
   F5: 'Take trades on' keeps ONLY 6 choices: CHOCH only, BOS
   only, CHOCH and BOS + the 3 OB-zone modes; REMOVE favourable / against / auto (9 choices). (Favourable = the section 4
   'Higher-timeframe filter' switch - same trades.) EA: give the new modes NEW enum numbers so old .set values 3-11 do not
   silently become OB modes. F6..: waiting for the user.
0. **v15.0** (v14.0 superseded): the user compiles all 3 (TradingView x2 + MetaEditor F7) and reports errors / warnings.
   (v13.1: MetaEditor 0 errors, TradingView fix 3 confirmed working by the user.) Then
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
