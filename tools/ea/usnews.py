# v11.1 group 29 'Automatic US news windows' worked out exactly like the Pine code (f_usHol, f_nfp, f_bday, f_auDay), New York clock with US summer time
import datetime as dt
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
def dow(y, m, d): return (dt.date(y, m, d).weekday() + 1) % 7 + 1          # Pine: 1 = Sunday ... 7 = Saturday
def addD(y, m, d, n): x = dt.date(y, m, d) + dt.timedelta(days=n); return x.year, x.month, x.day
def nthDow(y, m, w, n): return 1 + (w - dow(y, m, 1) + 7) % 7 + 7 * (n - 1)
def lastDow(y, m, w):
    L = 31 if m == 12 else (dt.date(y, m + 1, 1) - dt.timedelta(days=1)).day
    return L - (dow(y, m, L) - w + 7) % 7
def obs(y, M, D, m, d):
    w = dow(y, M, D); return m == M and d == (D - 1 if w == 7 else D + 1 if w == 1 else D)
def usHol(y, m, d, gf=False):
    if m == 1 and ((d == 1 and dow(y, 1, 1) not in (1, 7)) or (d == 2 and dow(y, 1, 1) == 1)): return "New Year"
    if m == 1 and d == nthDow(y, 1, 2, 3): return "MLK"
    if m == 2 and d == nthDow(y, 2, 2, 3): return "Presidents"
    if m == 5 and d == lastDow(y, 5, 2): return "Memorial"
    if y >= 2022 and obs(y, 6, 19, m, d): return "Juneteenth"
    if obs(y, 7, 4, m, d): return "Independence"
    if m == 9 and d == nthDow(y, 9, 2, 1): return "Labor"
    if m == 11 and d == nthDow(y, 11, 5, 4): return "Thanksgiving"
    if obs(y, 12, 25, m, d): return "Christmas"
    return ""
def nfp(y, m):
    py, pm = (y - 1, 12) if m == 1 else (y, m - 1)
    ry, rm, rd = addD(py, pm, 12 + (7 - dow(py, pm, 12)) % 7, 20)
    if rm == 1 and rd <= 3: ry, rm, rd = addD(ry, rm, rd, 7)
    if usHol(ry, rm, rd): ry, rm, rd = addD(ry, rm, rd, -1)
    return ry, rm, rd
def bday(y, m, d):
    n = 0
    if d <= 10 and dow(y, m, d) not in (1, 7) and usHol(y, m, d) == "":
        for k in range(1, d + 1):
            if dow(y, m, k) not in (1, 7) and usHol(y, m, k) == "": n += 1
    return n
def releases(y, m, d):
    out = []
    if nfp(y, m) == (y, m, d): out.append(("NFP", 8, 30))
    ty, tm, td = addD(y, m, d, 1); w = dow(y, m, d)
    if (w == 5 and usHol(y, m, d) == "") or (w == 4 and usHol(ty, tm, td) != ""): out.append(("Jobless claims", 8, 30))
    bd = bday(y, m, d); sh = 1 if m == 1 else 0
    if bd == 1 + sh: out.append(("ISM Manufacturing", 10, 0))
    if bd == 3 + sh: out.append(("ISM Services", 10, 0))
    return [(nm, int(dt.datetime(y, m, d, hh, mm, tzinfo=NY).timestamp())) for nm, hh, mm in out]
def blocked(bars, pre=10, post=20, bar_sec=60):
    """True for every bar whose close falls in a window (Pine f_auHit: close < T + post and close + bar > T - pre), on the NY date of the bar close"""
    cache = {}; out = []
    for b in bars:
        tc = b[0] + bar_sec; nyd = dt.datetime.fromtimestamp(tc, NY).date()
        if nyd not in cache: cache[nyd] = [T for _, T in releases(nyd.year, nyd.month, nyd.day)]
        out.append(any(tc < T + post * 60 and tc + bar_sec > T - pre * 60 for T in cache[nyd]))
    return out
if __name__ == "__main__":
    for y, m in ((2024, 3), (2024, 7), (2025, 1), (2025, 7), (2026, 1), (2026, 9)):
        print("NFP", y, m, nfp(y, m), "| first days:", [(d, [n for n, _ in releases(y, m, d)]) for d in range(1, 8) if releases(y, m, d)])
