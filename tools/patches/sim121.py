# v12.1 in the Python simulators (sim2/port120.py -> sim2/port121.py, the TradingView mirror; ea/porthp.py in place, the EA checks):
#   capAct "Base" = the hard cap's 4th choice 'Start again from the base risk (forget the losses)'
#   lmOn / lmAmt  = group 42: the losses carried reached the mark -> forgotten, the next trade risks the base again
#   pmOn / pmAmt  = group 42: won back pmAmt or more from the deepest point of the losing run (carPk) -> the rest is forgotten
#   ('no new trades before news' is the 'pre' flags porthp.py already has - group 41 of the EA)
R = "/home/user/smc-work/tools/"


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    return s.replace(old, new)


def patch(s):
    assert "lmOn" not in s
    s = rep(s, "    r3On=False, r3BrkOn=False, r3Brk=3.0, r3Fb=False, pbSwp2=False,\n",
            "    r3On=False, r3BrkOn=False, r3Brk=3.0, r3Fb=False, pbSwp2=False,\n"
            "    # v12.1: group 42 - start again from the base when the losses carried reach lmAmt; capAct 'Base' = the cap's 4th choice\n"
            "    lmOn=False, lmAmt=300.0, pmOn=False, pmAmt=200.0,\n")
    s = rep(s, "    seqLoss = 0.0; seqHalt = False; seqCapOn = False; seqLog = []; seqTot = 0.0; flPnl = 0.0; flPeak = 0.0\n",
            "    seqLoss = 0.0; seqHalt = False; seqCapOn = False; seqLog = []; seqTot = 0.0; flPnl = 0.0; flPeak = 0.0\n"
            "    carPk = 0.0   # v12.1: the most carried in the current losing run\n")
    s = rep(s, """            if seqHalt and p["capAct"] == "Day":
                seqHalt = False; seqLoss = 0.0; seqCapOn = False; seqTot = 0.0
""", """            if seqHalt and p["capAct"] == "Day":
                seqHalt = False; seqLoss = 0.0; seqCapOn = False; seqTot = 0.0; carPk = 0.0
""")
    s = rep(s, """            flPnl += ssum; flPeak = max(flPeak, flPnl)
            if car() <= 0.005 and p["capAct"] != "Perm":
""", """            flPnl += ssum; flPeak = max(flPeak, flPnl)
            # v12.1: group 42 - the losses carried reached the mark: forgotten, the next trade risks the base again
            if p["lmOn"] and p["seqMode"] != "Off" and car() >= p["lmAmt"] - 0.005:
                seqLoss = 0.0; seqTot = 0.0; cnt["lm"] = cnt.get("lm", 0) + 1
            # v12.1: group 42 - the profit mark: won back from the deepest point of this losing run -> the rest is forgotten
            if p["pmOn"] and p["seqMode"] != "Off" and car() > 0.005 and carPk - car() >= p["pmAmt"] - 0.005:
                seqLoss = 0.0; seqTot = 0.0; cnt["pm"] = cnt.get("pm", 0) + 1
            carPk = 0.0 if car() <= 0.005 else max(carPk, car())
            if car() <= 0.005 and p["capAct"] != "Perm":
""")
    s = rep(s, """            if not seqCapOn: seqCapOn = True
            riskNow = p["seqMax"]
            if p["capAct"] != "Clamp": seqHalt = True
""", """            if not seqCapOn: seqCapOn = True
            riskNow = p["seqMax"]
            if p["capAct"] == "Base":
                # v12.1: the losses carried are forgotten and the next trade risks the base again (never above the cap)
                if car() > 0.005:
                    seqLoss = 0.0; seqTot = 0.0; seqCapOn = False; carPk = 0.0; cnt["capBase"] = cnt.get("capBase", 0) + 1
                riskNow = min(p["risk"], p["seqMax"])
            elif p["capAct"] != "Clamp": seqHalt = True
""")
    return s


if __name__ == "__main__":
    a = open(R + "sim2/port120.py").read()
    open(R + "sim2/port121.py", "w").write(patch(a))
    b = open(R + "ea/porthp.py").read()
    open(R + "ea/porthp.py", "w").write(patch(b))
    print("port121.py and porthp.py written")
