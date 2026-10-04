# SMC Structure Strategy - project memory (read this first)

## The project
- Pine Script v6 strategy for TradingView: **SMC Structure Strategy**, traded on **XAUUSD 1-minute,
  OANDA feed**, executed at **FxPro MT5** through **TheConnector** (webhook). Alternative bridges:
  `metaapi_receiver/` (Cloudflare Worker -> MetaApi, about $0.039/hour = ~$29/month per account, the
  receiver only uses the free "MetaApi API") and the MQL5 VPS guide (`SMC_Strategy_v8.3_MQL5_VPS_GUIDE.pdf`).
- Owner: **Punit** (punit7870@gmail.com). Works from a phone. Wants **simple English, short examples with
  numbers, tables**. Times are **IST** (Asia/Kolkata).
- **Latest version: v11.1** = `SMC_Structure_Strategy_v11.1.txt` + `_NOTES.txt` + `_HANDBOOK.pdf`.
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

## How the v11.1 code works (key points)
- 118 inputs. Groups: 20 strategy, 21 risk / loss recovery, 24 safety, 25 daily blocking windows,
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
  -> NOT worth a v11.2. The existing fixed "skip if stop closer than" $5 was better (-0.07R 2021-23,
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

## Open items / next steps
1. **Waiting for the user's data**: v11.1 one-year backtests 2023, 2024, 2025, 2026 (loss recovery,
   floor, groups 36 / 37, daily limits all OFF, Properties initial capital 100,000), MT5 XAUUSD M1 bars
   2023 -> today [RECEIVED: tools/data/gold_m1_utc.npz, 2021-2026], optional 2025 runs (against mode; equilibrium ON). Then: edge per year, stop-size rule,
   target from each trade's best point (MFE), hours / days, with vs against the HTF, streaks. Choose
   rules on 2023-24, check them on 2025-26, report in plain English -> v11.2.
2. **v11.2 ATR minimum stop: tested, NOT recommended** (see above). Edge monitor (pause when the win
   rate of the last N trades falls below X%) not tested. The 5.75-year loss is the real issue: confirm
   in TradingView (v11.1 one-year backtests), then test any new idea on the 5.75 years BEFORE building.
3. **Open question**: the auto mode's alternatives - (b) opposite trades from the HTF break until the
   equilibrium touch, then NOTHING; (c) the same, then BOTH directions. Not decided yet.
