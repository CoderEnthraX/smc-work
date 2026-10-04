# group 41 rules worked out SEPARATELY in Python (not from the EA code): which bars are inside a calendar news window /
# holiday (close + block, like group 25 / 29) and which bars get 'no new trades before news' (block new entries only).
# A bar decides at its close tc for the next bar [tc, tc + bar): window = that bar touches [T - pre, T + post);
# before news = it touches [T - hours, T); holiday = the New York date at tc (or at the end of the next bar) is a holiday.
import bisect, datetime as dt, sys
from zoneinfo import ZoneInfo
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import usnews
NY = ZoneInfo('America/New_York')
def load(fn, cur='USD', imp2=3):
    news, hol = [], set()
    for line in open(fn):
        if line.startswith('#'): continue
        f = line.strip().split(',')
        if f[2] != cur: continue
        u, imp, typ = int(f[0]), int(f[3]), int(f[4]); ex = f[6] != '0' if len(f) > 6 else True
        if typ == 2: hol.add(dt.datetime.fromtimestamp(u, dt.timezone.utc).date())
        elif imp >= imp2 and ex: news.append(u)
    return sorted(set(news)), hol
def easter(y):   # Meeus / Jones / Butcher
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    return dt.date(y, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)
def rule_hol(d): return usnews.usHol(d.year, d.month, d.day) != '' or d == easter(d.year) - dt.timedelta(days=2)
def all_au():   # every group 29 release (NFP, claims, ISM M, ISM S), 2020-2026
    out = []; d = dt.date(2020, 1, 1)
    while d <= dt.date(2026, 12, 31):
        out += [T for _, T in usnews.releases(d.year, d.month, d.day)]; d += dt.timedelta(days=1)
    return sorted(out)
def touch(lst, a, b):   # does any T in the sorted list lie in (a, b)?
    i = bisect.bisect_right(lst, a); return i < len(lst) and lst[i] < b
def flags(bars, cs=60, cal=None, calPre=10, calPost=20, hol=None, ruleHol=False, au=None, auPre=10, auPost=20, preList=None, preH=0.0):
    """cal / au: sorted release times (windows); preList: sorted times for 'no new trades before news'"""
    NEWS, PRE = [], []
    for b in bars:
        tc = b[0] + cs
        w = False
        # window: tc < T + post and tc + cs > T - pre  <=>  T in (tc - post, tc + cs + pre)
        if cal is not None and touch(cal, tc - calPost * 60, tc + cs + calPre * 60): w = True
        if au is not None and not w and touch(au, tc - auPost * 60, tc + cs + auPre * 60): w = True
        if hol is not None or ruleHol:
            d0 = dt.datetime.fromtimestamp(tc, NY).date(); d1 = dt.datetime.fromtimestamp(tc + cs - 1, NY).date()
            isH = lambda d: (hol is not None and d in hol) or (ruleHol and rule_hol(d))
            if isH(d0) or (d1 != d0 and isH(d1)): w = True
        NEWS.append(w)
        # before news: tc < T and tc + cs > T - H  <=>  T in (tc, tc + cs + H)
        PRE.append(preList is not None and preH > 0 and touch(preList, tc, tc + cs + int(round(preH * 3600))))
    return NEWS, PRE
