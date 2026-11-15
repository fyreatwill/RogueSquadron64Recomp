#!/usr/bin/env python3
"""s7410 class BT: copy N64Recomp/RecompiledFuncs to DST with RS64_FSV probes (tools/s7410_fsv/rs64_fsv.h) in the 7 FR=1
hand-asm routines: entry snapshot of the callee-saved state, diff before every `return;`.
Usage: s7410_fsv_transform.py SRC DST"""
import os, re, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(dst, exist_ok=True)
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')
WANT = {'transformAndEmitFaceVertices', 'evalCubicSplineAtTime', 'mat3x4Multiply', 'transformVec3ByMat34',
        'rotateVec3ByMat3x3', 'quaternionToMat3x4', 'projectPointToScreen'}
ne = nr = 0; seen = set()
for name in sorted(os.listdir(src)):
    p = os.path.join(src, name)
    if not os.path.isfile(p): continue
    if not name.endswith('.c'):
        shutil.copy2(p, os.path.join(dst, name)); continue
    lines = open(p, errors='surrogateescape').read().split('\n'); out = []; cur = None
    for ln in lines:
        m = FN.match(ln)
        if m:
            cur = m.group(1)
            if cur in WANT: ln += ' RS64_FSV_ENTER();'; ne += 1; seen.add(cur)
        elif ln.startswith('}') or ln.startswith(';}'):
            cur = None
        elif cur in WANT and re.search(r'\breturn;', ln.split('//')[0]):
            ln = re.sub(r'\breturn;', '{ RS64_FSV_RET(); return; }', ln, count=1); nr += 1
        out.append(ln)
    with open(os.path.join(dst, name), 'w', errors='surrogateescape') as f:
        f.write('#include "rs64_fsv.h"\n' + '\n'.join(out))
for f in ('rs64_fsv.h', 'rs64_fsv_rt.c'): shutil.copy2(os.path.join(here, 's7410_fsv', f), dst)
print('entry_probes=%d return_probes=%d missing=%s' % (ne, nr, sorted(WANT - seen)))
