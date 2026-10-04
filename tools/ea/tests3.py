# hedge (two sides, own money) = the union of a Longs-only and a Shorts-only run; news windows; shared money checked separately later
import sys, pickle
from multiprocessing import Pool
from cmp import *
sys.path.insert(0, SP)
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1000.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
def hedge(name, P):
    a = run_py(dict(P, direction='Longs'), 60) + run_py(dict(P, direction='Shorts'), 60)
    b = run_cpp(P, 60, {'dirMode': 3, 'hedgeMoney': 0}, tag=name)
    key = lambda r: (r[2], r[5], r[1], r[3], r[4], r[6])
    ka = sorted([key(r) for r in a]); kb = sorted([key(r) for r in b])
    print('%-28s py %5d trades %12.2f | core %5d trades %12.2f | %s' % (name, len(a), sum(r[8] for r in a), len(b), sum(r[8] for r in b), 'IDENTICAL' if ka == kb else 'DIFF'))
    return ka == kb
def news(name, P):
    import usnews
    bars_ = bars(60)
    NB = pickle.load(open('news1m.pkl', 'rb'))
    return compare(name, dict(P, news=NB))
def job(t):
    kind, name, P = t
    return hedge(name, P) if kind == 'h' else news(name, P)
if __name__ == '__main__':
    import os
    if not os.path.exists('news1m.pkl'):
        import usnews
        pickle.dump(usnews.blocked(bars(60)), open('news1m.pkl', 'wb'))
        print('news flags ready')
    T = [('h', 'H_user', U), ('h', 'H_rev', dict(U, rev=True)), ('h', 'H_ruleC', REC), ('h', 'H_auto', dict(U, auto=True)),
         ('n', 'N_user', U), ('n', 'N_ruleC', REC), ('n', 'N_rev_both', dict(U, rev=True, sig='Both'))]
    with Pool(3) as pool: res = pool.map(job, T, chunksize=1)
    print('ALL IDENTICAL' if all(res) else 'SOME DIFFER: %d of %d identical' % (sum(res), len(res)))
