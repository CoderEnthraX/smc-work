SMC Toolkit — Project Handoff
Written: 11 August 2026 · Supersedes: SMC_HANDOFF_2026-08.md (written at v14.7). Everything current is in this file.

0. READ THIS FIRST
Which file to load
File	Contents	Use when
Market_Structure_SMC_v15.15_OPT.txt	Everything — 3 structure engines, session/day/anchored volume profiles, VWAP, killzone boxes, MTF table, alerts	one indicator doing all of it
SMC_Market_Structure_EMA_v1.5_OPT.txt	Structure + killzone boxes + EMA module	structure work with moving averages
SMC_Market_Structure_v1.0.txt	Structure + killzone boxes only	lightest structure-only chart
SMC_Volume_Profiles_VWAP_v1.1.txt	Session/day/anchored profiles + VWAP only	pair with a structure file

All four are on the v15.15 rule set. The _OPT builds and v1.0 have comments stripped and dead code removed; behaviour is identical to v15.15.
Two files that are NOT in that set
    • Market_Structure_SMC_v16.0.txt / SMC_Market_Structure_EMA_v2.0.txt — v15.15 plus rule C (§4). Not optimised. Rule C exists nowhere else.
    • Market_Structure_SMC_v16.1.txt / ..._v2.1.txt — added a "current + previous range only" toggle. User reported it does not work. Abandoned, cause never investigated. Do not build on these.
Delete these — superseded or known-broken
v15.16, v15.17, v15.18, v15.19, v15.20 (the vertical-line investigation, §6.1), v16.1, v2.1, and every EMA_v1.x / v15.x older than those listed above.

1. Session version history — cause, not just change
Starting point: v15.5 was current; the previous handoff documented only to v14.7.
Ver	What, and why
v15.6	Arming gate never worked for price triggers. f_armHit tested high >= lvl or low <= lvl; price sitting below the level satisfies low <= lvl on its own, so "Either" armed on the first live bar having touched nothing. Fixed with f_armTouch: the previous bar's close fixes which side price is on, and the wick must reach the level from that side. Measured over 3,000 random series: old "Either" false-armed in 2,224 of 2,224 no-touch series (100%); new test 0.
v15.6.1	Compile fix — raw " inside a Pine string literal ended it early (2177:706).
v15.7	MASTER B re-scoped to killzone boxes only; the London Close profile left the group.
v15.8	Killzone boxes can render as top/bottom lines only (fill and side edges suppressed), with line colour and width. Pine boxes have no per-side border control, so the box is made transparent and two real lines are drawn on its edges.
v15.9	All four killzones restored to MASTER B (v15.7 had removed London Close, so it had no box for lines to attach to). Edge lines carry the killzone name, with one set of text controls (position, align, colour, size) for all four.
v15.10	The retracement latch was spent where no alert could fire. mainRetFired := true sat inside the touch test, which runs on every bar including TradingView's historical replay when an alert is created. Alerts never fire on history, so the first touch was consumed and the level arrived at the live edge already spent. Fix: burn the latch only where an alert can be delivered (almOk and barstate.isrealtime).
v15.11	EMA module brought into the complete file.
v15.12	London killzone default session 0700-1000 → 0600-0900.
v15.13	EMA off by default with a master switch in the toggle group. It is a gate, not an override — it can silence the module but never turns on an EMA you unticked.
v15.14	Two rule changes, both requested — see §3.
v15.15	The pivot-2 promotion no longer moves the anchor. v15.14 promoted to the swept wick and set x1 to the sweep bar; the later opposite-side re-anchor then scanned from there and lost the sweep candle's own low. Brute-forced over 83,239 promotion-then-break sequences: the floor differs in 9,035 (10.9%), and the kept anchor is deeper or equal in every one.

Everything after v15.15 is either abandoned (§6.1) or rule C (§4).

2. The rules as they stand
3-candle pullback rule (Module 1) — swing HIGH; lows mirror
    1. Candidate = highest high so far; a new or equal extreme replaces it.
    2. Three bearish pullback candles: c1 = first bearish candle at/after the candidate (its low locks); c2 closes below c1's low; c3 closes below c2's low → confirmed.
    3. Always body-close beyond the previous locked wick. Never body-to-body.
    4. Noise pauses, never resets. The three need not be consecutive.
    5. A new or equal extreme restarts everything.
    6. Reported on the confirmation bar, anchored at the candidate's bar.
The user has confirmed this definition. Do not change it.
Two pivot streams
    • Main hiT/loT — free-running. Read by BOS/CHOCH only.
    • Internal aHiT/aLoT — alternating. Read by iBOS/iCHOCH and nBOS/nCHOCH.
Three nested engines
BOS/CHOCH → iBOS/iCHOCH → nBOS/nCHOCH, each anchored on its parent's trend-side level and reset by any parent event.
Each level: adopt into an empty slot only — an equal-price pivot never takes a level (v15.5) · first break of a range = CHOCH · with-trend = BOS, against = CHOCH + flip · broken side empties and refills · opposite side re-anchors to the retracement extreme · a sweep arms a pivot-2 promotion.
Invariants — break these and old bugs return
    1. Only a confirmed parent event starts a new child range.
    2. The range anchor is LATCHED for the life of the range. Re-creating the trend-side line inside a range must not re-scope it. (v13.6, and the cause of the v15.15 regression — see §6.1.)
    3. Main = free-running pivots; internal and inner = alternating.
    4. Never adopt or seed a level price has already closed beyond.
    5. New inputs must be APPENDED; use group = to place them on screen.
    6. rearm() reads the price buffers — never call it inside request.security().
    7. No variable-offset history references — use bufHi/bufLo/bufDir.
    8. Pine has no bitwise operators; the EVENT bitmask unpacks by subtraction.
    9. Any comparison involving na yields na, and if treats na as false. So x != na is FALSE. Guard every such test with na(x) first.
Invariant 4 is no longer universally true. v15.14 deliberately relaxed it for the pivot-2 promotion, which now promotes to a bare swept wick. See §3.

3. The v15.14 rule changes (in every current file)
A. The break candle counts toward the opposite level
f_retExtreme implemented the documented rule literally — the extreme wick strictly between the broken pivot candle and the break candle, both excluded. Excluding the pivot is right; excluding the break candle is not. It discarded the deepest point of the leg in exactly the case that matters most: the candle sweeps the previous low, takes the liquidity, then closes up through the level. That wick is the strong low.
f_retExtInc (identical but scanning to jEnd) is used at the six opposite-side re-anchors — main, internal, inner × up-break and down-break. It can only ever deepen a level, so on an ordinary break candle nothing moves.
Deliberately unchanged: the six opposite-reference calls that arm the pivot-2 promotion, the two IDM tests, and the two Module 1 alternation re-arms. They still use the exclusive f_retExtreme.
B. A pivot-2 promotion takes the swept wick
Previously the promotion called f_confExt and required the replacement to be a 3-candle-confirmed pivot. If the sweep high was never confirmed, no promotion happened and the old pivot kept the line — so a BOS printed at a level price had already swept.
Now it promotes to the recorded swept wick (swpP). Both triggers still apply: a genuine sweep of the level and price then taking out the opposite reference. This reverses invariant 4 for that path (added in v13.4/v13.6). If marks start landing on wicks that are not structure, this is the first place to look.
f_confExt lost its last caller and is removed in the _OPT builds.

4. Rule C — in v16.0 / v2.0 only
The rule, as specified by the user:
    • P1 — a swing high whose pullback P1→P2 never completed the 3-candle rule, so P1 was never confirmed and never became a level.
    • P3 — a later high whose pullback P3→P4 did complete it, and whose wick went above P1 without closing above it.
    • P4 — that pullback's low, which did not wick or close below P2.
When all of that holds the range stays on the original pair: P1 becomes the possible BOS pivot and P2 the possible CHOCH pivot. P3 only swept P1 and the range was never broken, so the original structure still governs.
P1 is the highest high between the current floor's pivot and P3 (option 1 of three offered to the user). P2 is the lowest low between P1 and P3.
Verified against the reported XAUUSD 15m candles:
	O	H	L	C
P1	4244.300	4265.290	4250.275	4257.715
P2	4233.030	4236.455	4224.890	4234.480
P3	4253.275	4268.090	4253.035	4263.000
P4	4245.480	4247.335	4243.060	4247.275

4268.090 > 4265.290 swept · 4263.000 ≤ 4265.290 no close above · 4243.060 > 4224.890 P2 held → fires. Control with P3's high below P1's: does not fire.
New machinery: bufCl (a close buffer — the engine kept only high/low/ direction, and the rule needs P3's close at its own bar), f_extWin (extreme within a bounded window; f_retExtreme/f_retExtInc both run to the current bar), f_barCl. The floor half is applied through a deferred request.
Unproven: the condition arithmetic and the code structure were verified; the engine was not ported to Node and replayed over those bars. The specific risk is the P1 search bound (florS.x1) — if the floor sits somewhere unexpected when P3 confirms, P1 may resolve to a different high than intended.

5. TradingView / Pine facts learned the hard way
Do not re-derive these.
Inputs
    • Saved settings are matched by declaration order. Inserting or moving an input shifts every input after it.
    • group = controls where an input is drawn, not its declaration position. A group renders where its earliest-declared member sits. This is how new inputs get appended (invariant 5) yet still appear at the top.
    • Pine cannot show, hide, grey out or disable an input conditionally.
Alerts
    • Settings are snapshotted when the alert is created. Changing the panel afterwards does nothing. Always delete and recreate alerts after loading a new file.
    • Creating an alert replays the whole loaded history with barstate.isrealtime == false. Alerts never fire on those bars, but script state still evolves — this is what caused the v15.10 latch bug. Any latch must only be spent where an alert can actually be delivered.
    • The ARM readout reflects the chart's current settings, never a running alert's snapshot. TradingView does not expose an alert's frozen inputs back to the script. It says nothing about which alert fired.
    • alert.freq_once_per_bar fires intrabar on the first call in the bar; ..._once_per_bar_close fires at the close. Structure events use the second, retracements the first.
    • Alert timestamp seconds are diagnostic. :00 means it fired at a bar boundary; :23 means intrabar on the touch. This is what finally isolated the v15.10 bug.
    • "Stopped — Calculation error" means a runtime fault or a resource limit in the alert environment, which is tighter than the chart's. Not investigated to root cause (§6.4).
    • Alert-dialog interface: three attempts in an earlier session, all failed. ALERT_DIALOG_TEST.txt was written to settle it and was never run. If this comes up again, get that test run before writing any code.
Language / runtime
    • Pine has no comma-separated declarations.
    • A function cannot be declared inside a conditional block.
    • A function may mutate a global array (array.push) but may not assign to a global with :=.
    • Pine cannot infer an array's type from a bare na argument. Passing na where an array<label> is expected will not compile — write separate typed functions instead.
    • ta.* functions must run on every bar to keep their state. Compute unconditionally and gate the plot, never the call.
    • Pine is indentation-sensitive. Any scripted patch must derive indentation from its anchor line, never hard-code it.
    • Drawing objects keep whatever state they were last given, so restyling them on the last bar is enough — this is how the killzone edge-line mode works.
    • TradingView keeps ~500 drawings per script and silently deletes the oldest when exceeded. Every queue must be bounded. (This was v13.6 bug #4, where unbounded internal queues were deleting main BOS/CHOCH lines.)

6. Open items
6.1 The vertical CHOCH* line — UNRESOLVED
In Replay only, and only on the sequence where P3 makes a new high and P4 a new low, the possible CHOCH* rendered as a vertical segment. Confirmed as ours: restyling CHOCH* to dashed width-3 restyled the vertical segment too.
Isolated by bisection, not by theory: v15.16 clean, v15.17 broken. The only difference on that path is the opposite-side shift v15.17 added inside the promotion branch — a second mkSLine creating the floor line from within the ceiling block.
The cause was never identified. Every line is created as line.new(b, p, bar_index, p) — the same price at both ends — and nothing mutates a line's y afterwards. A bad-index guard (v15.18) did not stop it, which rules out an out-of-range bar.
v15.19 removed the block (chart clean). v15.20 re-implemented the same rule with a deferred construction — the user never confirmed whether that is clean. The current files do not contain the opposite-side shift at all, so the possible CHOCH* does not move with the possible BOS* on a promotion. That requirement is outstanding.
6.2 Rule C is not in the optimised files
It exists only in v16.0 / v2.0, which are unoptimised. Porting it onto the _OPT builds is a contained change.
6.3 The "current + previous range only" toggle does not work
v16.1 / v2.1 added generation tagging across all three tiers plus a queue for main marks (freeze() never tracked its drawings before). User reported it does not work; cause not investigated. The main-tier queue is the novel part and the first place to look.
6.4 Alert "Calculation error" on AUDUSD 5m
Same script, same settings; XAUUSD 1m/5m and AUDUSD 1m were fine. Two candidate families — resource limits (18 request.security calls each running a full 3-engine simulation, plus the intrabar volume pull), or a genuine runtime fault on thinner data. Diagnostic not yet run: load the indicator on AUDUSD 5m and read the chart's own error text and line number.
6.5 Smaller items
    • mnHiP/mnHiB/mnLoP/mnLoB are now write-only (they only fed the removed f_confExt). Harmless; removable in a second pass.
    • The internal opposite-side re-anchor still installs a bare wick, and since v15.14 the promotion does too. Still the most likely source of "the mark is not on the swing I see".
    • Internal-stream pivot dots not implemented. "Mark confirmed pivots (•)" shows the main stream only, so a dot is not proof the internal engine saw that pivot. One appended input. Offered repeatedly, never built. Highest-value diagnostic remaining.
    • Nothing has ever been compiled by TradingView by the assistant. Every file ships unverified. If the user reports an error, ask for the message and the line number.

7. Working practices with this user
    • Deliver a complete .txt file every time, to Downloads\, sent with SendUserFile. Bump the header version and add a changelog entry describing the cause, not just the change.
    • Short messages; brief replies — except when explaining a diagnosis, where the mechanism should be spelled out.
    • Verify before shipping. Pine cannot be compiled locally. Port the affected logic to a Node simulation and prove it. Node is available; Python is not.
    • Never hand-retype the file. Every version is produced by a scripted surgical transformation of the previous one: named patches anchored on exact code lines, each asserting it applied, then an automated verification pass.
    • Do not change unrelated rules. The user says so explicitly and has reverted work that did.
    • The user reports problems with screenshots, and they have repeatedly contained the decisive clue. Read them carefully before theorising.
    • The user is the authority on the rules. When they specify one, implement it — but state plainly if it reverses an invariant.
Post-build verification checklist
    • Inputs by position, name, type and default vs the previous version
    • Encoding: no BOM, CRLF, no tabs, 💪 💎 🧨 intact, no mojibake
    • Position-independent (multiset) diff of executable lines — an index diff reports thousands of false differences after any insert
    • Zero executable lines added is the strongest proof a refactor changed nothing
    • Bracket balance; no empty blocks; no comma-separated declarations
    • Declaration order for every new identifier
    • String literals: a raw " inside a Pine string ends it early
    • Indentation of every inserted line, derived from its anchor
    • Undefined-identifier scan after any removal (calibrate it on a known-good file first — it must report zero there)

8. Mistakes made this session — do not repeat
    • Three wrong diagnoses from screenshots, each corrected only by a simulation or by the user's own evidence: the arm-gate latch theory; an algebraic argument that the anchor window "could not matter" (brute force found it matters in 10.9% of cases); and a "proof" that the script cannot draw a vertical line that was based on comparing line.new's y-arguments textually rather than their runtime values.
    • Claimed a delivered file did not exist. A tool error lost the record of v15.14; it was then asserted twice that nothing had shipped. Check the filesystem before telling the user something was not delivered.
    • Shipped a patch that stripped indentation from every inserted line, which in Pine throws the block to global scope. Caught by inspection before delivery — but only because it was inspected.
    • A shell edit corrupted a build script and the rebuild failed silently, leaving the previous file on disk. Always check the build actually ran.
    • Verifier constants were repeatedly stale, producing false failures (expected input counts, line counts, creation-site counts). When a check fails, first ask whether the checker is wrong — but never assume it; prove it.
    • A verifier read comment text as code more than once, because the changelog quotes the code it removed. Scan code lines only.
    • Heredocs and node -e in this shell mangle backslashes and regex literals. Write scripts to a file with the Write tool.

9. Orientation for the next agent
If the user reports a wrong mark:
    1. Which engine — main, internal or inner?
    2. Did the relevant stream confirm the pivot? A main-stream dot does not answer this for an internal mark (§6.5). Port Module 1 to Node and print both.
    3. In scope? Levels must sit strictly after the range anchor, latched per range.
    4. Was the level replaced? Check, in order: the opposite-side re-anchor after a break, the pivot-2 promotion (which since v15.14 promotes to a bare wick), the ALT-mode migration.
    5. Reproduce in a Node sim before changing anything, and measure against an independent ground truth — never the engine's own output.
If the user asks for a new setting: append the input, give it a group =, and check whether the code consuming it runs before the append point. If it does, defer the consuming code to the end of the script (the v14.0 pattern) — do not declare the input early, which shifts every input after it.
If a drawing artifact appears: bisect by version before theorising. That is what identified §6.1 when four separate theories failed.

