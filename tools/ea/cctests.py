# v12.0 checks of RULE 3 (entry at the close of the signal candle, group 39) and its 'close near the broken level' option,
# FxPro gold 1m 2021 - Oct 2026:
#  off  - with group 39 Off the v12.0 core and whole EA write byte-identical files to v11.2 (old binaries: argv[2] folder)
#  py   - the Python simulator (porthp.py) == the EA core for rule 3, the broken-level option, group 24 limits, units,
#         reverse, BOS stacks, partial profit, filters, Rule C
#  sep  - every rule 3 trade checked SEPARATELY from the bars: filled at the open of the candle after its signal candle;
#         the close at most r3Brk beyond the broken level (the level from the structure engine alone); the group 24
#         limits; size from the risk; a target exit at close +/- (R x distance + costs)
#  ea   - the whole EA in the fake MT5 == the core (touch, pending, hedge, Rule C) and with forced restarts == without
import sys, os, subprocess, csv, filecmp, pickle, math
from multiprocessing import Pool
from cmp import compare, run_cpp, cfg_of
from fullcmp import full
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import usnews
OLD = sys.argv[2] if len(sys.argv) > 2 else None
_news = None
def news():
    global _news
    if _news is None: _news = usnews.blocked(pickle.load(open('fx.pkl', 'rb')), pre=10, post=20, bar_sec=60)
    return _news
# your TradingView settings (recovery off, risk 50, a big account so it never empties)
U = dict(sig='CHOCH', r1=True, r2=True, pb=25.0, rr=3.0, slbuf=1.0, rev=False, wkHr=23, cmU=0.76, comm=0.3, lev=1.0, eq0=1e6,
         bosMode='Cancel', ldOn=True, ldN=4, ldD=3, seqMax=1e5, capAct='Clamp', pbSwp2=True)
def UN(**k): return dict(U, news=True, **k)          # news flags are filled in by the worker
BU = {'Price': 0, 'Pips': 1, 'Pct': 2}
def ex(P): return {'buMode': BU[P.get('buMode', 'Price')], 'buPips': P.get('buPips', 10.0), 'buPct': P.get('buPct', 0.02), 'buPip': P.get('pip', 0.1)}
def fix(P):
    P = dict(P)
    if P.get('news') is True: P['news'] = news()
    return P
PY = [('r3', UN(r3On=True)), ('r3_brk3', UN(r3On=True, r3BrkOn=True)), ('r3_brk1', UN(r3On=True, r3BrkOn=True, r3Brk=1.0)),
      ('r3_brk8_g24', UN(r3On=True, r3BrkOn=True, r3Brk=8.0, minStop=5.0, maxStop=30.0)), ('r12_g24', UN(minStop=3.0, maxStop=30.0)),
      ('r3_brk30pips', UN(r3On=True, r3BrkOn=True, r3Brk=30.0, buMode='Pips', buPips=10.0)), ('r3_brkpct', UN(r3On=True, r3BrkOn=True, r3Brk=0.1, buMode='Pct', buPct=0.03)),
      ('r3_reverse', dict(U, r3On=True, rev=True, ldOn=False)), ('r3_bos_stack', dict(U, r3On=True, sig='Both', maxOpen=3, ldOn=False)),
      ('r3_partial', dict(U, r3On=True, partOn=True, partPct=50.0, partR=1.0, partBe=True)), ('r3_filterB', dict(U, r3On=True, htfFilt=True)),
      ('r3_against', dict(U, r3On=True, agn=True)), ('r3brk_auto', dict(U, r3On=True, r3BrkOn=True, auto=True, eqPct=50.0)),
      ('r3_ruleC', UN(r3On=True, seqMode='C', split=3.0, capAct='Day', lev=100.0, eq0=10000.0))]
def py_case(t):
    import io, contextlib
    name, P = t
    P = fix(P)
    f = io.StringIO()
    with contextlib.redirect_stdout(f): ok = compare(name, P, cs=60, extra=ex(P))
    return f.getvalue().strip(), ok
_bars = None
_lv = {}
def levels(swp2):
    # the broken level of every bar from the structure engine alone: stCeilPrev / stFlorPrev = the ceiling / floor kept
    # from the bar before (Pine: the level the signal candle broke)
    if swp2 not in _lv:
        from cmp import porth
        E = porth.Engine(); E.swp2 = swp2
        cp = fp = None; C = []; F = []
        for i, (t_, o, h, l, c) in enumerate(_bars):
            C.append(cp); F.append(fp)
            E.step(i, o, h, l, c)
            cp = E.ceilS.price if E.ceilS is not None else cp
            fp = E.florS.price if E.florS is not None else fp
        _lv[swp2] = (C, F)
    return _lv[swp2]
def sep_case(t):
    name, P = t
    P = fix(P)
    global _bars
    if _bars is None: _bars = pickle.load(open('fx.pkl', 'rb'))
    rows = list(csv.DictReader(open('out_%s.csv' % name)))
    lim = lambda v, px: v * P.get('pip', 0.1) if P.get('buMode') == 'Pips' else (px * v / 100.0 if P.get('buMode') == 'Pct' else v)
    C, F = levels(bool(P.get('pbSwp2'))) if P.get('r3BrkOn') else (None, None)
    # the stop a setup was opened with: the file holds each trade's LAST stop (break-even moves it), so take the
    # furthest stop of the pieces that opened on the same candle the same way (partial profit = two pieces)
    s0 = {}
    for r in rows:
        k = (int(r['ebar']), int(r['dir'])); v = float(r['sl0'])
        s0[k] = v if k not in s0 else (min(s0[k], v) if k[1] == 1 else max(s0[k], v))
    bad = []; nm = 0; ntp = 0; nb = 0
    for r in rows:
        e, pb, d = int(r['ebar']), int(r['pbar']), int(r['dir'])
        ep, sl, q = float(r['ep']), s0[(e, d)], float(r['q'])
        c = _bars[pb][4]
        dist = d * (c - sl)
        if P.get('minStop', 0) > 0 or P.get('maxStop', 0) > 0:   # group 24 at the order, for every rule
            de = d * ((c if P.get('r3On') else ep) - sl)
            if P.get('r3On') or abs(ep - _bars[e][1]) > 1e-9 or True:
                ref = c if P.get('r3On') else None
                if ref is not None and not ((P.get('minStop', 0) <= 0 or de >= lim(P['minStop'], ref) - 1e-6) and (P.get('maxStop', 0) <= 0 or de <= lim(P['maxStop'], ref) + 1e-6)):
                    bad.append(('group 24 distance %.2f' % de, r))
        if not P.get('r3On'): continue
        if not (e == pb + 1 and abs(ep - _bars[e][1]) < 1e-9): bad.append(('not filled at the next open', r)); continue
        nm += 1
        if P.get('r3BrkOn'):
            brk = C[pb] if d == 1 else F[pb]
            if brk is None or d * (c - brk) > lim(P.get('r3Brk', 3.0), c) + 1e-9: bad.append(('close %.2f beyond the broken level' % (d * (c - brk) if brk else -1), r))
            else: nb += 1
        if not P.get('partOn') and P.get('seqMode', 'Off') == 'Off' and P.get('sig') == 'CHOCH':
            amt = 50.0; per = dist + P['cmU']; raw = amt / per; qq = math.floor(raw + 0.5)
            if qq * per > amt * 1.25: qq = math.floor(raw)
            if abs(qq - q) > 1e-6: bad.append(('size %g expected %g' % (q, qq), r))
        if r['why'] == 'TP':
            ntp += 1
            tgts = [c + d * (P['rr'] * dist + P['cmU'] * (P['rr'] + 1.0))]
            if P.get('partOn'):
                t1 = c + d * (P.get('partR', 1.0) * dist + P['cmU'] * (P.get('partR', 1.0) + 1.0))
                tgts.append(min(t1, tgts[0]) if d == 1 else max(t1, tgts[0]))
            xb = int(r['xbar']); xp = float(r['xp'])
            if all(abs(xp - tg) > 1e-6 and not (abs(xp - _bars[xb][1]) < 1e-9 and d * (_bars[xb][1] - tg) > 0) for tg in tgts): bad.append(('target %.2f expected %s' % (xp, ['%.2f' % x for x in tgts]), r))
    return '%-16s %5d trades, %5d at the next open, %5d near the break, %4d target exits: %s' % (name, len(rows), nm, nb, ntp, 'ALL CORRECT' if not bad else '%d WRONG, first %s' % (len(bad), bad[0])), not bad
# whole EA (1 year each, 2025) and restarts
Y = {'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1}
EAU = dict(U, lev=500.0)
EA = [('ea_r3_touch', EAU, dict(Y, exec=0, r3On=1, pbSwp2=1)), ('ea_r3brk_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1)),
      ('ea_r3brk_g24_touch', dict(EAU, minStop=5.0, maxStop=30.0), dict(Y, exec=0, r3On=1, r3BrkOn=1, r3Brk=8.0, pbSwp2=1)), ('ea_r3_hedge', EAU, dict(Y, exec=0, r3On=1, dirMode=3, hedgeMoney=0, pbSwp2=1)),
      ('ea_r3brk_ruleC_pend', dict(EAU, seqMode='C', split=3.0, capAct='Day', seqMax=1e5, lev=100.0, eq0=10000.0), dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1))]
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
RS = [('rs_r3_touch', EAU, dict(Y, exec=0, r3On=1, pbSwp2=1)), ('rs_r3brk_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1))]
# group 39 OFF = v11.2, byte for byte
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
    out = ['%-18s core: %5d trades, v12.0 = v11.2 %s' % (name, n, 'BYTE-IDENTICAL' if same else 'DIFFER')]
    if name in ('off_user', 'off_pips_hedge'):
        c2 = dict(c, **{'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1, 'exec': 1 if name == 'off_user' else 0})
        with open(fn, 'w') as f:
            for k, v in c2.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
        subprocess.run(['./simmain', fn, 'm1.bin', 'enew_%s.csv' % name], check=True, capture_output=True)
        subprocess.run([OLD + '/simmain', fn, 'm1.bin', 'eold_%s.csv' % name], check=True, capture_output=True)
        s2 = filecmp.cmp('enew_%s.csv' % name, 'eold_%s.csv' % name, shallow=False)
        out.append('%-18s whole EA (1 year): v12.0 = v11.2 %s' % (name, 'BYTE-IDENTICAL' if s2 else 'DIFFER'))
        same = same and s2
    return '\n'.join(out), same
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    res = []
    with Pool(4) as pool:
        if which in ('all', 'off'):
            for line, ok in pool.imap(off_case, OFFC, chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'py'):
            for line, ok in pool.imap(py_case, PY, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(sep_case, PY, chunksize=1): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
