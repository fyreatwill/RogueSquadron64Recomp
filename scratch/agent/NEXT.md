# NEXT work unit

## s379 ran batch 3/N of the sanctioned fixup_game_funcs.py function-scope-match backport

Full write-up: `docs/CURRENT-TRUTH.md` item -233, `PORTING-STATE.md` Session 379. One-paragraph
version: re-ran the AST scan against current line numbers, confirmed 132 file-scoped sites remained
(153 − batch 2's 21, exact match). Converted 24 more, all in `funcs_3.c` — the entire drain-mesh/
heap-walker cluster (`beginFrameDLChunk`, `emitAllocatedDLCommand`, `heapWalker`,
`heapFreeListDequeue`, `drainMeshReleaseQueue`) — verified via two independent fresh
`RecompiledFuncs/` regens producing byte-identical patch reports (same proof standard as batches
1-2). Built clean. Soak run directly by the orchestrating session (the delegated subagent hit a
hard interactive-approval wall trying to launch the compiled binary itself — see process note
below): ~110s, 0 crash markers, VI traversed the FULL 0→320→512→640→1024 phase timeline in one run.
**68/176 converted, 108 remain.**

## IMPORTANT process note for this batch

The last three batches all delegated the convert+verify+build work to one subagent successfully.
Batch 3 additionally tried delegating the soak step and it FAILED: launching
`build/RogueSquadron64Recomp` from the subagent's own non-interactive background session hit the
harness's interactive-approval gate on every form attempted (absolute path, relative path,
foreground, `nohup`/`disown` backgrounding, `dangerouslyDisableSandbox`) — a clean
blocked-before-start state (no log, no process), not a crash or hang, but zero soak coverage
resulted from delegating it.

**For batch 4: delegate the convert+verify+build steps to a subagent exactly as before, but run the
soak step yourself (the orchestrating/top-level session) once the subagent reports back a clean
build.** Use the standard recipe from `build/`:
```
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ./RogueSquadron64Recomp
```
~90-120s, SIGKILL (`kill -9`) not SIGTERM, then grep the log for crash markers
(`UnhandledJumpTarget`, `[defer-drop]`, `[dmem-race]`, `Assertion`, SIGSEGV/SIGBUS/SIGTRAP) and for
`vi_width=` values to confirm phase progression. A reusable self-contained soak script is at
`scratch/agent/soak_queue/s379_batch3_manual_soak.sh` if a quick copy/adapt is faster than
composing the launch+watchdog+kill sequence by hand again.

## This iteration's work unit: batch 4 of the same backport

### Concrete steps
1. Regenerate the current inventory (line numbers shifted again after batch 3's edits). In
   `~/Documents/Tools/N64Recomp/`, run the same AST-based scan: `ast.parse` over
   `fixup_game_funcs.py`, walk for `Call` nodes with `.attr == "subn"` whose arguments reference the
   bare `text` variable (not a `body`/`new_body` per-function slice). The subagent's own scan script
   from batch 3 may still be sitting at `~/Documents/Tools/N64Recomp/scratch_batch3/scan_filescoped.py`
   — reusable, or trivially rewritable from the same spec.
2. Pick ~20-30 sites for this batch. **No single obviously-largest cluster remains** as of s379 —
   the two big blocks (hangar/reserve-list, drain-mesh/heap-walker) are both now fully converted.
   Group whatever remains by file/function naturally from the scan output and pick the next cleanest
   cluster (or clusters) totaling ~20-30 sites.
3. Before editing: confirm `git -C ~/Documents/Tools/N64Recomp status --short -- fixup_game_funcs.py`
   still shows `??` (untracked), then back up:
   `cp fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch4`. Leave all prior
   batches' backup files in place (audit trail).
4. Convert each chosen site to the same idiom as batches 1-3: locate the target function via a
   `func_start_m`/`func_re` regex search for its `RECOMP_FUNC void <Name>(...)` signature, slice
   `body_start`/`body_end`, run the identical regex pattern and replacement against `body` instead of
   `text`, reassemble. Do not change regex patterns or replacement logic — scope-narrowing only.
5. Verify with the SAME before/after methodology as batches 1-3: regenerate fresh `RecompiledFuncs/`
   twice — once with the `.pre-scope-backport-backup-batch4` original, once with the converted live
   script — diff the two patch reports (must match exactly) and `diff -rq` the two output trees (must
   be zero-diff). Delete stale `RecompiledFuncs/*.c` before each regen (item -20's standing rule).
   Any mismatch = a genuine latent cross-function anchor collision — stop, exclude just that site,
   document it, continue with the rest of the batch.
6. One regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`) -> `cmake --build . -j8` cycle to
   confirm the build still succeeds. This part IS safe to delegate to a subagent.
7. **Soak in the orchestrating session** (see process note above — do not delegate this step).
8. Two site-classes remain correctly EXCLUDED from any batch: the `0x8008EC88` audio-gate durable
   hand patch; the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair.

### Expected outcome
Same shape as batches 1-3: clean conversion + byte-identical verification + clean build (delegated),
clean soak (run directly) — write up as ADVANCED. Or a genuine latent-collision finding at one
specific site (also valuable, write up and exclude that site).

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 4 of an open-ended bounded tooling task — not a
hypothesis chase, the usual 3-iteration pivot pressure doesn't apply the same way, but keep naming it
for the loop's bookkeeping). 108 remain after 4 batches averaging ~22-23/batch — roughly 4-5 more
batches at this rate. Worth a check next iteration (batch 5) whether the pace is holding or the
remaining sites are getting harder to cluster cleanly.
