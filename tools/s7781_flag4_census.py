#!/usr/bin/env python3
"""s7781: static census of rs_malloc (0x80001ACC) call sites whose flag argument a1 has bit 4 set (the frame-scoped FB scratch
arena, head 0x8010FEFC, dropped each frame by clearFrameReadyFlag). Source: the asm comments in N64Recomp/RecompiledFuncs/funcs_*.c.
For each jal the a1 value is resolved by a backward walk (delay slot first, then up to 24 insns back in the same function) over
addiu/ori/addu/or/move/lui writes to $a1. Then a forward walk (up to 40 insns after the delay slot) follows $v0: where it is first
stored (sw $v0 / copies to s-regs and their sw: base register sp = LOCAL, lui-global = GLOBAL, other = HEAP/STRUCT), and whether
rs_free (resolved by name from the generated code) is called within the function. Prints one row per flag-4 site, a class tally and
the unresolved count. rc 0 always for the census; rc 2 if the positive control fails (no site resolves a1 at all).
usage: s7781_flag4_census.py [--all]"""
import re, sys, glob
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
ins, fn, calls = {}, {}, {}
for f in sorted(glob.glob(D + "funcs_*.c")):
    cur = None
    for l in open(f, errors="replace"):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', l)
        if m: cur = m.group(1)
        m = re.match(r'\s*// 0x([0-9A-F]{8}): (\S+)\s*(.*)', l)
        if m:
            a = int(m.group(1), 16)
            if a not in ins: ins[a] = (m.group(2), [x.strip() for x in m.group(3).split(',')]); fn[a] = cur
        m = re.match(r'\s*(\w+)\(rdram, ctx\);', l)
        if m and cur: calls.setdefault(cur, set()).add(m.group(1))
def imm(s):
    s = s.strip(); neg = s.startswith('-'); s = s.lstrip('-')
    v = int(s, 16) if s.lower().startswith('0x') else int(s)
    return -v if neg else v
def resolve(reg, a, depth=0):
    """value of reg just before insn a (walk back in the same function)"""
    if reg == '$zero': return 0
    f = fn[a]; b = a - 4
    for _ in range(24):
        if b not in ins or fn.get(b) != f: return None
        op, ar = ins[b]
        if op in ('jal', 'jalr'): return None
        if ar and ar[0] == reg:
            try:
                if op == 'addiu' and ar[1] == '$zero': return imm(ar[2]) & 0xFFFFFFFF
                if op == 'ori' and ar[1] == '$zero': return imm(ar[2]) & 0xFFFF
                if op == 'lui': return (imm(ar[1]) & 0xFFFF) << 16
                if op in ('addu', 'or', 'daddu') and '$zero' in ar[1:]:
                    src = ar[2] if ar[1] == '$zero' else ar[1]
                    return resolve(src, b, depth + 1) if depth < 4 else None
                if op in ('ori', 'addiu') and depth < 4:
                    v = resolve(ar[1], b, depth + 1)
                    if v is None: return None
                    return (v | (imm(ar[2]) & 0xFFFF)) if op == 'ori' else (v + imm(ar[2])) & 0xFFFFFFFF
                if op == 'andi' and depth < 4:
                    v = resolve(ar[1], b, depth + 1)
                    return None if v is None else v & imm(ar[2])
            except Exception: return None
            return None
        b -= 4
    return None
FREE = {n for n in set().union(*calls.values()) if 'free' in n.lower()}
rows = []
for a in sorted(ins):
    op, ar = ins[a]
    if op != 'jal' or not ar or ar[0].upper() != '0X80001ACC': continue
    d = ins.get(a + 4); a1 = None
    if d and d[1] and d[1][0] == '$a1':
        # delay slot writes a1: resolve as if the delay insn were the last writer
        dop, dar = d
        try:
            if dop == 'addiu' and dar[1] == '$zero': a1 = imm(dar[2]) & 0xFFFFFFFF
            elif dop == 'ori' and dar[1] == '$zero': a1 = imm(dar[2]) & 0xFFFF
            elif dop in ('addu', 'or') and '$zero' in dar[1:]: a1 = 0 if dar[1] == dar[2] == '$zero' else resolve(dar[2] if dar[1] == '$zero' else dar[1], a)
            elif dop == 'andi': v = resolve(dar[1], a); a1 = None if v is None else v & imm(dar[2])
        except Exception: a1 = None
    else: a1 = resolve('$a1', a)
    # forward: follow v0
    regs = {'$v0'}; dest = []; c = a + 8
    for _ in range(40):
        if c not in ins or fn.get(c) != fn[a]: break
        o, r = ins[c]
        if o in ('jal', 'jalr'):
            if '$v0' in regs: regs.discard('$v0')
        if o in ('sw', 'sd') and r and r[0] in regs:
            m = re.match(r'(-?(?:0x)?[0-9A-Fa-f]+)\((\$\w+)\)', r[1])
            if m:
                base = m.group(2)
                kind = 'LOCAL' if base == '$sp' else ('GLOBAL' if resolve(base, c) is not None and resolve(base, c) >= 0x80000000 else 'STRUCT')
                dest.append('%s:%s' % (kind, r[1]))
        if o in ('addu', 'or', 'move') and len(r) >= 2 and any(x in regs for x in r[1:]) and '$zero' in r[1:]: regs.add(r[0])
        elif r and r[0] in regs and o not in ('sw', 'sd', 'sb', 'sh', 'beq', 'bne', 'beqz', 'bnez'): regs.discard(r[0])
        c += 4
    frees = sorted(calls.get(fn[a], set()) & FREE)
    rows.append((a, fn[a], a1, dest, frees))
# wrappers that forward a caller's flag: load_asset_with_malloc_flags(name, flags) -> rs_malloc(size, flags & 0xFFFF);
# flag-4-constant wrappers reached by jal (rs_zcalloc) or by function pointer (mallocWithFallbackStrategy: lui/addiu ref).
WRAP = {0x800647E0: 'load_asset_with_malloc_flags', 0x8000527C: 'rs_zcalloc', 0x80005224: 'mallocWithFallbackStrategy'}
wrows = []
for a in sorted(ins):
    op, ar = ins[a]
    if op == 'jal' and ar and int(ar[0], 16) in WRAP:
        t = int(ar[0], 16); d = ins.get(a + 4); v = None
        if t == 0x800647E0:
            if d and d[1] and d[1][0] == '$a1' and d[0] == 'addiu' and d[1][1] == '$zero': v = imm(d[1][2]) & 0xFFFFFFFF
            elif d and d[1] and d[1][0] == '$a1' and d[0] in ('addu', 'or'): v = resolve(d[1][2] if d[1][1] == '$zero' else d[1][1], a)
            else: v = resolve('$a1', a)
        wrows.append(('jal', a, fn[a], WRAP[t], v))
    if op == 'addiu' and len(ar) == 3 and ar[1] != '$zero':
        b = resolve(ar[1], a)
        if b is not None and ((b + imm(ar[2])) & 0xFFFFFFFF) in WRAP and ((b + imm(ar[2])) & 0xFFFFFFFF) != 0x800647E0:
            wrows.append(('fnptr', a, fn[a], WRAP[(b + imm(ar[2])) & 0xFFFFFFFF], None))
print("wrapper uses:")
for k, a, f, w, v in wrows:
    print(f"  {k:5s} 0x{a:08X} {f:44s} -> {w:28s} flags={'?' if v is None else hex(v)}{'  FLAG4' if v is not None and v & 4 else ''}")
res = [r for r in rows if r[2] is not None]
f4 = [r for r in res if r[2] & 4]
print(f"rs_malloc call sites={len(rows)} a1 resolved={len(res)} unresolved={len(rows)-len(res)} flag4={len(f4)}")
show = rows if '--all' in sys.argv else f4 + [r for r in rows if r[2] is None]
for a, f, a1, dest, frees in show:
    cls = 'UNRESOLVED' if a1 is None else ('FLAG4' if a1 & 4 else 'plain')
    print(f"{cls:10s} 0x{a:08X} {f:44s} a1={'?' if a1 is None else hex(a1):6s} v0->{','.join(dest[:3]) or 'reg-only'} free={','.join(frees) or '-'}")
if not res: print("CONTROL FAIL: no a1 resolved"); sys.exit(2)
