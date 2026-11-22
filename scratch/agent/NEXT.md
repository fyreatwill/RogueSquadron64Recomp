# NEXT (s7784; s7783 selected H-overlap port-only for item 32: the port puts DL chunks inside the FB pair, retail never does)
HYPOTHESIS-ID: fb-shared-slot
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Datum (s7783, CURRENT-TRUTH item 32, port 2 runs + retail oracle 2 instruments): retail DL-emitter store bases ($v1 at 0x8000D5A8 /
0x8000D5E0) are all in 720000..75DFFF during the 640x340 intro; the port's are 400004..7DFED4 with 2836/5004 inside [62B800,700000)
(pages 6F0000/6FF000). The free-chunk cache *0x801163B0 is outside the slots in every walk, so the in-FB chunks enter another way.

Question: WHERE does the port get a chunk at 0x806F0000-class addresses? Hypotheses:
- H-steal: findAndUnlinkSmallestEntry 0x8002221C (returns 0x80022304 / 0x80022364 / 0x800225F0 jr ra) hands the DL emitter a
  texture-LUT entry whose data pointer lies in FB memory, because the port's texture pool / heap layout differs from retail (heap
  start, osMemSize, dd spill arena, LUTSCALE, a fixup guard that substitutes memory).
- H-guard: one of our DL-pool guards/fixups (s434-437 0x801163B0 family, DL_BUFFER_POOL_GUARD 0x801163FC, s6098 DLPOOLX) supplies
  or repairs a chunk pointer with a non-retail value.
- H-reg: the port's DL emitter reads a different chunk base (*0x8011DC58 chain) for a recompilation reason (e.g. swl/swr address).

Unit, ONE port build + ONE oracle run:
1. Oracle: RS64_EXEC_REG_HIST=2 with --watch-pc on the instruction AFTER each jal 0x8002221C (callers 0x80007CF0, 0x80007D88,
   0x80007E70, 0x80007F30, 0x80007FF0, 0x800080B0, 0x8000844C, 0x80008F3C: watch jal+8, where $v0 is the return), 18 s, angrylion +
   cxd4 (recipe in PORTING-STATE s7783). Also RS64_EXEC_REG_HIST=2 at the pop sites of *0x801163B0 if they can be found by grep.
2. Port: same pcs, same register: add a ROGUESQ_S7779_ARENA-gated page histogram of v0 after each 0x8002221C call (fixup script,
   so it survives regen) + of *0x8011DC58 at each DL-emitter entry. Compare with tools/s7783_shared_slot_score.py style scoring.
Outcomes: port steal returns in-FB pages, retail never = H-steal (then name the allocator of that texture entry: the rs_malloc call
whose block holds it; port vs retail heap map). Steal returns match retail but emitter base differs = H-guard/H-reg (then grep the
fixups touching 0x801163B0/0x8011DC58 and disable each in an arm). Positive controls: the oracle [gpr-ctl] line; the port plant.
