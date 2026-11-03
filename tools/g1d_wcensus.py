#!/usr/bin/env python3
"""s6848 G1d wide-width idiom census: find every read of the screen width (global 0x8011A838 and screen-struct +0x10 via
the double-deref `lw p,0(x); lw w,0x10(p)` pattern), forward-taint it linearly (window N insns, kill on overwrite,
follows mtc1/cvt/fp arith), and report sinks: integer/fp compares, branches, 12-bit packs (andi 0xFFF), small-constant
addiu (epsilon), sll 2 (10.2 pack).  Census table: docs/G1D-WIDTH-CENSUS.md.  Usage: g1d_wcensus.py [RecompiledFuncs dir]"""
import re, sys, collections, glob
D = sys.argv[1] if len(sys.argv) > 1 else '/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs'
seen = {}
for f in sorted(glob.glob(D + '/funcs_*.c')):
    for l in open(f):
        m = re.match(r'\s*// (0x[0-9A-F]{8}): (\S+)\s*(.*)', l)
        if m: seen.setdefault(int(m.group(1), 16), (m.group(2), m.group(3)))
ins = sorted((a, o, r) for a, (o, r) in seen.items())
idx = {a: i for i, (a, o, r) in enumerate(ins)}
WIN = 48
def regs(r): return [x.strip() for x in re.split(r',\s*', r)]
def memop(s):
    m = re.match(r'(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)', s)
    return (int(m.group(1), 16) if 'x' in m.group(1) else int(m.group(1)), m.group(2)) if m else (None, None)
srcs = []
lui = {}
for i, (a, o, r) in enumerate(ins):
    R = regs(r)
    if o == 'lui': lui[R[0]] = (int(R[1], 16) << 16, a); continue
    if o in ('lw', 'lwc1'):
        off, base = memop(R[1])
        if base in lui and abs(a - lui[base][1]) < 0x200 and ((lui[base][0] + off) & 0xFFFFFFFF) == 0x8011A838:
            srcs.append((i, R[0], 'G838'))
        elif off in (0x10, 0x18) and (o == 'lw' or off == 0x10):
            # s6849: look back up to 4 insns (was 1) for `lw base, 0(x)`, stop at any other write of base
            for k in range(i - 1, max(i - 5, -1), -1):
                pa, po, pr = ins[k]; P = regs(pr)
                if po == 'lw' and P[0] == base and memop(P[1])[0] == 0 and P[0] != memop(P[1])[1]:
                    srcs.append((i, R[0], 'S+%X' % off)); break
                if P and P[0] == base and po not in ('sw', 'sh', 'sb', 'swc1') and not po.startswith('b'): break
    if o in ('jr', 'jal') : lui = {}
CMP = {'slt', 'sltu', 'slti', 'sltiu', 'c.lt.s', 'c.le.s', 'c.eq.s', 'c.lt.d', 'c.le.d', 'beq', 'bne', 'blez', 'bgtz', 'bltz', 'bgez'}
out = collections.OrderedDict()
for i, r0, kind in srcs:
    t = {r0}; sinks = []
    for j in range(i + 1, min(i + WIN, len(ins))):
        a, o, r = ins[j]; R = regs(r)
        if o in ('jr',) : break
        uses = [x for x in R if x.startswith('$') and x in t] + [memop(x)[1] for x in R if memop(x)[1] in t]
        dst = R[0] if R and R[0].startswith('$') and o not in ('sw','sh','sb','swc1','sdc1','mtc1') and o not in CMP and not o.startswith('b') else None
        if o == 'mtc1':
            if R[0] in t: t.add(R[1])
            elif R[1] in t: t.discard(R[1])
            continue
        if o.startswith('c.') or o in CMP or o in ('sltiu','slti','slt','sltu'):
            if any(x in t for x in R[:3]): sinks.append((a, o, r))
        if o == 'andi' and R[1] in t and R[2].upper() in ('0XFFF', '0XFFFF'): sinks.append((a, o, r))
        if o == 'addiu' and R[1] in t and R[2] not in ('0x0',):
            v = int(R[2], 16); 
            if -8 <= v <= 8: sinks.append((a, o, r))
        if o in ('sll',) and R[1] in t and R[2] in ('2', '0x2'): sinks.append((a, o, r))
        if o in ('sw','swc1','sh') and R[0] in t: sinks.append((a, o, r))
        if dst:
            srcin = any(x in t for x in R[1:]) or any(memop(x)[1] in t for x in R[1:]) and o not in ('lw','lwc1','lh','lhu','lb','lbu')
            if o in ('lw','lwc1','lh','lhu','lb','lbu'): srcin = False
            if srcin: t.add(dst)
            elif dst in t: t.discard(dst)
        if o == 'jal': t -= {'$v0','$v1','$f0','$f2'}
    out[ins[i][0]] = (kind, r0, sinks)
for a, (k, r0, s) in out.items():
    print('%08X %s %s' % (a, k, r0) + ('' if s else '  (no sink)'))
    for x in s: print('    %08X %-8s %s' % x)
