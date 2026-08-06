# NEXT work unit

## s378 ran batch 2/N of the sanctioned fixup_game_funcs.py function-scope-match backport

Full write-up: `docs/CURRENT-TRUTH.md` item -232, `PORTING-STATE.md` Session 378. One-paragraph
version: re-ran the AST scan (technique unchanged from s377: `ast.parse` over
`~/Documents/Tools/N64Recomp/fixup_game_funcs.py`, filter `Call` nodes with `.attr == "subn"`
referencing the bare `text` variable) against current line numbers, confirmed 153 file-scoped sites
remained (176 − batch 1's 23, exact match). Converted 21 more across 8 functions
(`reserveAndEmitDLEntry`, `activateAnimationKeyframe`, `composeNpcOrientationMatrix`,
`projectModelBoundsToScreen`, `updateHangarBayScene`, `musyxSynthFrame`, `acquireSampleStreamBlock`,
`fillSampleStreamRange`), verified via two independent fresh `RecompiledFuncs/` regens producing
byte-identical patch reports (same proof standard as batch 1). Built clean. ~100s soak clean, VI
progressed the full 0→320→640→1024→640→512 phase timeline. **44/176 converted, 132 remain.**

## This iteration's work unit: batch 3 of the same backport (continue the sanctioned tooling item)

Same task, same methodology, next slice. Per s377/s378's own recommendation, don't try to convert
all 132 remaining in one iteration — pick a bounded sub-batch (roughly 20-30 sites), convert, verify,
build, soak, leave the rest for batch 4.

### Concrete steps
1. Regenerate the current inventory — line numbers shifted again after s378's edits. In
   `~/Documents/Tools/N64Recomp/`, run the same AST-based scan: `ast.parse` over
   `fixup_game_funcs.py`, walk for `Call` nodes with `.attr == "subn"` whose arguments reference the
   bare `text` variable (not a `body`/`new_body` per-function slice). Do not hand-grep for variable
   names — the AST scan is the only reliable technique (survives the file's variable-naming
   inconsistencies, s377/s378 both confirmed this).
2. Pick ~20-30 sites for this batch. s378 flagged the clear next target: **the `funcs_3.c`
   drain-mesh/heap-walker guard cluster** — the single largest remaining block (the
   hangar/reserve-list clusters batches 1+2 targeted are now mostly drawn down). If that cluster's
   sites don't have clear per-patch target-function comments for easy verification, fall back to
   whatever remaining cluster does.
3. Before editing: confirm `git -C ~/Documents/Tools/N64Recomp status --short -- fixup_game_funcs.py`
   still shows `??` (untracked), then back up:
   `cp fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch3`. (Batch 1's and
   batch 2's own backup files, `.pre-scope-backport-backup` and `.pre-scope-backport-backup-batch2`,
   should still be sitting in that directory from prior sessions — leave them, don't delete, they're
   the audit trail.)
4. Convert each chosen site to the same idiom as batches 1 and 2: locate the target function via a
   `func_start_m`/`func_re` regex search for its `RECOMP_FUNC void <Name>(...)` signature, slice
   `body_start`/`body_end`, run the identical regex pattern and replacement against `body` instead of
   `text`, reassemble. Do not change regex patterns or replacement logic — scope-narrowing only.
5. Verify with the SAME before/after methodology as batches 1 and 2 (the part that actually catches
   bugs, don't skip it): regenerate fresh `RecompiledFuncs/` twice — once with the
   `.pre-scope-backport-backup-batch3` original, once with the converted live script — diff the two
   patch reports. Delete stale `RecompiledFuncs/*.c` before each regen (item -20's standing rule
   against stale-file patch-stacking). Every converted patch's `xN` count must match exactly. Any
   mismatch = a genuine latent cross-function anchor collision (a real, valuable finding, not a bug
   in this refactor task) — stop and document that one site specifically, excluding just it from the
   batch, rather than steamrolling past it.
6. One regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`) -> `cmake --build . -j8` cycle to
   confirm the build still succeeds.
7. One short soak (~90-120s, standard `ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
   ROGUESQ_STUB_MISSING_FUNCS=1` recipe, SIGKILL not SIGTERM) confirming no new crash class — a
   refactor of the patching mechanism, not game logic, so a light smoke test suffices.
8. Two site-classes are correctly EXCLUDED from any batch, don't try to convert them: the
   `0x8008EC88` audio-gate durable hand patch (no `p.name` guard, a separately-named mechanism, not a
   "session-added guard/instrument patch"); the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair
   whose shared regex is intentionally dual-target by design.

### Expected outcome
Same shape as batches 1-2: either clean conversion + byte-identical verification + clean build/soak
(write up as ADVANCED), or a genuine latent-collision finding at one specific site (also valuable,
write up and guard/exclude that site). Consider delegating this whole batch to one self-contained
subagent again — it has now worked cleanly twice in a row for a task this mechanical and
line-count-heavy.

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 3 of an open-ended bounded tooling task — not a
hypothesis chase, so the usual 3-iteration pivot pressure doesn't apply the same way; still keep
naming it so the loop's bookkeeping stays consistent. At iteration 3, worth a brief check next
iteration: is the remaining 132-site tail closer to done in one or two more batches, or does it need
splitting further? If batch 3 clears another ~20-30 with the same clean shape, that's still ~4-5 more
batches at this rate — reasonable to keep going one batch per iteration rather than trying to force
it faster).
