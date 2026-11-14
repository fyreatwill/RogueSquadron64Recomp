# NEXT (s7327): qualify the s7326 spill reset release + 8 MB arena on the owner's routes
HYPOTHESIS-ID: spill-scene-reset-leak
Context (s7326): spill blocks escaped the retail scene bulk free (coalesceFreeHeapBlocks) -> dd8 21:9 hangar route crashed at the first
mission load (arena full, rs_malloc NULL). Fix default on: rs64_s7326_spill_reset (ROGUESQ_SPILL_RESET=0 old) + 8 MB arena
(ROGUESQ_SPILL_MB=4 old, RAMTOP 24). Same-build 4-arm table in PORTING-STATE s7326. Soak s7326_spill_levels queued (L4 + L15 dd8 21:9).
1. Fold the s7326_spill_levels verdict (SOAK-RESULTS).
2. Owner route coverage, one build, arms run back to back (scratch/s7326/run.zsh <name> "<env>", 650 s, needs idle + unlocked screen):
   dd4 16:9 (owner recipe), dd6 21:9 WIDEWIN, dd8 16:9. Per arm: crash, arena full, "[s7326] spill reset" count/bytes, spill bump peak.
   Hypotheses: H-dd8-only (lower dd never spills the 0x2DFF00 buffers -> fix inert there) vs H-all-dd (lower dd also spills them and
   was one reset away from the same crash). Control: ROGUESQ_S7326_CTL=1 ctl seen == resets.
3. Class G re-check with blocks above 0x81400000: ROGUESQ_S7324_RCPREF=ctl + ALLOCMAP on arm c's route, tools/s7324_rcp_report.py
   (exit 1 on a hit). Expected: 0 direct / 0 alias (spill is above 16 MB in both layouts).
Outcomes: all clean -> close item 21 and tell the owner (OWNER-OPT-INS note: dd8 hangar route no longer crashes at mission load);
any crash -> backtrace + spill log, name the request that failed.
Parallel open (item 22): 46 audio reads of song-channel arrays freed 0-14 ms earlier at the scene transition.
