# v12.2 checks of Rule A / B / C split (the base risk grows in steps with the total profit - group 43), FxPro gold 2021 - Oct 2026:
#  off  - with the split rules not chosen, the v12.2 core and whole EA write byte-identical files to v12.1 (old binaries:
#         argv[2]) - also with the v12.1 cap reset and loss mark ON (the profit mark removal changed nothing else)
#  py   - the Python simulator (porthp.py) == the EA core: A / B / C split, default and low steps, longs only, 'counts from'
#         a date, the cap (clamp / start again / stop for the day / step base above the cap), the loss mark, the floor, 15m
#  sep  - every order's risk worked out SEPARATELY from the closed trades alone: the total profit of the counted trades ->
#         the step reached -> the base; the losses carried -> what Rule A / B / C asks; the cap -> the risk of the next
#         order, compared with the risk each order was sent with
#  same - the steps with another rule = that rule; Rule C split with every step off = Rule C
#  ea   - the whole EA in the fake MT5 == the core (pending, touch, hedge per side, hedge shared) and restarts == none
import sys, os, subprocess, csv, filecmp, pickle, math, datetime as dt
from collections import defaultdict
from multiprocessing import Pool
from cmp import compare, cfg_of
from fullcmp import full
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usnews
OLD = sys.argv[2] if len(sys.argv) > 2 else None
_news = None
def news():
    global _news
    if _news is None: _news = usnews.blocked(pickle.load(open('fx.pkl', 'rb')), pre=10, post=20, bar_sec=60)
    return _news
U = dict(sig='CHOCH', r1=True, r2=True, pb=25.0, rr=3.0, slbuf=1.0, rev=False, wkHr=23, cmU=0.76, comm=0.3, lev=1.0, eq0=1e6,
         bosMode='Cancel', ldOn=True, ldN=4, ldD=3, seqMax=1e5, capAct='Clamp', pbSwp2=True)
def UN(**k): return dict(U, news=True, **k)
def fix(P):
    P = dict(P)
    if P.get('news') is True: P['news'] = news()
    return P
# low steps with a base risk of 10 (a step base below the base risk is not used, so the steps must be above it to be tested)
LOW = dict(risk=10.0, sp1=30.0, spN1=2.0, sp2=60.0, spN2=3.0, sp3=100.0, spN3=4.0, spInc=50.0, spAdd=1.0)
T2025 = int(dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp())
M15 = dict(sig='CHOCH', auto=True, eqPct=50.0, r1=True, r2=True, pb=50.0, rr=2.0, rev=False, slbuf=1.0, bosMode='Follow', wkHr=23, lev=100.0, eq0=10000.0,
           htfTf=14400, barSec=900, ldOn=True, ldN=4, ldD=3, seqMax=300.0, capAct='Clamp', cmU=0.76, comm=0.3)
PY = [('plain_C3', UN(seqMode='C', split=3.0), 60),
      ('sp_C_user', UN(seqMode='Cs', split=3.0), 60), ('sp_C_low', UN(seqMode='Cs', split=3.0, **LOW), 60),
      ('sp_A_2025', UN(seqMode='As', seqMax=300.0, capAct='Base', liveT=T2025), 60), ('sp_B_2025', UN(seqMode='Bs', split=2.0, seqMax=300.0, capAct='Base', liveT=T2025), 60),
      ('sp_C_longs', UN(seqMode='Cs', split=3.0, direction='Longs'), 60), ('sp_C_2025', UN(seqMode='Cs', split=3.0, liveT=T2025), 60),
      ('sp_C_capbase', UN(seqMode='Cs', split=3.0, seqMax=150.0, capAct='Base', liveT=T2025), 60),
      ('sp_C_capday', UN(seqMode='Cs', split=3.0, seqMax=60.0, capAct='Day', **LOW), 60),
      ('sp_C_capabove', UN(seqMode='Cs', split=3.0, seqMax=120.0, capAct='Clamp', liveT=T2025), 60),
      ('sp_C_lm', UN(seqMode='Cs', split=3.0, lmOn=True, lmAmt=300.0, liveT=T2025), 60),
      ('sp_C_floor', UN(seqMode='Cs', split=3.0, flMode='Cap', flAmt=2000.0, liveT=T2025), 60),
      ('sp_C_user_10k', UN(seqMode='Cs', split=3.0, seqMax=1e5, capAct='Day', lev=100.0, eq0=10000.0), 60),
      ('sp_C_15m', dict(M15, seqMode='Cs', split=1.0), 900), ('sp_A_15m', dict(M15, seqMode='As', split=1.0, seqMax=1e5), 900),
      ('sp_B_15m', dict(M15, seqMode='Bs', split=2.0, seqMax=1e5), 900),
      ('sp_off_steps', UN(seqMode='C', split=3.0, sp1=30.0, spN1=2.0, sp2=60.0, spN2=3.0, sp3=100.0, spN3=4.0, spInc=50.0, spAdd=1.0), 60), ('sp_C_nosteps', UN(seqMode='Cs', split=3.0, sp1=0.0, sp2=0.0, sp3=0.0), 60)]
SEP = ('sp_C_user', 'sp_C_low', 'sp_A_2025', 'sp_B_2025', 'sp_C_longs', 'sp_C_2025', 'sp_C_capbase', 'sp_C_capabove', 'sp_C_lm', 'sp_C_15m', 'sp_A_15m', 'sp_B_15m')
SAME = [('sp_off_steps', 'plain_C3'), ('sp_C_nosteps', 'plain_C3')]
def py_case(t):
    import io, contextlib
    name, P, cs = t
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = compare(name, fix(P), cs=cs)
    return f.getvalue().strip(), ok
_bars = {}
def sep_case(t):
    # the risk of every order from the closed trades alone (no strategy code)
    name, P, cs = t
    if cs not in _bars: _bars[cs] = pickle.load(open('fx.pkl' if cs == 60 else 'fx15.pkl', 'rb'))
    bars = _bars[cs]
    p = dict(seqAdd=50.0, split=1.0, lmOn=False, lmAmt=300.0, risk=50.0, liveT=None, sp1=200.0, spN1=3.0, sp2=500.0, spN2=5.0, sp3=1000.0, spN3=8.0,
             spInc=500.0, spAdd=1.0); p.update(P)
    rows = list(csv.DictReader(open('out_%s.csv' % name)))
    mode = p['seqMode']; base = p['risk']; cap = p['seqMax']
    def steps(pf):
        # the steps written out: 200 / 3, 500 / 5, 1,000 / 8, then every 500 one more part (or the settings given)
        best = None
        for amt, n in ((p['sp1'], p['spN1']), (p['sp2'], p['spN2']), (p['sp3'], p['spN3'])):
            if amt > 0 and pf >= amt - 0.005 and (best is None or amt > best[0]): best = (amt, n)
        if best is not None and best[0] == p['sp3'] and p['spInc'] > 0:
            k = math.floor((pf - p['sp3'] + 0.005) / p['spInc'])
            best = (p['sp3'] + k * p['spInc'], p['spN3'] + k * p['spAdd'])
        return best[0] / best[1] if best else 0.0
    grp = defaultdict(float)
    for r in rows:
        if p['liveT'] is None or bars[int(r['ebar'])][0] >= p['liveT']: grp[int(r['xbar'])] += float(r['pnl'])
    ev = sorted(grp)
    debt = 0.0; prof = 0.0; ncb = nlm = 0; hist = defaultdict(int)
    def risk():
        nonlocal debt, ncb
        b = max(base, min(steps(prof), cap))
        if mode == 'As': r = max(b, (debt + p['seqAdd']) / p['split']) if debt > 0.005 else b
        elif mode == 'Bs': r = max(b, 2.0 * debt / p['split']) if debt > 0.005 else b
        else: r = max(b, debt / p['split']) if debt > 0.005 else b
        if r > cap:
            if p['capAct'] == 'Base':
                if debt > 0.005: debt = 0.0; ncb += 1
                r = min(b, cap)
            else: r = cap
        return r, b
    cur, bnow = risk(); ei = 0; bad = []; mx = 0.0
    for r in sorted(rows, key=lambda r: (int(r['pbar']), int(r['ebar']))):
        pb = int(r['pbar'])
        while ei < len(ev) and ev[ei] <= pb:
            s = grp[ev[ei]]; ei += 1
            d = debt - s; debt = 0.0 if d < 0.005 else d; prof += s
            if p['lmOn'] and debt >= p['lmAmt'] - 0.005: debt = 0.0; nlm += 1
            cur, bnow = risk()
        mx = max(mx, cur); hist[round(bnow, 2)] += 1
        if abs(cur - float(r['prisk'])) > 1e-3: bad.append((pb, cur, float(r['prisk'])))
    above = sum(v for k, v in hist.items() if k > base + 1e-9)
    ok = not bad and above > 0
    return '%-14s %5d trades: every risk %s | %4d orders on a profit step (bases %s) | cap resets %d, loss mark %d | biggest %.2f' % (
        name, len(rows), 'as worked out' if not bad else '%d DIFFER, first %s' % (len(bad), bad[0]), above,
        ', '.join('%.2f' % k for k in sorted(hist) if k > base + 1e-9)[:60] or '-', ncb, nlm, mx), ok
def same_case(t):
    a, b = t
    ra = list(csv.DictReader(open('out_%s.csv' % a))); rb = list(csv.DictReader(open('out_%s.csv' % b)))
    return '%-14s = %-9s %5d / %5d trades: %s' % (a, b, len(ra), len(rb), 'IDENTICAL' if ra == rb else 'DIFFER'), ra == rb
# ---- not chosen = v12.1, byte for byte (the v12.1 old binaries hold the profit mark - off here)
OFFC = [('off_user', dict(U, news=True), {}), ('off_defaults', {}, {}), ('off_bos_partial', dict(U, sig='Both', maxOpen=3, partOn=True), {}),
        ('off_ruleC', dict(U, news=True, seqMode='C', split=3.0, capAct='Day', lev=100.0, eq0=10000.0), {}), ('off_pips_hedge', U, {'buMode': 1, 'buPips': 50.0, 'dirMode': 3}),
        ('off_capbase_lm', dict(U, news=True, seqMode='C', split=3.0, seqMax=250.0, capAct='Base', lmOn=True, lmAmt=400.0), {}),
        ('off_Cp_lm', dict(U, news=True, seqMode='C+', split=3.0, lmOn=True, lmAmt=300.0), {})]
def off_case(t):
    name, P, e = t
    c = cfg_of(fix(P), 60); c.update(e)
    fn = 'ocfg_%s.txt' % name
    with open(fn, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    subprocess.run(['./harness', fn, 'm1.bin', 'onew_%s.csv' % name], check=True, capture_output=True)
    subprocess.run([OLD + '/harness', fn, 'm1.bin', 'oold_%s.csv' % name], check=True, capture_output=True)
    same = filecmp.cmp('onew_%s.csv' % name, 'oold_%s.csv' % name, shallow=False)
    n = sum(1 for _ in open('onew_%s.csv' % name)) - 1
    out = ['%-18s core: %5d trades, v12.2 = v12.1 %s' % (name, n, 'BYTE-IDENTICAL' if same else 'DIFFER')]
    if name in ('off_user', 'off_pips_hedge'):
        c2 = dict(c, **{'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1, 'exec': 1 if name == 'off_user' else 0})
        with open(fn, 'w') as f:
            for k, v in c2.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
        subprocess.run(['./simmain', fn, 'm1.bin', 'enew_%s.csv' % name], check=True, capture_output=True)
        subprocess.run([OLD + '/simmain', fn, 'm1.bin', 'eold_%s.csv' % name], check=True, capture_output=True)
        s2 = filecmp.cmp('enew_%s.csv' % name, 'eold_%s.csv' % name, shallow=False)
        out.append('%-18s whole EA (1 year): v12.2 = v12.1 %s' % (name, 'BYTE-IDENTICAL' if s2 else 'DIFFER'))
        same = same and s2
    return '\n'.join(out), same
# ---- whole EA (1 year, 2025) and restarts
Y = {'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1}
EAU = dict(U, lev=100.0, eq0=10000.0)
EA = [('ea_spC_pend', dict(EAU, seqMode='Cs', split=3.0, **LOW), dict(Y, exec=1, pbSwp2=1)),
      ('ea_spA_touch', dict(EAU, seqMode='As', seqMax=40.0, capAct='Base', **LOW), dict(Y, exec=0, pbSwp2=1)),
      ('ea_spC_default_pend', dict(EAU, seqMode='Cs', split=3.0), dict(Y, exec=1, pbSwp2=1)),
      ('ea_spC_hedge_own', dict(EAU, seqMode='Cs', split=3.0, seqMax=60.0, capAct='Base', **LOW), dict(Y, exec=0, dirMode=3, hedgeMoney=0, pbSwp2=1)),
      # shared money without the loss pause (with it, same-candle closes of the two sides are ordered by tick in the EA and by
      # candle in the core - see the v12.1 checks)
      ('ea_spC_hedge_shared', dict(EAU, seqMode='Cs', split=3.0, seqMax=60.0, capAct='Base', ldOn=False, **LOW), dict(Y, exec=1, dirMode=3, hedgeMoney=1, pbSwp2=1))]
def ea_case(t):
    import io, contextlib
    name, P, e = t
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = full(name, P, e)
    return f.getvalue().strip(), ok
def rs_case(t):
    name, P, e = t
    def one(tag, extra):
        c = cfg_of(P, 60); c.update(e); c.update(extra)
        fn = 'rcfg_%s.txt' % tag
        with open(fn, 'w') as f:
            for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
        r = subprocess.run(['./simmain', fn, 'm1.bin', 'rea_%s.csv' % tag], capture_output=True, text=True)
        return sorted([tuple(d.values()) for d in csv.DictReader(open('rea_%s.csv' % tag))]), r.stderr.strip().split('\n')[-1]
    a, sa = one(name + '_plain', dict(tester=0))
    b, sb = one(name + '_restart', dict(tester=0, restartEvery=1500))
    return '%-22s no restarts: %s | with restarts: %s | %s' % (name, sa, sb, 'IDENTICAL' if a == b else 'DIFFER'), a == b
RS = [('rs_spC_pend', EA[0][1], EA[0][2]), ('rs_spC_hedge_shared', EA[4][1], EA[4][2])]
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    res = []
    with Pool(4) as pool:
        if which in ('all', 'off'):
            for line, ok in pool.imap(off_case, OFFC, chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'py'):
            for line, ok in pool.imap(py_case, PY, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(sep_case, [t for t in PY if t[0] in SEP], chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in map(same_case, SAME): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
