#!/usr/bin/env python3
"""s7403 class BM: boot-global contract census.
Enumerate every LIVE guest (non-replaced, s7401 live()) read / address-take of the IPL3 low-memory block
0x80000300-0x8000033F and of the libultra .data words 0x80039100-0x8003910F (osClockRate, osViClock), with the
reading function and insn. Rows per word: retail value (IPL3 6102 NTSC cold boot / osInitialize) vs port value
(librecomp recomp.cpp init + s7402 clockfix).
Usage: tools/s7403_boot_globals.py [disasm=/tmp/s7419_canon.dis]"""
import sys, os, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
c7392 = importlib.import_module('s7392_mesg_census')
c7400 = importlib.import_module('s7400_replaced_contract')
c7401 = importlib.import_module('s7401_replaced_args')
c7402 = importlib.import_module('s7402_side_effects')
NAMES = {0x80000300: 'osTvType', 0x80000304: 'osRomType', 0x80000308: 'osRomBase', 0x8000030C: 'osResetType',
         0x80000310: 'osCicId', 0x80000314: 'osVersion', 0x80000318: 'osMemSize', 0x8000031C: 'osAppNMIBuffer',
         0x80039100: 'osClockRate.hi', 0x80039104: 'osClockRate.lo', 0x80039108: 'osViClock'}
RANGES = [(0x80000300, 0x80000340), (0x80039100, 0x80039110)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ins = c7392.parse(args[0] if args else c7392.DIS)
    allb = c7400.bodies()
    ign = __import__('s7404_rcp_access').ignored()   # s7419: N64Recomp ignored_funcs (e.g. __osException) never run in the port
    acc = c7402.scan(ins)
    live = {}
    rows = collections.defaultdict(list)
    for fn, lst in acc.items():
        for kind, v, a in lst:
            if not any(lo <= v < hi for lo, hi in RANGES):
                continue
            if fn not in live:
                live[fn] = fn not in allb and fn not in ign and c7401.live(ins, fn, allb)
            rows[v].append((kind, fn, a, live[fn], 'REPLACED' if fn in allb else 'IGNORED' if fn in ign else 'dead'))
    for v in sorted(rows):
        nm = NAMES.get(v, NAMES.get(v & ~3, '?') + '+%d' % (v & 3) if (v & ~3) in NAMES else '?')
        if 0x8000031C <= v < 0x8000035C:
            nm = 'osAppNMIBuffer+0x%X' % (v - 0x8000031C)
        for kind, fn, a, lv, rep in sorted(rows[v], key=lambda r: (not r[3], r[1])):
            tag = 'LIVE' if lv else rep
            print('%08X %-20s %s %-8s %-40s @%s' % (v, nm, kind, tag, fn, a))
    print('--- words=%d live_rows=%d' % (len(rows), sum(1 for v in rows for r in rows[v] if r[3])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
