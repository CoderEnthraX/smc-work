# v11.2 checks of the stop buffer unit over 2021-2026:
#  (1) the Python simulator (porthp.py, buf_at / lim_at) == the EA's core (harness) for pips and % settings
#  (2) 10 pips on gold == the old price buffer 1.0, 50 pips == 5.0 (core and Python)
#  (3) the WHOLE EA in the fake MT5 == the core for the new units (touch / pending / hedge / trailing)
import sys, subprocess
from multiprocessing import Pool
from cmp import compare, run_py, run_cpp, cfg_of
from fullcmp import full
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1.0,'rev':False,'eq0':1e6}
MODE = {'Price': 0, 'Pips': 1, 'Pct': 2}
def ex(P): return {'buMode': MODE[P.get('buMode', 'Price')], 'buPips': P.get('buPips', 10.0), 'buPct': P.get('buPct', 0.02), 'buPip': P.get('pip', 0.1)}
def py_case(t):
    name, P, cs = t
    if cs != 60: P = dict(P, barSec=cs)
    import io, contextlib
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = compare(name, P, cs=cs, extra=ex(P))
    return f.getvalue().strip(), ok
def eq_case(t):
    name, P1, P2 = t
    a = run_py(dict(P1), 60); b = run_py(dict(P2), 60)
    c = run_cpp(dict(P1), 60, ex(P1), tag='eq1_' + name); d = run_cpp(dict(P2), 60, ex(P2), tag='eq2_' + name)
    k = lambda rs: [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in rs]
    ok = k(a) == k(b) == k(c) == k(d)
    return '%-24s %d trades, Python and core, both settings: %s' % (name, len(a), 'IDENTICAL' if ok else 'DIFFER'), ok
B15 = dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', wkHr=23, lev=100.0, eq0=10000.0, htfTf=14400)
PY = [('pips10', dict(U, buMode='Pips', buPips=10.0), 60), ('pips50_min30_max300', dict(U, buMode='Pips', buPips=50.0, minStop=30.0, maxStop=300.0), 60),
      ('pct002', dict(U, buMode='Pct', buPct=0.02), 60), ('pct01', dict(U, buMode='Pct', buPct=0.1), 60), ('pct05', dict(U, buMode='Pct', buPct=0.5), 60),
      ('pct01_min005_max1', dict(U, buMode='Pct', buPct=0.1, minStop=0.05, maxStop=1.0), 60), ('pct01_trailLevel', dict(U, buMode='Pct', buPct=0.1, trail='Level'), 60),
      ('pips20_trailSwing_rev', dict(U, buMode='Pips', buPips=20.0, trail='Swing', rev=True), 60), ('pip001_pips80', dict(U, buMode='Pips', buPips=80.0, pip=0.01), 60),
      ('m15_pct005', dict(B15, buMode='Pct', buPct=0.05), 900)]
EQ = [('10pips=1.0', dict(U, buMode='Pips', buPips=10.0), dict(U, slbuf=1.0)), ('50pips=5.0', dict(U, buMode='Pips', buPips=50.0), dict(U, slbuf=5.0))]
Y = {'from': 20000, 'grid': 1, 'fixTies': 1}
EA = [('ea_pct01_touch', dict(U, lev=500.0), dict(Y, exec=0, buMode=2, buPct=0.1)), ('ea_pips50_pend', dict(U, lev=500.0), dict(Y, exec=1, buMode=1, buPips=50.0)),
      ('ea_pct01_minmax_trail', dict(U, lev=500.0, minStop=0.05, maxStop=1.0, trail='Level'), dict(Y, exec=1, buMode=2, buPct=0.1)),
      ('ea_pips20_hedge', dict(U, lev=500.0), dict(Y, exec=0, buMode=1, buPips=20.0, dirMode=3, hedgeMoney=0)),
      ('ea_pct002_pend', dict(U, lev=500.0), dict(Y, exec=1, buMode=2, buPct=0.02))]
def ea_case(t):
    import io, contextlib
    name, P, e = t
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = full(name, P, e)
    return f.getvalue().strip(), ok
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    res = []
    with Pool(4) as pool:
        if which in ('all', 'py'):
            for line, ok in pool.imap(py_case, PY, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(eq_case, EQ, chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d' % (sum(res), len(res)))
