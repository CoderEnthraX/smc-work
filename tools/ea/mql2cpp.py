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
    m = re.match(r'^(\s*)(\w+)(\s+)((?:\w+\[\]\s*,\s*)*\w+\[\])\s*;(.*)$', line)
    if m and m.group(2) not in ('return', 'else'):
        names = [n.strip()[:-2] for n in m.group(4).split(',')]
        line = '%sMqlArr<%s> %s;%s' % (m.group(1), m.group(2), ', '.join(names), m.group(5))
    out.append(line)
open(sys.argv[2], 'w').write('\n'.join(out))
