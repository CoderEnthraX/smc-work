# v15.2: the TradingView code of the new settings (the Pine text, translated by pine2py) against the EA core:
#   kz  - the kill zone flag stKzIn (f_dAhead, f_ovl, _tMk, stKzIn; hour / minute on the New York clock emulated with zoneinfo) on
#         the bars of the core's kill zone logs (v152tests.py kz, key kzLog) - every bar must agree
#   set - the C5 / C6 + RSI sets: the values in use (stFstOn ... stHrOff, stMnP) for every set x random boxes = the core's Derive()
#   xt  - the table row 'skipped: section 4 filters' written with the new helper f_xc = the v15.1 text, random states
# usage: NEWPINE=<file> OLDPINE=<file> python3 pinekz152.py
import os, sys, random, datetime
import numpy as np
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__))
import pine2py as P

NEW = os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.2.txt')
OLD = os.environ.get('OLDPINE', HERE + '/../../SMC_Structure_Strategy_v15.1.txt')


def item(text, start, n=1):
    L = text.split('\n')
    k = [i for i, l in enumerate(L) if l.startswith(start)]
    assert len(k) == 1, start
    its = P.split_items(text, k[0] + 1, k[0] + 40)[:n]
    return ['\n'.join(P.translate(it, [])) for it in its]


class NS: pass


def env():
    g = {}
    tz = {}
    def loc(t, z):
        if z not in tz: tz[z] = ZoneInfo(z)
        return datetime.datetime.fromtimestamp(t / 1000.0, tz[z])
    g['hour'] = lambda t, z: loc(t, z).hour
    g['minute'] = lambda t, z: loc(t, z).minute
    g['na'] = lambda x: x is None
    st = NS(); st.tostring = lambda x, *a: repr(x); st.substring = lambda s, a, b=None: s[a:b]
    st.startswith = lambda s, p: s.startswith(p)
    g['str'] = st
    return g


def kz_check():
    text = open(NEW).read()
    g = env()
    for src in item(text, 'f_dAhead(int t, int a) =>') + item(text, 'f_ovl(int t, int len, int a, int b) =>'):
        exec(compile(src, NEW, 'exec'), g)
    code = compile('\n'.join(item(text, 'int  _tMk = ', 2)), NEW, 'exec')
    import v152tests as V
    tot = bad = 0
    for name, Pp, extra, cs in V.KZ:
        log = os.path.join(HERE, 'x152_kz_%s.kz' % name)
        if not os.path.exists(log): print('   run "python3 v152tests.py kz" first'); return False
        rows = [ln.strip().split(',') for ln in open(log)]
        if cs == 60: rows = rows[::7]           # every 7th 1-minute bar (about 290,000 per setting)
        g.update(stKzOn=bool(int(extra.get('kzOn', 0))), _nyTz='America/New_York', _stCs=cs, _bMin=max(1, cs // 60))
        for k in V.ZW: g['st' + k[0].upper() + k[1:]] = bool(int(extra.get(k, V.ZD[k])))
        n = b = 0
        for bi, t, f in rows:
            g['time_close'] = (int(t) + cs) * 1000
            exec(code, g)
            n += 1
            if bool(g['stKzIn']) != (f == '1'):
                b += 1
                if b <= 3: print('   %s bar %s: pine %s core %s' % (name, bi, g['stKzIn'], f))
        tot += n; bad += b
        print('kz %-22s %7d bars: %s' % (name, n, 'PINE = CORE' if b == 0 else '%d DIFFER' % b), flush=True)
    return bad == 0 and tot > 0


def set_check():
    text = open(NEW).read()
    L = text.split('\n')
    a = [i for i, l in enumerate(L) if l.startswith('bool   stFstOn   = ')][0]
    src = '\n'.join(P.translate([(0, l.strip()) for l in L[a:a + 10]], []))
    src += '\n' + '\n'.join(P.translate([(0, [l for l in L if l.startswith('var float stMnP = ')][0].replace('var float ', 'float '))], []))
    code = compile(src, NEW, 'exec')
    rnd = random.Random(5)
    n = bad = 0
    for case in range(3000):
        c5, c6 = [(False, False), (True, False), (False, True)][case % 3]
        raw = dict(stFstOnI=rnd.random() < 0.5, stYdOnI=rnd.random() < 0.5, stLegMinI=rnd.randint(0, 30), stRsHOnI=rnd.random() < 0.5,
                   stRsHTfI=rnd.choice(['1 minute', '15 minutes', '1 hour', '1 day']), stRsHLenI=rnd.randint(1, 30),
                   stRsHModeI=rnd.choice(['Pullback: buy when RSI is BELOW', 'Momentum: buy when RSI is ABOVE']), stRsHLvlI=float(rnd.randint(0, 100)),
                   stHrOnI=rnd.randint(0, 23), stHrOffI=rnd.randint(0, 23), stMnPct=round(rnd.random() * 2, 2), stX1m=rnd.random() < 0.2)
        g = dict(raw, stC5=c5, stC6=c6)
        exec(code, g)
        # the core's Derive(): the sets, then the 1-minute-only switch (x1m) zeroes the min stop %
        e = dict(fst=raw['stFstOnI'], yd=raw['stYdOnI'], leg=raw['stLegMinI'], rsOn=raw['stRsHOnI'], rsTf=raw['stRsHTfI'], rsLen=raw['stRsHLenI'],
                 rsPull=raw['stRsHModeI'].startswith('Pullback'), rsLvl=raw['stRsHLvlI'], hrOn=raw['stHrOnI'], hrOff=raw['stHrOffI'], mn=raw['stMnPct'])
        if c5: e.update(mn=0.5, fst=True, yd=True, leg=12)
        if c6: e.update(hrOn=13, hrOff=21, mn=0.35, yd=True, leg=12, rsOn=True, rsTf='1 hour', rsLen=2, rsPull=True, rsLvl=50.0)
        if raw['stX1m']: e['mn'] = 0.0
        got = dict(fst=g['stFstOn'], yd=g['stYdOn'], leg=g['stLegMin'], rsOn=g['stRsHOn'], rsTf=g['stRsHTf'], rsLen=g['stRsHLen'],
                   rsPull=g['stRsHMode'].startswith('Pullback'), rsLvl=g['stRsHLvl'], hrOn=g['stHrOn'], hrOff=g['stHrOff'], mn=g['stMnP'])
        n += 1
        if got != e:
            bad += 1
            if bad <= 3: print('   c5 %s c6 %s: pine %s | core %s' % (c5, c6, got, e))
    print('set %d cases (none / C5 / C6 x random boxes): %s' % (n, 'PINE = CORE' if bad == 0 else '%d DIFFER' % bad))
    return bad == 0


def xt_check():
    def line(path, start):
        L = open(path).read().split('\n')
        k = [l for l in L if l.strip().startswith(start)]
        assert len(k) == 1, start
        return k[0].strip()
    old = line(OLD, 'string _xT = '); new = line(NEW, 'string _xT = ')
    text = open(NEW).read()
    g = env()
    g['f_xTfTxt'] = lambda tf: 'TF<' + tf + '>'
    g['f_unTxt'] = lambda u: ' U' + str(u)
    exec(compile(item(text, 'f_xc(bool on, string t, int n) =>')[0], NEW, 'exec'), g)
    co = compile(P.translate([(0, old)], [])[0], OLD, 'exec')
    cn = compile(P.translate([(0, new)], [])[0], NEW, 'exec')
    rnd = random.Random(9)
    n = bad = 0
    for case in range(5000):
        st = dict(stFstOn=rnd.random() < 0.5, stYdOn=rnd.random() < 0.5, stLegMin=rnd.choice([0, 0, 5, 12]), stTdOn=rnd.random() < 0.5,
                  stRsLOn=rnd.random() < 0.5, stRsHOn=rnd.random() < 0.5, stEmLOn=rnd.random() < 0.5, stEmHOn=rnd.random() < 0.5,
                  stMnP=rnd.choice([0.0, 0.0, 0.35, 0.5]), stLzN=rnd.choice([0.0, 3.5]), stLzX=rnd.choice([0.0, 30.0]), stBcE=rnd.choice([0.0, 10.0]),
                  stRsLTfS='15', stRsHTfS='60', stEmLTfS='5', stEmHTfS='240', stULz=rnd.randint(0, 2), stUBc=rnd.randint(0, 2))
        for i in range(12): st['stCntX%d' % i] = rnd.randint(0, 999)
        g.update(st)
        exec(co, g); a = g['_xT']
        exec(cn, g); b = g['_xT']
        n += 1
        if a != b:
            bad += 1
            if bad <= 3: print('   old %r\n   new %r' % (a, b))
    print('xt %d random states: the new table text %s' % (n, '= the v15.1 text' if bad == 0 else '%d DIFFER' % bad))
    return bad == 0


if __name__ == '__main__':
    ok = kz_check() & set_check() & xt_check()
    print('ALL PINE = CORE' if ok else 'SOME DIFFER')
