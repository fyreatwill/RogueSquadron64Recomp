#!/usr/bin/env python3
"""s7389: classify every [s7389-new]/[s7389-row] key from a build_fbld run as LOAD or STORE by reading the generated
source line (one line = one MIPS instruction), and name the function it sits in.  Exit 0 always; prints a table:
kind live op count func file:line page.  A control (kind=ctl) LOAD row must exist or the null is void (exit 2).
usage: s7389_fbld_report.py <run.log> [RecompiledFuncs dir]"""
import re, sys, pathlib, collections
log = pathlib.Path(sys.argv[1]).read_text(errors='replace').splitlines()
D = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else '/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
rows = {}
for l in log:
    m = re.match(r'\[s7389-(?:new|row)\] .*?(\S+\.c):(\d+) kind=(\w+) live=(\d)(?: n=(\d+))?.*?(?:phys|page)=0x([0-9A-F]+)', l)
    if not m: continue
    k = (m[1], int(m[2]), m[3], int(m[4]))
    n = int(m[5]) if m[5] else 1
    rows[k] = (max(rows.get(k, (0, ''))[0], n), m[6])
src = {}
def line_of(f, n):
    if f not in src:
        p = D / f
        src[f] = p.read_text(errors='replace').splitlines() if p.exists() else []
    L = src[f]
    if not (0 < n <= len(L)): return '?', '?'
    t = L[n - 1]
    fn = '?'
    for j in range(n - 1, -1, -1):
        mm = re.match(r'(?:RECOMP_FUNC )?void (\w+)\(uint8_t\* rdram', L[j])
        if mm: fn = mm[1]; break
    s = t.strip()
    op = 'STORE' if re.match(r'\{?\s*MEM_[A-Z]+\(', s) and re.search(r'\)\s*=[^=]', s) else 'LOAD'
    return op, fn
tab = collections.Counter(); out = []
for (f, n, kind, live), (cnt, page) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
    op, fn = line_of(f, n)
    tab[(kind, live, op)] += cnt
    out.append(f'{kind:5} live={live} {op:5} n={cnt:<9} {fn:40} {f}:{n} page=0x{page}')
for k, v in sorted(tab.items()): print('TOTAL kind=%s live=%d %s accesses=%d' % (k[0], k[1], k[2], v))
for o in out[:80]: print(o)
ctl = sum(v for k, v in tab.items() if k[0] == 'ctl' and k[2] == 'LOAD')
print('CONTROL', 'PASS' if ctl else 'FAIL (void)', ctl)
sys.exit(0 if ctl else 2)
