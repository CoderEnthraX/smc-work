# v12.0 in the Python simulators: RULE 3 / RULE 4 - enter at the close of the signal candle (group 39)
#   + PULLBACK RULE 3 (pbSwp2, in the Pine since v10.0 and in the EA core) so the simulators can run the user's settings
#   sim2/port112.py -> sim2/port120.py (the TradingView mirror) and ea/porthp.py (the EA checks), same edits
R = "/home/user/smc-work/tools/"


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    return s.replace(old, new)


def patch_swp2(s):
    if "swpLvl" in s:
        return s
    s = rep(s, "    def update(s, o, h, l, c, bi):\n", "    def update(s, o, h, l, c, bi, swpLvl=None):\n")
    s = rep(s, """        elif pb:
            beyond = s.refLevel is not None and (c < s.refLevel if s.isHigh else c > s.refLevel)
            if s.count == 0:
                s.count = 1; s.refLevel = rf
            elif s.count == 1 and beyond:
                s.count = 2; s.refLevel = rf
            elif s.count == 2 and beyond:
                confP = s.potential; confB = s.potentialBar
                s.potential = h if s.isHigh else l; s.potentialBar = bi
                s.count = 1; s.refLevel = rf; s.swept = False
""", """        else:
            # PULLBACK RULE 3 (pbSwp2): the pullback took out the opposite live level (a wick is enough)
            if swpLvl is not None and (l < swpLvl if s.isHigh else h > swpLvl):
                s.swept = True
            if pb:
                beyond = s.refLevel is not None and (c < s.refLevel if s.isHigh else c > s.refLevel)
                if s.count == 0:
                    s.count = 1; s.refLevel = rf
                elif s.count == 1 and beyond and s.swept:
                    confP = s.potential; confB = s.potentialBar
                    s.potential = h if s.isHigh else l; s.potentialBar = bi
                    s.count = 1; s.refLevel = rf; s.swept = False
                elif s.count == 1 and beyond:
                    s.count = 2; s.refLevel = rf
                elif s.count == 2 and beyond:
                    confP = s.potential; confB = s.potentialBar
                    s.potential = h if s.isHigh else l; s.potentialBar = bi
                    s.count = 1; s.refLevel = rf; s.swept = False
""")
    s = rep(s, """        phP, phB = s.hiT.update(o, h, l, c, bi)
        plP, plB = s.loT.update(o, h, l, c, bi)
""", """        swH = s.florS.price if (s.swp2 and s.florS is not None) else None
        swL = s.ceilS.price if (s.swp2 and s.ceilS is not None) else None
        phP, phB = s.hiT.update(o, h, l, c, bi, swH)
        plP, plB = s.loT.update(o, h, l, c, bi, swL)
""")
    s = rep(s, """        cfH, _ = s.tkHi.update(o, h, l, c, bi)
        cfL, _ = s.tkLo.update(o, h, l, c, bi)
""", """        cfH, _ = s.tkHi.update(o, h, l, c, bi, s.tFlor if s.swp2 else None)
        cfL, _ = s.tkLo.update(o, h, l, c, bi, s.tCeil if s.swp2 else None)
""")
    s = rep(s, "def htf_series(bars, tf):\n", "def htf_series(bars, tf, swp2=False):\n")
    s = rep(s, "    e = HTF(); tr = []\n", "    e = HTF(); e.swp2 = swp2; tr = []\n")
    s = rep(s, '        htf = htf_series(bars, p["htfTf"])\n', '        htf = htf_series(bars, p["htfTf"], p.get("pbSwp2", False))\n')
    return s


def patch(s):
    assert "ccMode" not in s
    s = patch_swp2(s)
    # the engines need a swp2 attribute (False = as before)
    n_init = s.count("    def __init__(s):\n")
    assert n_init >= 2
    s = s.replace("class Engine:\n    def __init__(s):\n", "class Engine:\n    def __init__(s):\n        s.swp2 = False\n", 1) if "class Engine:\n    def __init__(s):\n" in s else s
    s = s.replace("class HTF:\n    def __init__(s):\n", "class HTF:\n    def __init__(s):\n        s.swp2 = False\n", 1) if "class HTF:\n    def __init__(s):\n" in s else s
    s = rep(s, '    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,\n',
            '    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,\n'
            '    # v12.0: entry at the close of the signal candle - ccMode "Off" / "R3" / "R4"; R4 limits (0 = off, unit of group 38); ccFb = fall back to rule 1 / 2\n'
            '    ccMode="Off", ccMax=30.0, ccMin=3.0, ccFb=False, pbSwp2=False,\n')
    s = rep(s, "def run(bars, P=None, htf=None, log=False):\n", '''def cc_ok(p, r, ent):
    """v12.0: the rule 4 limits (Pine f_stCcOk)"""
    return (p["ccMin"] <= 0 or r >= lim_at(p, p["ccMin"], ent)) and (p["ccMax"] <= 0 or r <= lim_at(p, p["ccMax"], ent))


def run(bars, P=None, htf=None, log=False):
''')
    s = rep(s, "    stSeq = 0; stPlaced = False; stEntLock = None; stArmBar = None\n",
            "    stSeq = 0; stPlaced = False; stEntLock = None; stArmBar = None\n"
            "    stCcLim = False; stMktBar = None   # v12.0\n")
    # the engine gets the swp2 switch
    s = rep(s, '    E = Engine()\n', '    E = Engine()\n    E.swp2 = p.get("pbSwp2", False)\n')
    # a rule 3 / 4 entry has one chance; the live-stop update is for rule 1 only
    s = rep(s, '        if stDir != 0 and stRule != 2 and not (p["once"] and stPlaced) and frozen is None:\n',
            '        if stDir != 0 and stRule == 3 and ((stMktBar is not None and bi > stMktBar) or (stArmBar is not None and bi > stArmBar + 1)):\n'
            '            cancel(); cnt["canc"] += 1; stDir = 0\n'
            '        if stDir != 0 and stRule != 2 and stRule != 3 and not (p["once"] and stPlaced) and frozen is None:\n')
    # arming
    s = rep(s, """                if autoMode:
                    use = autoDir != 0 and d == autoDir and ((((p["r2"] and piv is not None) or (not p["r2"] and p["r1"]))) if eqOpen else p["r1"])
""", """                if autoMode:
                    use = autoDir != 0 and d == autoDir and ((((p["r2"] and piv is not None) or (not p["r2"] and p["r1"]))) if eqOpen else p["r1"])
                # v12.0: rules 3 / 4 - enter at the close of this candle (higher-timeframe filters still apply, no agreement needed)
                ccOn = p["ccMode"] != "Off"; ccR4 = p["ccMode"] == "R4"
                ccSl = None if opl is None else (opl - buf_at(p, opl) if d == 1 else opl + buf_at(p, opl))
                ccR = None if ccSl is None else d * (c - ccSl)
                ccFar = ccR4 and ccR is not None and p["ccMax"] > 0 and ccR > lim_at(p, p["ccMax"], c)
                ccNear = ccR4 and ccR is not None and p["ccMin"] > 0 and ccR < lim_at(p, p["ccMin"], c)
                ccMkt = ccOn and not ccFar and not ccNear
                ccBack = ccOn and ccFar and not ccNear and p["ccFb"]
                if ccOn:
                    useM = (autoDir != 0 and d == autoDir) if autoMode else ((stT15 == -d) if agnMode else (agree or not (p["htfFilt"] or favMode)))
                    if ccMkt: use = useM
                    elif not ccBack: use = False
                    if ccNear: cnt["ccNear"] = cnt.get("ccNear", 0) + 1
                    elif ccFar and not ccBack: cnt["ccFar"] = cnt.get("ccFar", 0) + 1
                    elif ccBack and use and opl is not None: cnt["ccFb"] = cnt.get("ccFb", 0) + 1
""")
    s = rep(s, '                    stDir = d; stRule = 2 if (agree and p["r2"] and not agnMode) else 1\n',
            '                    stDir = d; stRule = 3 if (ccOn and ccMkt) else (2 if (agree and p["r2"] and not agnMode) else 1)\n'
            '                    stCcLim = ccBack; stMktBar = None\n')
    s = rep(s, '            stEnt = stEntLock if (p["once"] and stPlaced and stEntLock is not None) else (stFix if stRule == 2 else retLvl(trendDir, mA, mO, p["pb"]))\n',
            '            stEnt = c if stRule == 3 else (stEntLock if (p["once"] and stPlaced and stEntLock is not None) else (stFix if stRule == 2 else retLvl(trendDir, mA, mO, p["pb"])))\n')
    s = rep(s, '            dOk = (p["minStop"] <= 0 or r >= lim_at(p, p["minStop"], stEnt)) and (p["maxStop"] <= 0 or r <= lim_at(p, p["maxStop"], stEnt))\n',
            '            dOk = (p["minStop"] <= 0 or r >= lim_at(p, p["minStop"], stEnt)) and (p["maxStop"] <= 0 or r <= lim_at(p, p["maxStop"], stEnt))\n'
            '            if ((stRule == 3 and p["ccMode"] == "R4") or stCcLim) and not cc_ok(p, r, stEnt): dOk = False   # v12.0\n')
    # market orders: a limit that every price touches = filled at the next open
    s = rep(s, '                    base = stPend[0]\n                    grp = base\n',
            '                    base = stPend[0]\n                    grp = base\n'
            '                    oLim = math.inf * stDir if stRule == 3 else stEnt   # v12.0: market order at the next open\n')
    s = rep(s, 'pend[base] = dict(dir=stDir, lim=stEnt, q=q - q1, sl=stSl, tgt=stTgt, grp=grp, piece="m")', 'pend[base] = dict(dir=stDir, lim=oLim, q=q - q1, sl=stSl, tgt=stTgt, grp=grp, piece="m")')
    s = rep(s, 'pend[base + "p"] = dict(dir=stDir, lim=stEnt, q=q1, sl=stSl, tgt=tp1, grp=grp, piece="p")', 'pend[base + "p"] = dict(dir=stDir, lim=oLim, q=q1, sl=stSl, tgt=tp1, grp=grp, piece="p")')
    s = rep(s, 'pend[base] = dict(dir=stDir, lim=stEnt, q=q, sl=stSl, tgt=stTgt, grp=grp, piece="")', 'pend[base] = dict(dir=stDir, lim=oLim, q=q, sl=stSl, tgt=stTgt, grp=grp, piece="")')
    s = rep(s, '                    stOrdLive = True; stLast = key\n',
            '                    stOrdLive = True; stLast = key\n'
            '                    if stRule == 3 and stMktBar is None: stMktBar = bi\n')
    return s


if __name__ == "__main__":
    a = open(R + "sim2/port112.py").read()
    open(R + "sim2/port120.py", "w").write(patch(a))
    b = open(R + "ea/porthp.py").read()
    open(R + "ea/porthp.py", "w").write(patch(b))
    print("port120.py and porthp.py written")
