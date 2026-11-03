#!/usr/bin/env python3
"""s6830 G1e FPS60 idiom census: integer CONSTANT-STEP accumulators the s6821 audit (g3_tick_counter_audit.py: +-1 steps
followed by a test) does not cover. Pattern, linear per function: load (lb/lbu/lh/lhu/lw) rX, off(base) -> within 4 instrs
addiu rY, rX, K with |K| > 1 -> within 4 instrs store of the same width rY, off(base). $sp locals are skipped.
Prints every site (func, pc, load, field, K). A triage list: per-tick phase/angle steps (e.g. tickTextureAnimSlots -256)
run 2x per game second at FPS60; heap/pointer strides (rs_free +16, mesh instance +88) are not time.
Usage: g1e_int_step_audit.py [RecompiledFuncs dir]"""
import re, glob, sys
R = sys.argv[1] if len(sys.argv) > 1 else '../N64Recomp/RecompiledFuncs'
LD = {'lb': 'sb', 'lbu': 'sb', 'lh': 'sh', 'lhu': 'sh', 'lw': 'sw'}
rows = []
def scan(fn, asm):
    for i, (pc, op, a) in enumerate(asm):
        if op not in LD or len(a) != 2 or '$sp' in a[1]: continue
        for j in range(i + 1, min(i + 5, len(asm))):
            _, oj, aj = asm[j]
            if oj in ('addiu', 'addi') and len(aj) == 3 and aj[1] == a[0]:
                try: k = int(aj[2], 0)
                except ValueError: break
                if abs(k) <= 1: break
                if any(o == LD[op] and len(x) == 2 and x[0] == aj[0] and x[1] == a[1] for _, o, x in asm[j + 1:j + 5]):
                    rows.append((fn, pc, op, a[1], k))
                break
for p in sorted(glob.glob(R + '/funcs_*.c')):
    fn = None; asm = []; last = None
    for ln in open(p):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', ln)
        if m:
            if fn: scan(fn, asm)
            fn = m.group(1); asm = []; last = None; continue
        m = re.match(r'\s*// (0x[0-9A-F]+): (\S+)\s*(.*)', ln)
        if m and fn:
            k = (m.group(1), m.group(2))
            if k == last: continue  # delay-slot comments are emitted twice
            last = k
            asm.append((int(m.group(1), 16), m.group(2), [x.strip() for x in m.group(3).split(',')] if m.group(3) else []))
    if fn: scan(fn, asm)
print('# %d sites in %d functions' % (len(rows), len({r[0] for r in rows})))
for r in rows: print('%-44s 0x%08X %-4s %-14s %+d' % r)
