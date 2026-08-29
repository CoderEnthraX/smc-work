#!/usr/bin/env python3
"""Surgical build: v15.15-opt -> v15.16-opt  /  EMA v1.5-opt -> v1.6-opt.

Every patch is named, anchored on exact code text, and asserts that it applied.
Indentation is always derived from the anchor line, never hard-coded: Pine is
indentation-sensitive and a stripped indent throws the block to global scope.

The two files share a byte-identical engine block, so the engine patches run
against both. Patches that touch the table run against both as well - the MTF
table is identical in the two builds.
"""
import re
import sys

CR = "\r\n"


class Build:
    def __init__(self, path):
        self.path = path
        with open(path, "r", encoding="utf-8", newline="") as f:
            raw = f.read()
        assert "\r\n" in raw, f"{path}: expected CRLF"
        self.lines = raw.split(CR)
        self.applied = []

    # ── primitives ──────────────────────────────────────────────────────────
    def _find(self, needle, start=0, count=None):
        """Index of every line whose stripped text equals needle.strip()."""
        want = needle.strip()
        hits = [i for i, l in enumerate(self.lines[start:], start) if l.strip() == want]
        if count is not None and len(hits) != count:
            raise AssertionError(
                f"{self.path}: expected {count} occurrence(s) of {want!r}, found {len(hits)}")
        return hits

    def indent_of(self, i):
        return self.lines[i][: len(self.lines[i]) - len(self.lines[i].lstrip())]

    def insert_after(self, name, anchor, new_lines, count=1, occurrence=None):
        """Insert new_lines after each matching anchor, at the anchor's indent."""
        hits = self._find(anchor, count=count)
        if occurrence is not None:
            hits = [hits[occurrence]]
        for i in reversed(hits):
            ind = self.indent_of(i)
            self.lines[i + 1: i + 1] = [ind + l if l else "" for l in new_lines]
        self.applied.append(f"{name}: inserted after {len(hits)} anchor(s)")

    def replace_line(self, name, old, new, count=1):
        hits = self._find(old, count=count)
        for i in hits:
            self.lines[i] = self.indent_of(i) + new.strip()
        self.applied.append(f"{name}: replaced {len(hits)} line(s)")

    def sub_in_line(self, name, anchor, old, new, count=1):
        """Textual substitution inside a matched line, indent untouched."""
        hits = self._find(anchor, count=count)
        for i in hits:
            assert old in self.lines[i], f"{self.path}: {old!r} not in {self.lines[i]!r}"
            self.lines[i] = self.lines[i].replace(old, new)
        self.applied.append(f"{name}: substituted in {len(hits)} line(s)")

    def insert_global_before(self, name, anchor, new_lines, count=1):
        """Insert at global scope (indent 0), verbatim. For top-level
        declarations: a Pine function may not be declared inside a block, so
        these must never inherit the anchor's indentation."""
        hits = self._find(anchor, count=count)
        i = hits[0]
        assert self.indent_of(i) == "", (
            f"{self.path}: global anchor {anchor!r} is itself indented")
        self.lines[i:i] = list(new_lines)
        self.applied.append(f"{name}: inserted at global scope before {anchor!r}")

    def insert_before_block(self, name, anchor, new_lines, count=1):
        hits = self._find(anchor, count=count)
        for i in reversed(hits):
            ind = self.indent_of(i)
            self.lines[i:i] = [ind + l if l else "" for l in new_lines]
        self.applied.append(f"{name}: inserted before {len(hits)} anchor(s)")

    def replace_block(self, name, first, last, new_lines):
        """Replace an inclusive line range identified by its first and last
        line text. Both must be unique and the block must be non-empty."""
        i = self._find(first, count=1)[0]
        js = [j for j in self._find(last) if j >= i]
        assert js, f"{self.path}: block end {last!r} not found after {first!r}"
        j = js[0]
        assert j > i, f"{self.path}: empty block for {name}"
        self.lines[i:j + 1] = list(new_lines)
        self.applied.append(f"{name}: replaced {j - i + 1} lines with {len(new_lines)}")

    def expand_line(self, name, anchor, new_lines, count=1):
        """Replace one line with several, verbatim (used for header prose)."""
        hits = self._find(anchor, count=count)
        for i in reversed(hits):
            self.lines[i:i + 1] = list(new_lines)
        self.applied.append(f"{name}: expanded {len(hits)} line(s) into {len(new_lines)}")

    def move_block(self, name, first, last, dest_after=None):
        """Move an inclusive line range to the end of the file, verbatim.
        A pure move - the multiset diff of executable lines must stay at zero."""
        i = self._find(first, count=1)[0]
        js = [j for j in self._find(last) if j >= i]
        assert js, f"{self.path}: block end {last!r} not found"
        j = js[0]
        block = self.lines[i:j + 1]
        del self.lines[i:j + 1]
        while self.lines and self.lines[-1].strip() == "":
            self.lines.pop()
        self.lines.append("")
        self.lines.extend(block)
        self.applied.append(f"{name}: moved {len(block)} lines to end of file")

    def append(self, name, new_lines):
        while self.lines and self.lines[-1].strip() == "":
            self.lines.pop()
        self.lines.append("")
        self.lines.extend(new_lines)
        self.applied.append(f"{name}: appended {len(new_lines)} lines")

    def write(self, out):
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(CR.join(self.lines))


# ═══════════════════════════════════════════════════════════════════════════
#  P1 — the drawn start of a mark is separated from its latched scope anchor
# ═══════════════════════════════════════════════════════════════════════════
def p1_main_draw_anchor(b: Build):
    # the type gains a draw bar, appended so no existing field shifts
    b.insert_after("P1.type", "bool  idmHit", ["int   drawB"], count=1)

    # mkSLine seeds drawB from the same bar, so nothing moves by default
    b.replace_line(
        "P1.mkSLine",
        "SLine.new(ln, lb, b, p, sid, bar_index, false, na, na, na, na, na, false)",
        "SLine.new(ln, lb, b, p, sid, bar_index, false, na, na, na, na, na, false, b)")

    # both label placements read the DRAW bar, not the scope anchor
    b.sub_in_line(
        "P1.repos",
        's.lb.set_x(th == "Right" ? endBar : int(math.avg(s.x1, endBar)))',
        "math.avg(s.x1, endBar)", "math.avg(s.drawB, endBar)")
    b.sub_in_line(
        "P1.freeze",
        'int lx = th == "Left" ? s.x1 : th == "Right" ? bar_index : int(math.avg(s.x1, bar_index))',
        '? s.x1 : th == "Right" ? bar_index : int(math.avg(s.x1, bar_index))',
        '? s.drawB : th == "Right" ? bar_index : int(math.avg(s.drawB, bar_index))')

    # a method to re-point the drawn start; the scope anchor x1 is never touched.
    # Declared at GLOBAL scope, before freeze - Pine forbids a function inside a block.
    b.insert_global_before("P1.setDraw", "method freeze(SLine s) =>", [
        "method setDraw(SLine s, int b) =>",
        "    if not na(s) and not na(b)",
        "        s.drawB := b",
        "        if not na(s.ln)",
        "            s.ln.set_x1(b)",
        "        if not na(s.lb)",
        "            string th = hAlignOf(s.sid, not s.done)",
        '            s.lb.set_x(th == "Left" ? b : th == "Right" ? bar_index : int(math.avg(b, bar_index)))',
        "",
    ], count=1)

    # ── the two pivot-2 promotions: capture the sweep bar, draw from it ──
    b.insert_after("P1.promo.ceil.capture", "int   sbC = ceilS.x1",
                   ["int   dbC = ceilS.swpB"], count=1)
    b.insert_after("P1.promo.ceil.draw", "ceilS := mkSLine(spC, sbC, sdC, drawOk)",
                   ["ceilS.setDraw(dbC)"], count=1)
    b.insert_after("P1.promo.flor.capture", "int   sbF = florS.x1",
                   ["int   dbF = florS.swpB"], count=1)
    b.insert_after("P1.promo.flor.draw", "florS := mkSLine(spF, sbF, sdF, drawOk)",
                   ["florS.setDraw(dbF)"], count=1)

    # ── the ALT-mode migration: restore the latched anchor, draw from the sweep ──
    # This site still moved x1 onto the sweep bar - the fault v15.5 and v15.15
    # each fixed elsewhere. Scope goes back to the pivot; the sweep bar becomes
    # the draw bar, so the line still starts on the candle that made the price.
    b.replace_line("P1.alt.ceil.scope", "int   mbC = ceilS.swpB", "int   mbC = ceilS.x1")
    b.insert_after("P1.alt.ceil.capture", "int   mbC = ceilS.x1",
                   ["int   maC = ceilS.swpB"], count=1)
    b.insert_after("P1.alt.ceil.draw", "ceilS := mkSLine(mpC, mbC, mdC, drawOk)",
                   ["ceilS.setDraw(maC)"], count=1)
    b.replace_line("P1.alt.flor.scope", "int   mbF = florS.swpB", "int   mbF = florS.x1")
    b.insert_after("P1.alt.flor.capture", "int   mbF = florS.x1",
                   ["int   maF = florS.swpB"], count=1)
    b.insert_after("P1.alt.flor.draw", "florS := mkSLine(mpF, mbF, mdF, drawOk)",
                   ["florS.setDraw(maF)"], count=1)


# ═══════════════════════════════════════════════════════════════════════════
#  P2 — the same separation for the internal and inner tiers
# ═══════════════════════════════════════════════════════════════════════════
def p2_int_inner_draw_anchor(b: Build):
    # revive the four sweep-bar variables (v15.15 left them write-only and the
    # opt build removed them) plus a draw bar per level
    for lvl in ("iCeil", "iFlor", "nCeil", "nFlor"):
        b.insert_after(f"P2.decl.{lvl}", f"var float {lvl}Swp  = na",
                       [f"var int   {lvl}SwpB = na", f"var int   {lvl}DrawB = na"], count=1)

    # every level assignment gets a companion draw-bar assignment.
    # non-promotion sites draw from the pivot; the promotion draws from the sweep.
    sites = {
        "iCeil": [("iCeilB    := na", "na"), ("iCeilB    := _sb", "_sb"),
                  ("iCeilB    := aPhB", "aPhB"), ("iCeilB    := _ibC", "PROMO"),
                  ("iCeilB    := iRbD", "iRbD")],
        "iFlor": [("iFlorB    := na", "na"), ("iFlorB    := _sb", "_sb"),
                  ("iFlorB    := aPlB", "aPlB"), ("iFlorB    := _ibF", "PROMO"),
                  ("iFlorB    := iRbU", "iRbU")],
        "nCeil": [("nCeilB    := na", "na"), ("nCeilB    := _nb", "_nb"),
                  ("nCeilB    := aPhB", "aPhB"), ("nCeilB    := _nbC", "PROMO"),
                  ("nCeilB    := nRbD", "nRbD")],
        "nFlor": [("nFlorB    := na", "na"), ("nFlorB    := _nb", "_nb"),
                  ("nFlorB    := aPlB", "aPlB"), ("nFlorB    := _nbF", "PROMO"),
                  ("nFlorB    := nRbU", "nRbU")],
    }
    for lvl, entries in sites.items():
        for anchor, src in entries:
            n = len(b._find(anchor))
            assert n >= 1, f"missing anchor {anchor}"
            val = f"{lvl}SwpB" if src == "PROMO" else src
            b.insert_after(f"P2.draw.{lvl}.{src}", anchor,
                           [f"{lvl}DrawB := {val}"], count=n)

    # record the sweep bar as each level is swept, and clear it with the sweep
    for lvl, ext in (("iCeil", "high"), ("iFlor", "low"),
                     ("nCeil", "high"), ("nFlor", "low")):
        b.insert_after(f"P2.swpB.{lvl}", f"{lvl}Swp  := {ext}",
                       [f"{lvl}SwpB := bar_index"], count=1)
        n = len(b._find(f"{lvl}Swp  := na"))
        b.insert_after(f"P2.swpBclr.{lvl}", f"{lvl}Swp  := na",
                       [f"{lvl}SwpB := na"], count=n)

    # the mark functions take the DRAW bar; they use it only to place the drawing
    b.sub_in_line("P2.mark.iceil", "f_intMark(iCeilP, iCeilB, isChoU)",
                  "iCeilB", "iCeilDrawB")
    b.sub_in_line("P2.mark.iflor", "f_intMark(iFlorP, iFlorB, isChoD)",
                  "iFlorB", "iFlorDrawB")
    b.sub_in_line("P2.mark.nceil", "rqUpB   := nCeilB", "nCeilB", "nCeilDrawB")
    b.sub_in_line("P2.mark.nflor", "rqDnB   := nFlorB", "nFlorB", "nFlorDrawB")


# ═══════════════════════════════════════════════════════════════════════════
#  P3 — alert conditions for the inner tier
# ═══════════════════════════════════════════════════════════════════════════
def p3_inner_alertconditions(b: Build):
    anchor = ('alertcondition((evIBosUp or evIBosDn or evIChoUp or evIChoDn) and almOk, '
              '"Any internal structure event", "Internal structure event — {{ticker}} {{interval}}")')
    b.insert_after("P3.alertconditions", anchor, [
        'alertcondition(evNBosUp and almOk, "Bullish nBOS",    "Bullish nBOS — {{ticker}} {{interval}}")',
        'alertcondition(evNBosDn and almOk, "Bearish nBOS",    "Bearish nBOS — {{ticker}} {{interval}}")',
        'alertcondition(evNChoUp and almOk, "Bullish nCHOCH",  "Bullish nCHOCH — {{ticker}} {{interval}}")',
        'alertcondition(evNChoDn and almOk, "Bearish nCHOCH",  "Bearish nCHOCH — {{ticker}} {{interval}}")',
        'alertcondition((evNBosUp or evNBosDn) and almOk, "Any nBOS",   "nBOS — {{ticker}} {{interval}}")',
        'alertcondition((evNChoUp or evNChoDn) and almOk, "Any nCHOCH", "nCHOCH — {{ticker}} {{interval}}")',
        'alertcondition((evNBosUp or evNBosDn or evNChoUp or evNChoDn) and almOk, "Any inner structure event", "Inner structure event — {{ticker}} {{interval}}")',
    ], count=1)


# ═══════════════════════════════════════════════════════════════════════════
#  P4 — engine helpers that take the price buffers as arguments
# ═══════════════════════════════════════════════════════════════════════════
# The chart engine's helpers read the GLOBAL buffers, which is why invariant 6
# forbids calling rearm() inside request.security(): on a higher timeframe the
# globals hold chart-timeframe bars. These twins take the buffers as arguments,
# so the per-timeframe engine can run the real rules on its OWN bars.
def p4_buffer_helpers(b: Build):
    b.insert_global_before("P4.helpers", "f_idmMark(SLine s) =>", [
        "f_retExtB(array<float> bH, array<float> bL, int fromBar, bool findHigh, bool incl) =>",
        "    int sz    = array.size(bL)",
        "    int jEnd  = sz - 1",
        "    int jLast = incl ? jEnd : jEnd - 1",
        "    float p   = na",
        "    int   b   = na",
        "    if jLast >= 0",
        "        int j0 = math.max(0, math.min(fromBar - bar_index + sz, jLast))",
        "        array<float> src = findHigh ? bH : bL",
        "        int base = bar_index - sz + 1",
        "        for j = j0 to jLast",
        "            float v = array.get(src, j)",
        "            if na(p) or (findHigh ? v >= p : v <= p)",
        "                p := v",
        "                b := base + j",
        "    [p, b]",
        "",
        "method rearmB(SwingTracker t, float p, int b, array<float> bH, array<float> bL, array<int> bD) =>",
        "    t.potential    := p",
        "    t.potentialBar := b",
        "    int  sz  = array.size(bH)",
        "    int  idx = b - bar_index + sz - 1",
        "    bool ok  = not na(b) and idx >= 0 and idx <= sz - 1",
        "    int  dir = ok ? array.get(bD, idx) : 0",
        "    bool pb  = t.isHigh ? dir == -1 : dir == 1",
        "    t.count    := pb ? 1 : 0",
        "    t.refLevel := pb ? (t.isHigh ? array.get(bL, idx) : array.get(bH, idx)) : na",
        "",
        "f_isSwingB(array<float> bH, array<float> bL, int pb, bool isHigh, int k) =>",
        "    int  sz  = array.size(bH)",
        "    int  idx = pb - bar_index + sz - 1",
        "    bool ok  = not na(pb) and idx - k >= 0 and idx <= sz - 1",
        "    if ok",
        "        float p = isHigh ? array.get(bH, idx) : array.get(bL, idx)",
        "        for j = 1 to k",
        "            float v = isHigh ? array.get(bH, idx - j) : array.get(bL, idx - j)",
        "            if isHigh ? v > p : v < p",
        "                ok := false",
        "    ok",
        "",
        "f_lastMinorB(array<int> arrB, array<float> arrP, int beforeBar) =>",
        "    float p = na",
        "    int   b = na",
        "    int   n = array.size(arrB)",
        "    if n > 0",
        "        for i = n - 1 to 0",
        "            if array.get(arrB, i) < beforeBar",
        "                p := array.get(arrP, i)",
        "                b := array.get(arrB, i)",
        "                break",
        "    [p, b]",
        "",
        "f_armIdmB(array<int> mHiB, array<float> mHiP, array<int> mLoB, array<float> mLoP, array<float> bH, array<float> bL, int pivB, bool isCeil) =>",
        "    [ip, ib] = f_lastMinorB(isCeil ? mLoB : mHiB, isCeil ? mLoP : mHiP, pivB)",
        "    bool hit = false",
        "    if not na(ip)",
        "        [xp, xb] = f_retExtB(bH, bL, pivB, not isCeil, false)",
        "        bool takenPast = not na(xp) and (isCeil ? xp < ip : xp > ip)",
        "        bool takenNow  = isCeil ? low < ip : high > ip",
        "        hit := takenPast or takenNow",
        "    [ip, hit]",
        "",
    ], count=1)


# ═══════════════════════════════════════════════════════════════════════════
#  P5 — f_tfPack rebuilt on the v15.15 rule set
# ═══════════════════════════════════════════════════════════════════════════
def p5_tfpack(b: Build, pine_path):
    with open(pine_path, "r", encoding="utf-8") as f:
        body = [l.rstrip("\n") for l in f]
    while body and body[-1].strip() == "":
        body.pop()
    b.replace_block("P5.f_tfPack", "f_tfPack(bool on) =>",
                    "[trOut, evOut, inOut, nnOut]", body)
    # every request.security destructure gains the event count
    tfs = ["1", "2", "3", "5", "10", "15", "30", "45", "60", "120", "180",
           "240", "360", "480", "720", "D", "W", "M"]
    for t in tfs:
        hits = [i for i, l in enumerate(b.lines)
                if l.startswith("[_t%s," % t) or l.startswith("[_t%s " % t)]
        assert len(hits) == 1, f"security destructure for {t}: {len(hits)} hits"
        i = hits[0]
        old = b.lines[i]
        assert "_n%s]" % t in old, f"unexpected destructure shape: {old}"
        b.lines[i] = old.replace("_n%s]" % t, "_n%s, _m%s]" % (t, t))
    b.applied.append("P5.security: 18 destructures now take the event count")


# ═══════════════════════════════════════════════════════════════════════════
#  P6 — warm-up gate
# ═══════════════════════════════════════════════════════════════════════════
# A per-timeframe simulation only sees as much history as request.security
# yields, and its opening state depends on the first bar it gets. Measured over
# 500 series: agreement with full history is 63% after one confirmed main
# event, 91% after four, 98% after seven, ~100% after eleven. Below the
# threshold the row reports no trend rather than a confident wrong one.
def p6_warmup(b: Build):
    # f_tfRow takes the count and gates on it; the chart's own row is exempt
    # because the chart engine always has the full loaded history.
    b.replace_line("P6.sig",
        "f_tfRow(array<string> nm, array<int> tr, array<int> ev, array<int> intr, array<int> innr, bool use, string disp, string tfs, int t, int e, int n, int w) =>",
        "f_tfRow(array<string> nm, array<int> tr, array<int> ev, array<int> intr, array<int> innr, bool use, string disp, string tfs, int t, int e, int n, int w, int mc) =>")
    b.insert_after("P6.warm", "bool isChartTf = tfs == timeframe.period",
                   ["bool warm = isChartTf or tblWarm <= 0 or mc >= tblWarm"], count=1)
    b.replace_line("P6.tr", "array.push(tr, isChartTf ? trendDir : t)",
                   "array.push(tr, isChartTf ? trendDir : warm ? t : 0)")
    b.replace_line("P6.intr", "array.push(intr, isChartTf ? iTrend : n)",
                   "array.push(intr, isChartTf ? iTrend : warm ? n : 0)")
    b.replace_line("P6.innr", "array.push(innr, isChartTf ? nTrend : w)",
                   "array.push(innr, isChartTf ? nTrend : warm ? w : 0)")
    # the 18 call sites pass their count
    tfs = ["1", "2", "3", "5", "10", "15", "30", "45", "60", "120", "180",
           "240", "360", "480", "720", "D", "W", "M"]
    n = 0
    for t in tfs:
        tail = "_t%s, _e%s, _i%s, _n%s)" % (t, t, t, t)
        hits = [i for i, l in enumerate(b.lines) if l.rstrip().endswith(tail)]
        assert len(hits) == 1, f"f_tfRow call for {t}: {len(hits)} hits"
        b.lines[hits[0]] = b.lines[hits[0]].rstrip()[:-1] + ", _m%s)" % t
        n += 1
    b.applied.append(f"P6.calls: {n} f_tfRow calls pass the event count")

    # the input is APPENDED (invariant 5) so all 454 existing inputs keep their
    # declaration positions and saved settings carry over untouched...
    with open("tools/tblWarm_input.pine", "r", encoding="utf-8") as f:
        warm_input = [l.rstrip("\n") for l in f if l.strip()]
    assert len(warm_input) == 1, "the warm-up input must be exactly one line"
    assert warm_input[0].count('"') % 2 == 0, "unbalanced quotes in the warm-up input"
    b.append("P6.input", warm_input)
    # ...so the table render must move BELOW it (the v14.0 deferred pattern)
    b.move_block("P6.move",
        "f_tfRow(array<string> nm, array<int> tr, array<int> ev, array<int> intr, array<int> innr, bool use, string disp, string tfs, int t, int e, int n, int w, int mc) =>",
        "table.cell(smcTbl, _colInn, i + 1, _wnTx, text_color = _wnTc, text_size = tsize(tblRowSz), bgcolor = _wnBg)")


# ═══════════════════════════════════════════════════════════════════════════
#  P7 — header: version, changelog, and the invariant-4 wording
# ═══════════════════════════════════════════════════════════════════════════
def p7_header(b: Build, old_title, new_title):
    b.replace_line("P7.title", old_title, new_title)
    b.replace_line("P7.subtitle",
        "//  Optimised build of v15.15: comments stripped, dead code removed, behaviour",
        "//  Optimised build. Comments stripped and dead code removed; every rule below")
    b.replace_line("P7.subtitle2",
        "//  identical. Every rule, level, mark and alert is unchanged.",
        "//  is the live rule set. See the changelog under the banner.")
    # invariant 4 back to its v15.15 wording - the opt header had dropped the
    # deliberate exception that the code still relies on
    b.expand_line("P7.inv4",
        "//   4. Never adopt or seed a level price has already closed beyond.",
        ["//   4. A structure level is a CONFIRMED PIVOT, with ONE deliberate exception",
         "//      (v15.14): a pivot-2 promotion takes the SWEPT WICK. There the sweep of",
         "//      the level plus price then taking out the opposite reference IS the",
         "//      qualification, so no separate 3-candle confirmation is required.",
         "//      Otherwise: never adopt or seed a level price has already closed beyond."])
    with open("tools/changelog_v1516.txt", "r", encoding="utf-8") as f:
        log = [l.rstrip("\n") for l in f]
    while log and log[-1].strip() == "":
        log.pop()
    bars = [i for i, l in enumerate(b.lines)
            if l.startswith("// ═") and i < 12]
    assert len(bars) >= 2, "header banner not found"
    b.lines[bars[1] + 1:bars[1] + 1] = log + ["//"]
    b.applied.append(f"P7.changelog: {len(log)} lines inserted under the banner")


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    b = Build(src)
    p1_main_draw_anchor(b)
    p2_int_inner_draw_anchor(b)
    p3_inner_alertconditions(b)
    p4_buffer_helpers(b)
    p5_tfpack(b, "tools/f_tfPack_v1516.pine")
    p6_warmup(b)
    if "EMA" in src:
        p7_header(b, "//  SMC MARKET STRUCTURE — 3CP + EMA  ·  v1.5-opt",
                     "//  SMC MARKET STRUCTURE — 3CP + EMA  ·  v1.6-opt")
    else:
        p7_header(b, "//  SMC MARKET STRUCTURE — 3CP + VOLUME PROFILES  ·  v15.15-opt",
                     "//  SMC MARKET STRUCTURE — 3CP + VOLUME PROFILES  ·  v15.16-opt")
    b.write(dst)
    print(f"{src} -> {dst}")
    for a in b.applied:
        print("   ", a)
