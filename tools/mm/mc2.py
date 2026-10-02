import pickle, random, statistics as st
from mc import D, WORLDS, EQ0
def floor_run(seq, budget, lock, frac, pause2=True):
    eq = pk = EQ0; day = None; lrun = 0; minfloor = None
    for (d, R, w) in seq:
        if d[:10] != day: day = d[:10]; lrun = 0
        if pause2 and lrun >= 2: continue
        floor = EQ0 - budget + lock * max(0.0, pk - EQ0)
        r = frac * (eq - floor)
        if r < 2: continue
        eq += R * r; lrun = lrun + 1 if R <= 0 else 0; pk = max(pk, eq)
    return eq - EQ0, EQ0 - budget + lock * max(0.0, pk - EQ0) - EQ0
random.seed(11); NP = 1500
for wn, dl in WORLDS.items():
    paths = [[x for _ in range(250) for x in random.choice(dl)] for _ in range(NP)]
    print("\n==", wn)
    for budget, lock, frac in ((250, 0.5, 0.10), (500, 0.5, 0.10), (1000, 0.5, 0.10), (500, 0.75, 0.10), (500, 0.5, 0.05)):
        res = [floor_run(p, budget, lock, frac) for p in paths]; net = sorted(r[0] for r in res); fl = sorted(r[1] for r in res)
        print("   budget %4d lock %3d%% risk %2d%% of cushion: profit %3.0f%%  median %+6.0f  worst5%% %+6.0f  worst %+6.0f  locked floor median %+6.0f" % (
            budget, lock * 100, frac * 100, 100 * sum(1 for x in net if x > 0) / NP, net[NP // 2], net[int(NP * .05)], net[0], fl[NP // 2]))
