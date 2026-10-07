# turn the .mq5 into C++ that compiles against mt5sim.h (a check of the WHOLE file, not only the core)
import re, sys, datetime
src = open(sys.argv[1]).read()
out = []
for line in src.split('\n'):
    if line.startswith('#property'): continue
    if line.startswith('#include <Trade\\Trade.mqh>'): out.append('#include "mt5sim.h"'); continue
    if line.startswith('input group'): continue
    if line.startswith('input '): line = line[6:]
    def dt(m):
        d = datetime.datetime.strptime(m.group(1), '%Y.%m.%d %H:%M').replace(tzinfo=datetime.timezone.utc)
        return str(int(d.timestamp()))
    line = re.sub(r"D'([0-9.]+ [0-9:]+)'", dt, line)
    line = re.sub(r"C'(\d+),(\d+),(\d+)'", lambda m: '((color)(%s | (%s << 8) | (%s << 16)))' % (m.group(1), m.group(2), m.group(3)), line)
    line = re.sub(r'\b(\w+) &(\w+)\[\]', r'MqlArr<\1> &\2', line)   # an array parameter: MqlRates &rr[]
    m = re.match(r'^(\s*)(\w+)(\s+)((?:\w+\[\]\s*,\s*)*\w+\[\])\s*;(.*)$', line)
    if m and m.group(2) not in ('return', 'else'):
        names = [n.strip()[:-2] for n in m.group(4).split(',')]
        line = '%sMqlArr<%s> %s;%s' % (m.group(1), m.group(2), ', '.join(names), m.group(5))
    out.append(line)
# a test hook: the fake MT5 sees every check of the v12.3 catch-up (the book is read by simmain, nothing is changed)
for i, l in enumerate(out):
    if l.startswith('int DropReached(double hi, double lo, datetime when)') and out[i + 1] == '{':
        out[i + 1] = '{ if (sim::onDrop) sim::onDrop(hi, lo, when);'
open(sys.argv[2], 'w').write('\n'.join(out))
