#!/usr/bin/env python3
"""s7406 class BP report over a build_fpat run log: last [s7406-dump] table, ranked per flag, split by kind
(stmt = guest float statement, call:X = host code inside callee X after its last instrumented stmt).
Control: site pc=fffffff0 (planted inline in guest fns) must show ufc>=1 (and idc>=1 when FZ=1).
rc 0 control PASS + H-none, rc 2 control FAIL, rc 3 guest stmt IDC or any IOC (retail would trap). usage: s7406_fpat_report.py <log> [--fz 0|1] [--tid 3]"""
import re, sys, collections
log = sys.argv[1]; fz = int(sys.argv[sys.argv.index('--fz') + 1]) if '--fz' in sys.argv else None
tidf = int(sys.argv[sys.argv.index('--tid') + 1]) if '--tid' in sys.argv else None
site = {}; hits = collections.defaultdict(list); last = None
R = re.compile(r'\[s7406-site\] pc=(\w+) fn=(\S+) kind=(\S+) hits=(\d+) ioc=(\d+) dzc=(\d+) ofc=(\d+) ufc=(\d+) idc=(\d+) tids=(\w+)')
H = re.compile(r'\[s7406-hit\] pc=(\w+) fn=(\S+) kind=(\S+) n=(\d+) fpsr=(\w+) tid=(-?\d+) thr=(.*?) a=(\w+) b=(\w+)')
for ln in open(log, errors='replace'):
    if '[s7406-dump]' in ln: last = ln.strip()
    m = R.search(ln)
    if m:
        pc, fn, kind = m.group(1, 2, 3); v = list(map(int, m.group(4, 5, 6, 7, 8, 9))); site[(pc, fn, kind)] = v + [int(m.group(10), 16)]
    m = H.search(ln)
    if m: hits[(m.group(1), m.group(2), m.group(3))].append(m.groups()[3:])
print('last dump:', last)
names = ['hits', 'ioc', 'dzc', 'ofc', 'ufc', 'idc']
def tids(mask): return ','.join(str(i) if i != 31 else 'host' for i in range(32) if mask >> i & 1)
rows = list(site.items())  # thread names come from the first 4 [s7406-hit] lines per site (bit 31 = named thread)
for fi, fname in [(4, 'ufc'), (5, 'idc'), (2, 'dzc'), (3, 'ofc'), (1, 'ioc')]:
    rs = sorted([r for r in rows if r[1][fi] > 0], key=lambda r: -r[1][fi])
    tot = sum(r[1][fi] for r in rs)
    bykind = collections.Counter()
    for (pc, fn, kind), v in rs: bykind['stmt' if kind == 'stmt' else ('plant' if kind == 'plant' else 'call')] += v[fi]
    print('\n== %s total=%d sites=%d by kind %s' % (fname, tot, len(rs), dict(bykind)))
    for (pc, fn, kind), v in rs[:20]:
        ex = hits.get((pc, fn, kind), [])
        e = ('a=%s b=%s fpsr=%s thr=%s' % (ex[0][4], ex[0][5], ex[0][1], '/'.join(sorted(set(x[3] for x in ex))))) if ex else ''
        print('  %s %-36s %-24s %s=%d hits=%d tids=%s %s' % (pc, fn, kind, fname, v[fi], v[0], tids(v[6]), e))
c = site.get(('fffffff0', None, None))
cs = [v for (pc, fn, kind), v in site.items() if pc == 'fffffff0']
cu = sum(v[4] for v in cs); ci = sum(v[5] for v in cs)
plants = int(re.search(r'plants=(\d+)', last).group(1)) if last else 0
ok = plants >= 1 and cu >= plants and (fz != 1 or ci >= plants)
print('\nCONTROL plants=%d plant_ufc=%d plant_idc=%d fz=%s -> %s' % (plants, cu, ci, fz, 'PASS' if ok else 'FAIL'))
sidc = sum(v[5] for (pc, fn, kind), v in site.items() if kind == 'stmt')
sioc = sum(v[1] for (pc, fn, kind), v in site.items() if kind != 'plant')
print('VERDICT stmt_idc=%d ioc=%d -> %s' % (sidc, sioc, 'H-none' if sidc == 0 and sioc == 0 else 'GUEST-DENORMAL-INPUT-OR-INVALID'))
sys.exit(2 if not ok else (3 if sidc or sioc else 0))
