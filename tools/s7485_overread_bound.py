#!/usr/bin/env python3
"""s7485 class EJ: prove the guest byte over-reads past an rs_malloc request are bounded.

Reads the recompiler's disasm comments in the generated C (default ../N64Recomp/RecompiledFuncs)
and checks the two idioms the s7484 load watch saw reading into the PAD=16 slack band:

  swizzleTextureRowsToTmem 0x80024880: each row copies (a3>>4)*8 = a3/2 bytes, then rewinds
    t7 = a3/2 - (a2+1)/2, so the last row over-reads t7 bytes. Its only caller (parseImageFile)
    passes a3 = (a2 + 15) & 0xFFF0  ->  t7 <= 7 < PAD.
  decodeJpegScanToImage chroma upsampler (0x800C9680..0x800C9700): taps centre, +/-1 column
    (t1, zeroed only at column 0 / width-1) and +/-row (s4), reads only; prints the tap loads.

Exit 0 when every expected instruction is present, 1 otherwise (the regen moved something).
"""
import glob, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'N64Recomp', 'RecompiledFuncs')
lines = {}
for f in sorted(glob.glob(os.path.join(root, '*.c'))):
    for m in re.finditer(r'// 0x([0-9A-F]{8}): (.*)', open(f, errors='replace').read()):
        lines.setdefault(int(m.group(1), 16), m.group(2).split())

def has(pc, *toks):
    ins = lines.get(pc)
    ok = ins is not None and all(t in ' '.join(ins) for t in toks)
    print(f"  {pc:08X} {' '.join(ins) if ins else '<missing>':40s} {'ok' if ok else 'FAIL'}")
    return ok

ok = True
print('swizzleTextureRowsToTmem callee rewind (t7 = a3/2 - (a2+1)/2):')
ok &= has(0x80024888, 'srl', '$t7', '$a3,', '1')
ok &= has(0x8002488C, 'addiu', '$t0', '$a2', '0x1')
ok &= has(0x80024890, 'srl', '$t0,', '$t0,', '1')
ok &= has(0x80024894, 'subu', '$t7', '$t7', '$t0')
ok &= has(0x800248A0, 'srl', '$t4', '$a3,', '4')
print('parseImageFile caller (a3 = (a2+15) & 0xFFF0):')
ok &= has(0x8001EE8C, 'addiu', '$v0', '$a2', '0xF')
ok &= has(0x8001EE90, 'andi', '$s0', '$v0', '0xFFF0')
ok &= has(0x8001EED8, 'jal', '0x80024880')
ok &= has(0x8001EEDC, '$a3', '$s0')
worst = max((((a2 + 15) & 0xFFF0) // 2) - (a2 + 1) // 2 for a2 in range(1, 1025))
print(f'  worst-case over-read over a2=1..1024: {worst} bytes (PAD band 16)')
ok &= worst < 16
print('decodeJpegScanToImage chroma taps (reads only):')
for pc in (0x800C96A8, 0x800C96AC, 0x800C96B8, 0x800C96D4, 0x800C96E8, 0x800C9700):
    ok &= has(pc, 'lbu')
print('VERDICT', 'EJ-bounded' if ok else 'PATTERN-MOVED')
sys.exit(0 if ok else 1)
