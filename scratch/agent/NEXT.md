# NEXT (s7779; s7778 fixed the gate-sweep contract only, s7777 FRAME-member unit still pending)
HYPOTHESIS-ID: dangling-global-heap-ptr-class
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Open member (CURRENT-TRUTH item 31, FRAME class): in the SELECT YOUR CRAFT hangar (owner route_long t=35.5-71.3) the VI swap slot
0x80128E9C = FB 0x80656000 (512 wide, RT64 presents drawn=0x656000 ~15/s), while rs_malloc hands 0x80656010..0x80674AC0 (inside
that FB) to the craft-model loaders (inflate*, parseHmtMaterials, load_hmt_and_hob, parseImageFile). s7777b log:
scratch/s7774/s7777b/run.log (deref-watch ON word=80128E9C t=35.5, OFF by initVideoSubsystem t=71.3).

Hypotheses:
- H-retail: the game's own sequence. partitionFramebufferMemory carves the hi-res FBs from heap memory that is later rs_free'd
  (or never reserved), so retail also runs loaders inside a displayed FB (tolerated: RDP overwrites only pixels, loaders finish
  between frames, or the slot is in rotation but not drawn).
- H-ours: our heap differs from retail (allocation order/sizes from M5 audio de-stubs, s7482 reservation, spill arenas, osMemSize
  path), so the loader blocks land inside FB A only in the port.
- H-stomp: in the port something writes RDRAM over the loader blocks during the window (RT64 render-to-RAM writeback of FB A,
  RDP fill/copy) -> corrupt craft assets that are just not visible.

Discriminating measurement, ONE build, ONE run (owner route_long, 300 s, save read-only):
1. The FB addresses the game itself computes: log partitionFramebufferMemory's outputs (and the swap-slot stores, s7777 already
   names initVideoSubsystem as the writer) plus every rs_malloc/rs_free whose block overlaps [0x80656000, 0x80700000) with t and
   ra (ROGUESQ_HEAPLOG prints only req>=0x4000; add a range filter). Who owned FB A's memory first: if the FB was carved from a
   block the game then rs_free'd itself -> H-retail shape; if the overlapping blocks come from allocations retail would not make
   (audio de-stub / port arenas) -> H-ours.
2. Host writes into the loader block while it is live: arm the s7489 host-write watch idea on the range (or checksum the live
   loader blocks before/after each RT64 present). Any host write = H-stomp. Same run, arm B: ROGUESQ_RENDER_TO_RAM=0.
Positive controls: the s7777 deref watch must still see inflate's own stores into 0x80656010+; a planted host write
(memset 4 bytes of a live loader block from the present hook once) must be counted.
Ground truth for H-retail: tools/oracle (mupen64plus retail) cannot reach the hangar; instead compare the partition/allocation
sequence with the decomp (rogue_squadron64 partitionFramebufferMemory + its caller) to see whether the FB block is freed by game code.
