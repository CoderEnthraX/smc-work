# fake MT5 economic calendars for the group 41 tests (UTC times; a holiday at 00:00 UTC of its date)
# columns: utc,utc_text,currency,importance,type,name,exact
import sys, random, datetime as dt
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import usnews
from zoneinfo import ZoneInfo
NY = ZoneInfo('America/New_York')
def txt(u): return dt.datetime.fromtimestamp(u, dt.timezone.utc).strftime('%Y.%m.%d %H:%M')
def basic():
    out = []
    d = dt.date(2020, 1, 1)
    while d <= dt.date(2026, 12, 31):
        for nm, T in usnews.releases(d.year, d.month, d.day): out.append((T, 'USD', 3, 1, nm, 1))
        d += dt.timedelta(days=1)
    return out
def rich(seed=7):
    rnd = random.Random(seed)
    out = basic()
    d = dt.date(2020, 1, 1)
    while d <= dt.date(2026, 12, 31):
        if d.weekday() < 5:
            r = rnd.random()
            if r < 0.35:   # a medium-impact US release at 10:00 or 14:00 New York
                hh = rnd.choice((10, 14)); out.append((int(dt.datetime(d.year, d.month, d.day, hh, 0, tzinfo=NY).timestamp()), 'USD', 2, 1, 'US medium %d' % hh, 1))
            if r > 0.9:    # a high-impact US item with no exact time (tentative): must be ignored
                out.append((int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp()), 'USD', 3, 0, 'US tentative', 0))
            if 0.5 < r < 0.7:   # low impact: never used
                out.append((int(dt.datetime(d.year, d.month, d.day, 11, 30, tzinfo=NY).timestamp()), 'USD', 1, 1, 'US low', 1))
            if rnd.random() < 0.25:   # EUR high at 09:00 UTC: only when EUR is chosen
                out.append((int(dt.datetime(d.year, d.month, d.day, 9, 0, tzinfo=dt.timezone.utc).timestamp()), 'EUR', 3, 1, 'EUR high', 1))
        d += dt.timedelta(days=1)
    for y in range(2020, 2027):
        def nth(m, wd, n):
            x = dt.date(y, m, 1); c = 0
            while True:
                if x.weekday() == wd:
                    c += 1
                    if c == n: return x
                x += dt.timedelta(days=1)
        for nm, day in (('Columbus Day', nth(10, 0, 2)), ('Veterans Day', dt.date(y, 11, 11)), ('Independence Day', dt.date(y, 7, 4))):
            out.append((int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp()), 'USD', 0, 2, nm, 1))
        out.append((int(dt.datetime(y, 5, 1, tzinfo=dt.timezone.utc).timestamp()), 'EUR', 0, 2, 'Labour Day', 1))
    return out
def write(fn, rows):
    rows = sorted(rows)
    with open(fn, 'w') as f:
        f.write('# fake MT5 calendar for the tests\n')
        for u, cur, imp, typ, nm, ex in rows: f.write('%d,%s,%s,%d,%d,%s,%d\n' % (u, txt(u), cur, imp, typ, nm, ex))
    return rows
if __name__ == '__main__':
    a = write('simcal_basic.csv', basic()); b = write('simcal_rich.csv', rich())
    print(len(a), 'basic rows,', len(b), 'rich rows')
