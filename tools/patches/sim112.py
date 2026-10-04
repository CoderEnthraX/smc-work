# v11.2 in the Python simulators: stop buffer unit - price (as before) / pips / % of price
#   sim2/port111.py -> sim2/port112.py (the TradingView mirror) and ea/porthp.py (the EA checks), same edits
R = "/home/user/smc-work/tools/"


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    return s.replace(old, new)


def patch(s):
    assert "buMode" not in s
    s = rep(s, '    mvStep=False, mvBe=False,\n', '    mvStep=False, mvBe=False,\n'
            '    # v11.2: stop buffer unit - "Price" (as before) / "Pips" / "Pct"; pip = the pip of the market; tick = the smallest price step\n'
            '    buMode="Price", buPips=10.0, buPct=0.02, pip=0.1, tick=0.01,\n')
    # the buffer beyond a level, and the group 24 limits, in the chosen unit
    s = rep(s, "def run(bars, P=None, htf=None, log=False):\n", '''def buf_at(p, lv):
    """v11.2: the stop buffer beyond the level lv, in price (Pine f_stBuf; math.round_to_mintick = nearest step, ties up)"""
    if p["buMode"] == "Pips": return math.floor(p["buPips"] * p["pip"] / p["tick"] + 0.5) * p["tick"]
    if p["buMode"] == "Pct": return math.floor(lv * p["buPct"] / 100.0 / p["tick"] + 0.5) * p["tick"]
    return p["slbuf"]


def lim_at(p, v, ent):
    """v11.2: a group 24 limit (skip closer / further than) in price - pips, or % of the entry price"""
    if p["buMode"] == "Pips": return v * p["pip"]
    if p["buMode"] == "Pct": return ent * v / 100.0
    return v


def run(bars, P=None, htf=None, log=False):
''')
    s = rep(s, 'tb = p["slbuf"] if p["trailBuf"] is None else p["trailBuf"]', 'tb = buf_at(p, lvl) if p["trailBuf"] is None else p["trailBuf"]')
    s = rep(s, 'stSl = live - p["slbuf"] if stDir == 1 else live + p["slbuf"]', 'stSl = live - buf_at(p, live) if stDir == 1 else live + buf_at(p, live)')
    s = rep(s, 'stSl = opl - p["slbuf"] if d == 1 else opl + p["slbuf"]', 'stSl = opl - buf_at(p, opl) if d == 1 else opl + buf_at(p, opl)')
    s = rep(s, 'dOk = (p["minStop"] <= 0 or r >= p["minStop"]) and (p["maxStop"] <= 0 or r <= p["maxStop"])',
            'dOk = (p["minStop"] <= 0 or r >= lim_at(p, p["minStop"], stEnt)) and (p["maxStop"] <= 0 or r <= lim_at(p, p["maxStop"], stEnt))')
    return s


src = open(R + "sim2/port111.py").read()
open(R + "sim2/port112.py", "w").write(patch(src).replace("port111", "port112"))
src = open(R + "ea/porthp.py").read()
open(R + "ea/porthp.py", "w").write(patch(src))
print("port112.py written, porthp.py patched")
