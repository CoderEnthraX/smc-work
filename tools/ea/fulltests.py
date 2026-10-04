from fullcmp import *
import pickle
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
REC = dict(U, seqMode='C', split=3.0, ldOn=True, ldN=4, ldD=3, capAct='Day', seqMax=100000.0)
Y = {'from': 20000, 'to': 390000, 'grid': 1, 'fixTies': 1}
res = []
res.append(full('touch', U, dict(Y, exec=0)))
res.append(full('pend_rev_both', dict(U, rev=True, sig='Both'), dict(Y, exec=1)))
res.append(full('pend_stack', dict(U, sig='Both', bosRiskPct=50.0, maxOpen=2), dict(Y, exec=1)))
res.append(full('pend_mvStep', dict(U, mvStep=True), dict(Y, exec=1)))
res.append(full('pend_mvBe', dict(U, mvBe=True), dict(Y, exec=1)))
res.append(full('pend_trail', dict(U, trail='Level'), dict(Y, exec=1)))
res.append(full('pend_part', dict(U, partOn=True), dict(Y, exec=1)))
res.append(full('pend_auto', dict(U, auto=True), dict(Y, exec=1)))
res.append(full('pend_hedge_own', U, dict(Y, exec=1, dirMode=3, hedgeMoney=0)))
res.append(full('pend_ruleC', REC, dict(Y, exec=1)))
res.append(full('pend_news', dict(U, news=[]), dict(Y, exec=1)))
print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d' % (sum(res), len(res)))
