#!/usr/bin/env python3
"""s7081: enumerate N64Recomp self-branch miscompiles in a generated tree.

N64Recomp prints a label at the first instruction whose vram >= label, so a
goto to a label below the function's first instruction (or past its last)
lands inside the function instead of at the real target. This lists every
`goto L_X` whose X lies outside [first instr vram, last instr vram] of the
containing RECOMP_FUNC, and where the label was actually printed.
Usage: scan_selfbranch.py <RecompiledFuncs dir> [--tsv out]
"""
import re, sys, glob, os
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')
INS = re.compile(r'^\s*// 0x([0-9A-F]{8}): ')
LAB = re.compile(r'^(L_[0-9A-F]{8}):')
GO = re.compile(r'goto (L_([0-9A-F]{8}));')

def scan(path):
    out = []
    cur = None
    def flush():
        if not cur or not cur['ins']:
            return
        lo, hi = min(cur['ins']), max(cur['ins'])
        for ln, lab, tgt in cur['gotos']:
            if tgt < lo or tgt > hi:
                printed_at = cur['labat'].get(lab)
                out.append((os.path.basename(path), cur['name'], lo, ln, tgt, printed_at))
    with open(path, errors='replace') as f:
        pending = []
        for ln, line in enumerate(f, 1):
            m = FN.match(line)
            if m:
                flush()
                cur = {'name': m.group(1), 'ins': [], 'gotos': [], 'labat': {}}
                pending = []
                continue
            if cur is None:
                continue
            m = LAB.match(line)
            if m:
                pending.append(m.group(1)); continue
            m = INS.match(line)
            if m:
                v = int(m.group(1), 16)
                cur['ins'].append(v)
                for p in pending:
                    cur['labat'].setdefault(p, v)
                pending = []
            for g in GO.finditer(line):
                cur['gotos'].append((ln, g.group(1), int(g.group(2), 16)))
        flush()
    return out

def main():
    d = sys.argv[1]
    rows = []
    for p in sorted(glob.glob(os.path.join(d, 'funcs_*.c'))) + sorted(glob.glob(os.path.join(d, '*.c'))):
        if p in [r for r in []]:
            pass
    seen = set()
    for p in sorted(glob.glob(os.path.join(d, '*.c'))):
        if p in seen: continue
        seen.add(p)
        rows += scan(p)
    print(f'{len(rows)} out-of-function gotos')
    lines = []
    for f, fn, lo, ln, tgt, at in rows:
        s = f'{f}\t{fn}\t0x{lo:08X}\tline{ln}\t0x{tgt:08X}\tlands@{("0x%08X" % at) if at else "NONE"}'
        lines.append(s); print(s)
    if '--tsv' in sys.argv:
        open(sys.argv[sys.argv.index('--tsv') + 1], 'w').write('\n'.join(lines) + '\n')

if __name__ == '__main__':
    main()
