#!/usr/bin/env python3
"""s6868: classify every address-named function in a generated tree (s6268 only counted the syms toml).
For each one: who jumps to it, whether each such site sits past the caller's real size (decoded data), what symbol
encloses it, and whether the ROM holds its address as a pointer. Offline, reads only.
usage: tools/audit_addr_named_funcs.py <RecompiledFuncs dir> <rom.z64> [--md out.md]"""
import argparse, glob, os, re, struct, sys

DEF = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')
ASM = re.compile(r'^\s*// 0x([0-9A-Fa-f]{8}): (\S+)\s*(\$\w+, )?(?:0x|L_)?([0-9A-Fa-f]{8})?')
LINKS = ('jal', 'j', 'bltzal', 'bgezal', 'bltzall', 'bgezall')
ADDR_NAMED = re.compile(r'(?:^|_)([0-9A-F]{8})$')
SHAPE = re.compile(r'^(data_gap|noopHandler|returnOne|returnZero)_')


def load_syms(path):
    text = open(path).read()
    pat = r'name = "([^"]+)", vram = 0x([0-9A-Fa-f]+), size = 0x([0-9A-Fa-f]+)'
    return [(int(v, 16), int(s, 16), n) for n, v, s in re.findall(pat, text)]


def scan(tree):
    """name -> first pc, and every (caller, pc, target) from the jump and branch-and-link comments N64Recomp emits."""
    first, sites, invalid = {}, [], {}
    for path in sorted(glob.glob(os.path.join(tree, 'funcs_*.c'))):
        cur = None
        for line in open(path, errors='replace'):
            m = DEF.match(line)
            if m:
                cur = m.group(1)
                continue
            m = ASM.match(line)
            if not m or cur is None:
                continue
            pc = int(m.group(1), 16)
            first.setdefault(cur, pc)
            if m.group(2) == '.word':
                invalid.setdefault(cur, pc)
            elif m.group(2) in LINKS and m.group(4) and m.group(3) != '$zero, ':  # bltzal $zero is never taken
                sites.append((cur, pc, int(m.group(4), 16)))
    return first, sites, invalid


def rom_pointers(rom):
    data = open(rom, 'rb').read()
    return {w for (w,) in struct.iter_unpack('>I', data[:len(data) & ~3]) if 0x80000000 <= w < 0x80200000}


def classify(name, addr, sites, sizes, first, invalid, syms, pointers):
    real, fake = [], []
    for caller, pc, target in sites:
        if target != addr or caller == name:
            continue
        size = sizes.get(caller)
        start = first.get(caller, pc)
        past_size = size is not None and pc >= start + size
        past_word = caller in invalid and pc >= invalid[caller]
        in_gap = SHAPE.match(caller) or caller.startswith('fake_func_') or caller.endswith('Preamble')
        (fake if past_size or past_word or in_gap else real).append((caller, pc))
    inside = [n for v, s, n in syms if v < addr < v + s]
    if real:
        kind = 'real'
    elif fake:
        kind = 'decoded-data-target'
    elif addr in pointers:
        kind = 'pointer-only'
    else:
        kind = 'unreferenced'
    return kind, real, fake, inside


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree')
    ap.add_argument('rom')
    ap.add_argument('--syms', default='syms/rogue_squadron.syms.toml')
    ap.add_argument('--md')
    args = ap.parse_args()
    syms = load_syms(args.syms)
    sizes = {n: s for _, s, n in syms}
    first, sites, invalid = scan(args.tree)
    pointers = rom_pointers(args.rom)
    rows = []
    for name in sorted(first, key=lambda n: first[n]):
        m = ADDR_NAMED.search(name)
        if not m:
            continue
        addr = int(m.group(1), 16)
        kind, real, fake, inside = classify(name, addr, sites, sizes, first, invalid, syms, pointers)
        if SHAPE.match(name):
            kind = 'shape-named'
        rows.append((name, addr, kind, real, fake, inside))
    counts = {}
    for row in rows:
        counts[row[2]] = counts.get(row[2], 0) + 1
    out = [f'{len(first)} functions, {len(rows)} address-named: ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())), '']
    out.append('| Name | Class | Real callers | Decoded-data callers | Inside |')
    out.append('|---|---|---|---|---|')
    for name, addr, kind, real, fake, inside in rows:
        if kind == 'shape-named':
            continue
        fmt = lambda xs: ' '.join(f'{c}@{p:08X}' for c, p in xs[:3]) or '-'
        out.append(f'| {name} | {kind} | {fmt(real)} | {fmt(fake)} | {" ".join(inside[:2]) or "-"} |')
    text = '\n'.join(out) + '\n'
    if args.md:
        open(args.md, 'w').write(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main()
