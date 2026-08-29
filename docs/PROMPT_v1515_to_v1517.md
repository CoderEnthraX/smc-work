# Prompt — build v15.17-opt / EMA v1.7-opt from the v15.15-opt base

Paste everything below the line into a fresh session, and attach the two base
files plus the project handoff.

---

I am attaching three files:

- `Market_Structure_SMC_v15.15_OPT.txt` — the complete indicator (three structure
  engines, session/day/anchored volume profiles, VWAP, killzone boxes, MTF table,
  EMA module, alert system). 454 inputs, 2620 executable lines.
- `SMC_Market_Structure_EMA_v1.5_OPT.txt` — structure + killzone boxes + EMA only.
  314 inputs, 2151 executable lines.
- `SMC_HANDOFF_20260811.md` — the project handoff. Read it fully before writing
  any code; it carries the rule set, the invariants, the TradingView facts we
  learned the hard way, and how I expect the work to be done.

Read all three completely first. The two Pine files share a **byte-identical
engine block** — verify that yourself rather than assuming it, then apply every
change to both files identically.

I want a new version, **v15.17-opt** and **EMA v1.7-opt**, with the three
changes below.

## Ground rule, before anything else

**Do not touch the market-structure engine.** The code that produces and draws
BOS / CHOCH, iBOS / iCHOCH and nBOS / nCHOCH must come out byte-for-byte
identical to v15.15-opt. No new rule, no changed anchor, no changed level, no
changed break condition. Everything below is the table, the alerts, and one new
drawing module.

When you are done, prove this rather than assert it: take a
position-independent (multiset) diff of executable lines between v15.15-opt and
your build, and show me that every removed line belongs to the old `f_tfPack`
body or to the two or three `f_tfRow` lines you deliberately changed. An index
diff is useless here — one insertion shifts everything after it and reports
hundreds of false differences.

## 1. The MTF table contradicts the chart, and prints dashes

Two separate problems.

**(a) The table runs a different rulebook from the chart.** `f_tfPack` — the
function each of the 18 `request.security` calls runs — is a second, older
implementation of the three engines. It has drifted five versions behind:

- an equal-price pivot still takes the level (v15.5 removed that)
- no sweep guard on the chart-start adopt (v15.1)
- levels are anchored on the **confirmation bar** instead of the pivot bar
- the opposite side re-anchors to a running extreme instead of `f_retExtInc`
  from the pivot (v15.14)
- no pivot-2 promotion at all (v15.14 / v15.15)
- no IDM gate and no `inPivK` pivot-strength filter

The chart's own row reads the real engine and every other row reads that older
one, so the same timeframe can read BULLISH on its own chart and BEARISH from
another. Rebuild `f_tfPack` as a faithful transcription of the v15.15 chart
engine.

The thing that makes this legal: invariant 6 forbids reading the chart's global
price buffers inside `request.security`, because on a higher timeframe those
globals hold chart-timeframe bars. So the rebuilt engine must run on
**function-local buffers**, and you will need buffer-parameterised twins of the
helpers — something like `f_retExtB`, `rearmB`, `f_isSwingB`, `f_lastMinorB`,
`f_armIdmB` — that take the arrays as arguments. `var` arrays declared inside
`f_tfPack` work; the existing code already does this with `qHiP` / `qHiB`.

Compute IDM per-timeframe **only while the ALTERNATE rule is on**. With it off,
`idmP` stays `na`, every break gate is satisfied by `na(idmP)`, and IDM cannot
reach the trend — so it costs nothing and changes nothing.

**(b) Make the readout simple, and never let a cell be empty.** The
possible-BOS / possible-CHOCH pair *is* the direction: **BOS\* above with
CHOCH\* below is bullish; BOS\* below is bearish.** Read the table that way.

No cell may ever show a dash or a blank. Resolve every tier through a cascade:

1. the tier's own trend, when it has one
2. otherwise the tier **above** it — internal falls back to main, inner falls
   back to internal and then to main. These are the imaginary iBOS\*/iCHOCH\*
   and nBOS\*/nCHOCH\* pairs: hold their state in variables, never draw them
3. and the main tier, before its very first event, reads where price sits
   inside the standing range — above the midpoint bullish, below it bearish

Apply the same cascade to the chart's own row so it cannot disagree with the
others. Guard the degenerate case where the two levels are equal, or that path
still returns zero and prints a dash.

**Be honest with me about what this cannot fix.** `request.security` only sees
as much history of a timeframe as the chart has loaded, and the engine's opening
range is anchored on the extreme of whatever window it gets, so a high timeframe
read from a low chart timeframe can still differ from the same timeframe on its
own chart. Measure that separately from the rule drift and tell me the numbers,
so I know which part of the disagreement you actually removed.

## 2. nBOS / nCHOCH are missing from the alert dialog

The inner events have `alert()` calls but no `alertcondition()` entries, and
`alertcondition` is what populates the Create-alert dropdown. There are 21
conditions and not one of them is inner.

Add seven: Bullish nBOS, Bearish nBOS, Bullish nCHOCH, Bearish nCHOCH, Any nBOS,
Any nCHOCH, Any inner structure event. They must obey the arming gate exactly
like every other condition. Add no inputs — the inner alert checkboxes already
in the settings drive the `alert()` path and stay as they are.

## 3. New — a range % line on all three tiers

Draw a level at a settable percentage of the possible-BOS / possible-CHOCH
range: the main pair, the internal iBOS\*/iCHOCH\* pair and the inner
nBOS\*/nCHOCH\* pair. Measure the percentage **down from the upper level**, so 0
is the upper level, 50 the midpoint and 100 the lower one, read the same way
whichever direction the range points.

Every part settable, in its own settings group:

- the percentage (default 50)
- which of the three tiers draw
- line colour, style (Solid / Dashed / Dotted) and width
- extend-right on or off
- label text, show-text on or off, text colour, text size
- text horizontal alignment (Left / Center / Right) and vertical position
  (Above / Middle / Below)
- a master on/off toggle, placed at the top with the other master switches

Leave the label text **empty** and it should write the percentage itself so the
label tracks the setting; give the internal and inner labels an `i` and `n`
prefix so three lines can be told apart.

Keep it completely independent of the existing "Retracement % for range alerts"
setting — that one is measured back from the leg's running extreme and drives
alerts, this one is a drawn level on the standing range. Changing either must
leave the other alone.

A tier draws only while **both** its levels exist. For a short spell after a
break one side is empty until the next pivot refills it, and a range with one
side missing has no midpoint — that is correct, do not invent a level to fill
the gap. Bound the drawing queue and wipe it on each last-bar execution;
TradingView keeps ~500 drawings per script and silently deletes the oldest.

## How I want this done

- **Append every new input at the very end** (invariant 5). TradingView matches
  saved settings by declaration order, so all 454 / 314 existing inputs must keep
  their positions and I must not need a settings reset. Use `group =` to place
  them on screen. If code that consumes an appended input runs before the append
  point, defer that code to the end of the file — the v14.0 pattern.
- **Never hand-retype a file.** Produce each version by a scripted surgical
  transformation of the previous one: named patches anchored on exact code lines,
  each asserting that it applied, then an automated verification pass. Derive the
  indentation of every inserted line from its anchor — Pine is
  indentation-sensitive — but insert top-level declarations verbatim at column 0,
  because a Pine function may not be declared inside a block.
- **Verify before shipping.** Pine cannot be compiled locally. Port the affected
  logic to a Node simulation and prove it. Validate that port against ground
  truth that is independent of the port itself — the behaviour the changelog
  describes in prose — never against the engine's own output. Node is available.
- Write scripts to a file rather than using heredocs or `node -e`; this shell
  mangles backslashes, and a mangled `\n` inside a Pine tooltip will silently
  split the string literal and break the build.
- Run these checks on the finished files and show me the results: input count and
  order by position, name, type and default against the base; multiset diff of
  executable lines; declaration order (every identifier declared before first
  use — calibrate the checker on the unmodified base first, it must report zero
  there); bracket balance; unterminated string literals; empty blocks;
  indentation; and encoding (CRLF, no BOM, no tabs, 💪 💎 🧨 intact).
- Bump the header version and add a changelog entry that explains the **cause**,
  not just the change.
- Deliver both complete `.txt` files. Tell me plainly that nothing has been
  compiled by TradingView, and that I must delete and recreate any existing
  alerts because an alert runs its own frozen copy of the code and settings.
- Flag the resource risk: each ticked timeframe will now run a full three-engine
  simulation where it used to run a lighter approximation, and the handoff
  already records an unexplained "Stopped — Calculation error" on AUDUSD 5m with
  the lighter one.

## Also fix, while you are in the header

The optimised header shortened invariant 4 to "never adopt or seed a level price
has already closed beyond". That contradicts the code it ships with: v15.14
deliberately reversed it for the pivot-2 promotion, which takes a bare swept
wick. Restore the full v15.15 wording so the next person reading the file is not
misled.

## What NOT to do

Do not change how marks are anchored or drawn. An earlier attempt separated the
drawn start of a mark from its latched scope anchor so that promoted levels would
not start on a candle predating the swept wick they sit at. It was measured and
it did what it claimed, but it did not fix what I was actually seeing, and I
reverted it. Leave that alone entirely — I will come back to it with examples.
