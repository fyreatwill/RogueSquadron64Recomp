# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s540 recap (read this first)

**Fold-in of s539's queued 2nd confirm came back WEAK, not clean.** The
`RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD` confirm crashed early (19.8s, only 7 frames captured) with
`hangarbay-entry n=5` — single-digit, below the double-digit-or-better bar this campaign requires for
a valid positive control. Discarded per iron rule 1 rather than trusting its 0-fires result. The crash
it hit (`submitSceneNodeRender+38976`/`last-guest-pc=0x8001086c`) was cross-checked against every
catalogued item -320..-331 address, found genuinely new, filed as **item -332** (explicitly flagged
low-confidence given the weak control). Re-queued the retry:
`scratch/agent/soak_queue/s539_render_lit_textured_mesh_faces_r2_confirm_retry.sh` — **check
SOAK-RESULTS.md for its result at the top of next iteration, same gotcha as always (real diagnostics
in the same-named results subdirectory's `run.log`, not the top-level driver `.log`)**.

Re-scanned fresh and found TWO TIED genuine candidates in `renderLitTexturedMeshFaces` itself
(`funcs_3.c:33902`/`0x8000FC24` and `funcs_3.c:34530`/`0x8000FECC`, both reg=r2/off=0X4, count=27),
fixed as **`RENDER_LIT_TEXTURED_MESH_FACES_R3_GUARD`** and **`_R4_GUARD`** (40th/41st guards in the
campaign), batched into one build/run, regenerated, built clean. 1st live-verify
(`s540_render_lit_textured_mesh_faces_r3_r4_manual`) is CLEAN: 0 fires on either new guard, 0 fires on
any other armed guard family at all, `hangarbay-entry n=31` positive control, full 300s duration, zero
crashes at all — the cleanest possible verify class. 2nd independent confirm already queued to
`scratch/agent/soak_queue/s540_render_lit_textured_mesh_faces_r3_r4_confirm.sh` — the loop should pick
this up between iterations.

**Two soaks are now queued simultaneously** (the R2 retry AND the R3/R4 confirm) — the loop runs up to
2 queued recipes between iterations, so both may land before next session. Check SOAK-RESULTS.md for
BOTH result lines at the top of next iteration.

## This iteration's work unit

**Step 1 — fold in BOTH queued confirm results (do this FIRST, before picking a new work unit).**
For each of `s539_render_lit_textured_mesh_faces_r2_confirm_retry` and
`s540_render_lit_textured_mesh_faces_r3_r4_confirm`, find its SOAK-RESULTS.md line, read the run.log
INSIDE the same-named results subdirectory (not the top-level `.log` driver file), and grep for:
- the relevant guard's fire count (expect 0 for a clean result) — `render-lit-textured-mesh-faces-r2-
  guard` for the retry, `-r3-guard` and `-r4-guard` for the confirm
- fires on any OTHER armed guard family (regression check)
- `hangarbay-entry` count — must be non-trivial (double digits+) or the run is vacuous per iron rule 1;
  if weak/absent AGAIN, discard and re-queue a second retry, don't just accept a weak result twice
- the crash signature this run hit — check against items -320 through -332 in `docs/CURRENT-TRUTH.md`
  Next-steps; if it's a genuinely new signature, file it as item -333

If R2's retry is clean with a valid positive control: mark `RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD`
FULLY CLOSED 2/2. If R3/R4's confirm is clean with a valid positive control: mark both
`RENDER_LIT_TEXTURED_MESH_FACES_R3_GUARD` and `_R4_GUARD` FULLY CLOSED 2/2. Any subset closing pushes
the campaign's fully-closed count up from 38 — add rows to `docs/PROJECT-OVERVIEW.md` §25's table
(matching row 38/39's format) for whichever guards close this iteration, and fold the summary into
`PORTING-STATE.md`.

**Step 2 — re-scan and audit the next-ranked tier, same iteration (fold-in-then-pick pattern).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Skip any entry matching `renderLitTexturedMeshFaces` reg=`r4`/off=`0X0` (the long-standing,
   repeatedly-re-derived shape mismatch — `ctx->r4` there is the function's own provably-non-null `$a0`
   argument, not a reloaded global; re-verify this is still the case each session, don't assume).
3. Identify the top-ranked write line NOT already fixed AND matching the exact shape (`reg=r2,
   off=0X4`, i.e. a `MEM_W(0X4, ctx->rN) = ctx->rM;` fed by a `lui $v0,0x8011`/`lw $v0,0x63B0($v0)` load
   pair gated by `beq $v0,$zero,...`). At the s540 scan the tier after `renderLitTexturedMeshFaces`'s
   FOUR now-fixed sites ran: `funcs_3.c:34629` (reg=r7/off=0X0, DIFFERENT shape, skip),
   `funcs_4.c:7648` (`renderFlatMeshFaceGroup`, count=26, NEW function), `funcs_4.c:14889`
   (`renderLitMeshFaceGroup`, count=26, NEW site — note this function already carries the
   `RENDER_LIT_MESH_R2`-`R8_GUARD` lineage under a DIFFERENT idiom from s496-519, check this isn't a
   duplicate/already-covered idiom before assuming new). Re-verify the fresh ranking; do not assume
   this list survives a fresh session's re-scan — `renderLitTexturedMeshFaces` may still have further
   sites once its 4 fixed ones drop out of the ranking.
4. Pull all raw reload addresses feeding the target write line: filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, then for each record check its
   `hits` list for an entry whose `line` matches the target write line — print that record's
   `guest_addr` for every match. See s540's Python one-liner in PORTING-STATE.md Session 540 for the
   exact recipe (note: `write_line` is NOT a top-level field, it's `hits[].line`).
5. Cross-check EVERY raw address against `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory, and NOT the same repo as `RogueSquadron64Recomp` — it's
   a separate standalone git checkout with its own origin, untracked `fixup_game_funcs.py`, no
   submodule-patches export needed). `submitSceneNodeRender` now carries R1-R4, `emitColorFillRect`
   R1-R2, `drawSubtitleText` R1, `renderLitTexturedMeshFaces` R1-R4 — check the new candidate isn't one
   of those or their own load addresses.
6. Read the generated source around any zero-hit write address to confirm the exact vulnerable shape
   AND that the dereferenced register is actually a reload of the `+0x63B0`-offset global-table idiom
   (not a function argument or other already-validated value) — check this BEFORE the reachability
   cross-check (the s535 lesson).
7. Fix the first genuine candidate using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` — bump `N` if the function already
   has guards from this campaign. If two candidates tie in rank (as R3/R4 did this session), batch both
   into one build/run per the batch-instrumentation rule.
8. Regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`, all four steps
   mandatory; delete `RecompiledFuncs/funcs_*.c` first via a `python3 -c` glob+os.remove loop, `find
   -delete` is blocked in this sandbox):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py > <path inside one of the 3 allowed repos>   # audit for exactly the
                                                                            # expected xN counts, then
                                                                            # delete the report after
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
   Gotcha (s533): the CMake build directory that actually links `RogueSquadron64Recomp` is
   `RogueSquadron64Recomp/build`, NOT `N64Recomp/build`. Gotcha (s535): redirecting
   `fixup_game_funcs.py`'s output to `/tmp` is blocked by the sandbox — redirect inside one of the
   three allowed repos, delete after auditing.
9. 1st live-verify, manual, foreground — copy the most recent guard's manual script from
   `scratch/agent/soak_queue/done/` (`s540_render_lit_textured_mesh_faces_r3_r4_manual_20260809-run.sh`
   is the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't
   remove any existing ones — batch-instrumentation rule), point output at a new
   `scratch/agent/soak_results/s541_..._manual` path, run with `Bash` (it will auto-background if it
   exceeds the foreground timeout), then `TaskOutput` with `block: true` and `timeout: 300000` to wait
   synchronously. After running it, move it to `soak_queue/done/` yourself so the loop doesn't
   re-execute it a second time.
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial (double-digit+) count.** If weak/absent,
    discard and re-run. If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s541_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard
itself would be the first actual confirmation this idiom class fires in practice (none of the 41
guards fixed so far have ever fired) — treat that as a genuinely new, high-priority finding.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source.
- Never trust a 0-fires result without confirming the positive control appears with a non-trivial
  (double-digit+) count — a single-digit `hangarbay-entry` (s539's confirm attempt: n=5) is NOT
  sufficient; discard and re-run.
- One build/run carries every armed guard's env var (batch-instrumentation rule).
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan`.
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- `fixup_game_funcs.py`: `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` — NOT
  under a `tools/` subdirectory, NOT part of the RogueSquadron64Recomp git repo (separate standalone
  checkout, untracked file, no submodule-patches export step applies).
- The build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `make_elf.py`: `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py` (a THIRD
  repo) — run it from that repo's root.
- **Soak result diagnostics gotcha (s539)**: a soak's real per-guard diagnostics can live in a `run.log`
  file INSIDE a same-named results subdirectory, not in the top-level `.log` driver file next to it —
  check both, grep the one with actual `[guard-name]` lines.
- **JSON report field gotcha (s540)**: `s494_item317_step3_report.json` records don't have a top-level
  `write_line` field — the write line lives inside each record's `hits[].line`. Filter by `func` then
  check each hit's `line`.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp` fairly often — prefer single simple commands. Grep with a literal path instead
  of a shell variable when the sandbox flags "shell syntax that cannot be statically analyzed".
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
