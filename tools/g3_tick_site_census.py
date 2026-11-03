#!/usr/bin/env python3
"""s6822 G3 FPS60: which levels run which whitelisted tick-timer sites (tools/fixup_fps60_ticks.py FIX). Reads
ROGUESQ_TICK_TRACE dumps (16-byte records pc, addr, value, tick; pc 0 = per-tick game-time record) and prints, per dump,
the execution count and distinct field addresses of every FIX site, plus a greedy minimal level cover.
Usage: g3_tick_site_census.py LABEL=dump.tick.bin [...]"""
import struct, sys, re, collections
src = open(__file__.rsplit('/', 1)[0] + '/fixup_fps60_ticks.py').read()
fix = {int(a, 16): n for a, n in re.findall(r'\s0x(800[0-9A-F]{5}): "([^"]+)"', src)}
hits = {}
for arg in sys.argv[1:]:
    lab, p = arg.split('=', 1)
    b = open(p, 'rb').read(); b = b[:len(b) // 16 * 16]
    cnt, flds, ticks = collections.Counter(), collections.defaultdict(set), 0
    for pc, a, v, k in struct.iter_unpack('<IIII', b):
        if pc == 0: ticks += 1
        elif pc in fix: cnt[pc] += 1; flds[pc].add(a)
    hits[lab] = cnt
    print(f'{lab}: ticks={ticks} ' + ' '.join(f'{pc:08X}:{cnt[pc]}/{len(flds[pc])}f' for pc in sorted(cnt)))
print('--- per site (levels with >=1 execution)')
for pc in sorted(fix):
    print(f'{pc:08X} {fix[pc]:55s} ' + ','.join(l for l in hits if hits[l][pc]))
left, cover = {pc for pc in fix if any(hits[l][pc] for l in hits)}, []
while left:
    l = max(hits, key=lambda l: sum(1 for pc in left if hits[l][pc]))
    cover.append(l); left -= {pc for pc in left if hits[l][pc]}
print('cover:', ' '.join(cover), '| never hit:', ' '.join(f'{pc:08X}' for pc in sorted(fix) if not any(hits[l][pc] for l in hits)))
