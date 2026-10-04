# group 41 step A: the EA saves the fake MT5 calendar to the file (live chart, end of the data) - check every line in Python
import subprocess, os, datetime as dt, pickle
from cmp import cfg_of
U = {'slbuf':1.0,'wkHr':23,'pb':25.0,'bosMode':'Cancel','seqMax':1e5,'capAct':'Clamp','lev':500.0,'rev':False,'eq0':1e6}
N = len(pickle.load(open('fx.pkl', 'rb')))
def export(tag, calMode, cur):
    d = 'simfiles_%s/' % tag
    os.makedirs(d, exist_ok=True)
    if os.path.exists(d + 'SMC_calendar.csv'): os.remove(d + 'SMC_calendar.csv')
    c = cfg_of(U, 60); c.update({'tester': 0, 'calSave': 1, 'calOn': 0, 'simCal': 'simcal_rich.csv', 'calMode': calMode, 'calCur': cur, 'fileDir': d,
                                 'from': N - 5000, 'warm': 3000, 'initOnly': 1})
    with open('xcfg_%s.txt' % tag, 'w') as f:
        for k, v in c.items(): f.write('%s %s\n' % (k, int(v) if isinstance(v, bool) else v))
    r = subprocess.run(['./simmain', 'xcfg_%s.txt' % tag, 'm1.bin', 'x_%s.csv' % tag], capture_output=True, text=True)
    return d + 'SMC_calendar.csv', r.stderr.strip()
def expect(cur, now_utc):
    out = []
    curs = cur.split(',')
    for line in open('simcal_rich.csv'):
        if line.startswith('#'): continue
        f = line.strip().split(',')
        u, c, imp, typ, ex = int(f[0]), f[2], int(f[3]), int(f[4]), f[6] != '0'
        if c not in curs or u < 1577836800 - 3 * 3600 or u > now_utc + 60 * 86400 + 3 * 3600: continue
        if typ == 2 or (imp >= 2 and ex): out.append((u, c, imp, typ, f[5]))
    return sorted(out)
def got(fn):
    out, head = [], []
    for line in open(fn):
        line = line.rstrip('\r\n')
        if line.startswith('#'): head.append(line); continue
        f = line.split(',')
        assert dt.datetime.fromtimestamp(int(f[0]), dt.timezone.utc).strftime('%Y.%m.%d %H:%M') == f[1], line
        out.append((int(f[0]), f[2], int(f[3]), int(f[4]), f[5]))
    return out, head
ok = True
for tag, mode, cur in (('rule_usd', 0, 'USD'), ('now_usd', 1, 'USD'), ('rule_usdeur', 0, 'usd,EUR,'), ('now_eur', 1, 'EUR')):
    fn, err = export(tag, mode, cur)
    a, head = got(fn)
    saved = int([h for h in head if h.startswith('#saved,')][0].split(',')[1])
    e = expect(cur.upper().replace(' ', '').strip(','), saved)
    # the file must hold exactly these, in time order; the last day (now + 60 days) may cut at a different minute: compare up to now + 59 days
    lim = saved + 59 * 86400
    a2 = [x for x in a if x[0] < lim]; e2 = [x for x in e if x[0] < lim]
    same = a2 == sorted(a2) == e2
    ok &= same
    print('%-12s calendar clock %-28s %5d lines (%d expected) %s | %s' % (tag, 'rule' if mode == 0 else 'offset of the moment', len(a2), len(e2), 'SAME' if same else 'DIFFER', head[0][-60:]))
    if not same:
        sa, se = set(a2), set(e2)
        print('   only in file:', sorted(sa - se)[:3], ' only expected:', sorted(se - sa)[:3])
print('ALL SAME' if ok else 'SOME DIFFER')
