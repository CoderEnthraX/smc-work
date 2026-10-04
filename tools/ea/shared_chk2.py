# Independent check of the hedge money modes (event replay written separately from the EA code):
# loss memory (Rule C / C+, split), hard cap + 'stop for the rest of the day', pause after N losses in a row.
import csv, subprocess, pickle
from cmp import cfg_of, SP
bars = pickle.load(open(SP + '/fx.pkl', 'rb')); T = [b[0] for b in bars]; IST = 19800
def run(P, extra, tag):
    c = cfg_of(P, 60); c.update(extra)
    with open('cfg_%s.txt' % tag, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    subprocess.run(['./harness2', 'cfg_%s.txt' % tag, 'm1.bin', 'out_%s.csv' % tag], check=True, capture_output=True)
    return [dict(side=int(d['side']), ebar=int(d['ebar']), xbar=int(d['xbar']), pnl=float(d['pnl']), pbar=int(d['pbar']), prisk=float(d['prisk'])) for d in csv.DictReader(open('out_%s.csv' % tag))]
def day(b): return (T[b] + IST) // 86400
def check(rows, shared, P):
    base, split, cap, mode, ldN, ldD = P['risk'] if 'risk' in P else 50.0, P['split'], P['seqMax'], P['seqMode'], P['ldN'], P['ldD']
    mons = [0] if shared else [0, 1]
    st = {m: dict(loss=0.0, tot=0.0, halt=False, run=0, until=None, lday=None) for m in mons}
    ev = {}
    for r in rows:
        ev.setdefault(r['xbar'], [[], []])[0].append(r)
        ev.setdefault(r['pbar'], [[], []])[1].append(r)
    bad = badp = badh = 0
    for b in sorted(ev):
        cl, pl = ev[b]
        for m in mons:
            s = st[m]
            if s['lday'] is not None and day(b) != s['lday'] and s['halt'] and P['capAct'] == 'Day':
                s['halt'] = False; s['loss'] = 0.0; s['tot'] = 0.0
            s['lday'] = day(b)
            g = sorted([r for r in cl if shared or r['side'] == m], key=lambda r: (r['side'], r['ebar']))
            if g:
                ssum = sum(r['pnl'] for r in g)
                d = s['loss'] - ssum; s['loss'] = 0.0 if d < 0.005 else d; s['tot'] += ssum
                car = max(0.0, -s['tot']) if mode == 'C+' else s['loss']
                if car <= 0.005 and P['capAct'] != 'Perm': s['halt'] = False
                for r in g:
                    xt = T[r['xbar']]
                    if s['until'] is not None and xt < s['until']: continue
                    s['run'] = s['run'] + 1 if r['pnl'] < 0 else (0 if r['pnl'] > 0 else s['run'])
                    if s['run'] >= ldN:
                        d0 = (xt + IST) // 86400; k = n_ = 0
                        while n_ < ldD:
                            k += 1
                            if (d0 + k + 3) % 7 < 5: n_ += 1
                        s['until'] = (d0 + k + 1) * 86400 - IST; s['run'] = 0
            car = max(0.0, -s['tot']) if mode == 'C+' else s['loss']
            risk = max(base, car / split) if car > 0.005 else base
            if risk > cap:
                risk = cap
                if P['capAct'] != 'Clamp': s['halt'] = True
            s['risk'] = risk
        for r in pl:
            s = st[0 if shared else r['side']]
            if abs(s['risk'] - r['prisk']) > 1e-6: bad += 1
            if s['halt']: badh += 1
            if s['until'] is not None and T[b] < s['until']: badp += 1
    return len(rows), bad, badh, badp
REC = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Day','lev':1000.0,'rev':False,'eq0':1e6,'seqMode':'C','split':3.0,'ldOn':True,'ldN':4,'ldD':3}
for nm, P, hm in (('shared C', REC, 1), ('own C', REC, 0), ('shared C+', dict(REC, seqMode='C+'), 1), ('own C+', dict(REC, seqMode='C+'), 0),
                  ('shared C cap300 clamp', dict(REC, seqMax=300.0, capAct='Clamp'), 1), ('shared C cap300 day', dict(REC, seqMax=300.0), 1)):
    rows = run(P, {'dirMode': 3, 'hedgeMoney': hm}, nm.replace(' ', '_').replace('+', 'p'))
    n, bad, badh, badp = check(rows, hm == 1, P)
    print('%-22s trades %5d  net %12.2f  | risk mismatches %d, orders while halted %d, orders during a pause %d' % (nm, n, sum(r['pnl'] for r in rows), bad, badh, badp))
