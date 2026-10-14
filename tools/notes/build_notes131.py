# writes SMC_Structure_v13.1_NOTES.txt = v131_head.txt (with the test results and the checks filled in) + the v13.0 notes
# usage: cd tools/notes && python3 build_notes131.py
R = '/home/user/smc-work/'
h = open('v131_head.txt').read()
for key, fn in (('{RESULTS}', 'v131_results.txt'), ('{RSIRESULTS}', 'v131_rsires.txt'), ('{EMARESULTS}', 'v131_emares.txt'), ('{CHECKS}', 'v131_checks.txt')):
    assert h.count(key) == 1, key
    h = h.replace(key, open(fn).read().rstrip('\n'))
bad = [(i + 1, len(l)) for i, l in enumerate(h.split('\n')) if len(l) > 78]
assert not bad, bad
old = open(R + 'SMC_Structure_v13.0_NOTES.txt').read()
out = h + old
assert all(ord(c) < 128 for c in out) and '\t' not in out
open(R + 'SMC_Structure_v13.1_NOTES.txt', 'w').write(out)
print('written', len(out.split('\n')), 'lines')
