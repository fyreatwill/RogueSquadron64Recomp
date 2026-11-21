#!/usr/bin/env python3
"""s7779: score a ROGUESQ_S7779_ARENA=1 (+ ROGUESQ_S7779_PLANT=<n>) log. FB-arena = retail rs_malloc(flag 4) scratch heap
(head 0x8010FEFC) over a free framebuffer slot, dropped each frame by clearFrameReadyFlag.
OWNER apis (the arena's own users: inflate's host zmemcpy, PI DMA of compressed data) are expected inside a live arena.
rc 0 = H-clean (plant counted, writeback ctl > 0, 0 non-owner host writes into a live arena, busy_slot_live 0);
rc 1 = H-stomp (a non-owner host write landed in a live arena, or the arena's slot was busy while live); rc 3 = control failed.
usage: s7779_arena_score.py <run.log>"""
import re, sys
OWNER = {"zmemcpy", "pi_rom_to_rdram", "s7779_plant"}
log = open(sys.argv[1], errors="replace").read().splitlines()
sums = [l for l in log if l.startswith("[s7779] sum")]
if not sums: print("no [s7779] sum lines"); sys.exit(3)
s = sums[-1]
api = {m[0]: tuple(int(x) for x in m[1:]) for m in re.findall(r" (\S+):hit=(\d+)/\d+B,ctl=(\d+)/\d+B,oth=(\d+)", s)}
ep = int(re.search(r"epochs=(\d+)", s)[1]); busy = int(re.search(r"busy_slot_live=(\d+)", s)[1])
gl = int(re.search(r"gst_live=(\d+)", s)[1])
plant = api.get("s7779_plant", (0, 0, 0))[0]; wb = api.get("rt64_writeback", (0, 0, 0))
bad = {k: v[0] for k, v in api.items() if k not in OWNER and v[0]}
print(f"epochs={ep} guest_stores_live={gl} busy_slot_live={busy} plant_hit={plant} writeback hit={wb[0]} ctl={wb[1]}")
for k, v in sorted(api.items()): print(f"  {k:20s} hit={v[0]:6d} ctl={v[1]:7d} other={v[2]}{'  OWNER' if k in OWNER else ''}")
if plant < 1 or wb[1] < 1 or ep < 1: print("CONTROL FAIL (plant / writeback ctl / epochs)"); sys.exit(3)
if bad or busy: print(f"H-stomp: non-owner hits {bad} busy_slot_live={busy}"); sys.exit(1)
print("H-clean: 0 non-owner host writes into a live FB arena"); sys.exit(0)
