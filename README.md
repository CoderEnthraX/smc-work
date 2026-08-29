# SMC Toolkit — working repo

## current/ — the live files (what is on the chart)
- `Market_Structure_SMC_v15.15_OPT.txt` — complete indicator. 454 inputs, 2620 executable lines.
- `SMC_Market_Structure_EMA_v1.5_OPT.txt` — structure + killzone boxes + EMA. 314 inputs, 2151 executable lines.

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

## Known open items
See `docs/SMC_HANDOFF_20260811.md` §6. Two additions found by inspection:

1. **ALT-mode sweep migration still moves the anchor.** `current/Market_Structure_SMC_v15.15_OPT.txt:941`
   and `:984` (EMA `:806` / `:849`) set the replacement line's `x1` to
   `ceilS.swpB` / `florS.swpB`. That is the fault v15.5 fixed for the
   equal-price retest and v15.15 fixed for the pivot-2 promotion: `x1` jumps
   forward, so the later `f_retExtInc(x1, ...)` window no longer contains the
   sweep candle's own wick and the opposite level comes out shallow. Latent —
   `altMode` is off by default, and only the main engine has this branch.
2. **The OPT header lost the invariant-4 exception.** v15.15's header reworded
   invariant 4 to record that a pivot-2 promotion deliberately takes a bare
   swept wick. The OPT header states only "never adopt or seed a level price
   has already closed beyond", so it now contradicts the code it ships with.
