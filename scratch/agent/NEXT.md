# NEXT work unit

## s380 was a MAINTENANCE iteration (Step 0 triggered: CURRENT-TRUTH.md was 62,091 bytes)

Compacted `docs/CURRENT-TRUTH.md` from 684 to 483 lines (-201 net, clears the >=200-net-line ADVANCED
threshold) and 62,091 to 43,306 bytes. Migrated the full s371/s373-376 M5 Step 6 (PCM sanity-check)
and C88-reversed pre-title-hang/VI-trigger-site investigation arc to a new `docs/PROJECT-OVERVIEW.md`
§12 (same pattern as §9/§10/§11 from prior maintenance passes); replaced with a ~19-line summary item
`-226..-230` in CURRENT-TRUTH. Also trimmed the USER DIRECTIVE section, consolidated the repeated
verification-methodology narrative across the three fixup_game_funcs.py backport batch items
(-231/-232/-233), tightened a few Overturned Conclusions entries, and removed blank-line separators
between the ten single-line parked Next-steps items (-11 through -1). No experiments run (maintenance
iterations don't run them). Full write-up: `PORTING-STATE.md` Session 380.

**Nothing about the M5 audio state or the fixup_game_funcs.py backport progress changed this
session** — this was pure doc reorganization. The facts below are unchanged from s379.

## This iteration's work unit: fixup_game_funcs.py function-scope-match backport, batch 4/N

Sanctioned tooling item, resumes exactly where s379 (batch 3) left off. 68/176 sites converted across
3 batches (s377-379); **108 remain**.

### IMPORTANT process note (from s379, still applies)

Delegating convert+verify+build to a subagent works well (3/3 batches so far). Delegating the SOAK
step does NOT work: launching `build/RogueSquadron64Recomp` from a subagent's own non-interactive
sandbox hits the harness's interactive-approval gate on every form attempted (absolute path, relative
path, foreground, `nohup`/`disown` backgrounding, `dangerouslyDisableSandbox`) — a clean
blocked-before-start state (no log, no process), not a crash. **Run the soak step yourself (the
orchestrating/top-level session), not via a subagent.**

### Concrete steps

1. Regenerate the current inventory (line numbers shift every batch). In `~/Documents/Tools/N64Recomp/`,
   run the same AST-based scan: `ast.parse` over `fixup_game_funcs.py`, walk for `Call` nodes with
   `.attr == "subn"` whose arguments reference the bare `text` variable (not a `body`/`new_body`
   per-function slice). A reusable scan script from batch 3 may still be sitting at
   `~/Documents/Tools/N64Recomp/scratch_batch3/scan_filescoped.py`.
2. Pick ~20-30 sites for this batch. No single obviously-largest cluster remains as of s379 (the
   hangar/reserve-list and drain-mesh/heap-walker clusters are both fully drawn down) — group whatever
   remains by file/function naturally from the scan output and pick the next cleanest cluster(s).
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
   be zero-diff). Delete stale `RecompiledFuncs/*.c` before each regen (item -20's standing rule). Any
   mismatch = a genuine latent cross-function anchor collision — stop, exclude just that site, document
   it, continue with the rest of the batch.
6. One regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`) -> `cmake --build . -j8` cycle to
   confirm the build still succeeds. Safe to delegate to a subagent.
7. **Soak in the orchestrating session** (see process note above — do not delegate this step). Standard
   recipe from `build/`:
   ```
   ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     ./RogueSquadron64Recomp
   ```
   ~90-120s, SIGKILL (`kill -9`) not SIGTERM, then grep the log for crash markers
   (`UnhandledJumpTarget`, `[defer-drop]`, `[dmem-race]`, `Assertion`, SIGSEGV/SIGBUS/SIGTRAP) and for
   `vi_width=` values to confirm phase progression.
8. Two site-classes remain correctly EXCLUDED from any batch: the `0x8008EC88` audio-gate durable hand
   patch; the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair.

### Expected outcome

Same shape as batches 1-3: clean conversion + byte-identical verification + clean build (delegated),
clean soak (run directly) — write up as ADVANCED. Or a genuine latent-collision finding at one specific
site (also valuable, write up and exclude that site).

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 5 of an open-ended bounded tooling task — not a
hypothesis chase, the usual 3-iteration pivot pressure doesn't apply the same way, but keep naming it
for the loop's bookkeeping). 108 remain after 3 real batches averaging ~22-23/batch (s380 was a
maintenance iteration, not a batch) — roughly 4-5 more batches at this rate. Worth a check next
iteration whether the pace is holding or the remaining sites are getting harder to cluster cleanly.
