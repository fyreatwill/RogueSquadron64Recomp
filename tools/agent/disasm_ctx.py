#!/usr/bin/env python3
"""Print N lines of scratch/agent/full_disasm.txt around each given address.
usage: disasm_ctx.py BEFORE AFTER ADDR [ADDR...]"""
import sys
L = open('scratch/agent/full_disasm.txt').read().split('\n')
idx = {l[:8]: i for i, l in enumerate(L) if len(l) > 8 and l[8] == ':'}
b, a = int(sys.argv[1]), int(sys.argv[2])
for ad in sys.argv[3:]:
    i = idx[ad.upper()]
    print('==', ad)
    for l in L[i - b:i + a]:
        print(l[:64])
