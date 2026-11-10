#!/usr/bin/env python3
"""s7075: summarise guest functions from the ELF disassembly: calls (current names), constant
addresses (lui/addiu|ori|lw|sw pairs), and strings in the menu overlay ROM image.
usage: s7075_fnsum.py <start_hex> <stop_hex> [--asm]"""
import re, subprocess, sys, glob, os
R = os.path.dirname(os.path.abspath(__file__)) + '/../../rogue_squadron64'
ELF = R + '/build/roguesquadron.elf'
names = {}
for f in glob.glob(R + '/symbol_files/*.txt'):
    for l in open(f, errors='replace'):
        m = re.match(r'\s*(\w+)\s*=\s*0x([0-9A-Fa-f]{8})', l)
        if m: names.setdefault(int(m.group(2), 16), m.group(1))
rom = open(ELF, 'rb').read()  # .ovl.menu file offset 0x10b410 (ELF, not the ROM)
def s_at(va):
    if rom is None or not (0x800A5130 <= va < 0x800D0000): return None
    off = va - 0x800A5130 + 0x10b410
    b = rom[off:off + 64].split(b'\0')[0]
    if len(b) >= 3 and all(32 <= c < 127 for c in b): return b.decode()
    return None
a, b = int(sys.argv[1], 16), int(sys.argv[2], 16)
out = subprocess.run(['mips64-elf-objdump', '-d', '-j', '.ovl.menu', '--start-address=%#x' % a,
                      '--stop-address=%#x' % b, ELF], capture_output=True, text=True).stdout
hi = {}
for l in out.splitlines():
    m = re.match(r'\s*([0-9a-f]{8}):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)', l)
    if not m:
        m2 = re.match(r'([0-9a-f]{8}) <(.*)>:', l)
        if m2:
            va = int(m2.group(1), 16); print('\n== %08X %s' % (va, names.get(va, m2.group(2)))); hi = {}
        continue
    pc, op, args = int(m.group(1), 16), m.group(2), m.group(3)
    if '--asm' in sys.argv: print('   %08X %-6s %s' % (pc, op, args))
    if op == 'jal':
        t = int(args.split()[0], 16); print('   %08X call %s' % (pc, names.get(t, hex(t))))
    elif op == 'lui':
        r, v = [x.strip() for x in args.split(',')]; hi[r] = int(v, 0) << 16
    else:
        mm = re.match(r'(\w+),(\w+),(-?0x[0-9a-f]+|-?\d+)$', args.replace(' ', ''))
        mo = re.match(r'(\w+),(-?0x[0-9a-f]+|-?\d+)\((\w+)\)$', args.replace(' ', ''))
        base = imm = None
        if mm and op in ('addiu', 'ori') and mm.group(2) in hi: base, imm = mm.group(2), int(mm.group(3), 0)
        elif mo and mo.group(3) in hi: base, imm = mo.group(3), int(mo.group(2), 0)
        if base is not None:
            va = (hi[base] + (imm if op != 'ori' else imm & 0xffff)) & 0xffffffff
            s = s_at(va)
            print('   %08X %-5s %08X %s%s' % (pc, op, va, names.get(va, ''), (' "%s"' % s) if s else ''))
