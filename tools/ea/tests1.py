import sys
from multiprocessing import Pool
from cmp import *
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':100.0,'rev':False}
def u(**k): d = dict(U); d.update(k); return d
REC = u(seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
T = [
 ('default_DEF', {}),
 ('user_rev', u(rev=True)),
 ('user_BOS', u(sig='BOS')),
 ('user_Both', u(sig='Both')),
 ('fav', u(fav=True)),
 ('agn', u(agn=True)),
 ('auto', u(auto=True)),
 ('auto_both_rev', u(auto=True, sig='Both', rev=True)),
 ('eqOn', u(eqOn=True, eqPct=50.0)),
 ('ruleC_split3_pause_day', REC),
 ('ruleCplus', dict(REC, seqMode='C+')),
 ('ruleA', dict(REC, seqMode='A10')),
 ('ruleAplus', dict(REC, seqMode='A+')),
 ('ruleB', dict(REC, seqMode='B')),
 ('ruleBplus', dict(REC, seqMode='B+')),
 ('ruleC_perm300', u(seqMode='C', seqMax=300.0, capAct='Perm')),
 ('ruleC_clamp300', u(seqMode='C', seqMax=300.0, capAct='Clamp')),
 ('floor_size', u(flMode='Size')),
 ('floor_cap_ruleC', u(flMode='Cap', seqMode='C', flAmt=2000.0, flPct=2.5)),
 ('mvStep', u(mvStep=True)),
 ('mvBe', u(mvBe=True)),
 ('trail_swing', u(trail='Swing')),
 ('trail_level', u(trail='Level')),
 ('liq', u(liqTgt=True, liqMinR=1.5)),
 ('part', u(partOn=True)),
 ('pd', u(pdOn=True)),
 ('lossN3', u(lossN=3)),
 ('stackBOS', u(sig='Both', bosRiskPct=50.0, maxOpen=2)),
 ('htfFilt', u(htfFilt=True)),
 ('maxTr_dayLoss', u(maxTrades=2, dayLoss=100.0)),
 ('exp_min_max', u(expBars=30, minStop=3.0, maxStop=20.0)),
 ('once', u(once=True)),
 ('longs', u(direction='Longs')),
 ('shorts', u(direction='Shorts')),
 ('sessOff', u(sessOff=True)),
 ('liveT', dict(REC, liveT=1700000000)),
 ('follow', u(bosMode='Follow')),
 ('r1only', u(r2=False)),
 ('r2only', u(r1=False)),
]
def job(t):
    name, P = t
    try: return compare(name, P)
    except Exception as e: print(name, 'ERROR', e); return False
if __name__ == '__main__':
    with Pool(3) as pool: res = pool.map(job, T, chunksize=1)
    print('ALL IDENTICAL' if all(res) else 'SOME DIFFER: %d of %d identical' % (sum(res), len(res)))
