import pickle
D = pickle.load(open("seqs.pkl", "rb"))
def run(seq, lim=None, ls=None):
    tot = 0.0; day = None; dp = 0.0; run_ = 0; n = 0
    for d, R, w in seq:
        if d[:10] != day: day = d[:10]; dp = 0.0; run_ = 0
        if lim is not None and dp <= -lim: continue
        if ls is not None and run_ >= ls: continue
        tot += R; dp += R; n += 1; run_ = run_ + 1 if R <= 0 else 0
    return tot * 50, n
print("%-32s %9s %9s %9s %9s %9s %9s" % ("sequence (net $ at 50 risk)", "none", "day -1R", "day -2R", "day -3R", "2 losses", "3 losses"))
for k, s in D.items():
    row = [run(s)[0], run(s, 1)[0], run(s, 2)[0], run(s, 3)[0], run(s, ls=2)[0], run(s, ls=3)[0]]
    print("%-32s " % k + " ".join("%+9.0f" % x for x in row))
