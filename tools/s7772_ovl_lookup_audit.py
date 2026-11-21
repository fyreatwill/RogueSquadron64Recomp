#!/usr/bin/env python3
"""s7772 overlay-aliased jal audit (HYPOTHESIS-ID ovl-aliased-lookup-audit).

s7771 found jal sites whose target is a function start only in an overlay other than the site's own section
(start_ovl). Runtime semantics (lib/N64ModernRuntime/librecomp/src/overlays.cpp): get_function looks the address up
in func_map, which holds only the functions of the sections currently loaded (load_overlay adds, the s7528 eviction
removes overlapping residents). So a lookup runs the body of whatever overlay is mapped at that VMA (hardware
semantics) or aborts loudly ("Failed to find function") when the address is not a function start there. The only
SILENT wrong-body path is the generated call site itself: if N64Recomp bound the site to one overlay's function by a
direct call, the loaded overlay is ignored. This tool checks every start_ovl site's generated call form.

Per site: LOOKUP (LOOKUP_FUNC(0x<target>)), DIRECT (named call: silent wrong body if another overlay is mapped),
NOTFOUND (site not in the generated tree). Per distinct target: the overlay sections where it is a start / interior.
--controls: mutation control (one LOOKUP site's text rewritten to a direct call must classify DIRECT) + a known
LOOKUP site (mainGameLoop+0xEC) must classify LOOKUP.
--gate: rc 1 if any in-function start_ovl site is DIRECT or NOTFOUND.
"""
import argparse, bisect, glob, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('--gen', default='../N64Recomp/RecompiledFuncs')
ap.add_argument('--syms', default='syms/rogue_squadron.syms.toml')
ap.add_argument('--controls', action='store_true')
ap.add_argument('--gate', action='store_true')
ap.add_argument('-v', action='store_true', help='print every site')
a = ap.parse_args()

out = subprocess.run([sys.executable, 'tools/s7771_jal_target_census.py'], capture_output=True, text=True).stdout
ROW = re.compile(r'^jal\s+(\S+)\s+site=0x([0-9A-F]{8})\s+(\S+)\s+-> 0x([0-9A-F]{8}) (\S+)\s+(\S+)')
rows = []
for line in out.splitlines():
    m = ROW.match(line)
    if m and m.group(5) == 'start_ovl':
        rows.append(dict(sec=m.group(1), pc=int(m.group(2), 16), site=m.group(3), t=int(m.group(4), 16), tsec=m.group(6)))
if not rows:
    print('FATAL no start_ovl rows from s7771 census'); sys.exit(4)

# generated tree index: (site, target) -> list of call texts following the jal comment
JC = re.compile(r'^\s*// 0x([0-9A-F]{8}): jal\s+0x([0-9A-F]{8})')
CALL = re.compile(r'(LOOKUP_FUNC\(0x([0-9A-Fa-f]{8})\)|\b([A-Za-z_][A-Za-z0-9_]*)\(rdram, ctx\);)')
want = {(r['pc'], r['t']) for r in rows}
gen = {}
files = sorted(glob.glob(os.path.join(a.gen, '*.c')))
if not files:
    print('FATAL no generated .c under', a.gen); sys.exit(4)
for fn in files:
    L = open(fn, errors='replace').read().splitlines()
    for i, line in enumerate(L):
        m = JC.match(line)
        if not m:
            continue
        key = (int(m.group(1), 16), int(m.group(2), 16))
        if key not in want:
            continue
        gen.setdefault(key, []).append('\n'.join(L[i + 1:i + 40]))


def classify(text):
    for m in CALL.finditer(text):
        if m.group(2):
            return 'LOOKUP', m.group(2).upper()
        if m.group(3) not in ('if', 'while', 'for', 'switch', 'return', 'sizeof'):
            return 'DIRECT', m.group(3)
    return 'NONE', '-'


def site_class(r):
    texts = gen.get((r['pc'], r['t']))
    if not texts:
        return 'NOTFOUND', '-'
    cs = {classify(t) for t in texts}
    bad = [c for c in cs if c[0] != 'LOOKUP' or int(c[1], 16) != r['t']]
    return (bad[0] if bad else next(iter(cs)))

# per-target overlay classification
funcs, cur = {}, None
for line in open(a.syms):
    m = re.match(r'name = "([^"]+)"', line)
    if m:
        cur = m.group(1); funcs[cur] = []; continue
    m = re.search(r'name = "([^"]+)", vram = 0x([0-9A-Fa-f]+), size = 0x([0-9A-Fa-f]+)', line)
    if m and cur:
        funcs[cur].append((int(m.group(2), 16), int(m.group(3), 16), m.group(1)))
for k in funcs:
    funcs[k].sort()


def tstat(sec, t):
    v = [f[0] for f in funcs[sec]]
    i = bisect.bisect_right(v, t) - 1
    if i >= 0 and funcs[sec][i][0] <= t < funcs[sec][i][0] + funcs[sec][i][1]:
        return 'start' if funcs[sec][i][0] == t else 'interior'
    return None

isdata = lambda r: r['site'] == 'OUTSIDE' or r['site'].startswith(('data_gap_', '__OSGlobalIntMask'))
cnt, bad = {}, []
for r in rows:
    r['cls'], r['call'] = site_class(r)
    k = ('data:' if isdata(r) else '') + r['cls']
    cnt[k] = cnt.get(k, 0) + 1
    if not isdata(r) and r['cls'] != 'LOOKUP':
        bad.append(r)
    if a.v or (not isdata(r) and r['cls'] != 'LOOKUP'):
        print('SITE %-8s %-15s 0x%08X %-40s -> 0x%08X %s call=%s' % (r['cls'], r['sec'], r['pc'], r['site'], r['t'], r['tsec'], r['call']))

tg = {}
for r in rows:
    if not isdata(r):
        tg.setdefault(r['t'], set()).add(r['sec'])
multi = 0
for t in sorted(tg):
    st = {s: tstat(s, t) for s in funcs if s.startswith('.ovl') or s == '.text'}
    starts = sorted(s for s, v in st.items() if v == 'start')
    inter = sorted(s for s, v in st.items() if v == 'interior')
    multi += len(starts) > 1
    print('TARGET 0x%08X start_in=%s interior_in=%s called_from=%s' % (t, ','.join(starts), ','.join(inter) or '-',
                                                                    ','.join(sorted(tg[t]))))
print('SUMMARY start_ovl_sites=%d %s in_function_nonlookup=%d distinct_in_function_targets=%d multi_start_targets=%d'
      % (len(rows), ' '.join('%s=%d' % kv for kv in sorted(cnt.items())), len(bad), len(tg), multi))

rc = 0
if a.controls:
    r0 = next((r for r in rows if r['site'] == 'mainGameLoop+0xEC'), None)
    pos = r0 and site_class(r0)[0] == 'LOOKUP'
    txt = gen[(r0['pc'], r0['t'])][0] if r0 and (r0['pc'], r0['t']) in gen else ''
    mut = classify(re.sub(r'LOOKUP_FUNC\(0x[0-9A-Fa-f]{8}\)\(rdram, ctx\);', 'menuFuncStub(rdram, ctx);', txt))[0]
    ok = bool(pos) and mut == 'DIRECT'
    print('CONTROLS %s (known_lookup=%s mutated=%s)' % ('PASS' if ok else 'FAIL', 'LOOKUP' if pos else 'no', mut))
    rc = 0 if ok else 3
if a.gate:
    print('GATE %s in_function_nonlookup=%d' % ('RED' if bad else 'GREEN', len(bad)))
    rc = rc or (1 if bad else 0)
sys.exit(rc)
