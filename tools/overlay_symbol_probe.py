#!/usr/bin/env python3
"""Check whether a VRAM address is a genuine function start inside an overlay.

Overlays all load at RAM 0x800A5130; each has its own ROM base. A real function
start is preceded by `jr $ra` + delay slot and usually begins with an
`addiu sp, sp, -N` prologue. Adding a symbol that is NOT a function start splits
the enclosing function and truncates its tail — the failure mode that broke the
bulk symbol move.

Usage: ovl_probe.py 0x800B3650 [mission|menu|cinematic]
"""
import sys, struct

ROM = '/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64'
RAM_BASE = 0x800A5130
OVERLAYS = {           # name: (rom_base, size)
    'mission':   (0x000A5D30, 0x000665A0),
    'menu':      (0x0010C2D0, 0x000283F0),
    'cinematic': (0x00137580, 0x0000B810),
}

def words(data, off, n):
    return struct.unpack('>%dI' % n, data[off:off + 4 * n])

def describe(w):
    op = w >> 26
    if w == 0:
        return 'nop'
    if w == 0x03E00008:
        return 'jr $ra'
    if op == 0x09 and ((w >> 21) & 31) == 29 and ((w >> 16) & 31) == 29:
        imm = w & 0xFFFF
        imm = imm - 0x10000 if imm & 0x8000 else imm
        return 'addiu $sp, $sp, %d   <-- PROLOGUE' % imm
    if op == 0x2B and ((w >> 21) & 31) == 29:
        return 'sw   ...($sp)'
    if op == 0x03:
        return 'jal 0x%08X' % (0x80000000 | ((w & 0x03FFFFFF) << 2))
    return 'op=0x%02X raw=0x%08X' % (op, w)

def main():
    addr = int(sys.argv[1], 16)
    names = [sys.argv[2]] if len(sys.argv) > 2 else list(OVERLAYS)
    data = open(ROM, 'rb').read()
    for name in names:
        rom_base, size = OVERLAYS[name]
        off = addr - RAM_BASE
        if off < 0 or off + 8 > size:
            print('%-10s address outside this overlay' % name)
            continue
        rom_off = rom_base + off
        pre = words(data, rom_off - 12, 3)
        at = words(data, rom_off, 4)
        # The reliable signal is the PROLOGUE at +0 (`addiu $sp, $sp, -N`).
        # A preceding `jr $ra` corroborates but is not required — the previous
        # function can end with a tail this 3-word window doesn't reach.
        prologue = (at[0] >> 26) == 0x09 and ((at[0] >> 21) & 31) == 29 and \
                   ((at[0] >> 16) & 31) == 29 and (at[0] & 0x8000) != 0
        ret_before = (0x03E00008 in pre)
        verdict = 'YES' if prologue else ('maybe' if ret_before else 'no')
        print('%-10s rom 0x%06X  function-start=%s (prologue=%d jr$ra-before=%d)'
              % (name, rom_off, verdict, prologue, ret_before))
        for i, w in enumerate(pre):
            print('    -%d  %08X  %s' % (12 - i * 4, w, describe(w)))
        for i, w in enumerate(at):
            print('    +%d  %08X  %s' % (i * 4, w, describe(w)))
        print()

main()
