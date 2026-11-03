#!/usr/bin/env python3
"""s6826 G3 FPS60 idiom audit: per-tick FLOAT quanta (the float sibling of g3_tick_counter_audit.py).
Pattern, linear per function: lwc1 fX, off(base) (base != $sp) -> within 8 instrs an add.s/sub.s/mul.s whose sources
include the loaded value -> within 8 more instrs swc1 of that result to the same off(base). The OTHER operand is
classified by a linear taint pass over the function:
  dt     - derived from an incoming argument (a0-a3 via mtc1, f12/f14, or a stack spill of either) or from the game
           clock 0x80130BA4; every per-tick handler receives the tick dt that way (0x800FA818 mfc1 $a1,$f20)
  const  - only rodata/literal (lwc1 off a lui-built address, mtc1 of a lui/ori/zero immediate)
  field  - a value loaded off an object/global base (e.g. pos += vel with no dt), not dt-tainted
  mixed  - anything else (call results, unknown)
Kinds: add/sub with const or field = STEP (per-tick quantum), mul with const = DAMP (per-tick multiplicative decay),
any dt operand = ok. Functions are tagged per-tick when reached from runInMissionFrame (jal depth <= 6) or from a handler-ish function
(name ends Update/Handler/Behavior*/Tick*, jal depth <= 4). Linear, ignores branches: a triage table, read flagged sites by hand.
Positive controls (printed first): updateNpcEventTimer 0x800EFE3C (+0x10 -= dt) and the s6817 collision resolver
stepObjectOrientationTowardTarget case accumulators must read 'dt'.
Usage: g3_float_quanta_audit.py [RecompiledFuncs dir] [--all] [--tsv out]"""
import re, glob, sys

LDF, STF = 'lwc1', 'swc1'
ARITH = {'add.s', 'sub.s', 'mul.s', 'div.s'}
UNARY = {'mov.s', 'neg.s', 'abs.s', 'sqrt.s', 'cvt.s.w', 'cvt.s.d', 'cvt.d.s', 'trunc.w.s', 'cvt.w.s'}
CONTROLS = {('updateNpcEventTimer', 0x800EFE3C)}

def parse(R):
    funcs, raw = {}, {}
    for p in sorted(glob.glob(R + '/funcs_*.c')):
        fn = None; last = None
        for ln in open(p):
            m = re.match(r'RECOMP_FUNC void (\w+)\(', ln)
            if m: fn = m.group(1); funcs[fn] = []; last = None; continue
            m = re.match(r'\s*// (0x[0-9A-F]+): (\S+)\s*(.*)', ln)
            if m and fn:
                k = (m.group(1), m.group(2))
                if k == last: continue
                last = k
                funcs[fn].append((int(m.group(1), 16), m.group(2), [x.strip() for x in m.group(3).split(',')] if m.group(3) else []))
    return funcs

def mem(a):
    m = re.match(r'(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)', a)
    return (int(m.group(1), 0), m.group(2)) if m else None

def taint(asm):
    """Per-instruction snapshot of register class: 'dt' | 'const' | 'field' | 'mixed' | 'ptr'. Linear pass."""
    cls = {'$a0': 'arg', '$a1': 'arg', '$a2': 'arg', '$a3': 'arg', '$f12': 'dt', '$f14': 'dt', '$zero': 'const'}
    lui = set()      # GPRs holding a lui-built (global/rodata) address or immediate
    gaddr = {}       # GPR -> absolute address when lui+addiu known
    stack = {}       # sp offset -> class
    snaps = []
    def j(*cs):
        cs = [c for c in cs if c]
        if 'dt' in cs or 'arg' in cs: return 'dt'
        if not cs: return 'mixed'
        if all(c == 'const' for c in cs): return 'const'
        if all(c in ('const', 'field') for c in cs): return 'field'
        return 'mixed'
    for pc, op, a in asm:
        snaps.append(dict(cls))
        if not a: continue
        d = a[0]
        if op == 'lui':
            cls[d] = 'const'; lui.add(d); gaddr[d] = (int(a[1], 0) << 16) & 0xFFFFFFFF; continue
        if op in ('addiu', 'ori') and len(a) == 3 and a[1] in lui:
            lui.add(d); cls[d] = 'const'
            if a[1] in gaddr: gaddr[d] = (gaddr[a[1]] + int(a[2], 0)) & 0xFFFFFFFF
            continue
        if op in ('lw', 'lwc1', 'ldc1', 'lh', 'lhu', 'lb', 'lbu') and len(a) == 2:
            ma = mem(a[1])
            lui.discard(d); gaddr.pop(d, None)
            if not ma: cls[d] = 'mixed'; continue
            off, b = ma
            if b == '$sp': cls[d] = stack.get(off, 'mixed')
            elif b in gaddr and ((gaddr[b] + off) & 0xFFFFFFFF) == 0x80130BA4: cls[d] = 'dt'
            elif b in lui and op in ('lwc1', 'ldc1'): cls[d] = 'const'
            else: cls[d] = 'field'
            continue
        if op in ('sw', 'swc1', 'sdc1', 'sd') and len(a) == 2:
            ma = mem(a[1])
            if ma and ma[1] == '$sp': stack[ma[0]] = cls.get(d, 'mixed')
            continue
        if op == 'mtc1' and len(a) == 2:
            cls[a[1]] = cls.get(a[0], 'mixed') if a[0] != '$zero' else 'const'
            if cls[a[1]] == 'arg': cls[a[1]] = 'dt'
            continue
        if op == 'mfc1' and len(a) == 2:
            cls[d] = cls.get(a[1], 'mixed'); continue
        if op in ('jal', 'jalr'):
            for r in ('$v0', '$v1', '$f0', '$f2', '$a0', '$a1', '$a2', '$a3'): cls[r] = 'mixed'
            for r in ('$f4', '$f6', '$f8', '$f10', '$f12', '$f14', '$f16', '$f18'): cls[r] = 'mixed'
            continue
        if op[0] in 'bjc' and op not in ('cvt.s.w', 'cvt.s.d', 'cvt.d.s', 'cvt.w.s'): continue
        if op in ARITH and len(a) == 3: cls[d] = j(cls.get(a[1]), cls.get(a[2])); continue
        if op in UNARY and len(a) == 2: cls[d] = cls.get(a[1], 'mixed'); continue
        if op in ('addu', 'or', 'subu', 'addiu', 'move') and len(a) >= 2:
            srcs = [cls.get(x) for x in a[1:] if x.startswith('$')]
            cls[d] = j(*srcs) if srcs else 'const'
            if d not in a[1:]: lui.discard(d); gaddr.pop(d, None)
            continue
        if d.startswith('$'): cls[d] = 'mixed'; lui.discard(d); gaddr.pop(d, None)
    return snaps

def scan(R):
    funcs = parse(R)
    addr2fn = {asm[0][0]: fn for fn, asm in funcs.items() if asm}
    calls = {fn: {addr2fn.get(int(a[0], 16)) for _, op, a in asm if op == 'jal' and a} - {None} for fn, asm in funcs.items()}
    reach, frontier = {'runInMissionFrame': 0}, ['runInMissionFrame']
    for dd in range(1, 7):
        nxt = []
        for f in frontier:
            for c in calls.get(f, ()):
                if c not in reach: reach[c] = dd; nxt.append(c)
        frontier = nxt
    handlerish = re.compile(r'(Update|Handler|Behavior\w*|Tick\w*)$')
    # handlers are installed by pointer (jalr), so also walk the jal graph below every handler-ish function
    frontier = [f for f in funcs if handlerish.search(f) and f not in reach]
    for f in frontier: reach[f] = 0
    for dd in range(1, 5):
        nxt = []
        for f in frontier:
            for c in calls.get(f, ()):
                if c not in reach: reach[c] = dd; nxt.append(c)
        frontier = nxt
    rows = []
    for fn, asm in funcs.items():
        snaps = None; n = len(asm)
        for i, (pc, op, a) in enumerate(asm):
            if op != LDF or len(a) != 2: continue
            ma = mem(a[1])
            if not ma or ma[1] == '$sp': continue
            fx = a[0]
            for k in range(i + 1, min(n, i + 9)):
                pk, ok, ak = asm[k]
                if ok in ARITH and len(ak) == 3 and fx in ak[1:]: break
                if ak and ak[0] == fx and ok not in (STF,): k = None; break
            else: k = None
            if k is None: continue
            pk, ok, ak = asm[k]
            if ok == 'div.s': continue
            res = ak[0]
            other = ak[2] if ak[1] == fx else ak[1]
            if other == fx: continue
            s = next((s for s in range(k + 1, min(n, k + 9)) if asm[s][1] == STF and len(asm[s][2]) == 2
                      and asm[s][2][0] == res and mem(asm[s][2][1]) == ma), None)
            if s is None: continue
            if snaps is None: snaps = taint(asm)
            oc = snaps[k].get(other, 'mixed')
            if oc == 'arg': oc = 'dt'
            if oc == 'dt': kind = 'ok'
            elif ok == 'mul.s': kind = 'DAMP' if oc == 'const' else 'mul-' + oc
            else: kind = 'STEP' if oc in ('const', 'field') else 'step-' + oc
            per = (fn in reach) or bool(handlerish.search(fn))
            rows.append((fn, pc, ma, ok, oc, kind, per, reach.get(fn)))
    return rows

if __name__ == '__main__':
    R = next((a for a in sys.argv[1:] if not a.startswith('--') and not a.endswith('.tsv')), '../N64Recomp/RecompiledFuncs')
    ALL = '--all' in sys.argv
    rows = scan(R)
    from collections import Counter
    print('# %d float load-op-store sites in %d functions; per-tick %d' % (len(rows), len({r[0] for r in rows}), sum(r[6] for r in rows)))
    print('# kinds (per-tick):', dict(Counter(r[5] for r in rows if r[6])))
    print('# kinds (all):     ', dict(Counter(r[5] for r in rows)))
    print('# controls:')
    for r in rows:
        if (r[0], r[1]) in CONTROLS or r[0] == 'stepObjectOrientationTowardTarget' and 0x800FF47C <= r[1] < 0x800FF98C:
            print('#  %-40s 0x%08X %-12s %s other=%s -> %s' % (r[0], r[1], '%#x(%s)' % r[2], r[3], r[4], r[5]))
    if '--tsv' in sys.argv:
        out = sys.argv[sys.argv.index('--tsv') + 1]
        with open(out, 'w') as f:
            for r in rows: f.write('%s\t0x%08X\t%#x(%s)\t%s\t%s\t%s\t%d\t%s\n' % (r[0], r[1], r[2][0], r[2][1], r[3], r[4], r[5], r[6], r[7]))
    print('%-44s %-10s %-14s %-6s %-6s %-6s %s' % ('func', 'pc', 'field', 'op', 'other', 'kind', 'depth'))
    for r in sorted(rows, key=lambda r: (r[5] == 'ok', r[0], r[1])):
        if not ALL and (r[5] == 'ok' or not r[6]): continue
        print('%-44s 0x%08X %-14s %-6s %-6s %-6s %s' % (r[0][:44], r[1], '%#x(%s)' % r[2], r[3], r[4], r[5], '-' if r[7] is None else r[7]))
