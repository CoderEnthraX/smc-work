# builds the price files the EA tests use, from tools/data/gold_m1_utc.npz:
# fx.pkl / fx15.pkl (simulator bars, 1m and 15m) and m1.bin / m15.bin (C++ tests: int64 time + 4 doubles)
import numpy as np, pickle, struct, os
here = os.path.dirname(os.path.abspath(__file__))
z = np.load(os.path.join(here, '..', 'data', 'gold_m1_utc.npz'))
t, o, h, l, c = z['t'], z['o'], z['h'], z['l'], z['c']
m1 = [(int(t[i]), o[i] / 100, h[i] / 100, l[i] / 100, c[i] / 100) for i in range(len(t))]
m15 = []
for b in m1:
    k = b[0] // 900 * 900
    if m15 and m15[-1][0] == k:
        a = m15[-1]; m15[-1] = (k, a[1], max(a[2], b[2]), min(a[3], b[3]), b[4])
    else: m15.append((k, b[1], b[2], b[3], b[4]))
for bars, pk, bn in ((m1, 'fx.pkl', 'm1.bin'), (m15, 'fx15.pkl', 'm15.bin')):
    pickle.dump(bars, open(os.path.join(here, pk), 'wb'))
    with open(os.path.join(here, bn), 'wb') as f:
        for x in bars: f.write(struct.pack('<q4d', *x))
    print(pk, bn, len(bars))
