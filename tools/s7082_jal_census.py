#!/usr/bin/env python3
"""s7082: classify every N64Recomp 'No function found for jal target' line.
For each (caller, target): caller section, and every section whose function
table has an entry starting exactly at target (a runtime lookup can resolve
it only if the loaded overlay has a function entry there).
Usage: s7082_jal_census.py <n64recomp.log> <RecompiledFuncs dir>"""
import re, sys, collections
log, d = sys.argv[1], sys.argv[2]
ov = open(d + '/recomp_overlays.inl').read()
secs = {}
for m in re.finditer(r'static FuncEntry (section_\d+_\w+?)_funcs\[\] = \{(.*?)\};', ov, re.S):
    secs[m.group(1)] = [(e.group(1), int(e.group(2), 16), int(e.group(3), 16))
                        for e in re.finditer(r'\.func = (\w+), \.offset = 0x([0-9A-F]+), \.rom_size = 0x([0-9A-F]+)', m.group(2))]
base = {}
for m in re.finditer(r'\.ram_addr = 0x([0-9A-F]+), \.size = 0x([0-9A-F]+), \.funcs = (section_\d+_\w+?)_funcs', ov):
    base[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
start = collections.defaultdict(list); owner = {}; inside = collections.defaultdict(list)
for s, fs in secs.items():
    b = base[s][0]
    for n, o, z in fs:
        start[b + o].append((s, n)); owner[n] = s
        for a in (b + o,): pass
def containing(t):
    r = []
    for s, fs in secs.items():
        b = base[s][0]
        for n, o, z in fs:
            if b + o < t < b + o + z: r.append((s, n, t - b - o))
    return r
pairs = collections.Counter(re.findall(r'No function found for jal target: 0x([0-9A-F]+) in (\w+),', open(log).read()))
cls = collections.Counter(); rows = []
for (t, c), k in sorted(pairs.items()):
    t = int(t, 16); cs = owner.get(c, '?')
    st = start.get(t, [])
    same = [x for x in st if x[0] == cs]
    if same: c_ = 'SAME-SECTION-START'   # static resolution should have worked
    elif st: c_ = 'OTHER-SECTION-START'   # cross-overlay, runtime lookup resolves if that overlay is loaded
    else:
        ins = containing(t)
        c_ = 'MID-FUNCTION' if ins else 'NO-FUNCTION'
        st = ins
    cls[c_] += k
    rows.append((c_, c, cs, '0x%08X' % t, k, st))
for r in rows: print('\t'.join(map(str, r)))
print('#', dict(cls), 'pairs', len(pairs), 'lines', sum(pairs.values()))
# per-target overlay map for cross-section targets: start-in vs mid-in each overlay
print('# target\tstart_in\tmid_in\tcallers')
tg = collections.defaultdict(set)
for (t, c), k in pairs.items(): tg[int(t, 16)].add(c)
for t in sorted(tg):
    s_in = sorted({s for s, n in start.get(t, [])}); m_in = sorted({s for s, n, o in containing(t)})
    print('#T\t0x%08X\t%s\t%s\t%s' % (t, ','.join(x.split('_')[-1] for x in s_in) or '-',
          ','.join(x.split('_')[-1] for x in m_in) or '-', ','.join(sorted(tg[t]))))
