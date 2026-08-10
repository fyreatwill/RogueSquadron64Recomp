# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

## s594 recap (read this first)

Item -361 (coalesce R2 guard fix, landed s593) is still awaiting its first
discriminating live re-verify. This session consumed 2 more queued retries,
both nulls, and clarified the soak script's own gate-line semantics:

- `s593_coalesce_r2_verify_a`/`_b` (queued s593, run+consumed s594): both
  `case6=0 hangar-sel=0 sec4=1 crash=CRASH` — died on unrelated background
  noise (`_a`: item -331 2nd occurrence, `heapFreeListDequeue`
  `last-guest-pc=0x8000d688`, now moderate confidence; `_b`: item -306's
  well-known weak-early-death signature) **before the force-exit env could
  even engage**. Neither reached hangar state 5, let alone post-exit sec4.
- **`sec4>=2` is the correct discriminating threshold in the soak script's
  gate line, not `sec4>=1`.** The `sec4` counter matches ANY
  `"[overlay] start-match: section 4"` line (`overlays.cpp`
  `load_overlays_by_start`), which fires once during normal boot-time
  overlay preload regardless of hangar exit. `sec4=1` = boot-only noise.
  `sec4=2` = boot hit + the genuine post-exit reload (confirmed against
  `s592_sec4_thr12_a`'s known-good post-exit-reaching run: hits at line
  6081 AND 278849). NEXT.md's own decision tree already used `sec4>=2`
  correctly — this was just verified/documented, not changed.
- Tally since item -359 opened this question: **5 consecutive path-gated or
  pre-engagement nulls** since s592a's one success (s592b, s593-manual,
  s593_coalesce_r2_verify_a, s593_coalesce_r2_verify_b — none reached
  `sec4>=2`). H13a (path-to-sec4-after-case6-force is intermittent) keeps
  getting reinforced. Queued `s594_coalesce_r2_verify_c`/`_d`, same recipe,
  currently sitting in `scratch/agent/soak_queue/` for the loop to run.

## This iteration's work unit

**Item -361 continued: consume the queued s594 retries; first one that
lands `sec4>=2` with both coalesce guards armed is the real discriminating
run for the fix.**

1. Read `scratch/agent/SOAK-RESULTS.md` tail for `s594_coalesce_r2_verify_c`
   / `_d` lines first, then the full gate-summary line at the end of each
   `scratch/agent/soak_results/s594_coalesce_r2_verify_{c,d}_*.log`.
2. If a run shows `sec4>=2` (real post-exit reload, not the boot-time hit) —
   this is the discriminating data point:
   - `coalesce_guard2_r2>0` AND `crash=ok` → **FIX CONFIRMED**. Check
     whether thr-12 (`entry=0x800495FC`, want a 3rd creation beyond the
     2 early-cinematic ones already seen every run) or section 2 followed.
     Close item -361's crash half; open thr-12/sec2 as the new frontier.
   - `coalesce_guard2_r2>0` AND `crash=CRASH` → bail value takes the wrong
     branch for this site after all — re-check the exit-path register-use
     analysis in `PORTING-STATE.md` Session 593 against this run's actual
     crash PC (did it move a few instructions, same shape as s354's
     original mistake?).
   - `coalesce_guard2_r2=0` AND `crash=CRASH` at `0x8000247c` again → the
     patch did not take. Check `fixup_game_funcs.py`
     (`~/Documents/Tools/N64Recomp`) for the `item -361` patch block,
     re-run the regen pipeline (`make_elf.py` -> `N64Recomp` -> fixup ->
     cmake), verify the fixup report shows the guard applying `x1` with no
     silent "REFUSING to run" sentinel.
3. If both `_c`/`_d` are again pre-engagement nulls (`case6=0`) or
   path-gated (`sec4=1` only): this makes **7 consecutive non-discriminating
   attempts** on the same live-reverify step. Per iron rule 8, do NOT queue
   a 3rd pair blindly — instead spend this iteration's work unit
   redesigning the recipe: consider whether `HOLD_S` is too short, whether
   the background-noise crashes (-331, -306) are frequent enough to warrant
   a pre-hangar stabilization pass first, or whether a driven (non-force)
   natural double_start path reaches sec4 more reliably than
   `ROGUESQ_FORCE_CASE6_START`. Write the redesigned recipe as the new
   queued script rather than repeating the same shape a 4th time.

### Do NOT
- Treat a `sec4=1`-only or `case6=0` null run as evidence about the fix
  (iron rule 1) — only a run that actually reaches `sec4>=2` with the
  guarded code path live counts.
- Re-open thr-11 as recvServiceMessage block (H12a closed).
- Re-litigate the s354-366 arc's FIRST guard/bail — only the NEW `_R2_`
  site is open here.
- Chase item -331 or item -306 reactively — both are filed breadcrumbs,
  watch-only until a 3rd/Nth occurrence per their own entries.

### Exact commands (if no queue result to consume)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s595_coalesce_r2_verify3 5 12
```
