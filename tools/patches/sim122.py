# v12.2 in the Python simulators: the v12.1 profit mark removed (start from the simulators of commit ec60510) and
#   seqMode "As" / "Bs" / "Cs" = Rule A / B / C split: the base risk from the profit steps of group 43 (sp1 / spN1, sp2 / spN2,
#   sp3 / spN3, then every spInc one more spAdd parts) - the step reached / its parts, never below the base risk, never above
#   the hard cap; the profit = flPnl (the counted closed trades, never reset)
#   sim2/port121.py (ec60510) -> sim2/port122.py (the TradingView mirror); ea/porthp.py (ec60510) -> ea/porthp.py (the EA checks)
import subprocess
R = "/home/user/smc-work/tools/"


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    return s.replace(old, new)


STEP = '''

def step_base(p, pf):
    """v12.2: Rule A / B / C split - the base risk from the profit steps: the step reached / its parts (0 = no step)"""
    a = 0.0; n = 1.0
    if p["sp1"] > 0 and pf >= p["sp1"] - 0.005 and p["sp1"] > a: a = p["sp1"]; n = p["spN1"]
    if p["sp2"] > 0 and pf >= p["sp2"] - 0.005 and p["sp2"] > a: a = p["sp2"]; n = p["spN2"]
    if p["sp3"] > 0 and pf >= p["sp3"] - 0.005 and p["sp3"] > a:
        a = p["sp3"]; n = p["spN3"]
        if p["spInc"] > 0:
            k = math.floor((pf - p["sp3"] + 0.005) / p["spInc"])
            a = p["sp3"] + k * p["spInc"]; n = p["spN3"] + k * p["spAdd"]
    return a / n if a > 0 else 0.0
'''


def patch(s):
    assert "pmOn" not in s and "step_base" not in s
    s = rep(s, "    lmOn=False, lmAmt=300.0,\n",
            "    lmOn=False, lmAmt=300.0,\n"
            "    # v12.2: group 43 - the profit steps of Rule A / B / C split (seqMode As / Bs / Cs)\n"
            "    sp1=200.0, spN1=3.0, sp2=500.0, spN2=5.0, sp3=1000.0, spN3=8.0, spInc=500.0, spAdd=1.0,\n")
    s = rep(s, "\n\ndef run(bars, P=None, htf=None, log=False):\n", STEP + "\n\ndef run(bars, P=None, htf=None, log=False):\n")
    s = rep(s, """        if p["seqMode"] != "Off" and p["flMode"] != "Size" and riskNow > p["seqMax"]:
""", """        # v12.2: Rule A / B / C split - the base grows in steps with the total profit (never below the base risk, never above the cap)
        basNow = p["risk"]
        if p["seqMode"] in ("As", "Bs", "Cs"):
            basNow = max(p["risk"], min(step_base(p, flPnl), p["seqMax"]))
            if p["seqMode"] == "As":
                riskNow = max(basNow, (car() + p["seqAdd"]) / p["split"]) if car() > 0.005 else basNow
            elif p["seqMode"] == "Bs":
                riskNow = max(basNow, 2.0 * car() / p["split"]) if car() > 0.005 else basNow
            else:
                riskNow = max(basNow, car() / p["split"]) if car() > 0.005 else basNow
        if p["seqMode"] != "Off" and p["flMode"] != "Size" and riskNow > p["seqMax"]:
""")
    s = rep(s, '                riskNow = min(p["risk"], p["seqMax"])\n', '                riskNow = min(basNow, p["seqMax"])\n')
    return s


def at(rev, path):
    return subprocess.run(["git", "-C", R, "show", "%s:tools/%s" % (rev, path)], capture_output=True, text=True, check=True).stdout


if __name__ == "__main__":
    open(R + "sim2/port122.py", "w").write(patch(at("ec60510", "sim2/port121.py")))
    open(R + "ea/porthp.py", "w").write(patch(at("ec60510", "ea/porthp.py")))
    print("port122.py and porthp.py written")
