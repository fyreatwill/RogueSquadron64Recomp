#!/usr/bin/env python3
"""s7082: classify every N64Recomp 'No function found for jal target' line.
For each (caller, target): caller section, and every section whose function
table has an entry starting exactly at target (a runtime lookup can resolve
it only if the loaded overlay has a function entry there).
Usage: s7082_jal_census.py <n64recomp.log[.gz]> <RecompiledFuncs dir> [--check] [--plant]
--check (s7722): exit 1 unless every pair is OTHER-SECTION-START or one of the ACCEPTED rows (docs/N64RECOMP-WARNING-CENSUS.md
class 2), the log has >= 1 pair, and (with --plant) a synthetic same-section jal line is reported OPEN (planted control)."""
import re, sys, collections
import gzip
args = [x for x in sys.argv[1:] if not x.startswith('--')]
CHECK, PLANT = '--check' in sys.argv, '--plant' in sys.argv
log, d = args[0], args[1]
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
LOGTXT = (gzip.open(log, 'rt') if log.endswith('.gz') else open(log)).read()
JAL = r'No function found for jal target: 0x([0-9A-F]+) in (\w+),'
pairs = collections.Counter(re.findall(JAL, LOGTXT))
def classify(pairs):
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
    return rows, cls
rows, cls = classify(pairs)
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

# s7722 --check: the three non-overlay rows are explained (class 1 applyVoiceDelayFilter table word, H-data cinematic gap).
ACCEPTED = {('MID-FUNCTION', 'fake_func_800AF6A8', '0x800EA01C'), ('NO-FUNCTION', 'applyVoiceDelayFilter', '0x8334B334'),
            ('NO-FUNCTION', 'static_3_8009D978', '0x8334B334')}
def open_rows(rs):
    return [r for r in rs if r[0] != 'OTHER-SECTION-START' and (r[0], r[1], r[3]) not in ACCEPTED]
if CHECK:
    op = open_rows(rows)
    for r in op: print('OPENROW\t' + '\t'.join(map(str, r[:5])))
    ok = not op and len(pairs) > 0
    print('OPEN %d accepted %d overlay-start %d pairs %d' % (len(op), sum(1 for r in rows if (r[0], r[1], r[3]) in ACCEPTED),
          sum(1 for r in rows if r[0] == 'OTHER-SECTION-START'), len(pairs)))
    if PLANT:
        # planted control: a caller jal'ing the START of a function in its own section must read SAME-SECTION-START -> OPEN
        n, s_ = next((n, s_) for n, s_ in owner.items() if s_ == 'section_3_text')
        t = next(a for a, l in start.items() if (s_, n) in l)
        planted = LOGTXT + '\nNo function found for jal target: 0x%08X in %s, using runtime lookup\n' % (t, n)
        prows, _ = classify(collections.Counter(re.findall(JAL, planted)))
        prow = ('', n, '', '0x%08X' % t)
        pc = len(open_rows(prows)) - len(op)
        print('plant control: same-section jal %s -> %s: +%d open -> %s' % (n, prow[3], pc, 'CONTROL PASS' if pc == 1 else 'CONTROL FAIL'))
        ok = ok and pc == 1
    print('VERDICT', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)
