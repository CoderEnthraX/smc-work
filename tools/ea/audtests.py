# v12.3 checks of the signal audit LABELS on the chart ('Signal audit' ON, group 44: size, how many to keep):
#  same  - display only: the trades with the labels on = off (live mode, where the EA draws), touch / pending / hedge
#  sep   - every label worked out SEPARATELY from the EA's journal lines ("[strategy] <time> CHOCH up: L12 R1 ARMED",
#          "L12 FILLED", "CANCELLED - ...") and the price bars: one label per traded-on signal (hedge: the long side labels
#          the buy signals, the short side the sell signals) at the signal candle - under its low for a buy signal, over
#          its high for a sell signal - every later step of the ARMED setup added; the text on the chart (63 characters at
#          most), the tooltip (all steps with their times), the colour of the last step (dark and light chart), the size;
#          only the newest N kept
#  rs    - restarts every ~1,500 bars: the labels at the end = the run with no restarts (they stay, a kept setup's label
#          goes on)
#  sleep - the same separate check with sleeps (the catch-up of v12.3 writes "CANCELLED - the entry was reached while
#          the EA was offline" on the label)
# usage: python3 audtests.py <simmain of v12.3>
import sys, os, subprocess, csv, math
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'aud_out')
BIN = os.path.abspath(sys.argv[1])
sys.argv = sys.argv[:1] + ['x', 'x']
import sleeptests as ST
DARK = {'REFUSED': 14, 'FILLED': 9, 'CANCELLED': 3, 'ARMED': 5, 'SKIP': 7}    # tomato, lime, orange, dodger blue, silver
LIGHT = {'REFUSED': 4, 'FILLED': 15, 'CANCELLED': 16, 'ARMED': 17, 'SKIP': 18}  # red, green, dark orange, medium blue, dim grey
SIZE = {0: 7, 1: 9, 2: 11, 3: 14}
B = dict(tester=0, draw=1, table=1, to=200000)
RUNS = {   # name: (base settings, changes)
    'touch':      ('rcfg_touch_user_plain.txt', dict(B)),
    'touch_off':  ('rcfg_touch_user_plain.txt', dict(B, audit=0)),
    'pend':       ('rcfg_pend_user_plain.txt', dict(B)),
    'pend_off':   ('rcfg_pend_user_plain.txt', dict(B, audit=0)),
    'hedge':      ('rcfg_touch_hedge_own_plain.txt', dict(B)),
    'hedge_off':  ('rcfg_touch_hedge_own_plain.txt', dict(B, audit=0)),
    'light_small_50': ('rcfg_touch_user_plain.txt', dict(B, chartBg=16777215, audSz=0, audMax=50)),
    'r3_huge':    ('fcfg_ea_r3_touch.txt', dict(B, to=1700000, audSz=3)),
    'rev_longs':  ('rcfg_touch_trail_rev_plain.txt', dict(B, dirMode=1)),
    'touch_rs':   ('rcfg_touch_user_restart.txt', dict(B)),
    'hedge_rs':   ('rcfg_touch_hedge_own_restart.txt', dict(B)),
    'sleep':      ('rcfg_touch_user_plain.txt', dict(B, sleepEvery=300, sleepMin=1, sleepMax=60)),
    'sleep_pend': ('rcfg_pend_user_plain.txt', dict(B, sleepEvery=300, sleepMin=1, sleepMax=60)),
}


def cfg(name):
    c = ST.read_cfg(RUNS[name][0]); c.update({k: str(v) for k, v in RUNS[name][1].items()})
    c.setdefault('audit', '1')
    return c


def run(name):
    c = cfg(name)
    f = lambda x: os.path.join(OUT, '%s.%s' % (name, x))
    c.update(printLog=f('log'), objDump=f('obj'), objPrefix='SMCA')
    with open(f('cfg'), 'w') as o:
        for k, v in c.items(): o.write('%s %s\n' % (k, v))
    r = subprocess.run([BIN, f('cfg'), os.path.join(HERE, 'm1.bin'), f('csv')], capture_output=True, text=True, cwd=HERE)
    return name, r.returncode, r.stderr.strip().split('\n')[-1]


def objs(name):
    d = {}
    for ln in open(os.path.join(OUT, name + '.obj')):
        f = ln.rstrip('\n').split('\t')
        d[f[0]] = dict(t=int(f[1]), p=float(f[2]), col=int(f[3]), anc=int(f[4]), fs=int(f[5]), text=f[6], tip=f[7].replace('\\n', '\n'))
    return d


def shown(tip):
    """the chart text, worked out here from the steps (63 characters at most)"""
    ln = tip.split('\n'); h = ln[0].find('  HTF'); sg = ln[0][:h] if h > 0 else ln[0]
    st = [x[x.find('  ') + 2:] for x in ln[1:]]
    v = ln[0] + ' | ' + ' > '.join(st)
    if len(v) > 63: v = sg + ' | ' + ' > '.join(st)
    if len(v) > 63: v = sg + ' | ' + st[-1]
    if len(v) > 63: v = v[:60] + '...'
    return v


def colour(st, light):
    P = LIGHT if light else DARK
    for k in ('REFUSED', 'FILLED'):
        if k in st: return P[k]
    if 'CANCELLED' in st or 'SKIPPED' in st: return P['CANCELLED']
    if 'ARMED' in st: return P['ARMED']
    return P['SKIP']


def sep(name, bars):
    c = cfg(name)
    hedge = c.get('dirMode') == '3'; mx = int(c.get('audMax', 200)); light = int(c.get('chartBg', 0)) > 0x7FFFFF
    st, O, H, L, C = bars
    idx = {int(t): i for i, t in enumerate(st)}
    lab = {}; cur = {0: None, 1: None}; order = []
    for ln in open(os.path.join(OUT, name + '.log')):
        # the broker side: an entry skipped (price already past its stop / target) or refused - added to its setup's label
        bk = None
        if ln.startswith('PRINT Entry ') and ' skipped: the price is already past its stop or target' in ln:
            bk = (ln.split()[2], 'SKIPPED - the price was already past the stop or target')
        elif ln.startswith('PRINT Entry ') and ' REFUSED by the broker: ' in ln:
            bk = (ln.split()[2], 'REFUSED BY THE BROKER - ' + ln.rstrip('\n').split(' REFUSED by the broker: ', 1)[1])
        elif ln.startswith('PRINT Order ') and ' REFUSED by the broker 5 times' in ln:
            bk = (ln.split()[3], 'REFUSED BY THE BROKER (5 times)')
        elif ln.startswith('PRINT Order ') and ' REFUSED by the broker: ' in ln:
            bk = (ln.split()[3], 'REFUSED BY THE BROKER - ' + ln.rstrip('\n').split(' REFUSED by the broker: ', 1)[1])
        if bk:
            tid = bk[0].rstrip('p'); side = 1 if hedge and tid[0] == 'S' else 0
            if cur[side] in lab and lab[cur[side]]['id'] == tid: lab[cur[side]]['steps'].append('?  ' + bk[1])
            continue
        if not ln.startswith('PRINT ['): continue
        body = ln[6:].rstrip('\n')
        who, rest = body[1:body.index(']')], body[body.index(']') + 2:]
        t, msg = rest.split(' ', 1); t = int(t)
        side = 1 if who == 'short side' else 0
        if msg.startswith('CHOCH ') or msg.startswith('BOS '):
            sg, s = msg.split(': ', 1); up = ' up' in sg
            if hedge and (side == 0) != up: continue
            nm = 'SMCA111001_XAUUSD_%d_%d' % (side, t)
            lab[nm] = dict(t=t, up=up, sg=sg, steps=['%d  %s' % (t, s)], id=s.split()[0] if 'ARMED' in s else '')
            order.append(nm)
            if 'ARMED' in s: cur[side] = nm
            # keep the newest N (by candle time)
            tt = sorted(lab[x]['t'] for x in lab)
            if len(tt) > mx:
                cut = tt[len(tt) - mx]
                for x in [x for x in lab if lab[x]['t'] < cut]: del lab[x]
        elif cur[side] in lab:
            lab[cur[side]]['steps'].append('%d  %s' % (t, msg))
    got = objs(name)
    bad = []
    if set(got) != set(lab): bad.append('names: %d labels, expected %d (%d missing, %d extra)' % (len(got), len(lab), len(set(lab) - set(got)), len(set(got) - set(lab))))
    for nm in set(got) & set(lab):
        e, g = lab[nm], got[nm]
        i = idx[e['t']]
        tip = g['tip'].split('\n')
        hd = tip[0]
        if not (hd.startswith(e['sg'] + '  HTF ') and hd.split('  HTF ')[1] in ('up', 'dn', '-', 'off')): bad.append('%s header %r' % (nm, hd))
        if len(tip) - 1 != len(e['steps']) or any(not (a == b or (b.startswith('?  ') and a.split('  ', 1)[1] == b[3:])) for a, b in zip(tip[1:], e['steps'])): bad.append('%s steps %r expected %r' % (nm, tip[1:], e['steps']))
        if g['text'] != shown(g['tip']) or len(g['text']) > 63: bad.append('%s text %r' % (nm, g['text']))
        if g['col'] != colour(e['steps'][-1], light): bad.append('%s colour %d for %r' % (nm, g['col'], e['steps'][-1]))
        px = float(L[i]) if e['up'] else float(H[i])
        if g['t'] != e['t'] or abs(g['p'] - px) > 0.005 or g['anc'] != (0 if e['up'] else 1): bad.append('%s place %d %.2f %d' % (nm, g['t'], g['p'], g['anc']))
        if g['fs'] != SIZE[int(c.get('audSz', 2))]: bad.append('%s size %d' % (nm, g['fs']))
    steps = sum(len(x['steps']) for x in lab.values())
    kinds = {}
    for x in lab.values():
        k = x['steps'][-1].split('  ', 1)[1]
        k = 'FILLED' if 'FILLED' in k else ('CANCELLED' if 'CANCELLED' in k else ('ARMED' if 'ARMED' in k else 'SKIP'))
        kinds[k] = kinds.get(k, 0) + 1
    return len(got), steps, kinds, bad


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if not os.environ.get('NORUN'):
        with Pool(4) as pool:
            for name, rc, err in pool.imap_unordered(run, list(RUNS)):
                print('  ran', name, rc, err)
                if rc != 0: sys.exit(1)
    bars = ST.load_bars(1700000)
    probs = 0
    print('display only (trades with the labels on = off):')
    for a in ('touch', 'pend', 'hedge'):
        same = open(os.path.join(OUT, a + '.csv')).read() == open(os.path.join(OUT, a + '_off.csv')).read()
        print('   %-6s %s' % (a, 'SAME' if same else 'DIFFERENT')); probs += not same
        if len(objs(a + '_off')) != 0: print('   %s_off has labels' % a); probs += 1
    print('restarts (labels at the end = no restarts):')
    for a, b in (('touch_rs', 'touch'), ('hedge_rs', 'hedge')):
        x, y = objs(a), objs(b)
        same = x == y
        print('   %-8s %d labels, %s' % (a, len(x), 'SAME' if same else 'DIFFERENT (%d of %d same)' % (sum(1 for k in x if y.get(k) == x[k]), len(y))))
        probs += not same
        same_t = open(os.path.join(OUT, a + '.csv')).read() == open(os.path.join(OUT, b + '.csv')).read()
        if not same_t: print('   %s trades differ' % a); probs += 1
    print('every label worked out separately from the journal and the bars:')
    for a in ('touch', 'pend', 'hedge', 'light_small_50', 'r3_huge', 'rev_longs', 'sleep', 'sleep_pend'):
        n, steps, kinds, bad = sep(a, bars)
        print('   %-14s %4d labels, %5d steps, last step %s: %s' % (a, n, steps, kinds, 'OK' if not bad else '%d PROBLEMS' % len(bad)))
        for b in bad[:5]: print('      ', b)
        probs += len(bad)
    print('ALL OK' if probs == 0 else 'PROBLEMS: %d' % probs)
