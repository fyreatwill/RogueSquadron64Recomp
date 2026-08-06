# NEXT work unit

## s377 ran batch 1/N of the sanctioned fixup_game_funcs.py function-scope-match backport

Full write-up: `docs/CURRENT-TRUTH.md` item -231, `PORTING-STATE.md` Session 377. One-paragraph
version: an AST-based scan (not a grep guess) found the real count of file-scoped `re.subn(...,
text, ...)` patch sites in `~/Documents/Tools/N64Recomp/fixup_game_funcs.py`: **176**, not the
docstring's "~150"/CURRENT-TRUTH's prior "~100" estimate. Converted 23 (all at pre-edit line <1250)
to the BREADCRUMB10-15 function-scoped idiom, verified via two independent fresh `RecompiledFuncs/`
regens (original script vs. converted script) producing **byte-identical patch reports** — the
strongest available proof that no anchor was silently matching the wrong function and that this
batch changed match SCOPE only, not behavior. Built clean, soaked clean (0 crash markers in ~70s,
though VI didn't reach 640 in that window — flagged as unlikely-regression given the byte-identical
proof, not chased further, single sample). **~152 patches remain.**

## This iteration's work unit: batch 2 of the same backport (continue the sanctioned tooling item)

Same task as batch 1, same methodology — just the next slice. Per s377's own recommendation, don't
try to convert all ~152 remaining in one iteration; pick another bounded sub-batch (roughly 20-30
sites), convert, verify, build, soak, and leave the rest for batch 3.

### Concrete steps
1. Regenerate the current inventory (line numbers shifted since s377's edits — don't rely on old
   line numbers). In `~/Documents/Tools/N64Recomp/`, run an AST-based scan: `ast.parse` over
   `fixup_game_funcs.py`, walk for `Call` nodes with `.attr == "subn"` whose arguments reference the
   bare `text` variable (not a `body`/`new_body` per-function slice). This is the exact technique
   s377 used — do not hand-grep for `new, n = re.subn(` variable-name patterns again; the AST scan
   is more reliable (it survived s377's own variable-naming inconsistencies).
2. Pick ~20-30 sites for this batch. s377 flagged two visible clusters to start with: the
   hangar/reserve-list patches in `funcs_40.c`/`funcs_15.c`/`funcs_23.c`/`funcs_24.c` (mostly
   musyx/audio-tick diagnostics — the SAME family of functions batch 1 already touched, so context
   from batch 1's conversions may transfer), then separately the `funcs_3.c` drain-mesh/heap-walker
   guard cluster (the single largest remaining block, roughly current lines 5000-10400 pre-this-
   session — will have shifted). Either cluster is a reasonable batch-2 target; pick whichever has
   clearer per-patch target-function comments (easier to verify correctly).
3. Before editing: confirm `git -C ~/Documents/Tools/N64Recomp status --short -- fixup_game_funcs.py`
   still shows `??` (untracked), then back up:
   `cp fixup_game_funcs.py fixup_game_funcs.py.pre-scope-backport-backup-batch2`.
4. Convert each chosen site to the BREADCRUMB10-15 idiom exactly as s377 did: locate the target
   function via a `func_start_m` regex search for its `RECOMP_FUNC void <Name>(...)` signature,
   slice `body_start`/`body_end` via `func_re.search`, run the identical regex pattern and
   replacement against `body` instead of `text`, reassemble. Do not change regex patterns or
   replacement logic — scope-narrowing only.
5. Verify with the SAME before/after methodology as batch 1 (this is the part that actually catches
   bugs, don't skip it): regenerate fresh `RecompiledFuncs/` twice — once fixed with the
   `.pre-scope-backport-backup-batch2` original, once with the converted live script — diff the two
   patch reports. Every converted patch's `xN` count must match exactly. Any mismatch = a real latent
   cross-function anchor collision (a genuine, valuable finding, not a bug in this refactor task) —
   stop and document that one site specifically rather than steamrolling past it.
6. One regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`) -> `cmake --build . -j8` cycle
   to confirm the build still succeeds.
7. One short soak (~90-120s, standard `ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
   ROGUESQ_STUB_MISSING_FUNCS=1` recipe, SIGKILL not SIGTERM) confirming no new crash class — this is
   a refactor of the patching mechanism, not game logic, so a light smoke test suffices, not a full
   validation campaign.
8. Two site-classes are correctly EXCLUDED from any batch, don't try to convert them: the
   `0x8008EC88` audio-gate durable hand patch (no `p.name` guard, a separately-named mechanism, not
   a "session-added guard/instrument patch"); the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine`
   pair whose shared regex is intentionally dual-target by design.

### Expected outcome
Same shape as batch 1: either clean conversion + byte-identical verification + clean build/soak
(write up as ADVANCED, same as batch 1), or a genuine latent-collision finding at one specific site
(also valuable, write up and guard that site). Consider delegating this whole batch to one
self-contained subagent again, same as s377 — it worked well for a task this mechanical and
line-count-heavy.

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 2 of an open-ended bounded tooling task — not a
hypothesis chase, so the usual 3-iteration pivot pressure doesn't apply in the same way; still keep
naming it so the loop's bookkeeping stays consistent, and re-evaluate around iteration 4-5 whether
this should be split further or is close enough to done to finish in one more pass).
