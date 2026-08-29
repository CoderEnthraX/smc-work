# SMC Toolkit — working repo

## current/ — the live files
- `Market_Structure_SMC_v15.16_OPT.txt` — complete indicator. 455 inputs, 3094 executable lines.
- `SMC_Market_Structure_EMA_v1.6_OPT.txt` — structure + killzone boxes + EMA. 315 inputs, 2625 executable lines.

`previous/` holds the v15.15-opt / v1.5-opt pair they were built from.
`build/` is the build output; `tools/build_v1516.py` is the transformation.

Every new version is derived from these by a scripted surgical transformation,
never hand-retyped. Encoding to preserve: CRLF, no BOM, no tabs, emoji intact.

## baseline/ — the unoptimised predecessors, kept as reference
`Market_Structure_SMC_v15.15.txt` and `SMC_Market_Structure_EMA_v1.5.txt`.

## Verified equivalence, current vs baseline
Each OPT build removes exactly 51 executable lines and adds **zero**:
the dead `f_confExt` (14 lines) plus seven write-only variables —
`mainRetBorn`, `intRetBorn`, `nnRetBorn`, `iCeilSwpB`, `iFlorSwpB`,
`nCeilSwpB`, `nFlorSwpB`. All eight identifiers were proven to have zero
reads in the baseline, and no dangling reference survives in the OPT build.
All 454 / 314 inputs match by position, name, type and default.
The engine block of the two OPT files is byte-identical to each other.

## tools/
- `compare_build.js <base> <new>` — input-by-position check + position-independent
  multiset diff of executable lines. Calibrate on a file against itself first:
  it must report zero. A positional diff is useless here — one removal shifts
  every later line and reports hundreds of false differences.
- `deadscan.js <base> <new>` — classifies each occurrence of an identifier as
  read or write, then scans the new file for dangling references and for any
  `:=` target that was never declared.
- `lint.js <file>` — unterminated string literals (the v15.6.1 fault), bracket
  balance, empty blocks, comma-separated declarations, indentation, emoji.
  The lone 5-space indent it reports is the `indicator()` continuation line,
  which is valid Pine and present in the baseline too.

## v15.17 — what changed

**Market structure is untouched.** The engine that draws BOS/CHOCH, iBOS/iCHOCH
and nBOS/nCHOCH is byte-for-byte v15.15-opt. The v15.16 mark-anchor change is
reverted in full, pending the reported cases. Verified: of the 215 lines
v15.15-opt has and this build does not, 212 are the old `f_tfPack` body and 3
are the `f_tfRow` lines below. Everything else is a pure insertion.

1. **Table reads the range, and never prints a dash.** BOS* above / CHOCH*
   below = bullish, BOS* below = bearish — which is what the engine's trend
   already means, so readout and marks cannot disagree. Every tier resolves
   through a cascade: its own trend, else the tier above it (the imaginary
   iBOS*/iCHOCH* and nBOS*/nCHOCH* pair, held in state, never drawn), else
   `f_provDir` — price versus the midpoint of the standing range. Measured:
   0 dashes across 360,000 cells. The v15.16 warm-up gate is removed with its
   input. The per-timeframe engine is still the rebuilt one (0 disagreements
   with the chart engine over 400 series, ALTERNATE off and on).

   Still not fixable: `request.security` only sees as much history of a
   timeframe as the chart has loaded, and the same engine over a short window
   disagrees with itself 65% at 40 bars and 2.5% at 300.

2. **Inner alert conditions.** Seven added; 21 → 28.

3. **New: range % line, group 10.** A level at a set percentage of the
   possible-BOS/possible-CHOCH range, on all three tiers. Percentage, tier
   selection, line colour/style/width, extend-right, label text/colour/size,
   horizontal alignment and vertical position, plus a master toggle. Empty
   label text auto-writes the percentage; internal and inner carry `i`/`n`
   prefixes. Independent of the retracement *alert* percentage. 15 appended
   inputs, so saved settings carry over.

## Verification tooling
`validate_port.js` (9 ground-truth cases), `measure_table.js`,
`measure_warmup.js`, `audit_anchors.js`, `declorder.js`, plus the build
comparators. Run `declorder.js` on any new build — Pine resolves identifiers
textually and nothing else in this toolchain catches use-before-declaration.
