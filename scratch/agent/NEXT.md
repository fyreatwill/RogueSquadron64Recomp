# NEXT (s7482)
HYPOTHESIS-ID: g1d-retarget-unreserved-pool

Context (s7481, CURRENT-TRUTH item 1a): apply_s6202_retarget (tools/apply_s6031_far.py ~line 214) moves the wide-phase frame pool
*(0x801163E8) to base=ec-t2 inside a FREE main-heap block (L7 menu at t~205: 0x8096D600..0x809B8600, t2=0x4B000). Its check only
compares block HEADERS to base, so the free block's extent is missed. Latent: nothing collided in 1 run, but the allocator owns it.

Hypotheses:
- H-collide: during the wide phase some rs_malloc returns a block overlapping [base, ec) (live corruption of DL pool / allocations).
- H-latent: no rs_malloc reaches that high in practice (first-fit from the low end of a 7.8 MB block), so it is a correctness hole only.
- H-reserve-safe: carving the span out properly (shrink the free block by t2+0x10 and write a used header at base-0x10 with the same
  flag the game's carve uses, fl=6, so the scene-reset coalesce reclaims it like the carve) keeps menus/title correct.

ONE build, both arms:
1. Collision detector (host, no regen): at rs_malloc exit (s7480_malloc / s7475_malloc hook in src/main/upstream_compat.cpp) log
   `[s7482] pool-collide ptr= req= e8= ec=` when [ptr, ptr+req) overlaps [e8, ec) and e8 != the retail cur (read e8 =
   *(0x801163E8); ec from the retarget log or export g1d span via a global set by the patch). Positive control: an env
   ROGUESQ_S7482_CTL=1 that treats the first wide-phase malloc as overlapping must log once.
2. Fix behind ROGUESQ_RETARGET_RESERVE=1 (patch in apply_s6031_far.py, then the full regen order make_elf -> N64Recomp ->
   fixup_game_funcs -> cmake): on "ok", if base lies inside a free block [b+0x10, b+0x10+sz) that ends at ec-0x10, split it.
   Otherwise reject.
3. Arms: L7 dd4 16:9 (reaches the menu at t~205) and the hangar abort/re-entry route, RESERVE=0 vs 1, HOLD=220, with
   ROGUESQ_S7480_UAF=1. Expected: RESERVE=1 -> loc_S=0 (no store lands in a free block), heap walk (s7472 heapchk) clean, menu frames
   match RESERVE=0. H-collide is selected if pool-collide > 0 in either arm.
Then make RESERVE default on if clean (it is a port bug fix; =0 restores the old behaviour) and record it in OWNER-OPT-INS if needed.
