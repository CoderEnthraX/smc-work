# v15.0 'no RSI / EMA filters' TradingView file (the user asked for two files: the complete one and one without the RSI and EMA
# filters of section 4). Takes the complete v15.0 text and removes ONLY the 4 RSI / EMA filters: their 20 settings (section 4),
# the values they read (6 request.security calls), their 4 checks in the setup filter chain, their counters and their table
# texts. Everything else is the same text as the complete file.
# usage: imported by pine150.py (strip(s) -> s)
import re


def _cut_term(s, start):
    """remove every ' + (start ... )' term of a string sum (balanced brackets, strings skipped)"""
    while True:
        k = s.find(' + ' + start)
        if k < 0: return s
        i = k + 3
        d = 0; q = False; j = i
        while j < len(s):
            c = s[j]
            if q:
                if c == '\\': j += 2; continue
                if c == '"': q = False
            elif c == '"': q = True
            elif c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: break
            j += 1
        s = s[:k] + s[j + 1:]


def strip(s):
    L = s.split('\n')
    a = [i for i, l in enumerate(L) if l.startswith('stRsLOn  = input.bool(')]
    b = [i for i, l in enumerate(L) if l.startswith('stEmHFast = input.int(')]
    assert len(a) == 1 and len(b) == 1 and b[0] - a[0] == 19, 'lite: the 20 RSI / EMA inputs'
    del L[a[0]:b[0] + 1]
    a = [i for i, l in enumerate(L) if l == '// the timeframe of an RSI / EMA filter; a timeframe not above the chart = the chart\'s own candles']
    b = [i for i, l in enumerate(L) if l.startswith('float stEmHf = ')]
    assert len(a) == 1 and len(b) == 1 and b[0] > a[0], 'lite: the RSI / EMA values'
    del L[a[0]:b[0] + 1]
    for k in (4, 5, 6, 7):
        n = len(L)
        L = [l for l in L if l != 'var int stCntX%d = 0' % k]
        assert len(L) == n - 1, 'lite: counter %d' % k
    # the 4 checks of the filter chain (each: else if ... / _xs := ... / stCntXk += 1)
    for head in ('            else if stRsLOn and ', '            else if stRsHOn and ', '            else if stEmLOn and ', '            else if stEmHOn and '):
        i = [j for j, l in enumerate(L) if l.startswith(head)]
        assert len(i) == 1 and L[i[0] + 1].startswith('                _xs := ') and re.match(r'^ {16}stCntX[4-7] \+= 1$', L[i[0] + 2]), 'lite: ' + head
        del L[i[0]:i[0] + 3]
    s = '\n'.join(L)
    for t in ('(stRsLOn ? ', '(stRsHOn ? ', '(stEmLOn ? ', '(stEmHOn ? '):
        n = s.count(' + ' + t)
        assert n == 2, 'lite: table term %s found %d x' % (t, n)
        s = _cut_term(s, t)
    s = s.replace('// ---- v13.1 (section 4): the New York trading day and the RSI / EMA filters - the same rules as the MT5 EA v13.1',
                  '// ---- v13.1 (section 4): the New York trading day - the same rules as the MT5 EA v13.1 (this file: no RSI / EMA filters)')
    for w in ('stRs', 'stEm', '_rsL', '_rsH', '_emL', '_emH', 'f_xRsOk', 'f_xTfTxt', 'f_xUp', 'f_xTf(', 'stCntX4', 'stCntX5', 'stCntX6', 'stCntX7', 'ta.rsi', 'ta.ema'):
        assert w not in s, 'lite: %s left' % w
    return s
