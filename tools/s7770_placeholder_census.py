#!/usr/bin/env python3
"""s7770: classify every placeholder (func_XXXXXXXX) entry of syms/rogue_squadron.syms.toml against the ELF itself.

s6268 and s6868 called the leftovers "shape-only / none a real function". s6868 only scanned the GENERATED tree, so it
could not see entries that N64Recomp never emits (the libultra exception block 0x8002B5F0.. is not recompiled), and
s6268 read 0x8002BB34 from an objdump view that printed it as data. This tool reads the ELF bytes directly:
  callers   jal/j words anywhere in a code section whose target == the entry address
  hilo      lui rX,hi + addiu/ori rY,rX,lo pairs (within 8 insns) building the address (function pointer)
  ptrs      raw 32-bit words equal to the address in any section (jump/dispatch tables)
  after_ret the predecessor ends in `jr ra; <delay>` right before the entry (a standalone start, not a fall-through)
  back      the body branches/jumps back into the predecessor (a tail fragment of it)
Verdict: CALLED (real, reachable, nameable), UNREF (standalone start, no reference found: dead or reached by a computed
address this scan cannot see), TAIL (a fragment of the predecessor; shape-only).

usage: s7770_placeholder_census.py [--elf E] [--syms S] [--controls] [--quiet]
  --controls  also classify 3 control rows and fail (rc 3) unless: __osEnqueueThread -> CALLED (positive),
              resampleVoiceLutSamplesPacked+0x20 (mid-body) -> not CALLED (negative), 0x80092F10 -> TAIL.
Prints `SUMMARY placeholders=N called=C unref=U tail=T`. rc 0 always for the census itself (the stop gate reads called=)."""
import argparse, re, struct, sys

ap = argparse.ArgumentParser()
ap.add_argument('--elf', default='../rogue_squadron64/build/roguesquadron.elf')
ap.add_argument('--syms', default='syms/rogue_squadron.syms.toml')
ap.add_argument('--controls', action='store_true')
ap.add_argument('--quiet', action='store_true')
a = ap.parse_args()

d = open(a.elf, 'rb').read()
shoff, = struct.unpack('>I', d[0x20:0x24])
shentsize, shnum, shstrndx = struct.unpack('>HHH', d[0x2E:0x34])
secs = []
for i in range(shnum):
    o = shoff + i * shentsize
    name, typ, flags, addr, off, size = struct.unpack('>IIIIII', d[o:o + 24])
    secs.append([name, typ, flags, addr, off, size])
stro = secs[shstrndx][4]
def sname(n):
    return d[stro + n:d.index(b'\0', stro + n)].decode()
CODE = [(sname(s[0]), s[3], s[4], s[5]) for s in secs if s[1] == 1 and s[2] & 4]   # PROGBITS + EXECINSTR
DATA = [(sname(s[0]), s[3], s[4], s[5]) for s in secs if s[1] == 1]


def words(sec):
    _, va, off, size = sec
    for i in range(0, size - 3, 4):
        yield va + i, struct.unpack('>I', d[off + i:off + i + 4])[0]


def word_at(vram):
    """first code section holding vram (.text before overlays; placeholders here are all in .text)."""
    for _, va, off, size in CODE:
        if va <= vram < va + size:
            return struct.unpack('>I', d[off + vram - va:off + vram - va + 4])[0]
    return None


syms = sorted((int(v, 16), int(s, 16), n) for n, v, s in
              re.findall(r'name = "([^"]+)", vram = 0x([0-9A-Fa-f]+), size = 0x([0-9A-Fa-f]+)', open(a.syms).read()))
byname = {n: (v, s) for v, s, n in syms}

# one pass over every code word: jal/j targets and lui/addiu|ori address pairs
jtarget, hilo = {}, {}
for sec in CODE:
    ws = list(words(sec))
    for k, (pc, w) in enumerate(ws):
        op = w >> 26
        if op in (2, 3):
            t = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
            jtarget.setdefault(t, []).append((pc, 'jal' if op == 3 else 'j'))
        elif op == 0x0F:                                   # lui rt, hi
            rt, hi = (w >> 16) & 31, w & 0xFFFF
            for pc2, w2 in ws[k + 1:k + 9]:
                op2 = w2 >> 26
                if op2 in (0x09, 0x0D) and (w2 >> 21) & 31 == rt:
                    lo = w2 & 0xFFFF
                    v = ((hi << 16) + (lo - 0x10000 if op2 == 0x09 and lo & 0x8000 else lo)) & 0xFFFFFFFF
                    hilo.setdefault(v, []).append(pc)
                    break
ptrword = {}
for sec in DATA:
    for pc, w in words(sec):
        if 0x80000000 <= w < 0x80400000:
            ptrword.setdefault(w, []).append(pc)


def classify(vram, size, label):
    prev = max((s for s in syms if s[0] < vram), default=None)
    callers = jtarget.get(vram, [])
    jal = [c for c in callers if c[1] == 'jal']
    hl = hilo.get(vram, [])
    pw = ptrword.get(vram, [])
    after_ret = word_at(vram - 8) == 0x03E00008
    back = 0
    if prev:
        p0, p1 = prev[0], vram
        for pc in range(vram, vram + size, 4):
            w = word_at(pc)
            if w is None:
                continue
            op = w >> 26
            if op in (2, 3):
                t = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
            elif op in (4, 5, 6, 7, 0x14, 0x15, 0x16, 0x17) or (op == 1 and (w >> 16) & 31 in (0, 1, 2, 3)):
                off = w & 0xFFFF
                t = pc + 4 + ((off - 0x10000 if off & 0x8000 else off) << 2)
            else:
                continue
            if p0 <= t < p1:
                back += 1
    if callers or hl or pw:
        v = 'CALLED'
    elif back and not after_ret:
        v = 'TAIL'
    elif back:
        v = 'TAIL'
    else:
        v = 'UNREF'
    row = dict(label=label, vram=vram, size=size, prev=prev[2] if prev else '-', jal=len(jal), j=len(callers) - len(jal),
               hilo=len(hl), ptrs=len(pw), after_ret=int(after_ret), back=back, verdict=v,
               first=hex(callers[0][0]) if callers else '-')
    if not a.quiet:
        print('%-26s 0x%08X size=0x%-4X prev=%-34s jal=%-3d j=%-2d hilo=%-2d ptrs=%-2d after_ret=%d back=%-2d first=%-10s %s'
              % (label, vram, size, row['prev'], row['jal'], row['j'], row['hilo'], row['ptrs'], row['after_ret'], back,
                 row['first'], v))
    return row


rows = [classify(v, s, n) for v, s, n in syms if re.fullmatch(r'(fake_)?func_[0-9A-Fa-f]{8}', n)]
c = {k: sum(r['verdict'] == k for r in rows) for k in ('CALLED', 'UNREF', 'TAIL')}
print('SUMMARY placeholders=%d called=%d unref=%d tail=%d' % (len(rows), c['CALLED'], c['UNREF'], c['TAIL']))
rc = 0
if a.controls:
    v, s = byname['__osEnqueueThread']
    pos = classify(v, s, 'CTL+__osEnqueueThread')
    v, s = byname['resampleVoiceLutSamplesPacked']
    neg = classify(v + 0x20, 0x20, 'CTL-midbody+0x20')
    tail = classify(0x80092F10, 0x84, 'CTL-tail80092F10')
    ok = pos['verdict'] == 'CALLED' and neg['verdict'] != 'CALLED' and tail['verdict'] == 'TAIL'
    print('CONTROLS %s (pos=%s neg=%s tail=%s)' % ('PASS' if ok else 'FAIL', pos['verdict'], neg['verdict'], tail['verdict']))
    rc = 0 if ok else 3
sys.exit(rc)
