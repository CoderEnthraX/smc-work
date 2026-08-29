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

## v15.16 — what changed and how it was proved

1. **The MTF table contradicted the chart.** `f_tfPack` was a second, older
   implementation of the three engines, five versions behind. Rebuilt as a
   faithful transcription of the chart engine on function-local buffers.
   Measured: 0 disagreements over 400 series on all three columns, with the
   ALTERNATE rule off and on (was 1.5%). Plus a warm-up gate, because the
   dominant cause is the `request.security` history window, which no rule
   change can fix: the same engine over a short window disagrees with itself
   65% at 40 bars and 2.5% at 300. Convergence tracks confirmed-event count
   (63% at 1 event, 91% at 4, 98% at 7, ~100% at 11), so a row now stays blank
   until its own simulation has 6 events. One appended input, default 6.

2. **No inner alert conditions.** Seven `alertcondition` entries added, so
   nBOS/nCHOCH now appear in the Create-alert dropdown. 21 → 28.

3. **Marks drawn at a price their anchor candle never traded.** Audited 19,748
   marks: 604 failed (5.7% of BOS, 6.7% of iBOS, 6.9% of nBOS, never a CHOCH),
   and all 604 were pivot-2 promotions. `x1` was doing two jobs — the latched
   scope anchor and the drawn start. Separated with a `drawB` field; scope is
   untouched, so v15.15's fix stands. Re-audited: 0/19,748.
   The ALT-mode sweep migration, same class, found by inspection, is fixed
   here too — it had kept moving `x1` onto the sweep bar.

Invariant 4 restored to its v15.15 wording; the opt header had dropped the
deliberate pivot-2 exception that the code relies on.

### Resource note
Each ticked timeframe now runs a full three-engine simulation instead of a
simplified one. Handoff §6.4 records an unexplained "Stopped — Calculation
error" on AUDUSD 5m with the *old*, lighter engine, so that risk is real and
is now larger. If it appears, untick timeframes in group 8. IDM is computed
per-timeframe only while the ALTERNATE rule is on, which is the main saving.

## Verification tooling
`validate_port.js` (9 ground-truth cases), `measure_table.js`,
`measure_warmup.js`, `audit_anchors.js`, `declorder.js`, plus the build
comparators. Run `declorder.js` on any new build — Pine resolves identifiers
textually and nothing else in this toolchain catches use-before-declaration.
