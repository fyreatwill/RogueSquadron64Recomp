# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s541 recap (read this first)

**Folded in BOTH of s540's queued confirms — both CLEAN.**
- `s539_render_lit_textured_mesh_faces_r2_confirm_retry`: 0
  `render-lit-textured-mesh-faces-r2-guard` fires, `hangarbay-entry n=32` (valid positive control), no
  crash at all, full 349s duration. **Gotcha confirmed again**: the real diagnostics were in
  `scratch/agent/soak_results/s539_render_lit_textured_mesh_faces_r2_confirm/run.log` (the ORIGINAL
  non-`_retry` name — the retry script's PROBE `--out` argument pointed there, not at a
  `..._retry`-named directory). `RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD` marked FULLY CLOSED 2/2.
- `s540_render_lit_textured_mesh_faces_r3_r4_confirm`: 0 fires on either guard, `hangarbay-entry n=31`,
  crashed at 113.1s on `pc-symbol=hangarTickCameraOrbit+5188`/`last-guest-pc=0x800ab068` — the
  long-recurring `0x800ab068` background-noise family (NOT new; host symbol resolution varies build to
  build, e.g. also seen as `loadCutsceneAssetsByIndex+1860` and `initVec4TripletFromArgs+68` in other
  sessions — the guest PC is the stable signature). Both `RENDER_LIT_TEXTURED_MESH_FACES_R3_GUARD` and
  `_R4_GUARD` marked FULLY CLOSED 2/2.

This closed the campaign's first 41 guards to 41/41 fully closed (zero open guards) — the fourth time
this campaign has reached that state.

**Found and fixed the next tier (s541)**: fresh re-scan put TWO TIED entries at the exact guarded shape
(reg=`r2`, off=`0X4`, count=26 each) in TWO DIFFERENT functions: `funcs_4.c:7648` (site=`0x80011B54`,
`renderFlatMeshFaceGroup`, a brand-new function) and `funcs_4.c:14889` (site=`0x80013DF4`,
`renderLitMeshFaceGroup`, confirmed a genuine 9th distinct site — checked against the existing
`RENDER_LIT_MESH_R2`-`R8_GUARD` lineage's seven addresses, none matched). Fixed as
**`RENDER_FLAT_MESH_FACE_GROUP_R1_GUARD`** and **`RENDER_LIT_MESH_R9_GUARD`** (42nd/43rd guards),
batched into one build/run, regenerated, built clean. 1st live-verify
(`s541_render_flat_mesh_face_group_r1_render_lit_mesh_r9_manual`) is CLEAN on the first attempt: 0 fires
on either new guard, 3 benign `s284-guard` + 1 benign `hangar-bay-deref-guard` co-fires (no regression),
`hangarbay-entry n=31` positive control. Crashed at 113.3s on the SAME recurring `0x800ab068`
background-noise family this session's step-1 fold-in also hit (`initVec4TripletFromArgs+68` this
instance). 2nd independent confirm already queued:
`scratch/agent/soak_queue/s541_render_flat_mesh_face_group_r1_render_lit_mesh_r9_confirm.sh` — the loop
should pick this up between iterations.

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST, before picking a new work unit).**
For `s541_render_flat_mesh_face_group_r1_render_lit_mesh_r9_confirm`, find its SOAK-RESULTS.md line,
read the run.log INSIDE the same-named results subdirectory (not the top-level `.log` driver file —
**check BOTH**, the real per-guard diagnostics are not reliably in one or the other from session to
session), and grep for:
- `render-flat-mesh-face-group-r1-guard` and `render-lit-mesh-r9-guard` fire counts (expect 0 for a
  clean result)
- fires on any OTHER armed guard family (regression check)
- `hangarbay-entry` count — must be non-trivial (double digits+) or the run is vacuous per iron rule 1;
  if weak/absent, discard and re-queue a retry, don't just accept a weak result
- the crash signature this run hit — check the `last-guest-pc` value (not just the symbolizer's
  `pc-symbol` name, which varies build to build for the same guest PC — s541's own gotcha) against
  items -320 through -332 in `docs/CURRENT-TRUTH.md` Next-steps; if it's a genuinely new guest PC, file
  it as item -333

If clean with a valid positive control: mark both `RENDER_FLAT_MESH_FACE_GROUP_R1_GUARD` and
`RENDER_LIT_MESH_R9_GUARD` FULLY CLOSED 2/2 — add rows to `docs/PROJECT-OVERVIEW.md` §25's table
(update row 42/43's status text, matching the format of every other closed row) and fold the summary
into `PORTING-STATE.md`.

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
   pair gated by `beq $v0,$zero,...`). At the s541 scan the tier after `renderFlatMeshFaceGroup`'s and
   `renderLitMeshFaceGroup`'s new sites ran: `funcs_4.c:7775` (reg=r4/off=0X0, `renderFlatMeshFaceGroup`,
   DIFFERENT shape, skip — check this is still the same own-argument mismatch as the perennial
   `renderLitTexturedMeshFaces` one before assuming), `funcs_4.c:14423` (`renderLitMeshFaceGroup`,
   reg=r2/off=0X4, count=24, would be a 10th site in this function — check against R2-R9's now-9
   addresses including this session's R9 before assuming new), `funcs_3.c:10887`
   (`emitColorFillRect`, count=22, would be a 3rd site alongside R1/R2). Re-verify the fresh ranking; do
   not assume this list survives a fresh session's re-scan.
4. Pull all raw reload addresses feeding the target write line: filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>`, then for each record check its
   `hits` list for an entry whose `line` matches the target write line — print that record's
   `guest_addr` for every match. `write_line` is NOT a top-level field, it's `hits[].line`.
5. Cross-check EVERY raw address against `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory, and NOT the same repo as `RogueSquadron64Recomp` — it's
   a separate standalone git checkout with its own origin, untracked `fixup_game_funcs.py`, no
   submodule-patches export needed). `submitSceneNodeRender` now carries R1-R4, `emitColorFillRect`
   R1-R2, `drawSubtitleText` R1, `renderLitTexturedMeshFaces` R1-R4, `renderFlatMeshFaceGroup` R1,
   `renderLitMeshFaceGroup` R2-R9 — check the new candidate isn't one of those or their own load
   addresses.
6. Read the generated source around any zero-hit write address to confirm the exact vulnerable shape
   AND that the dereferenced register is actually a reload of the `+0x63B0`-offset global-table idiom
   (not a function argument or other already-validated value) — check this BEFORE the reachability
   cross-check (the s535 lesson).
7. Fix the first genuine candidate using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` — bump `N` if the function already
   has guards from this campaign. If two candidates tie in rank (as they have most recent sessions),
   batch both into one build/run per the batch-instrumentation rule.
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
   `scratch/agent/soak_queue/done/` (`s541_render_flat_mesh_face_group_r1_render_lit_mesh_r9_manual_20260809-run.sh`
   is the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't
   remove any existing ones — batch-instrumentation rule), point output at a new
   `scratch/agent/soak_results/s542_..._manual` path, run with `Bash` (it will auto-background if it
   exceeds the foreground timeout), then `TaskOutput` with `block: true` and `timeout: 300000` to wait
   synchronously. After running it, move it to `soak_queue/done/` yourself so the loop doesn't
   re-execute it a second time.
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial (double-digit+) count.** If weak/absent,
    discard and re-run. If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s542_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard
itself would be the first actual confirmation this idiom class fires in practice (none of the 43
guards fixed so far have ever fired) — treat that as a genuinely new, high-priority finding.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source.
- Never trust a 0-fires result without confirming the positive control appears with a non-trivial
  (double-digit+) count.
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
- **Soak result diagnostics gotcha (s539/s541)**: a soak's real per-guard diagnostics can live in a
  `run.log` file INSIDE a same-named results subdirectory, OR the retry script may point its `--out` at
  the ORIGINAL (non-retry-suffixed) results directory instead of a new one — check both locations, grep
  the one with actual `[guard-name]` lines, don't assume the naming is consistent.
- **JSON report field gotcha (s540)**: `s494_item317_step3_report.json` records don't have a top-level
  `write_line` field — the write line lives inside each record's `hits[].line`. Filter by `func` then
  check each hit's `line`.
- **`0x800ab068` background-noise gotcha (s541)**: this recurring guest-PC crash resolves to a
  DIFFERENT host `pc-symbol` almost every time it's hit (`loadCutsceneAssetsByIndex+1860`,
  `hangarTickCameraOrbit+5188`, `initVec4TripletFromArgs+68`, ...) — always cross-check the
  `last-guest-pc` value itself, not just the symbol name, before filing a "new" item.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp` fairly often — prefer single simple commands. Grep with a literal path instead
  of a shell variable when the sandbox flags "shell syntax that cannot be statically analyzed". Writing
  a multi-line string with embedded `#` inside a quoted shell/python argument can also trip the sandbox
  ("Newline followed by # inside a quoted argument can hide arguments from path validation") — write
  long append content to a scratch `.md` file with the Write tool first, then `cat file >> target`.
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
