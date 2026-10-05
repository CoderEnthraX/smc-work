# v12.0 in the Python simulators: RULE 3 - enter at the close of the signal candle (group 39), optionally only when the
#   close is at most r3Brk beyond the broken level; r3Fb = a close too far falls back to the normal rule 1 / 2 setup
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
    assert "r3On" not in s
    s = patch_swp2(s)
    # the engines need a swp2 attribute (False = as before)
    n_init = s.count("    def __init__(s):\n")
    assert n_init >= 2
    s = s.replace("class Engine:\n    def __init__(s):\n", "class Engine:\n    def __init__(s):\n        s.swp2 = False\n", 1) if "class Engine:\n    def __init__(s):\n" in s else s
    s = s.replace("class HTF:\n    def __init__(s):\n", "class HTF:\n    def __init__(s):\n        s.swp2 = False\n", 1) if "class HTF:\n    def __init__(s):\n" in s else s
    s = rep(s, '    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,\n',
            '    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,\n'
            '    # v12.0: rule 3 - enter at the close of the signal candle; r3BrkOn = only when the close is at most r3Brk beyond the broken level\n'
            '    r3On=False, r3BrkOn=False, r3Brk=3.0, r3Fb=False, pbSwp2=False,\n')
    s = rep(s, "    stSeq = 0; stPlaced = False; stEntLock = None; stArmBar = None\n",
            "    stSeq = 0; stPlaced = False; stEntLock = None; stArmBar = None\n"
            "    stMktBar = None   # v12.0\n")
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
                # v12.0: rule 3 - enter at the close of this candle (higher-timeframe filters still apply, no agreement needed);
                # optionally only when the close is at most r3Brk beyond the broken level (the pivot); a close too far is skipped,
                # or (r3Fb) keeps the normal rule 1 / 2 setup computed above
                r3Use = False
                if p["r3On"]:
                    r3B = None if piv is None else d * (c - piv)
                    r3Far = p["r3BrkOn"] and (r3B is None or r3B > lim_at(p, p["r3Brk"], c))
                    r3Fb = r3Far and p["r3Fb"] and (p["r1"] or p["r2"])
                    if not r3Fb:
                        r3Use = True
                        useM = (autoDir != 0 and d == autoDir) if autoMode else ((stT15 == -d) if agnMode else (agree or not (p["htfFilt"] or favMode)))
                        use = useM and not r3Far
                    if r3Fb: cnt["r3Fb"] = cnt.get("r3Fb", 0) + 1
                    elif r3Far: cnt["r3Far"] = cnt.get("r3Far", 0) + 1
""")
    s = rep(s, '                    stDir = d; stRule = 2 if (agree and p["r2"] and not agnMode) else 1\n',
            '                    stDir = d; stRule = 3 if r3Use else (2 if (agree and p["r2"] and not agnMode) else 1)\n'
            '                    stMktBar = None\n')
    s = rep(s, '            stEnt = stEntLock if (p["once"] and stPlaced and stEntLock is not None) else (stFix if stRule == 2 else retLvl(trendDir, mA, mO, p["pb"]))\n',
            '            stEnt = c if stRule == 3 else (stEntLock if (p["once"] and stPlaced and stEntLock is not None) else (stFix if stRule == 2 else retLvl(trendDir, mA, mO, p["pb"])))\n')
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
