#!/usr/bin/env python3
"""s6824 G3 FPS60: per-press check of a button-edge-gated tick-trace site (default 800B5350, the +0x15C C-down cycle).
Reads a ROGUESQ_TICK_TRACE dump (tools/fixup_fps60_ticks.py; rows pc=2 = held word 0x80130B88 + config +0x1E/+0x1A)
and reports, per tick where the config +0x1E bit is set in the held word: whether the site ran and the value it loaded,
so a press that runs but does not advance the counter (game-time step 0) shows as a repeated value.
Usage: g3_press_cycle.py ARM.tick.bin [ARM2 ...] [--site 800B5350]"""
import struct, sys
args = [a for a in sys.argv[1:] if not a.startswith('--')]
site = int(next((a.split('=')[1] for a in sys.argv[1:] if a.startswith('--site=')), '800B5350'), 16)
for p in args:
    b = open(p, 'rb').read(); b = b[:len(b) // 16 * 16]
    held, mask, tt, ex = {}, {}, {}, {}
    for pc, a, v, k in struct.iter_unpack('<IIII', b):
        if pc == 0: tt[k] = struct.unpack('<f', struct.pack('<I', a))[0]
        elif pc == 2: held[k] = a; mask[k] = v >> 16
        elif pc == site: ex[k] = v
    press = [k for k in sorted(held) if held[k] & mask[k]]
    vals = [ex[k] for k in sorted(ex)]
    adv = sum(1 for i in range(1, len(vals)) if vals[i] != vals[i - 1])
    print(f"{p}: press ticks {len(press)}, site ran {len(ex)} (on press ticks {sum(1 for k in press if k in ex)}), "
          f"loaded values {vals}, advanced {adv}/{max(len(vals) - 1, 0)}")
