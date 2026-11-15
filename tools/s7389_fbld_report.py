#!/usr/bin/env python3
"""s7389: classify every [s7389-new]/[s7389-row] key from a build_fbld run as LOAD or STORE by reading the generated
source line (one line = one MIPS instruction), and name the function it sits in.  Exit 0 always; prints a table:
kind live op count func file:line page.  A control (kind=ctl) LOAD row must exist or the null is void (exit 2).
s7390: every live colour/Z LOAD row gets a class: HEAP (rs_free / coalesceFreeHeapBlocks* block-header reads, i.e. a heap
block re-used inside an over-estimated fb span), DUMMYZ (Z page < 0x100000: the game's dummy SetZImage at phys 0), BOOTDL (Z
page 0xC00000-0xC05FFF: boot display-list memory named by a boot SetZImage), else UNCLASSED. Exit 3 when any live colour
LOAD or UNCLASSED live Z LOAD exists (a real fb reader candidate), 2 when the control is void, else 0.
Path tag per row: LD / LWLR when the source line is an ld/ldc1 or lwl/lwr (wrapped from s7390), else MEM.
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
    if not (0 < n <= len(L)): return '?', '?', '?'
    t = L[n - 1]
    fn = '?'
    for j in range(n - 1, -1, -1):
        mm = re.match(r'(?:RECOMP_FUNC )?void (\w+)\(uint8_t\* rdram', L[j])
        if mm: fn = mm[1]; break
    s = t.strip()
    op = 'STORE' if re.match(r'\{?\s*MEM_[A-Z]+\(', s) and re.search(r'\)\s*=[^=]', s) else 'LOAD'
    path = 'LD' if re.search(r'\bLD\(', s) else 'LWLR' if re.search(r'\bdo_lw[lr]\(', s) else 'MEM'
    return op, fn, path
def klass(kind, page, fn):
    pg = int(page, 16)
    if fn == 'rs_free' or fn.startswith('coalesceFreeHeapBlocks'): return 'HEAP'
    if kind == 'z' and pg < 0x100000: return 'DUMMYZ'
    if kind == 'z' and 0xC00000 <= pg < 0xC06000: return 'BOOTDL'
    return 'UNCLASSED'
tab = collections.Counter(); out = []; live_rows = []; paths = collections.Counter()
for (f, n, kind, live), (cnt, page) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
    op, fn, path = line_of(f, n)
    tab[(kind, live, op)] += cnt
    paths[(kind, path)] += cnt
    out.append(f'{kind:5} live={live} {op:5} n={cnt:<9} {fn:40} {f}:{n} page=0x{page} path={path}')
    if live and op == 'LOAD' and kind in ('color', 'z'):
        live_rows.append((kind, klass(kind, page, fn), cnt, fn, f, n, page, path))
for k, v in sorted(tab.items()): print('TOTAL kind=%s live=%d %s accesses=%d' % (k[0], k[1], k[2], v))
for k, v in sorted(paths.items()): print('PATH kind=%s path=%s accesses=%d' % (k[0], k[1], v))
for o in out[:80]: print(o)
cls = collections.Counter()
for kind, c, cnt, fn, f, n, page, path in live_rows:
    cls[(kind, c)] += cnt
    if c == 'UNCLASSED' or kind == 'color':
        print(f'LIVELOAD {kind} {c} n={cnt} {fn} {f}:{n} page=0x{page} path={path}')
for k, v in sorted(cls.items()): print('LIVECLASS kind=%s class=%s accesses=%d' % (k[0], k[1], v))
bad = sum(v for (kind, c), v in cls.items() if kind == 'color' or c == 'UNCLASSED')
ctl = sum(v for k, v in tab.items() if k[0] == 'ctl' and k[2] == 'LOAD')
print('CONTROL', 'PASS' if ctl else 'FAIL (void)', ctl)
print('VERDICT', 'void' if not ctl else 'READER-CANDIDATE %d' % bad if bad else 'no-reader')
sys.exit(2 if not ctl else 3 if bad else 0)
