import sys
from multiprocessing import Pool
from cmp import *
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':1.0,'rev':False,'eq0':1e6}
def u(**k): d = dict(U); d.update(k); return d
REC = u(seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
B15 = dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', seqMode='C', split=1.0,
           seqMax=300.0, capAct='Clamp', ldOn=True, ldN=4, ldD=3, wkHr=23, lev=100.0, eq0=10000.0, barSec=900, htfTf=14400)
T = [
 ('B_user', u()),
 ('B_rev', u(rev=True)),
 ('B_BOS', u(sig='BOS')), ('B_Both', u(sig='Both')), ('B_fav', u(fav=True)), ('B_agn', u(agn=True)), ('B_auto', u(auto=True)),
 ('B_auto_both_rev', u(auto=True, sig='Both', rev=True)), ('B_eqOn', u(eqOn=True)),
 ('B_ruleC', REC), ('B_ruleCp', dict(REC, seqMode='C+')), ('B_ruleA', dict(REC, seqMode='A10')), ('B_ruleAp', dict(REC, seqMode='A+')),
 ('B_ruleB', dict(REC, seqMode='B')), ('B_ruleBp', dict(REC, seqMode='B+')),
 ('B_C_perm300', u(seqMode='C', seqMax=300.0, capAct='Perm')), ('B_C_clamp300', u(seqMode='C', seqMax=300.0)), ('B_C_day300', u(seqMode='C', seqMax=300.0, capAct='Day')),
 ('B_floor_size', u(flMode='Size')), ('B_floor_capC', u(flMode='Cap', seqMode='C')),
 ('B_mvStep', u(mvStep=True)), ('B_mvBe', u(mvBe=True)), ('B_trSwing', u(trail='Swing')), ('B_trLevel', u(trail='Level')),
 ('B_liq', u(liqTgt=True)), ('B_part', u(partOn=True)), ('B_part_rr1', u(partOn=True, rr=1.0, partR=0.5)), ('B_pd', u(pdOn=True)), ('B_lossN', u(lossN=3)),
 ('B_stack', u(sig='Both', bosRiskPct=50.0, maxOpen=2)), ('B_stack_nolimit', u(sig='BOS', bosRiskPct=50.0)), ('B_htfFilt', u(htfFilt=True)),
 ('B_maxTr_dayLoss', u(maxTrades=2, dayLoss=100.0)), ('B_exp_min_max', u(expBars=30, minStop=3.0, maxStop=20.0)), ('B_once', u(once=True)),
 ('B_longs', u(direction='Longs')), ('B_shorts', u(direction='Shorts')), ('B_sessOff', u(sessOff=True)), ('B_follow', u(bosMode='Follow')),
 ('B_r1', u(r2=False)), ('B_r2', u(r1=False)), ('B_htf1h', u(htfTf=3600)), ('B_htf4h_auto', u(htfTf=14400, auto=True)),
 ('B_ldOn_only', u(ldOn=True, ldN=3, ldD=2)), ('B_hours', u(hrOn=13, hrOff=21, hrFlat=13)), ('B_wkThu', u(wkDow=3, wkHr=20)),
 ('M15_user', dict(u(), barSec=900, htfTf=14400)), ('M15_best', B15), ('M15_best_sessOff', dict(B15, sessOff=True)),
 ('M15_rev_both', dict(u(), barSec=900, htfTf=14400, rev=True, sig='Both')), ('M15_hours', dict(u(), barSec=900, htfTf=14400, hrOn=13, hrOff=21, hrFlat=1)),
]
def job(t):
    name, P = t
    cs = P.pop('barSec', 60)
    if cs != 60: P['barSec'] = cs
    try: return compare(name, P, cs=cs)
    except Exception as e:
        import traceback; traceback.print_exc(); print(name, 'ERROR', e); return False
if __name__ == '__main__':
    with Pool(3) as pool: res = pool.map(job, T, chunksize=1)
    print('ALL IDENTICAL' if all(res) else 'SOME DIFFER: %d of %d identical' % (sum(res), len(res)))
