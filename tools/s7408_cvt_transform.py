#!/usr/bin/env python3
"""s7408 class BR: copy N64Recomp/RecompiledFuncs to DST, wrapping every CVT_W_S/CVT_W_D/TRUNC_W_S/TRUNC_W_D macro use as
RS64_CVT(pc, kind, MACRO, operand) keyed by the guest PC from the generated `// 0xPC:` comment (rs64_cvt.h). Line
numbers preserved. Usage: s7408_cvt_transform.py SRC DST"""
import os, re, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(dst, exist_ok=True)
PC = re.compile(r'^\s*// 0x([0-9A-Fa-f]{8}):')
MAC = re.compile(r'\b(TRUNC_W_S|TRUNC_W_D|CVT_W_S|CVT_W_D)\(([^()]*)\)')
KIND = {'TRUNC_W_S': 0, 'TRUNC_W_D': 1, 'CVT_W_S': 2, 'CVT_W_D': 3}
n = 0
for name in sorted(os.listdir(src)):
    p = os.path.join(src, name)
    if not os.path.isfile(p): continue
    if not name.endswith('.c'):
        shutil.copy2(p, os.path.join(dst, name)); continue
    out = []; pc = '0u'
    for ln in open(p, errors='surrogateescape'):
        m = PC.match(ln)
        if m: pc = '0x%su' % m.group(1).upper()
        elif not ln.lstrip().startswith('//') and MAC.search(ln):
            def rep(mm):
                global n; n += 1
                return 'RS64_CVT(%s, %d, %s, %s)' % (pc, KIND[mm.group(1)], mm.group(1), mm.group(2))
            ln = MAC.sub(rep, ln)
        out.append(ln)
    with open(os.path.join(dst, name), 'w', errors='surrogateescape') as f:
        f.write('#include "rs64_cvt.h"\n'); f.write(''.join(out))
shutil.copy2(os.path.join(here, 's7408_cvt', 'rs64_cvt.h'), dst)
shutil.copy2(os.path.join(here, 's7408_cvt', 'rs64_cvt_rt.c'), dst)
print('wrapped=%d' % n)
