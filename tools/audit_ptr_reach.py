#!/usr/bin/env python3
"""s6870: can anything but a decoded data tail reach these addresses? Scans an ELF's load sections, and any raw big-endian
RDRAM images, for each address as a data word and as a lui + addiu/ori pair within 16 instructions. Controls name
addresses known to be taken as pointers; each must hit, or a zero on the targets means nothing.
usage: audit_ptr_reach.py <elf> --targets a,b,... --controls c,d,... [--rdram file ...]"""
import argparse, struct, sys


def sections(path):
    d = open(path, 'rb').read()
    shoff, = struct.unpack_from('>I', d, 32)
    shentsize, shnum = struct.unpack_from('>HH', d, 46)
    for i in range(shnum):
        _, typ, _, addr, off, size = struct.unpack_from('>IIIIII', d, shoff + i * shentsize)
        if typ == 1 and size:
            yield f'{addr:08X}', d[off:off + size - size % 4]


def scan(blob, want):
    hits = {a: [0, 0] for a in want}
    words = struct.unpack(f'>{len(blob) // 4}I', blob)
    his = {}
    for a in want:
        his.setdefault(a >> 16, []).append(a)
        his.setdefault(((a + 0x8000) >> 16) & 0xFFFF, []).append(a)
    for i, w in enumerate(words):
        if w in hits:
            hits[w][0] += 1
        if w >> 26 == 0x0F and (w & 0xFFFF) in his:
            for x in words[i + 1:i + 17]:
                op = x >> 26
                if op not in (0x09, 0x0D, 0x08) or (x >> 21) & 31 != (w >> 16) & 31:
                    continue
                lo = x & 0xFFFF
                val = (((w & 0xFFFF) << 16) | lo) if op == 0x0D else (((w & 0xFFFF) << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF
                if val in hits:
                    hits[val][1] += 1
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('elf')
    ap.add_argument('--targets', required=True)
    ap.add_argument('--controls', required=True)
    ap.add_argument('--rdram', nargs='*', default=[])
    a = ap.parse_args()
    tg = [int(x, 16) for x in a.targets.split(',')]
    ct = [int(x, 16) for x in a.controls.split(',')]
    total = {x: [0, 0] for x in tg + ct}
    blobs = list(sections(a.elf)) + [(p, open(p, 'rb').read()) for p in a.rdram]
    for name, blob in blobs:
        for k, v in scan(blob, tg + ct).items():
            total[k][0] += v[0]
            total[k][1] += v[1]
    print(f'{len(blobs)} blobs, {sum(len(b) for _, b in blobs)} bytes')
    for x in ct:
        print(f'control {x:08X}: data {total[x][0]} code {total[x][1]}')
    for x in tg:
        print(f'target  {x:08X}: data {total[x][0]} code {total[x][1]}')
    return 1 if any(sum(total[x]) == 0 for x in ct) else 0


if __name__ == '__main__':
    sys.exit(main())
