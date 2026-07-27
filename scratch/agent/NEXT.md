# NEXT work unit — M3: guard `activateAnimationKeyframe`'s unchecked table deref (16th crash class)

s98 instrumented the 14th crash class (`reserveAndEmitDLEntry`) per s97's
plan — clean positive control (19428/19428 fires, no crash on that path)
— but the process died anyway to a brand-new **16th** crash class
(`activateAnimationKeyframe`). This is the **4th consecutive session**
(s95, s96, s97, s98 — 6 soaks) where a soak reaches the "SELECT YOUR
CRAFT stable → hold" window and dies to a *different, previously-unseen*
crash before reaching the ~140s DMA-caller window. Read PORTING-STATE.md's
Session 98 entry before doing anything else; this file only has the
actionable summary.

## The pivot (read this before planning another instrument)

Per rule 8 and s98's own assessment: **stop landing observe-only entry-log
instruments for new crashes.** Four sessions of that approach have each
found a different bug, never the same one twice, and never made a soak
survive meaningfully longer. s98 source-characterized the 16th class's
crash mechanism (see below) — the productive move now is to **guard the
site**, not log it. This mirrors the two guards that already worked in
this codebase: s83's `evalCubicSplineAtTime` 0/0 NaN guard, and s84's
`resume_thread_tagged` `bad=1` skip-gate.

## What's established (do not re-derive)

- The blind DMA-caller repro is parked (3/3 attempts spent s95-s97).
  Its instrument (`ROGUESQ_LOG_DMA_CALLER=1`) stays armed in every soak —
  it's free — but do not plan a soak around it specifically.
- `get_function` is the confirmed chokepoint for indirect calls (s95).
  Do not re-derive.
- Do NOT re-plan "dump the `OSIoMesg` at `mb`" (refuted s92), cite
  `ra=0x00000000` as corruption evidence (refuted s92, routine on 487+
  calls, reconfirmed multiple sessions since), or re-open "consumer
  index-desync"/"external stomp" (s94 rules out both).
- Do NOT re-grep for `submitDmaRequestBatch(rdram` or `LOOKUP_FUNC(`
  call-site counts (done, stable, s93/s94/s95).
- **Do NOT plan "shorten the hold to outrun the crash family and reach
  the DMA window faster."** s98 checked this against timing data already
  in PORTING-STATE.md: the DMA-adjacent `do_rom_read` crash consistently
  lands hold+11-15s (s85, s91, s93, s94), while this crash family's
  one-offs land hold+3-17s across sessions — **the two windows overlap,
  they are not sequential.** There is no "past the family, into the DMA
  window" — they are the same few seconds. (This corrects a literal
  reading of s97 NEXT.md's own outcome-2 suggestion; s97's actual point —
  stop instrumenting one-offs — still stands, just not via a shorter hold.)
- `ROGUESQ_LOG_DLENTRY=1` (14th class, `reserveAndEmitDLEntry`) is landed
  and confirmed working (19428/19428 fires, s98). Its own crash did NOT
  recur — 1-for-2 across sessions that reached it (hit s97, clean s98).
  Not worth a dedicated re-test soak; it stays armed opportunistically.

## The crash-class picture (16 total, all in M3)

Two families:
- **Hangar-tick / unguarded-lookup-or-arg-deref family** (guest-side,
  real bugs, fixable): 9th `updateAnimatedTextureStreaming` (1x, s89),
  10th `static_5_800B4048` (1x, s90), 11th `projectModelBoundsToScreen`
  (1x, s92), 12th `composeNpcOrientationMatrix` (2x: s74, s95), 14th
  `reserveAndEmitDLEntry` (1x, s97), **16th `activateAnimationKeyframe`
  (1x, s98, source-characterized — see below, this session's target)**.
- **RT64-internal asserts** (no source-level bug on our side): 13th
  `reinterpretTileRecord` (1x, s96), 15th `loadDrawState` zero-sample-size
  (1x, s97). Not useful to instrument or guard — no fix available on our
  side even once characterized; only worth tracking recurrence.

## The work unit

Guard the 16th class's crash site. `activateAnimationKeyframe`
(`N64Recomp/RecompiledFuncs/funcs_14.c:1629`, guest `0x80061C74`) does,
right at entry (`funcs_14.c:1656-1661`):

```c
// funcs_14.c:1640-1649 (table base computation)
ctx->r3 = ADD32(S32(0x800A << 16), -0x3F0);      // table_base = 0x8009FC10
ctx->r2 = S32((ctx->r4 & 0xFFFF) << 2);           // idx = (arg_r4 & 0xFFFF) * 4
ctx->r2 = ADD32(ctx->r2, ctx->r3);                // addr = table_base + idx
// funcs_14.c:1656-1657
ctx->r17 = MEM_W(ctx->r2, 0X0);                   // s1 = *(addr)   <- table lookup
// funcs_14.c:1660-1661
ctx->r3 = MEM_W(ctx->r17, 0X30);                  // deref s1+0x30, NO CHECK on ctx->r17
```

`ctx->r4` (first arg, an animation/keyframe index) indexes a pointer
table unchecked; whatever comes out is dereferenced at `+0x30` with no
null/range check. This is the crash.

1. In `N64Recomp/fixup_game_funcs.py`, add a new patch targeting the
   `RECOMP_FUNC void activateAnimationKeyframe(...)` prologue (same
   regex-on-prologue pattern as every other patch in this file — search
   `_compose_npc_orientation_patch` for the template to copy). Insert the
   guard **after** the `ctx->r17 = MEM_W(ctx->r2, 0X0);` line (need a
   second regex anchored on that specific line, since this patch must
   land mid-function, not at the prologue like the entry-log instruments
   — check how `_dma_ring_producer_patch` anchors mid-function on
   `L_80005768:` for the pattern to copy instead).
2. The guard: if `ctx->r17` is 0, or clearly outside plausible guest RAM
   (e.g. `< 0x80000000 || >= 0x80800000` — check what range other
   guest-pointer sanity checks in this codebase already use, e.g. the
   s78 wild-FB-refuse gate's bounds, for a consistent convention rather
   than inventing a new one), skip the rest of the function body (an
   early `return;` is safe here — re-check the function's full control
   flow first to confirm nothing after this point has side effects
   other code depends on; if unsure, skip only the crashing deref and
   substitute a safe default the same way s84's gate does, rather than
   bailing the whole function) and log once via a new always-on flag
   (e.g. `ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1`, following the
   `s_*_enabled`/`getenv` pattern every other instrument uses).
3. `cd /Users/williambuckley/Documents/Tools/N64Recomp && python3 fixup_game_funcs.py`
   — verify `patched x1` for the new guard, not x0.
4. Rebuild: `cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j 8` — exit clean.
5. Soak with the full flag set plus the new guard flag:
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_COMPOSE_NPC=1 ROGUESQ_LOG_DLENTRY=1 \
       ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1 \
       ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
       ROGUESQ_LOG_THREAD_RESUME=0 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       scratch/s73_post_a_scene/run_mission_keys.sh s99_animkeyframe_guard1 0 12
   ```
   (rename the flag in this command to whatever you actually landed in
   step 2, and update this doc to match if it changes.)

Outcomes:

1. **Guard fires, process survives further** (later hold-iter, or reaches
   the ~140s DMA-caller window) — real progress. If it reaches the DMA
   window, immediately re-check `ROGUESQ_LOG_DMA_CALLER` and
   `do_rom_read` per M3's original question (CURRENT-TRUTH item 1) — all
   instruments are already armed in the same soak, no rebuild needed.
2. **Guard never fires, a DIFFERENT crash (17th class) preempts it** —
   informative (this site wasn't this run's blocker), do not spend a 2nd
   soak chasing this exact site. Per this pattern's own precedent, move
   to the next-most-recurring characterized class
   (`composeNpcOrientationMatrix`, 2 occurrences: s74, s95) for the same
   guard-not-instrument treatment.
3. **Guard fires but the process still dies the same way** — the guard's
   bounds check is wrong (too permissive) or the skip path itself has a
   side effect that breaks something downstream; read the crash log's
   new backtrace, it will tell you which.

## Do not

- Do not land another observe-only entry-log instrument for a new crash
  class as the primary work unit — 4 sessions of that found a different
  bug every time and never converged. Guard, don't just log.
- Do not plan around "shorten the hold to reach the DMA window before the
  crash family" — refuted by s98's timing-data check, the windows overlap.
- Do not re-run the plain DMA-caller repro as a dedicated work unit.
- Do not re-grep for `submitDmaRequestBatch(rdram`, ring literal
  constants, or `LOOKUP_FUNC(` call-site counts.
- Do not cite `ra=0x00000000` as corruption evidence.
- Do not re-plan "dump the `OSIoMesg` at `mb`".
- Do not re-open "consumer index-desync" or "external stomp after a
  clean write".
- Do not combine `ROGUESQ_LOG_THREAD_RESUME=1` with any of these repros
  without a specific reason (confirmed confound, s93).
- Do not spend a soak trying to characterize the 13th or 15th crash
  classes (RT64-internal asserts, no fix available on our side).
- Do not grep `run.log` for the script's own `[keys]`/phase-timing lines
  — they're in the Bash tool's own stdout capture, not `run.log`.
