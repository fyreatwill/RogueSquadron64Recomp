#!/usr/bin/env python3
"""s7520 class FQ, offline line: the regen ELF's code bytes (what N64Recomp compiled) vs the ROM the port loads, over
every recompiled function extent listed in recomp_overlays.inl (FuncEntry offset / rom_size per section).
rc 0 = every word equal; 1 = differences (printed); 3 = --controls failed.  --controls flips one byte in memory copies
of each image and requires the comparer to report exactly one bad word per flip."""
import re, struct, subprocess, sys
INL = '../N64Recomp/RecompiledFuncs/recomp_overlays.inl'
ELF = '../rogue_squadron64/build/roguesquadron.elf'
ROM = 'build/rogue_squadron.z64'

def sections():
    t = open(INL).read()
    funcs = {}
    for m in re.finditer(r'static FuncEntry (section_(\d+)_\w+)\[\] = \{(.*?)\n\};', t, re.S):
        funcs[m.group(1)] = [(int(a, 16), int(b, 16)) for a, b in
                             re.findall(r'\.offset = 0x([0-9A-Fa-f]+), \.rom_size = 0x([0-9A-Fa-f]+)', m.group(3))]
    secs = []
    for m in re.finditer(r'\{ \.rom_addr = 0x([0-9A-F]+), \.ram_addr = 0x([0-9A-F]+), \.size = 0x([0-9A-F]+), \.funcs = (\w+),', t):
        secs.append((int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16), m.group(4), funcs[m.group(4)]))
    return secs

def elf_sections(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 2
    shoff, = struct.unpack_from('>I', d, 0x20); shentsize, shnum, shstrndx = struct.unpack_from('>HHH', d, 0x2E)
    hdr = [struct.unpack_from('>IIIIIIIIII', d, shoff + i * shentsize) for i in range(shnum)]
    stro = hdr[shstrndx][4]
    out = {}
    for h in hdr:
        name = d[stro + h[0]: d.index(b'\0', stro + h[0])].decode()
        out[name] = (h[3], d[h[4]: h[4] + h[5]])  # addr, bytes
    return out

def compare(secs, elf, rom):
    rows, words = [], 0
    for rom_addr, ram, size, fname, fl in secs:
        cand = [n for n, (a, b) in elf.items() if a == ram and len(b) == size]
        if len(cand) != 1:
            rows.append(f'NOSEC {fname} ram={ram:08X} size={size:X} cand={cand}'); continue
        eb = elf[cand[0]][1]
        for off, sz in fl:
            for o in range(off, off + sz - 3, 4):
                words += 1
                if eb[o:o + 4] != rom[rom_addr + o: rom_addr + o + 4]:
                    rows.append(f'DIFF {cand[0]} va={ram + o:08X} elf={eb[o:o+4].hex()} rom={rom[rom_addr+o:rom_addr+o+4].hex()}')
    return rows, words

def main():
    secs = sections(); elf = elf_sections(ELF); rom = bytearray(open(ROM, 'rb').read())
    if '--controls' in sys.argv:
        ok = True
        for k, (rom_addr, ram, size, fname, fl) in enumerate(secs):
            off, sz = fl[len(fl) // 2]
            r2 = bytearray(rom); r2[rom_addr + off + 1] ^= 0x10
            rows, _ = compare(secs, elf, r2)
            good = len(rows) == 1 and rows[0].startswith('DIFF') and f'va={ram + off:08X}' in rows[0]
            print(f'ctl {fname}: {"PASS" if good else "FAIL"} rows={len(rows)}'); ok &= good
        if not ok: sys.exit(3)
    rows, words = compare(secs, elf, rom)
    nf = sum(len(s[4]) for s in secs)
    print(f'sections={len(secs)} funcs={nf} words={words} diffs={len(rows)}')
    for r in rows[:40]: print(r)
    sys.exit(1 if rows else 0)
main()
