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

## Open items / next steps
1. **Waiting for the user's data**: v11.1 one-year backtests 2023, 2024, 2025, 2026 (loss recovery,
   floor, groups 36 / 37, daily limits all OFF, Properties initial capital 100,000), MT5 XAUUSD M1 bars
   2023 -> today, optional 2025 runs (against mode; equilibrium ON). Then: edge per year, stop-size rule,
   target from each trade's best point (MFE), hours / days, with vs against the HTF, streaks. Choose
   rules on 2023-24, check them on 2025-26, report in plain English -> v11.2.
2. **Proposed for v11.2** (needs the user's written permission): (a) automatic minimum stop = X x ATR;
   (b) edge monitor - pause when the win rate of the last N trades falls below X%.
3. **Open question**: the auto mode's alternatives - (b) opposite trades from the HTF break until the
   equilibrium touch, then NOTHING; (c) the same, then BOTH directions. Not decided yet.
