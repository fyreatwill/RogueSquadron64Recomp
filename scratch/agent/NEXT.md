# NEXT work unit — M3: guard `projectModelBoundsToScreen` (11th crash class, s101)

s100 landed and validated the `composeNpcOrientationMatrix` guard (12th
class) — clean negative control (0/544 fires), no evidence the guard is
wrong — but the process died to a **new, 17th** crash inside
`updateHangarBayScene` itself before the guard's fire rate could be
tested against a real bad case. Read PORTING-STATE.md's Session 100
entry before doing anything else; this file only has the actionable
summary.

## The work unit

Per CURRENT-TRUTH.md's own outcome-(b) branch (guard landed cleanly, a
different crash preempted it — move to the next-most-recurring
characterized class): guard **`projectModelBoundsToScreen`** (11th
crash class, 1 occurrence: s92), same guard-not-instrument treatment as
s99 gave the 16th class and s100 gave the 12th.

1. **Source-read the crash mechanism first — this has NOT been done
   yet.** s92 only captured a backtrace and confirmed the real symbol
   name (`0x80065E98`, `N64Recomp/RecompiledFuncs/funcs_15.c:4928`); the
   actual crash line inside the function body has never been read. Read
   the function and confirm it has the same "unguarded pointer from a
   table lookup / arg" shape as the rest of this family (12th, 16th, and
   probably the new 17th) before writing a guard. **If it turns out to
   be a different shape** — e.g. the way s98 found `reserveAndEmitDLEntry`
   (14th class) was actually a scene-graph-traversal/display-list-entry
   issue, not a `MEM_W`-off-an-arg deref — characterize first, guard
   second, exactly as s98 did. If `projectModelBoundsToScreen` turns out
   to be a bad fit for a guard, fall back to `reserveAndEmitDLEntry`
   (14th class, `N64Recomp/RecompiledFuncs/funcs_3.c`, entry-log
   instrument `ROGUESQ_LOG_DLENTRY=1` already armed and gave a clean
   positive control at s98) instead — but characterize its actual shape
   first too, it is explicitly flagged as possibly different from the
   table-lookup family.
2. Guard the confirmed crash site in `N64Recomp/fixup_game_funcs.py`,
   following the `_compose_npc_orient_guard_patch` template (freshest,
   most-annotated example — search for that function name). Three
   things to get right, all learned the hard way in s99/s100:
   - **ABI safety**: find the function's own real exit label (the
     epilogue that restores callee-saved registers / pops `$sp`) and
     `goto` there instead of a bare `return;` — do not assume `return;`
     is safe without checking the prologue first.
   - **64-bit sign-extension**: guest registers (`ctx->rN`) are `gpr` =
     `uint64_t` (`recomp.h:84`); `MEM_W` returns a signed `int32_t`.
     **Always truncate through `U32()` first**
     (`uint32_t lo = U32(ctx->rN);` then compare `lo` against
     `0x80000000u`/`0x80800000u`). Skipping this gave s99's guard a
     30333/30333 false-positive rate before it was caught same-session.
   - **File-scope the regex anchor.** s100 found that an instruction-
     text-only regex anchor (no function-boundary check) can match
     inside a *different* function in a *different* overlay that
     happens to share the same guest address range and coincidentally
     contains the identical instruction sequence — `fixup_game_funcs.py`
     reported `patched x1` in **two** files for the s100 guard before
     the bug was caught (`funcs_27.c`'s `hangarInitialize`, an unrelated
     working function, would have silently gotten a broken `goto`).
     **After running the fixup script, check the `patched xN` report
     names exactly the one file the target function is defined in** —
     if it reports more than one file, that's a bug to find (scope the
     substitution with `if p.name == "the_right_file.c":`), not a bonus.
3. `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   — verify the new patch reports `patched x1` in exactly the expected
   file, no others.
4. If `fixup_game_funcs.py` reports patching a *stale* `RecompiledFuncs/`
   (e.g. a leftover buggy patch from a prior attempt this session), you
   must regenerate fresh first: `zsh -c "cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py"`
   then `zsh -c "cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml"`,
   THEN re-run `fixup_game_funcs.py`. Otherwise (pristine `RecompiledFuncs/`
   still on disk from the last regen) the fixup script alone is enough.
5. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
6. Soak with the full flag set plus every family instrument (all free,
   keep them all armed — add whatever new `ROGUESQ_LOG_*` flag the new
   guard defines):
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_COMPOSE_NPC=1 ROGUESQ_LOG_DLENTRY=1 \
       ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD=1 \
       ROGUESQ_LOG_<NEW_GUARD_FLAG>=1 \
       ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
       ROGUESQ_LOG_THREAD_RESUME=0 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_mission_keys.sh s101_<name>_guard1 0 12
   ```
   Run in the **background**; wait for the actual game PID (`pgrep -f
   './RogueSquadron64Recomp'` or check the PID the wrapper script prints,
   e.g. `pid 96755` in its own stdout) to exit — **s100 wasted a full
   wait cycle by polling `pgrep -f "build/RogueSquadron64Recomp"`, which
   never matches because the binary is launched as `./RogueSquadron64Recomp`
   from inside `build/`, not with a `build/` prefix in its argv0/cmdline**.
   Prefer waiting on the specific PID printed by the wrapper script
   (`kill -0 $PID` in a loop) or grep for `RogueSquadron64Recomp$` without
   a path prefix. Do not declare an outcome before the process has
   genuinely exited and `run.log` / the wrapper's own stdout summary
   block (`--- summary ---` ... `--- done ---`) has been read.

## Outcomes

1. **Guard fires (at a plausible, non-universal rate) and the process
   survives further** — real progress. If it reaches the ~140s DMA
   window, immediately check `ROGUESQ_LOG_DMA_CALLER` and
   `do_rom_read`/`pi-start-dma` per M3's original open question
   (CURRENT-TRUTH item 1) — all instruments are already armed in the
   same soak, no rebuild needed.
2. **Guard never fires, a different crash preempts it.** Read the new
   backtrace carefully before concluding anything — s100 initially
   suspected a recurrence of the 10th class from the outer three frames
   matching, but the *depth* of the backtrace (5 frames vs. the 10th
   class's 6) proved it was actually a new, 17th class. Check whether
   the innermost frame matches an already-known leaf site exactly
   (function name AND presence/absence of the expected deeper frame),
   not just the outer call chain. If it's a genuine recurrence of an
   already-catalogued class (9-17, or the RT64-internal 13th/15th),
   that's a cleaner signal — do not spend a 2nd soak on this exact site,
   move to whichever of {`projectModelBoundsToScreen`,
   `reserveAndEmitDLEntry`} you didn't just try. If it's an genuinely new
   (18th+) class, catalog it (name, address, backtrace, call chain) and
   still move on rather than chasing it — this family has never
   rewarded a same-site retry, per rule 8.
3. **Guard fires but the process still dies the same way** — the bounds
   check is wrong (too permissive, or the `U32()` truncation was
   skipped) or the skip path has a side effect that breaks something
   downstream. Read the new backtrace; it will tell you which.

## Do not

- Do not re-soak `composeNpcOrientationMatrix` or
  `activateAnimationKeyframe` — both guards are landed and validated
  (clean negative controls, s99/s100). Leave both
  `ROGUESQ_LOG_ANIM_KEYFRAME_GUARD=1` and
  `ROGUESQ_LOG_COMPOSE_NPC_GUARD=1` armed in every soak going forward
  (they're free) but treat both as closed, not targets.
- Do not skip the source-read step before guarding — confirm the crash
  shape matches the table-lookup-then-deref family before copy-pasting
  the guard pattern. If it's a different shape (like the 14th class may
  be), characterize first.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against
  32-bit literal bounds — always truncate through `U32()` first.
- Do not assume a bare `return;` is ABI-safe inside a guard without
  first checking whether the function spills callee-saved registers /
  adjusts `$sp` in its prologue.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched — s100 found a real regex collision
  across overlays; verify it's exactly the one expected file.
- Do not plan around "shorten the hold to reach the DMA window before
  the crash family" — refuted s98, the windows overlap.
- Do not re-run the plain DMA-caller repro as a dedicated work unit
  (3/3 attempts spent s95-s97, parked).
- Do not re-grep for `submitDmaRequestBatch(rdram`, ring literal
  constants, or `LOOKUP_FUNC(` call-site counts (done, stable, s93-s95).
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  routine on 487+ calls, reconfirmed every session since).
- Do not spend a soak trying to characterize the 13th or 15th crash
  classes (RT64-internal asserts, no fix available on our side) — track
  recurrence only.
- Do not poll for the game process with `pgrep -f "build/RogueSquadron64Recomp"`
  — it never matches (the binary is launched as `./RogueSquadron64Recomp`
  with no `build/` prefix in argv0). Use the PID the wrapper script
  prints, or `pgrep -f 'RogueSquadron64Recomp$'`.
- Do not invoke the N64Recomp binary or `make_elf.py` by a bare/relative
  path from an unapproved cwd. Use `zsh -c "..."` wrapping or
  `python3 ...` (matches `Bash(python3:*)`); `cmake --build /abs/path -j 8`
  (no leading `cd`) matches `Bash(cmake:*)` directly.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design (every session since s95) — do not attempt to commit it
  there; the durable record lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md`
  in this repo.
