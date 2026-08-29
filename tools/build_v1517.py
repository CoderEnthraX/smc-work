#!/usr/bin/env python3
"""Surgical build: v15.15-opt -> v15.17-opt  /  EMA v1.5-opt -> v1.7-opt.

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
    b.applied.append("P5.security: 18 destructures unchanged (still 4 values)")


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
    with open("tools/changelog_v1517.txt", "r", encoding="utf-8") as f:
        log = [l.rstrip("\n") for l in f]
    while log and log[-1].strip() == "":
        log.pop()
    bars = [i for i, l in enumerate(b.lines)
            if l.startswith("// ═") and i < 12]
    assert len(bars) >= 2, "header banner not found"
    b.lines[bars[1] + 1:bars[1] + 1] = log + ["//"]
    b.applied.append(f"P7.changelog: {len(log)} lines inserted under the banner")



# ═══════════════════════════════════════════════════════════════════════════
#  P4b — f_provDir, and the chart-side three-tier cascade
# ═══════════════════════════════════════════════════════════════════════════
# The table must never print a dash. A tier reports its own trend; while that
# tier is still neutral it inherits the tier above it; and the main tier, before
# its first event, reads where price sits inside the standing range. So every
# cell always carries a direction, and it is always derived from real structure.
def p4b_provdir(b: Build):
    b.insert_global_before("P4b.f_provDir", "f_idmMark(SLine s) =>", [
        "f_provDir(float ce, float fl, float hi, float lo, float px) =>",
        "    float c = na(ce) ? hi : ce",
        "    float f = na(fl) ? lo : fl",
        "    int d = 0",
        "    if not na(c) and not na(f) and c >= f",
        "        d := px >= math.avg(c, f) ? 1 : -1",
        "    d",
        "",
    ], count=1)


def p6_chart_cascade(b: Build):
    # computed at global scope after the engine block, read by f_tfRow
    b.insert_global_before("P6.chartCascade",
        "f_tfRow(array<string> nm, array<int> tr, array<int> ev, array<int> intr, array<int> innr, bool use, string disp, string tfs, int t, int e, int n, int w) =>", [
        "float _chCe = na",
        "float _chFl = na",
        "if not na(ceilS)",
        "    _chCe := ceilS.price",
        "if not na(florS)",
        "    _chFl := florS.price",
        "int _chPv = f_provDir(_chCe, _chFl, allHi, allLo, close)",
        "int _chTr = trendDir != 0 ? trendDir : _chPv",
        "int _chIn = iTrend   != 0 ? iTrend   : _chTr",
        "int _chNn = nTrend   != 0 ? nTrend   : _chIn",
        "",
    ], count=1)
    b.replace_line("P6.tr", "array.push(tr, isChartTf ? trendDir : t)",
                   "array.push(tr, isChartTf ? _chTr : t)")
    b.replace_line("P6.intr", "array.push(intr, isChartTf ? iTrend : n)",
                   "array.push(intr, isChartTf ? _chIn : n)")
    b.replace_line("P6.innr", "array.push(innr, isChartTf ? nTrend : w)",
                   "array.push(innr, isChartTf ? _chNn : w)")


# ═══════════════════════════════════════════════════════════════════════════
#  P8 — the range % line
# ═══════════════════════════════════════════════════════════════════════════
def p8_midline(b: Build):
    with open("tools/midline_module.pine", "r", encoding="utf-8") as f:
        mod = [l.rstrip("\n") for l in f]
    while mod and mod[-1].strip() == "":
        mod.pop()
    # APPENDED (invariant 5): every existing input keeps its declaration
    # position, and the drawing sits below the inputs it reads.
    b.append("P8.midline", mod)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    b = Build(src)
    p3_inner_alertconditions(b)
    p4_buffer_helpers(b)
    p4b_provdir(b)
    p5_tfpack(b, "tools/f_tfPack_v1517.pine")
    p6_chart_cascade(b)
    p8_midline(b)
    if "EMA" in src:
        p7_header(b, "//  SMC MARKET STRUCTURE — 3CP + EMA  ·  v1.5-opt",
                     "//  SMC MARKET STRUCTURE — 3CP + EMA  ·  v1.7-opt")
    else:
        p7_header(b, "//  SMC MARKET STRUCTURE — 3CP + VOLUME PROFILES  ·  v15.15-opt",
                     "//  SMC MARKET STRUCTURE — 3CP + VOLUME PROFILES  ·  v15.17-opt")
    b.write(dst)
    print(f"{src} -> {dst}")
    for a in b.applied:
        print("   ", a)
