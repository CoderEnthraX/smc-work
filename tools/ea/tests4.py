from multiprocessing import Pool
from cmp import *
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
B15 = dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', seqMode='C', split=1.0,
           seqMax=300.0, capAct='Clamp', ldOn=True, ldN=4, ldD=3, wkHr=23, lev=100.0, eq0=10000.0, barSec=900, htfTf=14400)
T = [('R_user', U), ('R_mvStep', dict(U, mvStep=True)), ('R_mvBe', dict(U, mvBe=True)), ('R_part', dict(U, partOn=True)), ('R_trLevel', dict(U, trail='Level')),
     ('R_ruleC', REC), ('R_rev_both', dict(U, rev=True, sig='Both')), ('R_15m_best', B15)]
def job(t):
    name, P = t; cs = P.pop('barSec', 60)
    if cs != 60: P['barSec'] = cs
    return compare(name, P, cs=cs)
if __name__ == '__main__':
    with Pool(3) as pool: res = pool.map(job, T, chunksize=1)
    print('ALL IDENTICAL' if all(res) else 'SOME DIFFER: %d of %d' % (sum(res), len(res)))
