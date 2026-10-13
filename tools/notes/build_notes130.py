# writes SMC_Structure_v13.0_NOTES.txt = v130_head.txt + the settings map (worked out from the v12.2 / v12.3 and v13.0 files)
# + v130_tail.txt (with the check results) + the v12.0 TradingView notes + the v12.0 EA notes
# usage: cd tools/notes && python3 build_notes130.py "<checks text file>"
import re, sys, os
R = '/home/user/smc-work/'


def tv(fn):
    L = open(R + fn).read().split('\n')
    gv = {}
    for l in L:
        m = re.match(r'^(g\w+)\s*=\s*"([^"]*)"\s*$', l)
        if m: gv[m.group(1)] = m.group(2)
    out = {}
    for l in L:
        m = re.match(r'^(\w+)\s*=\s*input\.(\w+)\((.*)$', l)
        if not m: continue
        g = re.search(r'group = (\w+)', l).group(1)
        strs = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(3))
        t = m.group(2)
        lab = '  - window time' if t == 'session' else (strs[1] if t in ('string', 'time') else strs[0])
        out[m.group(1)] = (gv[g], lab)
    return out


def ea(fn):
    out = {}; grp = None
    for l in open(R + fn):
        m = re.match(r'^input group "([^"]*)"', l)
        if m: grp = m.group(1); continue
        m = re.match(r'^input\s+\w+\s+(\w+)\s*=.*?//\s*(.*)$', l)
        if m: out[m.group(1)] = (grp, m.group(2).strip())
    return out


def num(g):
    m = re.match(r'^(\d+)\.', g)
    return m.group(1) if m else 'eng'


def emit(title, new, old):
    o = [title]
    sec = None
    for k, (g, lab) in new.items():
        if g != sec:
            sec = g; o.append(''); o.append('  ' + g.split(' - ')[0].upper())
        lab = re.sub(r' +', ' ', lab).strip()
        if lab.startswith('- '): lab = '  ' + lab
        lab = lab if len(lab) <= 62 else lab[:59] + '...'
        o.append('    %-62s %s' % (lab, ('was ' + num(old[k][0])) if k in old else 'NEW'))
    return o


lines = open('v130_head.txt').read().rstrip('\n').split('\n')
lines += emit('TRADINGVIEW - 136 settings', tv('SMC_Structure_Strategy_v13.0.txt'), tv('SMC_Structure_Strategy_v12.2.txt'))
lines += ['', '    gone: "stop buffer in pips", "stop buffer in % of price" (old group 38)',
          '          - now the one stop buffer box in section 5', '']
lines += emit('MT5 EA - 154 settings', ea('SMC_Structure_EA_v13.0.mq5'), ea('SMC_Structure_EA_v12.3.mq5'))
lines += ['', '    gone: InBuPips, InBuPct (old group 38) - now the one box InSlBuf',
          '    NEW:  InHgBase (section 3, the hedge option of part 5)']
tail = open('v130_tail.txt').read().replace('{CHECKS}', open(sys.argv[1]).read().rstrip('\n'))
lines += tail.rstrip('\n').split('\n')
new = '\n'.join(lines)
long_ = [l for l in new.split('\n') if len(l) > 78]
if long_: raise SystemExit('lines over 78: %s' % long_[:3])
old = open(R + 'SMC_Structure_Strategy_v12.0_NOTES.txt').read().rstrip('\n') + '\n\n\n' + open(R + 'SMC_Structure_EA_v12.0_NOTES.txt').read()
out = new + '\n' + old
for ch in out:
    if ord(ch) > 126 or (ord(ch) < 32 and ch not in '\n'): raise SystemExit('not ASCII / tab: %r' % ch)
open(R + 'SMC_Structure_v13.0_NOTES.txt', 'w').write(out)
print('written', len(out.split('\n')), 'lines (new part', len(new.split('\n')), ')')
