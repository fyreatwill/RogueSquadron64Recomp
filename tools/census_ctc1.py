#!/usr/bin/env python3
"""M3 idiom census: COP1 control-register moves (ctc1/cfc1 $31). Runtime lowering (recomp.h set_cop1_cs/get_cop1_cs)
keeps ONLY rounding-mode bits [1:0] (via fesetround, per-host-thread) and drops flags/enables/FS/cond.
For each ctc1 site, backtracks <=6 words for the register's constant (addiu/ori/lui+ori) and reports the value;
cfc1 sites are listed with the next 4 words so consumers of dropped bits (andi 0x800000 / 0x7C / 0x1F000) show.
Usage: census_ctc1.py <rom.z64>"""
import struct, sys, collections
rom = open(sys.argv[1] if len(sys.argv) > 1 else "rs64.n64.us.1.0.z64", "rb").read()
n = len(rom)//4; w = struct.unpack(">%dI" % n, rom[:n*4])
def const(i, reg):
    for j in range(i-1, max(i-7, 0), -1):
        x = w[j]; op = x>>26; rt = (x>>16)&31; rs=(x>>21)&31
        if op in (8,9,13) and rt == reg:   # addiu/ori
            if rs == 0: return x & 0xFFFF if op==13 else (x & 0xFFFF)
            if op==13:
                for k in range(j-1, max(j-4,0), -1):
                    if w[k]>>26 == 15 and ((w[k]>>16)&31)==rs: return ((w[k]&0xFFFF)<<16)|(x&0xFFFF)
            return None
        if op == 15 and rt == reg: return (x&0xFFFF)<<16
        if (x>>11)&31 == reg and op == 0: return None
    return None
ct = collections.Counter(); unk = []; cf = []
for i, x in enumerate(w):
    if x>>26 != 0x11 or (x & 0xFFFF) != 0xF800: continue
    sub = (x>>21)&31; rt = (x>>16)&31
    if sub == 6:   # ctc1
        c = const(i, rt); ct[None if c is None else hex(c)] += 1
        if c is None: unk.append(i*4)
    elif sub == 2: cf.append(i*4)
print("ctc1 $31 constants:", dict(ct)); print("ctc1 unresolved at:", [hex(a) for a in unk[:20]])
print("cfc1 $31 sites:", len(cf))
for a in cf[:20]:
    print(hex(a), " ".join("%08X" % w[a//4+k] for k in range(0,5)))
