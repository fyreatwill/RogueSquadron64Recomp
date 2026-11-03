#!/usr/bin/env python3
"""s6821 G3 FPS60 idiom audit: per-object integer TICK counters (the s6820 despawn-grace class, generalised).
Pattern, linear per function: L: load (lb/lbu/lh/lhu/lw) rX, off(base) -> within 4 instrs addiu rY, rX, +-1 -> within 4
instrs store same width rY, off(base) (same base+off) -> within 8 instrs a test of rY (or a reload of off(base)):
slti/sltiu vs constant, or beq/bne/beqz/bnez/blez/bgtz/bltz/bgez. base=$sp is a stack local (loop index) and is listed
separately. Functions are tagged by whether they run per tick: reached from the mission-frame root runInMissionFrame
through the static jal graph (depth <= 6) or installed as an NPC handler (name ends in Update/Handler/Behavior*).
Sites carrying the s6820 tag are reported as 'fixed'. A triage table - read the flagged sites by hand.
Usage: g3_tick_counter_audit.py [RecompiledFuncs dir] [--all]"""
import re, glob, sys
def scan(R):
    """rows: (func, pc, load op, (off, base reg), step, test, kind, perTick, depth, fixed)"""
    funcs, addr2fn, raw = {}, {}, {}
    for p in sorted(glob.glob(R + '/funcs_*.c')):
        fn = None; last = None
        for ln in open(p):
            m = re.match(r'RECOMP_FUNC void (\w+)\(', ln)
            if m: fn = m.group(1); funcs[fn] = []; raw[fn] = []; last = None; continue
            if fn: raw[fn].append(ln)
            m = re.match(r'\s*// (0x[0-9A-F]+): (\S+)\s*(.*)', ln)
            if m and fn:
                k = (m.group(1), m.group(2))
                if k == last: continue  # delay-slot comments are emitted twice
                last = k
                funcs[fn].append((int(m.group(1), 16), m.group(2), [x.strip() for x in m.group(3).split(',')] if m.group(3) else []))
    for fn, asm in funcs.items():
        if asm: addr2fn[asm[0][0]] = fn
    # static call graph
    calls = {fn: {addr2fn.get(int(a[0], 16)) for _, op, a in asm if op == 'jal' and a} - {None} for fn, asm in funcs.items()}
    root = 'runInMissionFrame'
    reach, frontier = {root: 0}, [root]
    for d in range(1, 7):
        nxt = []
        for f in frontier:
            for c in calls.get(f, ()):
                if c not in reach: reach[c] = d; nxt.append(c)
        frontier = nxt
    handlerish = re.compile(r'(Update|Handler|Behavior\w*|Tick\w*)$')
    LD = {'lb': 1, 'lbu': 1, 'lh': 2, 'lhu': 2, 'lw': 4}
    ST = {'sb': 1, 'sh': 2, 'sw': 4}
    BR1 = {'beqz', 'bnez', 'blez', 'bgtz', 'bltz', 'bgez', 'beqzl', 'bnezl', 'blezl', 'bgtzl', 'bltzl', 'bgezl'}
    BR2 = {'beq', 'bne', 'beql', 'bnel'}
    def mem(a):
        m = re.match(r'(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)', a)
        return (int(m.group(1), 0), m.group(2)) if m else None
    rows = []
    for fn, asm in funcs.items():
        n = len(asm)
        for i, (pc, op, a) in enumerate(asm):
            if op not in LD or len(a) < 2: continue
            rx, ma = a[0], mem(a[1])
            if not ma: continue
            for j in range(i + 1, min(n, i + 5)):
                pj, oj, aj = asm[j]
                if oj in ('addiu', 'addi') and len(aj) == 3 and aj[1] == rx and aj[2] in ('1', '-1', '0x1', '-0x1'):
                    ry, step = aj[0], int(aj[2], 0)
                    break
                if aj and aj[0] == rx and oj not in ST: j = None; break
            else: j = None
            if j is None: continue
            k = next((k for k in range(j + 1, min(n, j + 5)) if asm[k][1] in ST and len(asm[k][2]) == 2 and asm[k][2][0] == ry and mem(asm[k][2][1]) == ma), None)
            if k is None: continue
            test = None
            regs = {ry}
            for t in range(j + 1, min(n, k + 9)):
                pt, ot, at = asm[t]
                if ot in LD and len(at) == 2 and mem(at[1]) == ma: regs.add(at[0]); continue
                if ot in ('sll', 'sra', 'andi') and len(at) >= 2 and at[1] in regs: regs.add(at[0]); continue
                if ot in ('slti', 'sltiu') and len(at) == 3 and at[1] in regs: test = '%s %s' % (ot, at[2]); break
                if ot in ('slt', 'sltu') and len(at) == 3 and (at[1] in regs or at[2] in regs): test = '%s reg' % ot; break
                if ot in BR1 and at and at[0] in regs: test = ot; break
                if ot in BR2 and len(at) >= 2 and (at[0] in regs or at[1] in regs): test = '%s %s' % (ot, at[1] if at[0] in regs else at[0]); break
            if test is None: continue
            fixed = any('s6820' in l for l in raw[fn]) and test.endswith('0x15')
            perTick = (fn in reach) or bool(handlerish.search(fn))
            kind = 'stack' if ma[1] == '$sp' else ('global' if ma[1] in ('$gp', '$at') or (ma[1] != '$zero' and False) else 'field')
            rows.append((fn, pc, op, ma, step, test, kind, perTick, reach.get(fn), fixed))
    return rows

if __name__ == '__main__':
    R = next((a for a in sys.argv[1:] if not a.startswith('--')), '../N64Recomp/RecompiledFuncs')
    SHOW_ALL = '--all' in sys.argv
    rows = scan(R)
    print('# %d counter sites in %d functions (stack %d); per-tick-tagged %d' % (len(rows), len({r[0] for r in rows}),
          sum(r[6] == 'stack' for r in rows), sum(r[7] for r in rows)))
    print('%-44s %-10s %-4s %-14s %4s %-14s %-6s %-5s %s' % ('func', 'pc', 'ld', 'field', 'step', 'test', 'kind', 'depth', 'fixed'))
    for r in sorted(rows, key=lambda r: (not r[7], r[6] == 'stack', r[0], r[1])):
        if not SHOW_ALL and (r[6] == 'stack' or not r[7]): continue
        fn, pc, op, ma, step, test, kind, pt, d, fx = r
        print('%-44s 0x%08X %-4s %-14s %+4d %-14s %-6s %-5s %s' % (fn[:44], pc, op, '%#x(%s)' % (ma[0], ma[1]), step, test, kind, '-' if d is None else d, 'FIXED' if fx else ''))
