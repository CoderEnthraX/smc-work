import pickle, sys, datetime as dt
from port import *
bars = pickle.load(open("m1.pkl", "rb"))
H = htf_series(bars, 900)
def ist(t): return dt.datetime.utcfromtimestamp(t + IST)
T0 = bars[0][0] + 2 * 86400            # 2 warm-up days
TM = int(dt.datetime(2026, 4, 11).timestamp())  # split point
BASE = {'slbuf': 1.0, 'wkHr': 23, 'pb': 25.0}
def ev(P, name):
    Q = dict(BASE); Q.update(P)
    cl, op, cnt = run(bars, Q, H)
    cl = [tr for tr in cl if bars[tr.ebar][0] >= T0]
    a = [tr for tr in cl if bars[tr.ebar][0] < TM]; b = [tr for tr in cl if bars[tr.ebar][0] >= TM]
    s = stats(cl); sa = stats(a); sb = stats(b)
    print("%-44s n %4d  net %7.0f  win %4.1f%%  PF %4.2f  maxDD %6.0f  costs %6.0f | 1st half %6.0f  2nd half %6.0f" % (
        name, s["n"], s["net"], s["win"], s["pf"], s["dd"], s["comm"], sa["net"], sb["net"]), flush=True)
    return s, sa, sb
if __name__ == "__main__":
    for name, P in eval(open(sys.argv[1]).read()):
        ev(P, name)
