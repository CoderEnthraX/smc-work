# v15.0: make the TradingView file smaller (TradingView: at most 100,256 compiled tokens; v14.0 had 100,771) WITHOUT changing
# what it does. Every step only rewrites code that the chart / the trades get the same result from:
#  1. values nobody reads (written but never used: old run highs / lows, old event flags, unused arrays)
#  2. the fixed display choices of the old Market Structure indicator written as plain values (line style, label size,
#     alignment, colours that were the same black / blue / yellow / gray for every choice)
#  3. the internal tier (blue iBOS / iCHOCH) and the inner tier (yellow nBOS / nCHOCH) were two copies of the same code, each
#     written out twice (ceiling / floor): now ONE routine run for both tiers and both sides - display only, no trade reads them
#  4. f_retExtreme / f_retExtInc (the same loop, one bar apart) = one function
# usage: imported by pine150.py (compact(s) -> s)
import re


class Txt:
    def __init__(self, s): self.s = s

    def rep(self, old, new, n=1):
        c = self.s.count(old)
        if c != n: raise SystemExit('compact: expected %d x, found %d x: %r' % (n, c, old[:150]))
        self.s = self.s.replace(old, new)

    def block(self, first, last, new):
        """replace the lines from the one equal to 'first' to the next one equal to 'last' (both included)"""
        L = self.s.split('\n')
        a = [i for i, l in enumerate(L) if l == first]
        if len(a) != 1: raise SystemExit('compact: first line %r found %d x' % (first, len(a)))
        b = [i for i in range(a[0], len(L)) if L[i] == last]
        if not b: raise SystemExit('compact: last line %r not found' % last)
        L[a[0]:b[0] + 1] = new.split('\n') if new != '' else []
        self.s = '\n'.join(L)

    def drop(self, line, n=1):
        """remove whole lines equal to 'line'"""
        L = self.s.split('\n')
        k = [i for i, l in enumerate(L) if l == line]
        if len(k) != n: raise SystemExit('compact: line %r found %d x' % (line, len(k)))
        self.s = '\n'.join(l for l in L if l != line)


def _args(s, i):
    """s[i] == '(' -> (list of top-level argument texts, index after the closing bracket)"""
    d = 0; q = False; j = i; parts = []; a = i + 1
    while j < len(s):
        c = s[j]
        if q:
            if c == '\\': j += 2; continue
            if c == '"': q = False
        elif c == '"': q = True
        elif c in '([': d += 1
        elif c in ')]':
            d -= 1
            if d == 0:
                parts.append(s[a:j]); return parts, j + 1
        elif c == ',' and d == 1:
            parts.append(s[a:j]); a = j + 1
        j += 1
    raise SystemExit('compact: unbalanced at %d' % i)


def _helpers(s):
    """str.tostring(x, format.mintick) -> f_mt(x); str.tostring(math.round(x * 100) / 100) -> f_r2(x)"""
    out = []; i = 0; n_mt = n_r2 = 0
    while True:
        k = s.find('str.tostring(', i)
        if k < 0: out.append(s[i:]); break
        out.append(s[i:k])
        args, e = _args(s, k + len('str.tostring'))
        if len(args) == 2 and args[1].strip() == 'format.mintick':
            out.append('f_mt(' + _helpers(args[0]) + ')'); n_mt += 1
        elif len(args) == 1 and re.match(r'^math\.round\(.*\) / 100$', args[0].strip()):
            inner, e2 = _args(args[0].strip(), len('math.round'))
            if e2 == len(args[0].strip()) - len(' / 100') and len(inner) == 1 and inner[0].endswith(' * 100'):
                out.append('f_r2(' + _helpers(inner[0][:-len(' * 100')]) + ')'); n_r2 += 1
            else:
                out.append('str.tostring(' + ','.join(_helpers(a) for a in args) + ')')
        else:
            out.append('str.tostring(' + ','.join(_helpers(a) for a in args) + ')')
        i = e
    r = ''.join(out)
    if n_mt or n_r2:
        _helpers.count = getattr(_helpers, 'count', 0) + n_mt + n_r2
    return r


def compact(s):
    t = Txt(s)
    # ---- 2. fixed display choices
    t.block('intDefOn = true', 'strSz   = "Small"', '')
    t.block('lstyle(string s) => s == "Dashed" ? line.style_dashed : s == "Dotted" ? line.style_dotted : line.style_solid',
            'lblStyle(string tv) => tv == "Above" ? label.style_label_down : tv == "Below" ? label.style_label_up : label.style_none', '')
    t.block('var color b1_lcE = color.black', '            => [c2_lcE, c2_tcE, "Solid", 1, "CHOCH", "Small", "Middle", "Center", true]', '')
    t.block('hAlignOf(int sid, bool pend) =>', '            s.lb.set_x(f_xClamp(th == "Right" ? endBar : int(math.avg(s.x1, endBar))))',
            '''method repos(SLine s, int endBar) =>
    if not na(s) and not na(s.ln) and not na(s.lb)
        s.lb.set_x(f_xClamp(int(math.avg(s.x1, endBar))))''')
    t.block('method freeze(SLine s) =>', '            f_addLb(mainLb, mainCnt, s.lb)',
            '''method freeze(SLine s) =>
    if not na(s) and not na(s.ln)
        s.done := true
        s.ln.set_x2(bar_index)
        s.ln.set_extend(extend.none)
        s.ln.set_style(line.style_solid)
        if not na(s.lb)
            s.lb.delete()
        s.lb := label.new(f_xClamp(int(math.avg(s.x1, bar_index))), s.price, s.sid <= 1 ? "BOS" : "CHOCH", color = color(na), textcolor = color.black, style = label.style_none, size = size.small)
        f_addLn(mainLn, mainCnt, s.ln)
        f_addLb(mainLb, mainCnt, s.lb)''')
    t.block('mkSLine(float p, int b, int sid, bool draw) =>', '    SLine.new(ln, lb, b, p, sid, bar_index, false, na, na, na, na, na, false, false)',
            '''mkSLine(float p, int b, int sid, bool draw) =>
    line ln = na
    label lb = na
    int _bx = f_xClamp(b)
    if draw
        ln := line.new(_bx, p, bar_index, p, color = color.black, width = 1, style = line.style_dotted, extend = extend.right)
        lb := label.new(int(math.avg(_bx, bar_index)), p, sid <= 1 ? "BOS*" : "CHOCH*", color = color(na), textcolor = color.black, style = label.style_none, size = size.small)
    SLine.new(ln, lb, b, p, sid, bar_index, false, na, na, na, na, na, false, false)''')
    t.rep('size = tsize(strSz)))', 'size = size.small))', 2)
    t.rep('label.new(rbC, na, strTxt,', 'label.new(rbC, na, "#",')
    t.rep('label.new(rbF, na, strTxt,', 'label.new(rbF, na, "#",')
    # f_idmMark did nothing (a local value only)
    t.block('f_idmMark(SLine s) =>', '    bool inWin = (last_bar_index - bar_index) <= 500', '')
    t.rep('''            if takenPast or takenNow
                s.idmHit := true
                f_idmMark(s)''', '''            if takenPast or takenNow
                s.idmHit := true''')
    t.rep('''        ceilS.idmHit := true
        f_idmMark(ceilS)''', '''        ceilS.idmHit := true''')
    t.rep('''        florS.idmHit := true
        f_idmMark(florS)''', '''        florS.idmHit := true''')

    # ---- 4. one function for the extreme since a bar (inc = up to this bar, else up to the bar before)
    t.block('f_retExtreme(int fromBar, bool findHigh) =>', '    [p, b]', '''f_retExt(int fromBar, bool findHigh, bool inc) =>
    int sz = array.size(bufLo)
    int e  = inc ? sz - 1 : sz - 2
    float p  = na
    int   b  = na
    if e >= 0
        array<float> src = findHigh ? bufHi : bufLo
        for j = math.max(0, math.min(fromBar - bar_index + sz, e)) to e
            float v = array.get(src, j)
            if na(p) or (findHigh ? v >= p : v <= p)
                p := v
                b := bar_index - sz + 1 + j
    [p, b]''')
    t.block('f_retExtInc(int fromBar, bool findHigh) =>', '    [p, b]', '')
    t.s = re.sub(r'f_retExtreme\(([^()]*)\)', r'f_retExt(\1, false)', t.s)
    t.s = re.sub(r'f_retExtInc\(([^()]*)\)', r'f_retExt(\1, true)', t.s)
    assert 'f_retExtreme' not in t.s and 'f_retExtInc' not in t.s

    # ---- 1. values nobody reads
    t.drop('var array<float> mnHiP = array.new_float()')
    t.drop('var array<float> mnLoP = array.new_float()')
    t.rep('''        array.push(mnHiP, phP)
        array.push(mnHiB, phB)
        if array.size(mnHiB) > 300
            array.shift(mnHiP)
            array.shift(mnHiB)''', '''        array.push(mnHiB, phB)
        if array.size(mnHiB) > 300
            array.shift(mnHiB)''')
    t.rep('''        array.push(mnLoP, plP)
        array.push(mnLoB, plB)
        if array.size(mnLoB) > 300
            array.shift(mnLoP)
            array.shift(mnLoB)''', '''        array.push(mnLoB, plB)
        if array.size(mnLoB) > 300
            array.shift(mnLoB)''')
    t.rep('''            if high > ceilS.price
                evSwpHi := true
''', '''            if high > ceilS.price
''')
    t.rep('''            if low < florS.price
                evSwpLo := true
''', '''            if low < florS.price
''')
    t.drop('var bool stCapFlag = false')
    t.drop('            stCapFlag := false')
    t.drop('string _eId   = ""')
    t.drop('int    _eDir  = 0')
    t.drop('        _eId  := strategy.opentrades.entry_id(strategy.opentrades - 1)')
    t.drop('        _eDir := strategy.opentrades.size(strategy.opentrades - 1) > 0 ? 1 : -1')
    # the higher timeframe's internal tier: its trend and event flag were never read (only its levels feed pullback rule 3)
    t.drop('        var int   iTr  = 0')
    t.drop('        bool iEvt    = false')
    t.rep('''            iTr  := 0
            iAnc := na''', '''            iAnc := na''')
    t.rep('''                iTr  := 1
                iEvt := true
''', '')
    t.rep('''                iTr  := -1
                iEvt := true
''', '')

    # ---- 3. the internal and inner tiers: one routine
    t.block('bool intUse = altMode ? intAltOn : intDefOn', '        f_intPrune()', '')
    t.block('f_intStrong(int b, bool isLow) =>', '        f_intPrune()', '')
    t.block('bool evSwpHi  = false', 'bool evIChoDn = false', '')
    t.block('var float iRunHi = na', 'var int   iTrend    = 0', '')
    t.block('var int   iAncB     = na', 'bool  _intClrReq = false', '''
// v15.0 (made smaller): the internal tier (blue iBOS / iCHOCH, inside the main leg) and the inner tier (yellow nBOS / nCHOCH,
// inside the internal leg) - display only. One level = one ceiling or floor of a tier.
type TLvl
    float p
    int   b
    int   born
    float swp
    int   swpB
    bool  swpT = false
    float ref
    float idmP
    bool  idmHit = false
    line  pl
    label plb

type Tier
    int    tr = 0
    int    anc
    TLvl   c
    TLvl   f
    bool   ev = false
    bool   st = false
    color  col
    string tx
    array<line>  ln
    array<label> lb
    array<int>   cnt

// a new level at a pivot (p, bar b) with its IDM
method lvSet(TLvl l, float p, int b, bool up) =>
    l.p    := p
    l.b    := b
    l.born := bar_index
    l.swp  := na
    l.swpB := na
    l.ref  := na
    [ip, ih] = f_intArmIdm(b, up)
    l.idmP   := ip
    l.idmHit := ih

method lvClr(TLvl l) =>
    l.p    := na
    l.b    := na
    l.born := na
    l.swp  := na
    l.swpB := na
    l.ref  := na
    l.idmP   := na
    l.idmHit := false

f_tMark(Tier t, float p, int pb, bool isCho) =>
    if (last_bar_index - bar_index) <= 500 and f_xNear(pb)
        f_addLn(t.ln, t.cnt, line.new(pb, p, bar_index, p, color = t.col, width = 1, style = line.style_solid))
        f_addLb(t.lb, t.cnt, label.new(int(math.avg(pb, bar_index)), p, t.tx + (isCho ? "CHOCH" : "BOS"), color = color(na), textcolor = t.col, style = label.style_none, size = size.small))

// a pivot of the tier's own swing tracker becomes the level if it has none (d = 1 the ceiling, -1 the floor)
f_tAdopt(Tier t, int d, float p, int b) =>
    TLvl l = d == 1 ? t.c : t.f
    if not na(p) and b > t.anc and (close - p) * d < 0 and na(l.p)
        l.lvSet(p, b, d == 1)

// at a new anchor: the first stored pivot after it that the close has not passed
f_tSeed(Tier t, int d) =>
    TLvl l = d == 1 ? t.c : t.f
    array<int>   ab = d == 1 ? pvHiB : pvLoB
    array<float> ap = d == 1 ? pvHiP : pvLoP
    if na(l.p) and array.size(ab) > 0
        for s = 0 to array.size(ab) - 1
            if array.get(ab, s) > t.anc and (close - array.get(ap, s)) * d < 0
                l.lvSet(array.get(ap, s), array.get(ab, s), d == 1)
                break

// the IDM of the level taken
f_tIdm(Tier t, int d) =>
    TLvl l = d == 1 ? t.c : t.f
    if not na(l.p) and not l.idmHit and not na(l.idmP) and ((d == 1 ? low : high) - l.idmP) * d < 0
        l.idmHit := true

// a close beyond the level = the tier's CHOCH / BOS; else its sweep and re-level
f_tBrk(Tier t, int d) =>
    TLvl l = d == 1 ? t.c : t.f
    TLvl o = d == 1 ? t.f : t.c
    float x = d == 1 ? high : low
    float y = d == 1 ? low : high
    if not na(l.p) and not na(l.born) and bar_index > l.born
        if (close - l.p) * d > 0 and (t.tr != d or not altMode or l.idmHit or na(l.idmP))
            bool isCho = t.tr != d
            t.ev := true
            f_tMark(t, l.p, l.b, isCho)
            [rp, rb] = f_retExt(l.b, d == -1, true)
            if not na(rp)
                o.lvSet(rp, rb, d == -1)
            if t.st and not isCho and l.idmHit and not na(rb) and (last_bar_index - bar_index) <= 500 and f_xNear(rb)
                f_addLb(t.lb, t.cnt, label.new(rb, na, "+", yloc = d == 1 ? yloc.belowbar : yloc.abovebar, style = label.style_none, textcolor = color.gray, size = size.small))
            t.tr := d
            l.lvClr()
        else
            if (x - l.p) * d > 0
                if na(l.ref)
                    [rp, rb] = f_retExt(l.b, d == -1, false)
                    l.ref := rp
                if na(l.swp) or (x - l.swp) * d > 0
                    l.swp  := x
                    l.swpB := bar_index
                    l.swpT := false
                if altMode and not l.idmHit and not na(l.idmP) and (close - l.p) * d > 0 and not na(l.swp)
                    l.lvSet(l.swp, l.swpB, d == 1)
                    l.swpT := false
            if not na(l.swpB) and l.swpB == bar_index and t.tr == d and not na(l.ref) and (y - l.ref) * d < 0
                l.swpT := true
            if t.tr == d and not na(l.swp) and not na(l.ref) and (y - l.ref) * d < 0 and (not l.swpT or f_swpConf(d == 1 ? pvHiB : pvLoB, l.swpB))
                l.lvSet(l.swp, l.b, d == 1)

// one bar of a tier: rst = the tier above made a CHOCH / BOS (all levels and marks go), anc = the bar the tier starts after
f_tier(Tier t, bool rst, int anc, float hp, int hb, float lp, int lq) =>
    t.ev := false
    if rst
        t.tr  := 0
        t.anc := na
        t.c.lvClr()
        t.f.lvClr()
        f_cutAll(t.ln, t.lb, t.cnt)
    if na(t.anc) and not na(anc)
        t.anc := anc
        f_tSeed(t, 1)
        f_tSeed(t, -1)
    if not rst and not na(t.anc)
        f_tAdopt(t, 1, hp, hb)
        f_tAdopt(t, -1, lp, lq)
        f_tIdm(t, 1)
        f_tIdm(t, -1)
        f_tBrk(t, 1)
        f_tBrk(t, -1)

var Tier tI = Tier.new(0, na, TLvl.new(), TLvl.new(), false, true, color.blue, "i", array.new<line>(), array.new<label>(), array.new<int>())
var Tier tN = Tier.new(0, na, TLvl.new(), TLvl.new(), false, false, color.yellow, "n", array.new<line>(), array.new<label>(), array.new<int>())''')
    t.rep('[_ph, _phb] = aHiT.update(pbSwp2 ? iFlorP : na)', '[_ph, _phb] = aHiT.update(pbSwp2 ? tI.f.p : na)')
    t.rep('[_pl, _plb] = aLoT.update(pbSwp2 ? iCeilP : na)', '[_pl, _plb] = aLoT.update(pbSwp2 ? tI.c.p : na)')
    t.block('    int iAnchor = na', '        nRunLo := na(nRunLo) ? low  : math.min(nRunLo, low)', '''    int iAnchor = na
    if trendDir == 1
        if not na(ceilS)
            iAnchor := ceilS.x1
    else if trendDir == -1
        if not na(florS)
            iAnchor := florS.x1
    f_tier(tI, mainEvt, iAnchor, aPhP, aPhB, aPlP, aPlB)
    f_tier(tN, mainEvt or tI.ev, tI.tr == 1 ? tI.c.b : tI.tr == -1 ? tI.f.b : na, aPhP, aPhB, aPlP, aPlB)''')
    # the inner marks were drawn after the engine from a request; now drawn at once (same bar, nothing drawn in between)
    t.block('nnLc     = color.new(color.yellow, 0)', '        f_innPrune()', '')
    t.block('if not na(rqUpP)', '    f_innMark(rqDnP, rqDnB, rqDnCho)', '')
    t.block('ip1_lc   = color.new(color.blue, 0)', 'var label npFlorLb = na', '')
    t.block('var float mCHi  = na', 'bool eqLive  = "Range (BOS*/CHOCH* pair)"   == "Live leg (from the break)"', '')
    t.block('f_hLine(line ln, label lb, bool on, float p, int b, string txt, color lc, color tc, string ls, int w, string ts, bool showT, string tv, string th) =>',
            '    [_l, _b]', '''f_hLine(line ln, label lb, float p, int b, string txt, color c, string ls) =>
    line  _l = ln
    label _b = lb
    if na(p) or na(b)
        if not na(_l)
            line.delete(_l)
            _l := na
        if not na(_b)
            label.delete(_b)
            _b := na
    else
        int _x1 = b
        int _hMin = math.max(last_bar_index - 500, bar_index - 1500)
        if _x1 < _hMin
            _x1 := _hMin
        if _x1 < 0
            _x1 := 0
        if _x1 > bar_index
            _x1 := bar_index
        if na(_l)
            _l := line.new(_x1, p, bar_index, p, color = c, width = 1, style = ls, extend = extend.right)
        else
            line.set_xy1(_l, _x1, p)
            line.set_xy2(_l, bar_index, p)
            line.set_color(_l, c)
            line.set_width(_l, 1)
            line.set_style(_l, ls)
        int _lx = int(math.avg(_x1, bar_index))
        if na(_b)
            _b := label.new(_lx, p, txt, color = color(na), textcolor = c, style = label.style_none, size = size.small)
        else
            label.set_xy(_b, _lx, p)
            label.set_text(_b, txt)
            label.set_textcolor(_b, c)
            label.set_style(_b, label.style_none)
            label.set_size(_b, size.small)
    [_l, _b]

// the waiting level of a tier side, drawn on the last bar (BOS* = with the tier's trend, CHOCH* = against it)
f_tDraw(Tier t, int d) =>
    TLvl l = d == 1 ? t.c : t.f
    bool bos = t.tr == d
    [a, b] = f_hLine(l.pl, l.plb, l.p, l.b, t.tx + (bos ? "BOS*" : "CHOCH*"), color.new(t.col, bos ? 0 : 40), line.style_dotted)
    l.pl  := a
    l.plb := b''')
    t.block('f_ipStyle(bool isBos) =>', '        [np2_lc, np2_tc, "Dotted", 1, "nCHOCH*", "Small", true, "Middle", "Center"]', '')
    t.block('f_eqBar(int b1, int b2, string mode) =>', '    s', '')
    t.block('f_lastDraw() =>', '    [_icL, _icB, _ifL, _ifB, _ncL, _ncB, _nfL, _nfB, _eqML, _eqMB]', '''f_lastDraw() =>
    f_tDraw(tI, 1)
    f_tDraw(tI, -1)
    f_tDraw(tN, 1)
    f_tDraw(tN, -1)
    float _eqMp = na
    int   _eqMb = na
    if not na(ceilS) and not na(florS)
        _eqMp := f_eqLvl(ceilS.price, florS.price, 50.0)
        _eqMb := math.min(ceilS.x1, florS.x1)
    f_hLine(eqMLn, eqMLb, _eqMp, _eqMb, "EQ 50%", color.gray, line.style_dashed)''')
    t.block('    [_icL, _icB, _ifL, _ifB, _ncL, _ncB, _nfL, _nfB, _eqML, _eqMB] = f_lastDraw()', '    npFlorLb := _nfB', '''    [_eqML, _eqMB] = f_lastDraw()''')
    t.block('int _capMain = true ? 10 : 0 > 0 ? 0 : 500', '    f_innClear()', '''f_cutOld(mainLn, mainLb, mainCnt, 10)
f_cutOld(tI.ln, tI.lb, tI.cnt, 10)
f_cutOld(tN.ln, tN.lb, tN.cnt, 10)''')
    # ---- 5. the counter table: one global table (no table parameter in every row call); two text helpers used many times
    t.rep('var table stTbl = na\n', '')
    t.rep('f_stCell(table t, int r, string a, string b, color c) =>\n    table.cell(t, 0, r, a,', 'var table stTbl = na\nf_stCell(int r, string a, string b, color c) =>\n    table.cell(stTbl, 0, r, a,')
    t.rep('    table.cell(t, 1, r, b,', '    table.cell(stTbl, 1, r, b,')
    n = t.s.count('f_stCell(_t, ')
    assert n > 50, n
    t.s = t.s.replace('f_stCell(_t, ', 'f_stCell(')
    for k in (1, 2, 3, 4):
        t.rep('f_stTab%d(table _t) =>' % k, 'f_stTab%d() =>' % k)
        t.rep('    f_stTab%d(stTbl)\n' % k, '    f_stTab%d()\n' % k)
    t.rep('    table.cell(_t, 0, 0, "STRATEGY', '    table.cell(stTbl, 0, 0, "STRATEGY')
    t.rep('    table.cell(_t, 1, 0, "value",', '    table.cell(stTbl, 1, 0, "value",')
    assert 'table _t' not in t.s and '(_t, ' not in t.s.split('f_stTab1() =>')[1].split('if stStatOn and bar_index == last_bar_index')[0]
    t.s = _helpers(t.s)
    t.rep('\nf_xClamp(int b) =>', '\n// v15.0 (smaller file): two texts used many times\nf_mt(float v) => str.tostring(v, format.mintick)\nf_r2(float v) => str.tostring(math.round(v * 100) / 100)\nf_xClamp(int b) =>')
    # f_hLine: a line / label handle always gets the same width, style and size (each handle has one use), only its place,
    # text and colour change
    t.rep("""            line.set_color(_l, c)
            line.set_width(_l, 1)
            line.set_style(_l, ls)
""", """            line.set_color(_l, c)
""")
    t.rep("""            label.set_textcolor(_b, c)
            label.set_style(_b, label.style_none)
            label.set_size(_b, size.small)
""", """            label.set_textcolor(_b, c)
""")
    for w in ('intUse', 'intAltOn', 'intDefOn', 'iCeil', 'iFlor', 'nCeil', 'nFlor', 'iTrend', 'nTrend', 'rqUp', 'rqDn', 'rqStr', 'rqClear', '_intClrReq',
              'evIBos', 'evICho', 'evNBos', 'evNCho', 'iRunHi', 'nRunHi', 'f_intMark', 'f_innMark', 'f_intStrong', 'f_intPrune', 'f_innPrune',
              'f_intClear', 'f_innClear', 'intLn', 'innLn', 'lstyle', 'tsize(', 'lblStyle', 'styleOf', 'hAlignOf', 'f_ipStyle', 'f_npStyle',
              'f_eqBar', 'f_eqTxt', 'eqLive', 'eqClose', 'mCHi', 'evSwp', 'mnHiP', 'mnLoP', 'stCapFlag', '_eId', '_eDir', 'strTxt', 'strSz',
              'ip1_', 'np1_', 'eqM_lc', 'inLc', 'nnLc', '_lcE', 'f_idmMark', 'intKeep', 'iEvt', ' iTr '):
        assert w not in t.s, 'compact: %s left' % w
    return t.s
