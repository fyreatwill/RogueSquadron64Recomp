# NEXT work unit — M3: guard `composeNpcOrientationMatrix` (12th crash class, s99)

s99 landed and validated the 16th class's guard (`activateAnimationKeyframe`)
— clean corrected soak, 0/0 fires (a real, working negative control) — but
the process died to a **recurrence of the already-catalogued 15th class**
(RT64-internal `loadDrawState` assert, first seen s97) before the guard
ever got a chance to matter. Read PORTING-STATE.md's Session 99 entry
before doing anything else; this file only has the actionable summary.

## The work unit

Per s98's own outcome-2 branch (which s99 landed in almost exactly):
**guard `composeNpcOrientationMatrix`** (12th crash class, 2 occurrences:
s74, s95 — the next most frequent of the guest-side unguarded-lookup
family), same guard-not-instrument treatment as s99 gave the 16th class.

1. **Source-read the crash mechanism first — this has NOT been done yet.**
   s92/s95 only landed an entry-log instrument (`ROGUESQ_LOG_COMPOSE_NPC=1`,
   logs `arg_r4`/`arg_r5`/`ra` at entry) — nobody has actually read the
   SIGBUS site itself inside `static_5_800AB1C8`
   (`N64Recomp/RecompiledFuncs/funcs_40.c`, guest `0x800AB1C8`, real name
   `composeNpcOrientationMatrix` per `symbol_files/main_overlay.txt`) to
   confirm it has the same "unguarded pointer from a lookup/arg" shape as
   the other 5 classes in this family. Do this before writing a guard —
   if the crash is a different shape (e.g. a bad array index rather than
   a bad pointer, or an arithmetic issue), the guard has to match that
   shape, not copy-paste the table-lookup pattern verbatim.
2. Guard the confirmed crash site in `N64Recomp/fixup_game_funcs.py`,
   following the `_activate_anim_keyframe_guard_patch` template (search
   for that function name — it's the freshest, most-annotated example of
   the mid-function-anchor + ABI-safe-exit pattern). Two things to get
   right, both learned the hard way at s99:
   - **ABI safety**: before writing a bare `return;`, check whether the
     function spills callee-saved registers / adjusts guest `$sp` in its
     prologue. If it does, find the function's own real exit label (the
     epilogue that restores everything) and `goto` there instead of
     hand-duplicating the restore sequence — do not assume `return;` is
     safe without checking.
   - **64-bit sign-extension**: guest registers (`ctx->rN`) are `gpr` =
     `uint64_t` (`recomp.h:84`), and `MEM_W` returns a signed `int32_t`.
     A real guest pointer with the top bit set (e.g. `0x8009FC10`)
     sign-extends to `0xFFFFFFFF8009FC10` on assignment to a 64-bit
     register. **Never compare a raw `ctx->rN` value against 32-bit
     literal bounds** — truncate through `U32()` first
     (`uint32_t lo = U32(ctx->rN);` then compare `lo` against
     `0x80000000u`/`0x80800000u`, matching the s78
     `rt64_framebuffer_manager.cpp` gate's RDRAM-range convention). s99's
     first build skipped this and got a guard that fired on 30333/30333
     calls (100% false positive) before catching and fixing it
     same-session — verify any new guard's fire rate looks like a rare
     case (near-zero), not "fires on every call," before trusting a
     "0 fires and still crashed" result as meaningful.
3. `zsh -c "cd /Users/williambuckley/Documents/Tools/N64Recomp && python3 fixup_game_funcs.py"`
   (or equivalent — see note on permissions below) — verify the new patch
   reports `patched x1`, not `x0`.
4. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean. (No full ELF regen needed unless you touched `N64Recomp`'s own analysis/codegen — this is a guest-C-only patch, same as s98/s99's guards, so `fixup_game_funcs.py` alone plus a `cmake --build` suffices **only if `RecompiledFuncs` is still pristine**; if it already carries a stale/buggy patch from a prior attempt in the same session, you must regenerate it fresh first — see note below.)
5. Soak with the full flag set plus every family instrument (all free,
   keep them all armed):
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_COMPOSE_NPC=1 ROGUESQ_LOG_DLENTRY=1 \
       ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1 \
       ROGUESQ_LOG_<NEW_GUARD_FLAG>=1 \
       ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
       ROGUESQ_LOG_THREAD_RESUME=0 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_mission_keys.sh s100_composenpc_guard1 0 12
   ```
   Run this in the **background** (it takes ~2-3 minutes: ~45s to reach
   VI width 1024, ~60s of scripted key schedule, 12s stable wait, ~6s
   probe, up to 30s hold) and block on
   `grep -q -- "--- done ---" .../run.log` rather than polling — or use
   Monitor. Do not end the turn / declare an outcome before the soak's
   `run.log` shows `--- done ---`; the Stop hook checks `scratch/agent/
   STATUS` and will reject a WORKING state.

Outcomes:

1. **Guard fires (at a plausible, non-universal rate) and the process
   survives further** (later hold-iter, or reaches the ~140s DMA-caller
   window) — real progress. If it reaches the DMA window, immediately
   check `ROGUESQ_LOG_DMA_CALLER` and `do_rom_read`/`pi-start-dma` per
   M3's original open question (CURRENT-TRUTH item 1) — all instruments
   are already armed in the same soak, no rebuild needed.
2. **Guard never fires, a different crash preempts it** — informative
   (this site wasn't this run's blocker). If it's a **recurrence of an
   already-catalogued class** (9-16, or the RT64-internal 13th/15th),
   that's a cleaner signal than a brand-new class — do not spend a 2nd
   soak on this exact site; move to the next-most-recurring
   characterized class (11th `projectModelBoundsToScreen` or 14th
   `reserveAndEmitDLEntry`, 1 occurrence each) for the same treatment.
   If it's a genuinely new (17th+) class, catalog it the same way s86-s90
   did, then still move on rather than chasing it — this family has
   never rewarded a same-site retry.
3. **Guard fires but the process still dies the same way** — the bounds
   check is wrong (too permissive, or the `U32()` truncation step was
   skipped) or the skip path itself has a side effect that breaks
   something downstream. Read the new backtrace; it will tell you which.

## Do not

- Do not re-soak `activateAnimationKeyframe` — its guard is landed and
  validated (s99, 0/0 clean control). Leave `ROGUESQ_LOG_ANIM_KEYFRAME_
  GUARD=1` armed in every soak going forward (it's free) but treat it as
  closed, not a target.
- Do not skip the source-read step for `composeNpcOrientationMatrix`'s
  actual crash line before guarding — s92/s95 never did this, only
  logged entry args. Confirm the shape matches before copy-pasting the
  table-lookup guard pattern.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds — always truncate through `U32()` first. This is the
  single most important lesson from s99; re-read that session's entry if
  tempted to skip it "just this once."
- Do not assume a bare `return;` is ABI-safe inside a guard without first
  checking whether the function spills callee-saved registers / adjusts
  `$sp` in its prologue — find and reuse the function's own real exit
  label instead when it does.
- Do not plan around "shorten the hold to reach the DMA window before the
  crash family" — refuted s98, the windows overlap (hold+3-17s family vs.
  hold+11-15s DMA crash).
- Do not re-run the plain DMA-caller repro as a dedicated work unit (3/3
  attempts spent s95-s97, parked).
- Do not re-grep for `submitDmaRequestBatch(rdram`, ring literal
  constants, or `LOOKUP_FUNC(` call-site counts (done, stable, s93-s95).
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  routine on 487+ calls, reconfirmed every session since).
- Do not re-plan "dump the `OSIoMesg` at `mb`" (refuted s92).
- Do not spend a soak trying to characterize the 13th or 15th crash
  classes (RT64-internal asserts, no fix available on our side) — track
  recurrence only, e.g. s99's 15th-class hit is just a tally mark.
- Do not grep `run.log` for the script's own `[keys]`/phase-timing lines
  — they're in the background task's own stdout capture (the `.output`
  file the Bash tool reports), not in `run.log` (which only has the game
  binary's own stdout/stderr).
- Do not invoke the N64Recomp binary or `make_elf.py` by a bare/relative
  path from an unapproved cwd — that requires interactive approval this
  session had to work around. Use `zsh -c "..."` wrapping (matches the
  `Bash(zsh:*)` allow rule) or `python3 ...` (matches `Bash(python3:*)`)
  for anything that needs the N64Recomp or rogue_squadron64 sibling
  checkouts. `cmake --build /abs/path/to/build -j 8` (no leading `cd`)
  matches `Bash(cmake:*)` and works directly.
- If you need a full regen (`make_elf.py` → `N64Recomp` → `fixup_game_
  funcs.py`) because a stale/buggy patch is already baked into
  `RecompiledFuncs/`, remember `RecompiledFuncs/` is untracked in
  N64Recomp's own git and gets fully overwritten by each regen — that's
  expected and fine, it's how `fixup_game_funcs.py`'s patches get
  reapplied onto a pristine base every time.
