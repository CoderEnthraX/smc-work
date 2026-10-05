# tools/ - how each version was built and checked

Everything here was used to build and test the SMC Structure Strategy versions in the
main folder. Nothing in this folder is needed to TRADE - only to build, test and analyse.
All paths inside the scripts point at `/home/user/smc-work/tools/...`.

## Folders

| Folder | What is inside | How to use it |
|---|---|---|
| `parsechk.py` | Syntax check of a Pine file with the pynescript parser (the full Pine grammar). | `pip install pynescript` then `python3 tools/parsechk.py SMC_Structure_Strategy_v11.2.txt` (takes ~8 minutes) |
| `patches/` | `patchNN.py` - each one turns the previous version into the next (e.g. `patch111.py` + `patch111b.py`: v11.0 -> v11.1; `patch112.py` v11.1 -> v11.2, `sim112.py` the same change in the simulators; `patch120.py` v11.2 -> v12.0, `sim120.py` the simulators, `ea120.py` the MT5 EA). | Read them to see exactly what changed in each version. Write the next one the same way (assert every replacement matches exactly once). |
| `sim2/` | The Python simulator: a port of the strategy (main-tier structure engine, 15m HTF engine, rule 1 / rule 2, sessions, weekend, broker emulator with limit / stop / target fills, sizing, lot steps, leverage cap) and every feature up to v11.1. `port120.py` is the latest (v12.0: rule 3 entry at the close of the signal candle, `r3On` / `r3BrkOn` / `r3Brk` = only when the close is near the broken level, and PULLBACK RULE 3 `pbSwp2`; v11.2: stop buffer unit, `buf_at` / `lim_at`). `m1.pkl` = real XAUUSD 1-minute bars, Feb 25 - May 26 2026 (list of `(utc_epoch_s, o, h, l, c)`). | `cd tools/sim2 && python3 t111b.py` (each `tNNN.py` is the test of version NNN; `t112.py` = v11.2). User settings: `{'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':100.0,'rev':False}` -> 112 trades, +793.31. |
| `mm/` | Statistics on the user's trade files: edge per year, Monte Carlo, sizing / floor tests, time of day, day of month, stop size. `*.pkl` = the trade sequences already loaded. | `cd tools/mm && python3 stats.py` (edge), `python3 timewin.py` (hours / days), `python3 gmc.py` (Monte Carlo with 1-oz steps) |
| `notes/` | `build_notesNNN.py` writes `SMC_Structure_Strategy_vNNN_NOTES.txt` (new part + the previous notes). | `cd tools/notes && python3 build_notes111.py` |
| `hb/` | Handbook builder: `common.py` (styles), `hbNNN.py` (each builds on the previous), `render.js` (Playwright -> PDF), fonts. `dr104.py` = the data-request PDF. | `cd tools/hb && python3 hb112.py && node render.js $PWD/hb_v11.2.html $PWD/front_v11.2.pdf "title"`, then append pages 2..end of `SMC_Structure_Strategy_v8.3_HANDBOOK.pdf` with pymupdf (see the end of the v11.1 handbook build in the chat history / CLAUDE.md). | Note: `hb91.py`..`hb112.py` also read `sim2/final.json`, `sim2/equity.json`, `ana/csvstats.json`, `ana/whatif.json` (older test results, kept outside the repository) - rebuild those first or point `docs.py` at a copy.
| `data/uploads/` | The user's TradingView List-of-Trades exports used in the analyses (one-year files 2021-22, 2023-24, 2025-26 CHOCH only; Sep 2026 Off / Rule A / B / C; the 2023 Rule C+ file). | Read by `mm/*.py`. |
| `ea/` | Checks of the MT5 EA `SMC_Structure_EA_v11.2.mq5`: its core compiled as C++ vs the simulator, and the whole EA in a small fake MetaTrader 5 (`mt5sim.h`), with restarts. | See `tools/ea/README.md`: `python3 mkdata.py`, build, then `tests2.py`, `fulltests.py`, `restarts.py`, `fulllong.py`. |
| `data/gold_m1_utc.npz` | FxPro MT5 "GOLD" (XAUUSD) 1-minute bars, 4 Jan 2021 - 2 Oct 2026, 2,037,534 bars, cleaned: the 441 fake whole-day bars at 00:00 server time (Jan 2021 - Oct 2022, each holding the whole day's high and low) removed; time converted to UTC (FxPro server = UTC+2, UTC+3 in EU summer time). Prices in cents (int32). FxPro is about +0.25 USD vs OANDA (median, Feb-May 2026; 99% of minutes within 0.74). `sp` = MT5 spread in points (0.01). | `z = numpy.load(...)`; keys `t` (UTC epoch s), `o h l c` (cents), `tv` (tick volume), `sp` (spread). Bars for the simulator: `[(t, o/100, h/100, l/100, c/100), ...]` |

## Checks every new version must pass

1. Parser: `PARSED OK`.
2. Settings: old settings in the same order and places; new ones appended at the END; ASCII only; no tabs; no `strategy.close_all(`.
3. Every new name declared before use and not clashing with an old name (also in the simulator - a clash with the simulator's `fav` variable once broke a test).
4. Simulator: with the new feature OFF, every order and trade identical to the previous version.
5. Simulator: the feature's own rule worked out SEPARATELY (not with the same code) and compared - 0 differences.

## Building the handbook PDF (part 1 + the v8.3 handbook as part 2)

```python
import pymupdf
old = pymupdf.open("SMC_Structure_Strategy_v8.3_HANDBOOK.pdf")
d = pymupdf.open("tools/hb/front_vX.pdf")
d.insert_pdf(old, from_page=1, to_page=len(old) - 1)
d.set_metadata({"title": "SMC Structure Strategy vX - Handbook", "author": "Punit"})
d.save("SMC_Structure_Strategy_vX_HANDBOOK.pdf", garbage=3, deflate=True)
```
