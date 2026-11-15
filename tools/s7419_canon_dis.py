#!/usr/bin/env python3
"""s7419 class CB: the ONE canonical objdump listing for the objdump-based censuses (s7392-s7405, s7418, s7419).

Why (s7419): the ELF header says `o32, mips1`, so plain `objdump -d` decodes MIPS I only and leaves every MIPS II/III op
as `.word` / `c1 0x..` (ldc1 1334, sdc1 1202, trunc.w.s 1073, beql/bnel/bc1tl/bc1fl/bltzl/bgezl/blezl/bgtzl 2445, sqrt.s 94,
cache 33, ld/sd/dsll* 140, eret ...). It also dumps any OBJECT symbol inside a code section as bytes, which hides real code
labelled OBJECT inside a FUNC (texPackTlutAtAllocSlot inside getTextureAttrBySlot; the __osException sub-handler labels
counter/rcp/prenmi/sw1/sw2/redispatch, which then got misattributed as LIVE functions named `rcp` / `prenmi`), and it skips
zero runs as `...`. Canonical listing: a temp ELF copy with every SIZE-0 OBJECT label that lies strictly inside a FUNC's
[start, start+size) in an executable section stripped (unless that FUNC also holds a sized object, i.e. runs into data), then `objdump -d -z -m mips:4300 -M cp0-names=r3000`
(r3000 cp0 names keep the s7405 spelling c0_sr / $9 / $11).

Usage: tools/s7419_canon_dis.py [out=/tmp/s7419_canon.dis] [--force]   (prints the path; regenerates when missing/stale)
Library: ensure(path) -> path.
"""
import os, sys, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELF = os.path.join(ROOT, '../rogue_squadron64/build/roguesquadron.elf')
DEFAULT = '/tmp/s7419_canon.dis'
STAMP = '# s7419-canon'

def inner_objects(elf=ELF):
    secs = {}
    for ln in subprocess.run(['mips64-elf-readelf', '-SW', elf], capture_output=True, text=True, check=True).stdout.splitlines():
        p = ln.replace('[ ', '[').split()
        if len(p) > 7 and p[0].startswith('[') and p[0].endswith(']') and p[0][1:-1].isdigit():
            secs[p[0][1:-1]] = 'X' in p[7]
    funcs, objs = [], []
    for ln in subprocess.run(['mips64-elf-readelf', '-sW', elf], capture_output=True, text=True, check=True).stdout.splitlines():
        p = ln.split()
        if len(p) < 8 or not p[0].endswith(':') or not secs.get(p[6]): continue
        a, sz, ty, nm = int(p[1], 16), int(p[2], 0), p[3], p[7]
        (funcs if ty == 'FUNC' else objs if ty == 'OBJECT' else []).append((a, sz, nm, p[6]))
    def host(a, sec): return [(f, fs, fn) for f, fs, fn, s in funcs if s == sec and f < a < f + fs]
    # a FUNC whose range holds a SIZED object runs into data (synthetic ELF: __OSGlobalIntMask, osYieldThread, audioCompandS16,
    # lvj_checkComplexObjectives, ...); its labels stay, so its data keeps printing as bytes exactly as before
    datahosts = set(h[2] for a, sz, nm, sec in objs if sz > 0 for h in host(a, sec))
    out = []
    for a, sz, nm, sec in objs:
        hs = host(a, sec)
        if sz == 0 and hs and not any(h[2] in datahosts or h[2].startswith("data_gap_") for h in hs): out.append(nm)
    return sorted(set(out))

def ensure(path=DEFAULT, force=False):
    if not force and os.path.exists(path) and os.path.getmtime(path) >= os.path.getmtime(ELF):
        with open(path) as f:
            if f.readline().startswith(STAMP): return path
    strip = inner_objects()
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, 'canon.elf')
        cmd = ['mips64-elf-objcopy'] + ['--strip-symbol=' + s for s in strip] + [ELF, tmp]
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)   # objcopy warns about LMA re-layout; VMAs (what objdump prints) unchanged
        dis = subprocess.run(['mips64-elf-objdump', '-d', '-z', '--no-show-raw-insn', '-m', 'mips:4300', '-M', 'cp0-names=r3000', tmp],
                             capture_output=True, text=True, check=True).stdout
    with open(path, 'w') as f:
        f.write('%s stripped_inner_objects=%d %s\n' % (STAMP, len(strip), ','.join(strip)))
        f.write(dis)
    return path

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    print(ensure(a[0] if a else DEFAULT, '--force' in sys.argv))
