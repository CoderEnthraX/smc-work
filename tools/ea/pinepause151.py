# v15.1: the TradingView every-other-day test f_ldAlt (the Pine text, translated by pine2py; Pine's time functions emulated with the
# session timezone) against the EA's AltHalt rule (MT5 day of week 1 = Sunday .. 7 = Saturday, days since 1970 in the session
# timezone): many start days x every candle hour of the following 30 days x skip 1..4 x Monday-Friday / every day
# usage: NEWPINE=<file> python3 pinepause151.py [timezone, default Asia/Kolkata]
import sys, os, datetime, random
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__))
import pine2py as P
import pinerun as R

PINE = os.environ.get('NEWPINE', HERE + '/../../SMC_Structure_Strategy_v15.1.txt')
TZ = sys.argv[1] if len(sys.argv) > 1 else 'Asia/Kolkata'


def load():
    g = R.mk_env({})
    z = ZoneInfo(TZ)
    loc = lambda t, tz: datetime.datetime.fromtimestamp(t / 1000.0, ZoneInfo(tz))
    g['year'] = lambda t, tz=TZ: loc(t, tz).year
    g['month'] = lambda t, tz=TZ: loc(t, tz).month
    g['dayofmonth'] = lambda t, tz=TZ: loc(t, tz).day
    g['dayofweek'] = lambda t, tz=TZ: (loc(t, tz).isoweekday() % 7) + 1          # Pine: 1 = Sunday .. 7 = Saturday
    dw = R.NS(); dw.sunday, dw.saturday = 1, 7
    g['dayofweek'].saturday = 7
    g['timestamp'] = lambda tz, y, m, d, hh, mm: int(datetime.datetime(y, m, d, hh, mm, tzinfo=ZoneInfo(tz)).timestamp() * 1000)
    g['na'] = lambda x: x is None
    g['stTz'] = TZ
    import math as _m
    g['math'].floor = _m.floor
    text = open(PINE).read()
    text = text.replace('dayofweek.saturday', '7').replace('dayofweek.sunday', '1')
    L = text.split('\n')
    k = [i for i, l in enumerate(L) if l.startswith('f_ldAlt(int t) =>')][0] + 1
    it = P.split_items(text, k, k + 18)[:1]
    exec(compile('\n'.join(P.translate(it[0], [])), PINE, 'exec'), g)
    return g


def alt_ea(t_ms, altD, skip, all7):
    """the EA's AltHalt: dn = days since 1970 of the session-local date"""
    loc = datetime.datetime.fromtimestamp(t_ms / 1000.0, ZoneInfo(TZ))
    dn = (datetime.date(loc.year, loc.month, loc.day) - datetime.date(1970, 1, 1)).days
    dow = lambda d: (d + 4) % 7 + 1
    if dn <= altD: return True
    if not all7 and dow(dn) in (1, 7): return True
    full, rem = (dn - altD) // 7, (dn - altD) % 7
    m = full * (7 if all7 else 5)
    for k in range(1, rem + 1):
        if all7 or dow(altD + full * 7 + k) not in (1, 7): m += 1
    return m % (skip + 1) != 0


if __name__ == '__main__':
    g = load()
    rnd = random.Random(7)
    n = bad = blocked = 0
    for case in range(400):
        altD = rnd.randint(18600, 20700)                     # 2020 .. 2026
        skip = rnd.randint(1, 4)
        all7 = rnd.random() < 0.3
        base = altD * 86400000
        for h in range(0, 30 * 24, 3):
            t = base + h * 3600000 + rnd.randint(0, 59) * 60000
            g.update(stLdAlt=True, stLdAltD=altD, stLdSkip=skip, stCls=4 if all7 and rnd.random() < 0.5 else 2, stWk247=all7)
            if all7 and g['stCls'] == 4: g['stWk247'] = False   # crypto (class 4) = every day too, like 24/7
            p = g['f_ldAlt'](t)
            e = alt_ea(t, altD, skip, all7)
            n += 1; blocked += e
            if p != e:
                bad += 1
                if bad <= 5: print('   t %d altD %d skip %d all %s: pine %s | EA %s' % (t, altD, skip, all7, p, e))
    print('f_ldAlt (%s): %d times, %d blocked: %s' % (TZ, n, blocked, 'PINE = EA' if bad == 0 else '%d DIFFER' % bad))
