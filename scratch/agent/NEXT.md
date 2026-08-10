# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s593 recap (read this first)

Item -361 escalated to a mechanistic fix this session:

- **H13c CONFIRMED 2/2**: s589 + `s592_sec4_thr12_a` (consumed from the soak
  queue this session) both independently reached post-exit section 4 on
  force (case6+inject) and both crashed byte-identically 2-4 log lines
  later at `cinematicLoopBody→initSceneForMission→coalesceFreeHeapBlocks
  +4424`/`0x8000247c`, before thr-12 (`entry=0x800495FC`) could be created.
- **Root cause + fix landed**: `coalesceFreeHeapBlocks` (`funcs_0.c`) has a
  SECOND unguarded block-header-walk loop (`L_80002474`, base `$s2`) with
  the same idiom the s354-366 arc already guarded on the FIRST loop
  (`L_80002358`, base `$t0`). Added a second guard at `0x8000247C` in
  `~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
  (`ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD`, tag `[coalesce-heap-r2-guard]`),
  reusing the already-verified-safe bail value (`ctx->r3=0x8`). Full regen
  (make_elf→N64Recomp→fixup→cmake) clean, patch applied `x1`, build OK.
- **Live re-verify this session was a NULL, not a refutation**: same
  case6+inject recipe with both coalesce guards armed reached hangar exit
  (state=8) but the run's post-exit sec4 never fired this time — 0 guard
  hits (expected, code path never ran), 0 crash, full 251s hold survived.
  Per iron rule 1 this is not evidence either way — it's a 3rd data point
  that **H13a (path-to-sec4 after case6-force is intermittent)** still
  holds, on top of the fix, not against it.

Queued for the loop: `scratch/agent/soak_queue/s593_coalesce_r2_verify_{a,b}.sh`
— same recipe, both coalesce guards armed, retry until sec4 lands.

## This iteration's work unit

**Item -361 continued: consume the queued s593 retries; first one that lands
post-exit sec4 is the real discriminating run for the fix.**

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s593_coalesce_r2_verify_a`
   / `_b` lines first. Each verdict line's summary already reports
   `coalesce_guard1=`, `coalesce_guard2_r2=`, `sec4=`, `crash=`.
2. If a run shows `sec4>=2` (post-exit reached) — this is the discriminating
   data point:
   - `coalesce_guard2_r2>0` AND `crash=ok` → **FIX CONFIRMED** (guard caught
     the bad pointer, run survived past the old crash site). Check whether
     thr-12 (`thr495FC_creates`) or section 2 (`sec2`) followed. Close item
     -361's crash half; open thr-12/sec2 as the new frontier if thr-12
     still doesn't create.
   - `coalesce_guard2_r2>0` AND `crash=CRASH` → bail value takes the wrong
     branch for this site after all (re-check the exit-path register-use
     analysis in `PORTING-STATE.md` Session 593 against the actual crash
     PC this run — did it move a few instructions, same shape as s354's
     original mistake?).
   - `coalesce_guard2_r2=0` AND `crash=CRASH` at `0x8000247c` again → the
     patch did not take. Check `fixup_game_funcs.py` for the `item -361`
     patch block, re-run the regen pipeline, verify the fixup report shows
     `coalesceFreeHeapBlocks 2nd-loop next-block-header read guard` `x1`
     with no `REFUSING to run` sentinel silently short-circuiting it.
3. If both `_a`/`_b` are still `sec4=0/1` (path-gated, no post-exit sec4):
   queue 1-2 more identically-shaped retries and move on — do NOT babysit a
   3rd manual attempt this session (budget rule already spent one this
   session on `s593_coalesce_r2_verify`, itself a null).

### Do NOT
- Treat a `sec4=0` null run as evidence about the fix (iron rule 1) — only a
  run that actually reaches the guarded code path counts.
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-litigate the s354-366 arc's FIRST guard/bail — only the NEW `_R2_` site
  is open here.

### Exact commands (if no queue result to consume)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s594_coalesce_r2_verify2 5 12
```
