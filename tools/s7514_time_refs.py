#!/usr/bin/env python3
"""s7514 class FK: resolve lui/addiu/off(reg) address references in RecompiledFuncs asm comments and list every
function touching the game's time-derived globals. Linear per-function lui tracking (lui value kept until the reg is
overwritten); good enough for the `lui r,HI; op x, LO(r)` idiom this compiler emits. Usage: s7514_time_refs.py DIR lo-hi..."""
import re, sys, glob, collections
d = sys.argv[1]; ranges = [tuple(int(x, 16) for x in a.split('-')) for a in sys.argv[2:]]
fn_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')
op_re = re.compile(r'^\s*// (0x8[0-9A-F]+): (\w+)\s+(.*)$')
def num(s): return int(s, 16) if s.lstrip('-').startswith('0x') else int(s)
hits = collections.defaultdict(set)
for f in sorted(glob.glob(d + '/*.c')):
    fn = None; regs = {}
    for line in open(f, errors='replace'):
        m = fn_re.match(line)
        if m: fn = m.group(1); regs = {}; continue
        m = op_re.match(line)
        if not m or not fn: continue
        pc, op, args = m.groups(); a = [x.strip() for x in args.split(',')]
        if op == 'lui':
            regs[a[0]] = (num(a[1]) << 16) & 0xFFFFFFFF; continue
        addr = None
        if op in ('addiu', 'ori') and len(a) == 3 and a[1] in regs:
            v = num(a[2]); addr = (regs[a[1]] + v) & 0xFFFFFFFF if op == 'addiu' else regs[a[1]] | v
            regs[a[0]] = addr
        else:
            mm = re.match(r'(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)', a[-1]) if a else None
            if mm and mm.group(2) in regs:
                addr = (regs[mm.group(2)] + num(mm.group(1))) & 0xFFFFFFFF
            if a and a[0].startswith('$') and op not in ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'beq', 'bne'):
                regs.pop(a[0], None)
        if addr is not None:
            for lo, hi in ranges:
                if lo <= addr < hi: hits[(addr, op if op not in ('addiu','ori') else 'addr')].add(f"{fn}@{pc}")
for (addr, op), s in sorted(hits.items()):
    print(f"{addr:08X} {op:5s} {len(s):3d} " + ' '.join(sorted(s)[:6]))
