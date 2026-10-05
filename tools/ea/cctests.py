# v12.0 checks of RULE 3 (entry at the close of the signal candle, group 39), its 'close near the broken level' option and
# 'if the close is too far: fall back to RULE 1 / 2',
# FxPro gold 1m 2021 - Oct 2026:
#  off  - with group 39 Off the v12.0 core and whole EA write byte-identical files to v11.2 (old binaries: argv[2] folder)
#  py   - the Python simulator (porthp.py) == the EA core for rule 3, the broken-level option, group 24 limits, units,
#         reverse, BOS stacks, partial profit, filters, Rule C
#  sep  - every rule 3 trade checked SEPARATELY from the bars: filled at the open of the candle after its signal candle;
#         the close at most r3Brk beyond the broken level (the level from the structure engine alone); the group 24
#         limits; size from the risk; a target exit at close +/- (R x distance + costs). With the fall back ON: a trade from
#         a near signal is the market entry, a trade from a too-far signal is a limit at the rule 2 level (the broken pivot)
#         or the rule 1 level (the pullback % of the leg, from the structure engine) - or the open when that limit was
#         already reached
#  same - settings that must give exactly the same trades (the switch without the near option; only rule 3 + fall back)
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
      ('r3_ruleC', UN(r3On=True, seqMode='C', split=3.0, capAct='Day', lev=100.0, eq0=10000.0)),
      # the fall back to rule 1 / 2
      ('r3brk_fb', UN(r3On=True, r3BrkOn=True, r3Fb=True)), ('r3brk1_fb', UN(r3On=True, r3BrkOn=True, r3Brk=1.0, r3Fb=True)),
      ('r3brk_fb_g24', UN(r3On=True, r3BrkOn=True, r3Fb=True, minStop=5.0, maxStop=30.0)), ('r3brk_fb_r1', UN(r3On=True, r3BrkOn=True, r3Fb=True, r2=False)),
      ('r3brk_fb_r2', UN(r3On=True, r3BrkOn=True, r3Fb=True, r1=False)), ('r3brk_fb_none', UN(r3On=True, r3BrkOn=True, r3Fb=True, r1=False, r2=False)),
      ('r3_fb_nobrk', UN(r3On=True, r3Fb=True)), ('r3brk_fb_pips', UN(r3On=True, r3BrkOn=True, r3Brk=30.0, buMode='Pips', buPips=10.0, r3Fb=True)),
      ('r3brk_fb_filterB', dict(U, r3On=True, r3BrkOn=True, r3Fb=True, htfFilt=True)), ('r3brk_fb_against', dict(U, r3On=True, r3BrkOn=True, r3Fb=True, agn=True)),
      ('r3brk_fb_auto', dict(U, r3On=True, r3BrkOn=True, r3Fb=True, auto=True, eqPct=50.0)),
      ('r3brk_fb_ruleC', UN(r3On=True, r3BrkOn=True, r3Fb=True, seqMode='C', split=3.0, capAct='Day', lev=100.0, eq0=10000.0))]
SAME = [('r3_fb_nobrk', 'r3'), ('r3brk_fb_none', 'r3_brk3')]
def same_case(t):
    a, b = t
    ra = list(csv.DictReader(open('out_%s.csv' % a))); rb = list(csv.DictReader(open('out_%s.csv' % b)))
    ok = ra == rb
    return '%-16s = %-10s %5d / %5d trades: %s' % (a, b, len(ra), len(rb), 'IDENTICAL' if ok else 'DIFFER'), ok
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
    # + the CHOCH bars of each direction and the leg (trend, anchor, origin) after each bar for the rule 1 level
    if swp2 not in _lv:
        from cmp import porth
        E = porth.Engine(); E.swp2 = swp2
        cp = fp = None; C = []; F = []; CH = {1: [], -1: []}; LG = []
        for i, (t_, o, h, l, c) in enumerate(_bars):
            C.append(cp); F.append(fp)
            bu, bd, cu, cd = E.step(i, o, h, l, c)
            if cu: CH[1].append(i)
            if cd: CH[-1].append(i)
            mA, mO = E.anchors(); LG.append((E.trendDir, mA, mO))
            cp = E.ceilS.price if E.ceilS is not None else cp
            fp = E.florS.price if E.florS is not None else fp
        _lv[swp2] = (C, F, CH, LG)
    return _lv[swp2]
def r1lvl(lg, pct):
    # the rule 1 entry: pct % back from the leg's extreme toward its origin
    td, a, o = lg
    if a is None or o is None: return None
    if td == 1 and a > o: return a - (a - o) * pct / 100.0
    if td == -1 and a < o: return a + (o - a) * pct / 100.0
    return None
def sep_case(t):
    name, P = t
    P = fix(P)
    global _bars
    if _bars is None: _bars = pickle.load(open('fx.pkl', 'rb'))
    rows = list(csv.DictReader(open('out_%s.csv' % name)))
    lim = lambda v, px: v * P.get('pip', 0.1) if P.get('buMode') == 'Pips' else (px * v / 100.0 if P.get('buMode') == 'Pct' else v)
    C, F, CH, LG = levels(bool(P.get('pbSwp2'))) if P.get('r3BrkOn') else (None, None, None, None)
    fb = bool(P.get('r3On') and P.get('r3BrkOn') and P.get('r3Fb'))
    nf = 0
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
        g24 = lambda de, ref: (P.get('minStop', 0) <= 0 or de >= lim(P['minStop'], ref) - 1e-6) and (P.get('maxStop', 0) <= 0 or de <= lim(P['maxStop'], ref) + 1e-6)
        if (P.get('minStop', 0) > 0 or P.get('maxStop', 0) > 0) and not fb:   # group 24 at the order, for every rule
            de = d * ((c if P.get('r3On') else ep) - sl)
            if P.get('r3On') or abs(ep - _bars[e][1]) > 1e-9 or True:
                ref = c if P.get('r3On') else None
                if ref is not None and not ((P.get('minStop', 0) <= 0 or de >= lim(P['minStop'], ref) - 1e-6) and (P.get('maxStop', 0) <= 0 or de <= lim(P['maxStop'], ref) + 1e-6)):
                    bad.append(('group 24 distance %.2f' % de, r))
        if not P.get('r3On'): continue
        if fb:
            import bisect
            k = bisect.bisect_right(CH[d], pb) - 1
            if k < 0: bad.append(('no signal before the order', r)); continue
            sg = CH[d][k]; cs = _bars[sg][4]; brk = C[sg] if d == 1 else F[sg]
            if brk is not None and d * (cs - brk) <= lim(P.get('r3Brk', 3.0), cs) + 1e-9:
                if not (pb in (sg, sg + 1) and e == pb + 1 and abs(ep - _bars[e][1]) < 1e-9): bad.append(('near signal %d but not the entry at the close' % sg, r)); continue
            else:
                nf += 1
                lv = ([brk] if (P.get('r2', True) and brk is not None) else []) + ([r1lvl(LG[pb], P['pb'])] if P.get('r1', True) else [])
                lv = [x for x in lv if x is not None]
                o = _bars[e][1]
                hit = [x for x in lv if abs(ep - x) < 1e-4 or (abs(ep - o) < 1e-9 and d * (o - x) <= 1e-9)]
                if not hit:
                    bad.append(('too-far signal %d: entry %.2f not at a rule 1 / 2 level %s' % (sg, ep, ['%.2f' % x for x in lv]), r))
                elif not any(g24(d * (x - sl), x) for x in hit):
                    bad.append(('group 24 distance (fall back) %s' % ['%.2f' % (d * (x - sl)) for x in hit], r))
                continue
            if not g24(dist, c): bad.append(('group 24 distance %.2f' % dist, r)); continue
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
    return '%-16s %5d trades, %5d at the next open, %5d near the break, %4d fell back, %4d target exits: %s' % (name, len(rows), nm, nb, nf, ntp, 'ALL CORRECT' if not bad else '%d WRONG, first %s' % (len(bad), bad[0])), not bad
# whole EA (1 year each, 2025) and restarts
Y = {'from': 1500000, 'to': 1870000, 'grid': 1, 'fixTies': 1}
EAU = dict(U, lev=500.0)
EA = [('ea_r3_touch', EAU, dict(Y, exec=0, r3On=1, pbSwp2=1)), ('ea_r3brk_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1)),
      ('ea_r3brk_g24_touch', dict(EAU, minStop=5.0, maxStop=30.0), dict(Y, exec=0, r3On=1, r3BrkOn=1, r3Brk=8.0, pbSwp2=1)), ('ea_r3_hedge', EAU, dict(Y, exec=0, r3On=1, dirMode=3, hedgeMoney=0, pbSwp2=1)),
      ('ea_r3brk_ruleC_pend', dict(EAU, seqMode='C', split=3.0, capAct='Day', seqMax=1e5, lev=100.0, eq0=10000.0), dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1)),
      ('ea_r3fb_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, r3Fb=1, pbSwp2=1)), ('ea_r3fb_touch', EAU, dict(Y, exec=0, r3On=1, r3BrkOn=1, r3Fb=1, pbSwp2=1)),
      ('ea_r3fb_hedge_ruleC', dict(EAU, seqMode='C', split=3.0, capAct='Day', seqMax=1e5, lev=100.0, eq0=10000.0), dict(Y, exec=0, r3On=1, r3BrkOn=1, r3Fb=1, dirMode=3, hedgeMoney=0, pbSwp2=1))]
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
RS = [('rs_r3_touch', EAU, dict(Y, exec=0, r3On=1, pbSwp2=1)), ('rs_r3brk_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, pbSwp2=1)),
      ('rs_r3fb_pend', EAU, dict(Y, exec=1, r3On=1, r3BrkOn=1, r3Fb=1, pbSwp2=1))]
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
            for line, ok in map(same_case, SAME): print(line, flush=True); res.append(ok)
        if which in ('all', 'ea'):
            for line, ok in pool.imap(ea_case, EA, chunksize=1): print(line, flush=True); res.append(ok)
            for line, ok in pool.imap(rs_case, RS, chunksize=1): print(line, flush=True); res.append(ok)
    print('ALL SAME' if all(res) else 'SOME DIFFER: %d of %d ok' % (sum(res), len(res)))
