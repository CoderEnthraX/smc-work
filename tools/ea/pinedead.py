# v15.1: the internal (second) swing tracker removed from f_tfPack (the higher timeframe function) was dead code. This checks it:
#   1. every line of the v15.0 f_tfPack that v15.1 dropped assigns (=, :=, +=, method call on an object, array.push ...) only
#      names that NO kept line reads;
#   2. the SwingTracker methods those lines called write only the tracker's own fields (t.<field>) and their locals - nothing shared.
# usage: python3 pinedead.py SMC_Structure_Strategy_v15.0.txt SMC_Structure_Strategy_v15.1.txt
import re, sys

NAME = re.compile(r'(?<![\w.])([A-Za-z_]\w*)')


def strip(l):
    out, q = [], False
    i = 0
    while i < len(l):
        c = l[i]
        if q:
            if c == '\\': i += 2; continue
            if c == '"': q = False
        elif c == '"': q = True
        elif l.startswith('//', i): break
        else: out.append(c)
        i += 1
    return ''.join(out).rstrip()


def func(path, head):
    L = open(path).read().split('\n')
    a = [i for i, l in enumerate(L) if l.startswith(head)]
    assert len(a) == 1, head
    b = a[0] + 1
    while b < len(L) and (L[b].startswith(' ') or not L[b].strip()): b += 1
    return [strip(l) for l in L[a[0] + 1:b] if strip(l).strip()]


def assigned(l):
    s = l.strip()
    m = re.match(r'^(?:var\s+)?(?:\w+(?:<[\w<>]+>)?\s+)?([A-Za-z_]\w*)\s*(?::=|=|\+=|-=)(?!=)', s)
    if m: return {m.group(1)}
    m = re.match(r'^\[([^\]]*)\]\s*=', s)
    if m: return {x.strip() for x in m.group(1).split(',')}
    m = re.match(r'^([A-Za-z_]\w*)\.(\w+)\s*(?::=|=)', s)                 # obj.field := ...
    if m: return {m.group(1)}
    m = re.match(r'^([A-Za-z_]\w*)\.(armHere|update|rearm)\(', s)          # method call on an object
    if m: return {m.group(1)}
    m = re.match(r'^array\.(push|shift|set|remove|insert|pop|clear)\(([A-Za-z_]\w*)', s)
    if m: return {m.group(2)}
    return set()


def reads(l):
    s = re.sub(r'"[^"]*"', '""', l)
    m = re.match(r'^\s*(?:var\s+)?(?:\w+(?:<[\w<>]+>)?\s+)?[A-Za-z_]\w*\s*(?::=|=|\+=|-=)(?!=)(.*)$', s)
    body = m.group(1) if m else s
    return set(NAME.findall(body))


old = func(sys.argv[1], 'f_tfPack(bool on) =>')
new = func(sys.argv[2], 'f_tfPack(bool on) =>')
ns = set(x.strip() for x in new)
dropped = [l for l in old if l.strip() not in ns]
kept = [l for l in old if l.strip() in ns]
gone = set()
for l in dropped:
    if re.match(r'^\s*(if|else|for|while|break|continue)\b', l) or l.strip().startswith('[trOut'): continue   # the old 4-value return
    a = assigned(l)
    if not a: raise SystemExit('dropped line with no assignment target: ' + l)
    gone |= a
used = set()
for l in kept: used |= reads(l)
# the same names in the new function (it adds tRLoT / tRHiT / tLegT / lgOut, none of them dropped)
for l in new: used |= reads(l)
newasg = set()
for l in new: newasg |= assigned(l)
rewritten = sorted(gone & newasg)        # dropped lines whose names the new function assigns another way (checked by hand)
gone -= newasg
bad = sorted(gone & used)
print('f_tfPack: %d lines dropped, they assign %d names: %s' % (len(dropped), len(gone), ', '.join(sorted(gone))))
print('  rewritten (assigned again by the new lines, same values - see pine151.py): %s' % ', '.join(rewritten))
print('  read by a kept / new line: %s' % (bad or 'NONE'))
# the SwingTracker methods: only t.<field> and their own locals are assigned
src = open(sys.argv[2]).read().split('\n')
ok = True
for head in ('method update(SwingTracker t', 'method rearm(SwingTracker t', 'method armHere(SwingTracker t'):
    body = func(sys.argv[2], head)
    locs = set()
    for l in body:
        s = l.strip()
        m = re.match(r'^(?:\w+\s+)([A-Za-z_]\w*)\s*=(?!=)', s) or re.match(r'^\[([^\]]*)\]\s*=', s)
        if m: locs |= {x.strip() for x in m.group(1).split(',')}
        m = re.match(r'^([A-Za-z_][\w.]*)\s*(?::=|\+=|-=)', s)
        if m and not m.group(1).startswith('t.') and m.group(1) not in locs:
            ok = False; print('  %s writes %s' % (head, m.group(1)))
        if re.search(r'array\.(push|shift|set|remove|insert|pop|clear)\(', s):
            ok = False; print('  %s changes an array: %s' % (head, s))
print('SwingTracker methods write only their own fields / locals: %s' % ('YES' if ok else 'NO'))
print('DEAD CODE CONFIRMED' if not bad and ok else 'NOT DEAD')
