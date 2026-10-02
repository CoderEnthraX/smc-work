import pickle, math, statistics as st
D = pickle.load(open("seqs.pkl", "rb"))
for k, v in D.items():
    R = [x[1] for x in v]; n = len(R)
    w = [r for r in R if r > 0]; l = [r for r in R if r <= 0]
    m = st.mean(R); sd = st.pstdev(R); se = sd / math.sqrt(n)
    # longest losing streak, max drawdown in R
    run = best = 0; cum = pk = dd = 0.0
    for r in R:
        run = run + 1 if r <= 0 else 0; best = max(best, run)
        cum += r; pk = max(pk, cum); dd = max(dd, pk - cum)
    # lag-1 autocorrelation of win/loss and runs test
    b = [1 if r > 0 else 0 for r in R]; p = sum(b) / n
    ac = sum((b[i] - p) * (b[i + 1] - p) for i in range(n - 1)) / max(1e-9, sum((x - p) ** 2 for x in b))
    runs = 1 + sum(1 for i in range(1, n) if b[i] != b[i - 1]); n1 = sum(b); n0 = n - n1
    mu = 2 * n1 * n0 / n + 1; var = (mu - 1) * (mu - 2) / (n - 1); z = (runs - mu) / math.sqrt(var) if var > 0 else 0
    need = (1.96 * sd / m) ** 2 if m != 0 else float('inf')
    bysig = {}
    for x in v:
        s = 'SL/TP' if 'exit' in x[2] or x[2] in ('SL', 'TP') else x[2]
        bysig.setdefault(s, []).append(x[1])
    print("%-32s n=%4d win=%4.1f%% avgW=%+.2f avgL=%+.2f E=%+.3fR CI95=[%+.3f,%+.3f] streak=%d maxDD=%.1fR ac1=%+.3f runsZ=%+.2f need~%d" % (
        k, n, 100 * len(w) / n, st.mean(w), st.mean(l), m, m - 1.96 * se, m + 1.96 * se, best, dd, ac, z, min(need, 99999)))
    print("     by exit: " + ", ".join("%s %d E=%+.2f sum=%+.1f" % (s, len(a), st.mean(a), sum(a)) for s, a in sorted(bysig.items(), key=lambda t: -len(t[1]))))
