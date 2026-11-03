#!/usr/bin/env python3
"""s6831 G1e FPS60: advanceNpcOnCurvedPath +0x1E speed-ramp durations from ROGUESQ_TICK_TRACE dumps
(tools/fixup_fps60_int_step.py hook pc 0x8006C124, value = +0x1E as loaded, before the +0x20 step).
Per arm: executions per game second of 0x8006C124 and of the s6821 +0x1C countdown 0x8006C024 (control: per-tick site),
and per NPC record, ramp episodes in GAME seconds:
  up   = first positive value below 0x20 (a fresh +1 seed) -> first value 0xFF (clamped)  [30 Hz: 8 ticks = 0.267 s]
  down = first negative value -> first value 0 after it                                     [|v|/32 ticks]
A frame-locked ramp halves at FPS60; a fixed one matches 30 Hz.
Usage: g1e_int_step_rates.py ARM.tick.bin [ARM2.tick.bin ...]"""
import struct, sys, statistics as st, collections
PC, CTRL = 0x8006C124, 0x8006C024
for p in sys.argv[1:]:
    b = open(p, 'rb').read(); b = b[:len(b) // 16 * 16]
    tt, ev, n = {}, collections.defaultdict(list), collections.Counter()
    for pc, a, v, k in struct.iter_unpack('<IIII', b):
        if pc == 0: tt[k] = struct.unpack('<f', struct.pack('<I', a))[0]
        elif pc in (PC, CTRL):
            n[pc] += 1
            if pc == PC: ev[a].append((k, (v & 0xFFFF) - ((v & 0x8000) << 1)))
    gs = (max(tt.values()) - min(tt.values())) if tt else 0
    up, down = [], []
    for a, rows in ev.items():
        s_up = s_dn = None
        for k, v in rows:
            if k not in tt: continue
            if 0 < v < 0x20: s_up = s_up if s_up is not None else tt[k]
            elif v == 0xFF and s_up is not None: up.append(tt[k] - s_up); s_up = None
            elif v <= 0: s_up = None
            if v < 0: s_dn = s_dn if s_dn is not None else tt[k]
            elif v == 0 and s_dn is not None: down.append(tt[k] - s_dn); s_dn = None
            elif v > 0: s_dn = None
    f = lambda xs: 'n=%d med=%.3f min=%.3f max=%.3f' % (len(xs), st.median(xs), min(xs), max(xs)) if xs else 'n=0'
    print('%s: game_s=%.1f ticks=%d | 8006C124 %.1f/gs  8006C024 %.1f/gs | npcs=%d | up %s | down %s' % (
        p.rsplit('/', 1)[-1], gs, len(tt), n[PC] / gs if gs else 0, n[CTRL] / gs if gs else 0, len(ev), f(up), f(down)))
