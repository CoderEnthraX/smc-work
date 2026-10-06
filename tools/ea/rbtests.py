# v12.1 checks, FxPro gold 1m 2021 - Oct 2026:
#  off  - with the new settings OFF the v12.1 core and whole EA write byte-identical files to v12.0 (old binaries: argv[2])
#  (v12.2 removed the profit mark - its settings are out of this list; the replay still knows it)
#  py   - the Python simulator (porthp.py) == the EA core: the hard cap's 'start again from the base risk' and the group 42
#         loss mark and profit mark (won back from the deepest point), with Rule A / B / C / B+ / C+, split, the floor, 'Stop for the day', the user's 10k account
#  sep  - every trade's risk worked out SEPARATELY from the closed trades alone (no strategy code): the losses carried
#         after each candle's closes, the loss mark, the rule, the split, the cap and its reset -> the risk of the next
#         order, compared with the risk each order was sent with
#  same - settings that must give exactly the same trades (the new settings with loss recovery Off = plain)
#  pine - the TradingView 'no new trades before news' test (group 41) written out line by line from the Pine code ==
#         the separate calculation calflags.py (which the EA's group 41 was checked against), 1m and 15m, 0.5 / 1 / 2 / 24 h
#  ea   - the whole EA in the fake MT5 == the core (pending, touch, hedge per side, hedge shared) and restarts == none
import sys, os, subprocess, csv, filecmp, pickle, datetime as dt
from collections import defaultdict
from multiprocessing import Pool
from zoneinfo import ZoneInfo
from cmp import compare, cfg_of
from fullcmp import full
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usnews, calflags
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
PY = [('plain', UN()),
      ('cb_C1_200', UN(seqMode='C', seqMax=200.0, capAct='Base')), ('cb_C3_300', UN(seqMode='C', split=3.0, seqMax=300.0, capAct='Base')),
      ('cb_Cp3_300', UN(seqMode='C+', split=3.0, seqMax=300.0, capAct='Base')), ('cb_A_400', UN(seqMode='A10', seqMax=400.0, capAct='Base')),
      ('cb_B_300', UN(seqMode='B', seqMax=300.0, capAct='Base')), ('cb_Bp_500', UN(seqMode='B+', seqMax=500.0, capAct='Base')),
      ('cb_base_above', UN(seqMode='C', seqMax=40.0, capAct='Base')),
      ('lm_C3_300', UN(seqMode='C', split=3.0, lmOn=True, lmAmt=300.0)), ('lm_C1_500', UN(seqMode='C', lmOn=True, lmAmt=500.0)),
      ('lm_Cp3_300', UN(seqMode='C+', split=3.0, lmOn=True, lmAmt=300.0)), ('lm_A_200', UN(seqMode='A10', lmOn=True, lmAmt=200.0)),
      ('lm_B_300', UN(seqMode='B', lmOn=True, lmAmt=300.0)), ('lm_cb_C3', UN(seqMode='C', split=3.0, seqMax=250.0, capAct='Base', lmOn=True, lmAmt=400.0)),
      ('lm_off_seq', UN(lmOn=True, lmAmt=300.0, capAct='Base', seqMax=40.0)),
      ('lm_C3_day', UN(seqMode='C', split=3.0, seqMax=1000.0, capAct='Day', lmOn=True, lmAmt=2000.0)),
      ('lm_floor', UN(seqMode='C', split=3.0, lmOn=True, lmAmt=300.0, flMode='Cap', flAmt=2000.0)),
      ('cb_user_10k', UN(seqMode='C', split=3.0, seqMax=200.0, capAct='Base', lev=100.0, eq0=10000.0)),
      ('lm_user_10k', UN(seqMode='C', split=3.0, seqMax=1e5, capAct='Day', lmOn=True, lmAmt=300.0, lev=100.0, eq0=10000.0))]
SEP = ('cb_C1_200', 'cb_C3_300', 'cb_Cp3_300', 'cb_A_400', 'cb_B_300', 'cb_Bp_500', 'cb_base_above', 'lm_C3_300', 'lm_C1_500', 'lm_Cp3_300',
       'lm_A_200', 'lm_B_300', 'lm_cb_C3', 'cb_user_10k')
SAME = [('lm_off_seq', 'plain')]
def py_case(t):
    import io, contextlib
    name, P = t
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = compare(name, fix(P), cs=60)
    return f.getvalue().strip(), ok
def sep_case(t):
    # the risk of every order from the closed trades alone
    name, P = t
    p = dict(seqAdd=50.0, split=1.0, lmOn=False, lmAmt=300.0, pmOn=False, pmAmt=200.0, risk=50.0); p.update(P)
    rows = list(csv.DictReader(open('out_%s.csv' % name)))
    mode = p['seqMode']; plus = mode.endswith('+'); base = p['risk']; cap = p['seqMax']
    grp = defaultdict(float)
    for r in rows: grp[int(r['xbar'])] += float(r['pnl'])
    ev = sorted(grp)
    debt = tot = pk = 0.0; nlm = ncb = npm = 0
    car = lambda: max(0.0, -tot) if plus else debt
    def risk():
        nonlocal debt, tot, ncb, pk
        c = car()
        if mode in ('A10', 'A+'): r = max(base, (c + p['seqAdd']) / p['split']) if c > 0.005 else base
        elif mode in ('B', 'B+'): r = max(base, 2.0 * c / p['split']) if c > 0.005 else base
        else: r = max(base, c / p['split']) if c > 0.005 else base
        if r > cap:
            if p['capAct'] == 'Base':
                if c > 0.005: debt = tot = pk = 0.0; ncb += 1
                r = min(base, cap)
            else: r = cap
        return r
    cur = risk(); ei = 0; bad = []; mx = 0.0
    for r in sorted(rows, key=lambda r: (int(r['pbar']), int(r['ebar']))):
        pb = int(r['pbar'])
        while ei < len(ev) and ev[ei] <= pb:
            s = grp[ev[ei]]; ei += 1
            d = debt - s; debt = 0.0 if d < 0.005 else d; tot += s
            if p['lmOn'] and car() >= p['lmAmt'] - 0.005: debt = tot = 0.0; nlm += 1
            if p['pmOn'] and car() > 0.005 and pk - car() >= p['pmAmt'] - 0.005: debt = tot = 0.0; npm += 1
            pk = 0.0 if car() <= 0.005 else max(pk, car())
            cur = risk()
        mx = max(mx, cur)
        if abs(cur - float(r['prisk'])) > 1e-3: bad.append((pb, cur, float(r['prisk'])))
    ok = not bad and (ncb + nlm + npm > 0 or name == 'cb_base_above')
    return '%-14s %5d trades: every risk %s | resets: cap %4d, loss mark %4d, profit mark %4d | biggest risk %8.2f' % (
        name, len(rows), 'as worked out' if not bad else '%d DIFFER, first %s' % (len(bad), bad[0]), ncb, nlm, npm, mx), ok
def same_case(t):
    a, b = t
    ra = list(csv.DictReader(open('out_%s.csv' % a))); rb = list(csv.DictReader(open('out_%s.csv' % b)))
    return '%-12s = %-6s %5d / %5d trades: %s' % (a, b, len(ra), len(rb), 'IDENTICAL' if ra == rb else 'DIFFER'), ra == rb
# ---- the Pine group 41 test, written out from the Pine code (f_auDay today + tomorrow on the New York date of time_close,
#      f_preHit = time_close < t and time_close + bar > t - hours)
NY = ZoneInfo('America/New_York')
def pine_pre(bars, cs, hrs):
    preMs = int(round(hrs * 3600)) * 1000; lenMs = cs * 1000
    key = None; T = []; out = []
    for b in bars:
        tc = (b[0] + cs) * 1000
        d = dt.datetime.fromtimestamp(tc / 1000, NY).date()
        if d != key:
            key = d; e = d + dt.timedelta(days=1)
            T = [x * 1000 for _, x in usnews.releases(d.year, d.month, d.day)] + [x * 1000 for _, x in usnews.releases(e.year, e.month, e.day)]
        out.append(any(tc < t and tc + lenMs > t - preMs for t in T))
    return out
def pine_case(t):
    cs, hrs = t
    bars = pickle.load(open('fx.pkl' if cs == 60 else 'fx15.pkl', 'rb'))
    a = pine_pre(bars, cs, hrs)
    _, b = calflags.flags(bars, cs=cs, preList=calflags.all_au(), preH=hrs)
    nd = sum(1 for x, y in zip(a, b) if x != y)
    return '%3dm, %4.1f h before: %7d bars, %6d blocked - %s' % (cs // 60, hrs, len(a), sum(a), 'SAME as the separate calculation' if nd == 0 and len(a) == len(b) else '%d DIFFER' % nd), nd == 0
# ---- group 42 / cap OFF = v12.0, byte for byte
OFFC = [('off_user', dict(U, news=True), {}), ('off_defaults', {}, {}), ('off_bos_partial', dict(U, sig='Both', maxOpen=3, partOn=True), {}),
        ('off_ruleC', dict(U, news=True, seqMode='C', split=3.0, capAct='Day', lev=100.0, eq0=10000.0), {}), ('off_pips_hedge', U, {'buMode': 1, 'buPips': 50.0, 'dirMode': 3})]
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
    out = ['%-18s core: %5d trades, v12.1 = v12.0 %s' % (name, n, 'BYTE-IDENTICAL' if same else 'DIFFER')]
    if name in ('off_user', 'off_pips_hedge'):
        c2 = dict(c, **{'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1, 'exec': 1 if name == 'off_user' else 0})
        with open(fn, 'w') as f:
            for k, v in c2.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
        subprocess.run(['./simmain', fn, 'm1.bin', 'enew_%s.csv' % name], check=True, capture_output=True)
        subprocess.run([OLD + '/simmain', fn, 'm1.bin', 'eold_%s.csv' % name], check=True, capture_output=True)
        s2 = filecmp.cmp('enew_%s.csv' % name, 'eold_%s.csv' % name, shallow=False)
        out.append('%-18s whole EA (1 year): v12.1 = v12.0 %s' % (name, 'BYTE-IDENTICAL' if s2 else 'DIFFER'))
        same = same and s2
    return '\n'.join(out), same
# ---- whole EA (1 year, 2025) and restarts
Y = {'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1}
EAU = dict(U, lev=100.0, eq0=10000.0)
EA = [('ea_cb_pend', dict(EAU, seqMode='C', split=3.0, seqMax=200.0, capAct='Base'), dict(Y, exec=1, pbSwp2=1)),
      ('ea_lm_touch', dict(EAU, seqMode='C', split=3.0, seqMax=1e5, capAct='Day', lmOn=True, lmAmt=300.0), dict(Y, exec=0, pbSwp2=1)),
      ('ea_lmcb_hedge_own', dict(EAU, seqMode='C+', split=3.0, seqMax=250.0, capAct='Base', lmOn=True, lmAmt=300.0), dict(Y, exec=0, dirMode=3, hedgeMoney=0, pbSwp2=1)),
      # shared money: without the loss pause - with it, two sides closing on the SAME candle are counted in the real tick order
      # by the EA but in a fixed order by the core (it only sees candles), so the pause can start one trade apart (v12.0 too)
      ('ea_lmcb_hedge_shared', dict(EAU, seqMode='C', split=3.0, seqMax=250.0, capAct='Base', lmOn=True, lmAmt=300.0, ldOn=False), dict(Y, exec=1, dirMode=3, hedgeMoney=1, pbSwp2=1)),
      ('ea_lmcb_hedge_shared_touch', dict(EAU, seqMode='C+', split=3.0, seqMax=250.0, capAct='Base', lmOn=True, lmAmt=300.0, ldOn=False), dict(Y, exec=0, dirMode=3, hedgeMoney=1, pbSwp2=1))]
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
RS = [('rs_cb_pend', EA[0][1], EA[0][2]), ('rs_lmcb_hedge_shared', EA[3][1], EA[3][2])]
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
        if which in ('all', 'pine'):
            for line, ok in pool.imap(pine_case, [(60, 0.5), (60, 1.0), (60, 2.0), (60, 24.0), (900, 1.0), (900, 2.0)], chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
