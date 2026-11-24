# NEXT (s7903)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7902): m11 burst-replay crawl tail odd frames (5639..5771) draw flame meshes (instance mtx 700100/700140, equal to retail)
whose 64-byte vertex blocks exist VERBATIM in retail RDRAM, but at another VI/address. Crawl sim = half render rate (retail matrix
pool changes every 4 VI), so the odd frame re-renders with fresh flame jitter. Retail's display list (0x72xxxx..0x74Dxxx) was
outside the s7900 dump window, so which mesh retail binds to each instance on the odd frame is unknown.
Hypotheses:
  H-bind: the port binds the instance to the other parity buffer (*(0x8013889C)&1 read at a different time than retail), so it
          draws the even frame's / next pair's flame block.
  H-alloc: the per-frame heap hands out flame blocks in a different order (port 74DE48 vs retail 74C060 for the same values),
          and the DL points at a block filled for another instance.
  H-time: retail writes the odd frame's flame values AFTER the gfx task for that frame was loaded on our side (CPU/RSP overlap:
          retail CPU runs ahead into the buffer being drawn).
Discriminator (one retail oracle run, offline vs the kept port snapshots scratch/s7902/m11snap/tasks s5680-s5685 + .dma logs):
  retail dump at osSpTaskLoad 0x80033E3C, VI 10555:10600, pool 0x80700000:0x80700800 + --pc-ram-dump-also 0x80720000:0x80728000
  0x80728000:0x80730000 0x80749000:0x80751000 (4 ranges max, 8192 words each), plus a --watch-pc/--pc-ram-dump of 0x8013889C.
  Base: scratch/s7900/run_retail.sh (edit the XO ranges/VI window; output scratch/s7903/r1). Parse retail's DL (F5 vertex-load
  and matrix commands, docs/F5-UCODE-REFERENCE.md) to get (instance mtx -> mesh address) per retail gfx task, then for the odd
  frames: does retail bind the block whose bytes the port drew to a different instance (H-bind/H-alloc) or does the port's block
  hold values retail writes only later (H-time)? Then m6 (0x31=5) with the burst arm.
Gotcha: ROGUESQ_S7751_SNAP does not mkdir its directory (every write fails with "[s7751] open failed"); mkdir it first.
Tools: tools/s7902_arena_cmp.py, scratch/s7902/mesh_search.py, scratch/s7902/shift_search.py, tools/s7900_tri_source.py.
