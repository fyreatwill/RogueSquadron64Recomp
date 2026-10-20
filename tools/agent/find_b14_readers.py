#!/usr/bin/env python3
"""Find loads of byte/half/word at +4 from a register set to 0x80130B10 (addiu r,r,2832 after lui 0x8013)
or directly 2836(lui 0x8013). Tracks register until redefined (window 300 insns)."""
import re
L = open('scratch/agent/full_disasm.txt').read().split('\n')
a = re.compile(r'^([0-9A-F]{8}): \w{8}\s+addiu r(\d+), r\d+, 2832$')
ins = re.compile(r'^([0-9A-F]{8}): \w{8}\s+(\w+) (.*)$')
ld = re.compile(r'^(lb|lbu|lh|lhu|lw|lwu) r(\d+), (-?\d+)\(r(\d+)\)$')
wr = re.compile(r'^(?:\w+) r(\d+),')
for i, l in enumerate(L):
    m = a.match(l)
    if not m: continue
    r = m.group(2)
    for j in range(i + 1, min(i + 300, len(L))):
        n = ins.match(L[j])
        if not n: continue
        t = n.group(2) + ' ' + n.group(3)
        d = ld.match(t)
        if d and d.group(4) == r and d.group(3) == '4':
            print(l[:8], '->', L[j][:64])
        if d and d.group(2) == r and d.group(4) != r: break
        w = wr.match(t)
        if w and w.group(1) == r and not t.startswith(('sw ', 'sb ', 'sh ', 'beq', 'bne', 'bl', 'jr')) and not d: break
