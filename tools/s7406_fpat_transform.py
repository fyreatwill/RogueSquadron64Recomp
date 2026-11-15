#!/usr/bin/env python3
"""s7406 class BP: copy N64Recomp/RecompiledFuncs to DST, wrapping every guest FP statement and every call line with an
FPSR check keyed by the guest PC from the generated `// 0xPC:` comment (rs64_fpat.h). Line numbers are preserved.
Usage: s7406_fpat_transform.py SRC DST [--plant fnA,fnB]   (plant = positive-control functions)."""
import os, re, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
plant = set(sys.argv[sys.argv.index('--plant') + 1].split(',')) if '--plant' in sys.argv else {'distanceFromCameraToPoint', 'transformVec3ByAffineMatrix', 'normalizeVec3'}
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(dst, exist_ok=True)
PC = re.compile(r'^\s*// 0x([0-9A-Fa-f]{8}):')
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(')
ST = re.compile(r'^(\s+)((?:ctx->f\d+\.(?:fl|d|u32l|u32h|u64)|c1cs)\s*=\s*(.*);)\s*$')
CALL = re.compile(r'^(\s+)((\w+|LOOKUP_FUNC\([^;]*\))\(rdram, ctx\);)\s*$')
REG = re.compile(r'ctx->f(\d+)\.(?:fl|d|u32l|u32h|u64)')
FPRHS = re.compile(r'\.fl\b|\.d\b|CVT_|TRUNC_|ROUND_|FLOOR_|CEIL_|sqrt|do_cvt')
nst = ncall = nplant = 0
for name in sorted(os.listdir(src)):
    p = os.path.join(src, name)
    if not os.path.isfile(p): continue
    if not name.endswith('.c'):
        shutil.copy2(p, os.path.join(dst, name)); continue
    out = []; pc = '0u'; fn = None; planted = False
    for ln in open(p, errors='surrogateescape'):
        m = PC.match(ln)
        if m: pc = '0x%su' % m.group(1).upper()
        m = FN.match(ln)
        if m: fn = m.group(1); planted = fn not in plant
        m = ST.match(ln)
        if m and 'goto' not in ln and '{' not in m.group(2) and FPRHS.search(m.group(3)):
            ind, stmt, rhs = m.groups()
            regs = []
            for r in REG.findall(rhs):
                if r not in regs: regs.append(r)
            a = 'ctx->f%s.u64' % regs[0] if regs else '0'
            b = 'ctx->f%s.u64' % regs[1] if len(regs) > 1 else '0'
            pre = ''
            if not planted:
                planted = True; nplant += 1
                pre = 'rs64_fpat_plant(); RS64_FPCHK(0xFFFFFFF0u, "plant", 0, 0); '
            ln = '%s{ %suint64_t _fa = %s, _fb = %s; %s RS64_FPCHK(%s, "stmt", _fa, _fb); }\n' % (ind, pre, a, b, stmt, pc)
            nst += 1
        else:
            m = CALL.match(ln)
            if m and fn is not None:
                ind, call, callee = m.groups()
                cs = 'call:' + (callee if not callee.startswith('LOOKUP_FUNC') else 'LOOKUP')
                ln = '%s{ %s RS64_FPCHK(%s, "%s", 0, 0); }\n' % (ind, call, pc, cs)
                ncall += 1
        out.append(ln)
    body = ''.join(out)
    body = '#include "rs64_fpat.h"\n' + body if False else body
    with open(os.path.join(dst, name), 'w', errors='surrogateescape') as f:
        f.write('#include "rs64_fpat.h"\n'); f.write(body)
shutil.copy2(os.path.join(here, 's7406_fpat', 'rs64_fpat.h'), dst)
shutil.copy2(os.path.join(here, 's7406_fpat', 'rs64_fpat_rt.c'), dst)
print('stmts=%d calls=%d plants=%d' % (nst, ncall, nplant))
