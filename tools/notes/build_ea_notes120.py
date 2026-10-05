# SMC_Structure_EA_v12.0_NOTES.txt = the new v12.0 part + the EA v11.2 notes (from "NEW IN v11.2" on)
import sys
R = "/home/user/smc-work/"
old = open(R + "SMC_Structure_EA_v11.2_NOTES.txt").read()
k = old.index("NEW IN v11.2 - THE STOP BUFFER")
body = old[k:]
CHECK = open(sys.argv[1]).read().rstrip("\n") if len(sys.argv) > 1 else "  CHECKS"
NEW = """SMC STRUCTURE EA v12.0 (+ HEDGE) - NOTES
=========================================
File: SMC_Structure_EA_v12.0.mq5 (MetaTrader 5 Expert Advisor, MQL5)
Owner: Punit. Times in these notes are IST unless they say otherwise.
The EA follows the TradingView strategy v12.0. Install it like v11.1
(section 3); you can delete SMC_Structure_EA_v11.2 from MT5.


NEW IN v12.0 - RULE 3 / RULE 4: ENTER AT THE CLOSE OF THE SIGNAL CANDLE
-----------------------------------------------------------------------
The same rules as the TradingView strategy v12.0 (its notes, item 121).
A new group at the very END of the EA settings (after group 38), so your
saved settings keep their places:
  39. Entry at the close of the signal candle - rules 3 / 4 (v12.0)
    Entry at the close of the signal candle
                         Off (rules 1 / 2 as now) / RULE 3 - always
                         enter at the close / RULE 4 - enter at the
                         close only if the stop distance is within
                         the limits
    - RULE 4: skip if the stop is FURTHER than (0 = off)    30
    - RULE 4: skip if the stop is CLOSER than (0 = off)      3
    - RULE 4: when the stop is too far      Skip the setup / Fall back
                                            to RULE 1 / 2 (wait for the
                                            pullback)
Default "Off": the EA trades exactly like v11.2 (tested, byte for byte).

RULE 3: when a candle closes and confirms the signal (your CHOCH), the
EA buys or sells AT MARKET on the first tick of the next candle - the
same moment TradingView fills it (the next open). Stop = CHOCH* level +
buffer; target = your R from the entry; size from your risk.
RULE 4: the same, only if the distance from the close to the stop is
within the limits (3 - 30 = 3.00 - 30.00 on gold in the Price unit;
the unit of group 38 like group 24). Too far: skipped, or falls back to
rule 1 / 2 (a pullback order that must keep the same limits). Too
close: always skipped.
Example: stop 4,089.00; the candle closes at 4,101.00 -> distance 12.00,
enters; a huge candle closes at 4,125.00 -> 36.00, too far.

"How entries are executed" (group 40) does not matter for rules 3 / 4:
both touch and pending mode send a MARKET order at once. If the order
does not fill on that candle (refused, market closed), the setup is
dropped - it is never sent again at a later price (TradingView does the
same). With "close and reverse" ON a signal that reverses an open trade
enters one candle later, after the old trade is closed.

THE TABLE: "ENTRY AT THE SIGNAL CLOSE (group 39)" (Full table), e.g.
"RULE 4 (3 - 30)  -  12 entered  |  skipped: too far 4 / too close 1",
and "- by ENTRY RULE 3 / 4 (signal close)" under the entries. The audit
(group 20) writes "R4 ARMED - entry at the close" or "SKIP - RULE 4:
stop too far (36.00)" in the Experts tab.

HOW IT WAS CHECKED
""" + CHECK + """
  NOT checked here: the real MQL5 compiler. Compile it (F7) and send me
  any error lines.

IS IT BETTER? Not tested for profit (you asked for the build without the
test). Entering at the close means a further stop than rule 1's pullback
(a smaller size for the same risk) and the full spread on every entry.
Test it in the Strategy Tester and on a demo account first.


""" + "=" * 74 + """
EVERYTHING BELOW IS FROM THE EA v11.2 NOTES - still true for v12.0.
(Where it says v11.2 or v11.1, read v12.0.)
""" + "=" * 74 + "\n\n"
t = NEW + body
assert all(ord(c) < 128 for c in t)
bad = [l for l in NEW.split("\n") if len(l) > 78]
assert not bad, bad
open(R + "SMC_Structure_EA_v12.0_NOTES.txt", "w").write(t.rstrip("\n") + "\n")
print("EA v12.0 notes", len(t.split("\n")), "lines")
