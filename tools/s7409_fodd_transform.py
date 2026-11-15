#!/usr/bin/env python3
"""s7409 class BS: copy N64Recomp/RecompiledFuncs to DST inserting RS64_FRP probes (tools/s7409_fodd/rs64_frp.h):
 - entry of every function that touches an odd FPR (f_odd or own odd slot) or writes Status: expect FR=1 for the three
   callees that run inside transformAndEmitFaceVertices' FR=1 region, -1 (just record) for data_gap_*, else FR=0;
 - after every cop0_status_write: expect 1 after an OR-built value, 0 after an AND-built value.
Usage: s7409_fodd_transform.py SRC DST"""
import os, re, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(dst, exist_ok=True)
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')
ODD = re.compile(r'ctx->f_odd\[|ctx->f(1|3|5|7|9|11|13|15|17|19|21|23|25|27|29|31)\.(fl|d|u32l|u64)')
FR1 = {'fetchIndexedVertexPosition', 'fetchVertexPositionPrimary', 'normalizeVec3InPlace'}
ne = ns = 0
# bisect (s7409): S7409_ONLY=entry|status|fn1,fn2 limits which probes are inserted
ONLY = os.environ.get('S7409_ONLY', '')
ok = lambda kind, fn: not ONLY or ONLY == kind or fn in ONLY.split(',')
for name in sorted(os.listdir(src)):
    p = os.path.join(src, name)
    if not os.path.isfile(p): continue
    if not name.endswith('.c'):
        shutil.copy2(p, os.path.join(dst, name)); continue
    lines = open(p, errors='surrogateescape').read().split('\n')
    # pass 1: which functions qualify
    want = set(); cur = None
    for ln in lines:
        m = FN.match(ln)
        if m: cur = m.group(1); continue
        if cur and (ODD.search(ln.split('//')[0]) or 'cop0_status_write' in ln): want.add(cur)
    out = []; cur = None; prev = ''
    for ln in lines:
        m = FN.match(ln)
        if m:
            cur = m.group(1)
            if cur in want and ok('entry', cur):
                e = 1 if cur in FR1 else -1 if cur.startswith('data_gap_') else 0
                ln += ' RS64_FRP("entry", %d);' % e; ne += 1
        elif 'cop0_status_write(ctx, ' in ln and ok('status', cur):
            e = 1 if ' | ' in prev else 0 if ' & ' in prev else -1
            ln = re.sub(r'(cop0_status_write\(ctx, [^;]*\);)', r'\1 RS64_FRP("status_w", %d);' % e, ln, count=1); ns += 1
        code = ln.split('//')[0]
        if code.strip(): prev = code
        out.append(ln)
    with open(os.path.join(dst, name), 'w', errors='surrogateescape') as f:
        f.write('#include "rs64_frp.h"\n' + '\n'.join(out))
for f in ('rs64_frp.h', 'rs64_frp_rt.c'): shutil.copy2(os.path.join(here, 's7409_fodd', f), dst)
print('entry_probes=%d status_probes=%d' % (ne, ns))
