# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## IMPORTANT: run Step 0 first this iteration

`docs/CURRENT-TRUTH.md` is 62762 bytes as of the end of s537 (was 59145 at s537's start, under the
60000 trigger -- this session's additions pushed it over). **Per `tools/agent/ITERATION.md` Step 0,
the NEXT iteration is a MAINTENANCE iteration**: compact `docs/CURRENT-TRUTH.md` toward its ~35 KB
target before picking a new work unit. Do NOT run the s538 experiment below until the maintenance
pass is done (or `wc -c` confirms it's back under 60000 for some other reason).

Maintenance targets, in order of easiest/safest to cut:
- Item -317's now very long guard-by-guard narrative (currently spans ~140 lines) is the single
  biggest block. Migrate the older, already-FULLY-CLOSED guard paragraphs (everything through
  `SUBMIT_SCENE_NODE_RENDER_R4_GUARD`, i.e. up through s534) into `docs/PROJECT-OVERVIEW.md` §22-§24
  (which already holds a summary table -- extend it, don't duplicate prose) and leave only the
  current/open guard's detail plus a one-line-per-closed-guard table entry in CURRENT-TRUTH.
  `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD` (open, pending 2nd confirm) and its immediate predecessor
  context should stay; `BEGIN_FRAME_DL_CHUNK_R1`-`R10`, `EMIT_COLOR_FILL_RECT_R1`-`R2`,
  `SUBMIT_SCENE_NODE_RENDER_R1`-`R4`, `DRAW_SUBTITLE_TEXT_R1` are all fully closed and safe to
  compress to a table row each.
- The USER DIRECTIVE headline (top of file) re-derives detail already in item -317 below it --
  shorten to just the current tally + pointer, drop the per-guard blow-by-blow that's now duplicated.
- Renumber/audit is NOT needed (numbering convention is append-only, never renumbered) -- just prune
  prose, don't renumber items.
- A net shrink of >=200 lines counts as ADVANCED for this iteration. Do NOT run experiments in a
  maintenance iteration.

## s537 recap -- read this after maintenance, before the s538 work unit

1. **Folded in `EMIT_COLOR_FILL_RECT_R2_GUARD`'s 2nd confirm** (`s536_emit_color_fill_rect_r2_confirm`,
   rc=3, 161s): 0 fires, 0 fires on any other armed guard family, `hangarbay-entry n=31` positive
   control. Crashed on `heapFreeListInsert+72`/`last-guest-pc=0x800220b8` -- a NEW signature (distinct
   from item -324's same-symbol `0x80015544`), filed as item -330. Marked FULLY CLOSED 2/2 -- this
   closes item -317 step 3's 37 guards to 37/37 fully closed (zero open guards) for the FIFTH time this
   campaign.
2. **Re-scanned for the next tier** (fresh `--scan` + `s506_dedupe.py`, no custom `--out`). Top of the
   table (`funcs_3.c:34432`, `renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`, count=27) re-checked and
   confirmed the SAME shape mismatch identified s535/s536 -- correctly re-skipped, no guard written.
3. **Moved to the next-ranked shape-matching entry**: `renderLitTexturedMeshFaces`'s OWN second site
   (`funcs_3.c:34329` at scan time, count=26, reg=`r2`/off=`0X4` -- the exact guarded shape). Cross-checked
   all 24 raw reload addresses feeding that write line directly against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- none present anywhere in it,
   genuinely uncovered (neither the write's own address `0x8000FE14` nor its load pair
   `0x8000FE04`/`0x8000FE08`). Read the generated source and confirmed the exact idiom shape.
4. **Fixed `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD`** in `fixup_game_funcs.py`, full regen/build applied
   cleanly (patched exactly x1, no duplicate-stacking).
5. **1st live-verify clean on the FIRST attempt** (unlike s536's 3 attempts): 0
   `render-lit-textured-mesh-faces-r1-guard` fires, 0 fires on any other armed guard family,
   `hangarbay-entry n=31` positive control (checked explicitly before trusting the 0-fires result, per
   the s536 lesson). Crashed at 115.7s on `heapFreeListInsert+72`/`last-guest-pc=0x800220b8` -- the
   IDENTICAL signature to the immediately-preceding `s536_emit_color_fill_rect_r2_confirm` run's crash,
   a genuine 2nd occurrence back-to-back. **Read this as weak corroboration, not strong**: same binary,
   same probe script, adjacent wall-clock time -- a shared transient is more likely than a stable
   recurring bug per the boring-first prior. Filed as item -330's 2nd sighting, watching for a 3rd in an
   unrelated run before escalating (same policy as item -327). 2nd independent confirm queued:
   `scratch/agent/soak_queue/s537_render_lit_textured_mesh_faces_r1_confirm.sh`.
6. Tally: item -317 step 3 now 38/~150 fixed, 37 fully closed 2/2,
   `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD` pending its 2nd confirm. ~108 sites remain across further
   tiers, unaudited.

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 537.

## The work unit for the iteration AFTER maintenance (s538 or later)

**If `scratch/agent/SOAK-RESULTS.md` has a new line for
`s537_render_lit_textured_mesh_faces_r1_confirm`**: read its directory's own `run.log`
(`scratch/agent/soak_results/s537_render_lit_textured_mesh_faces_r1_confirm/run.log` -- NOT just the
flat top-level summary file). **First check `hangarbay-entry` actually fired and reached a
double-digit-or-higher count** (if it shows 0 hangar-prefixed diagnostics anywhere, treat the run as
vacuous and re-queue rather than recording it). If 0 fires on `render-lit-textured-mesh-faces-r1-guard`
AND a real positive control, mark `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD` FULLY CLOSED 2/2 in
`docs/CURRENT-TRUTH.md` item -317 (38 fixed, 38 fully closed -- item -317 step 3 would then be 100%
closed on everything fixed so far, for the SIXTH time this campaign) and fold the result into
`PORTING-STATE.md`. **Also check whether this confirm run's crash (if any) is a THIRD occurrence of
item -330's `heapFreeListInsert+72`/`0x800220b8` signature** -- if so, that would be 3 occurrences
across independent runs and should be escalated (source-traced) per the campaign's standing policy for
2-in-N-sessions patterns (see item -327's precedent). Then continue to the next step below in the SAME
iteration (fold-in-then-pick pattern, s521-s537).

**Then (or if no confirm result is queued yet), re-scan and audit the next-ranked tier** using the SAME
cross-check methodology -- do NOT skip it and trust the raw tracer count. Always verify the write's
register/offset is `reg=r2, off=0X4` (the guarded shape) before investigating further -- the raw top count
(`funcs_3.c:34432`, `renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`) is now a KNOWN, three-times-confirmed
shape mismatch (s535, s536, s537) -- skip it without re-deriving from scratch, but do re-run the
scan/dedupe fresh each session since line numbers shift after every regen.

1. **Re-run the tracer fresh** (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. **Identify the top-ranked write line NOT already fixed AND matching the exact shape** (`reg=r2,
   off=0X4`, i.e. the generated source shows `MEM_W(0X4, ctx->r2) = ctx->r3;` fed by a `lui
   $v0,0x8011`/`lw $v0,0x63B0($v0)` load pair gated by a `beq $v0,$zero,...`). At the s537 scan (line
   numbers will shift after this session's regen, re-check), the table after
   `renderLitTexturedMeshFaces:34329` (26, now fixed as `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD`) ran:
   `funcs_4.c:7648` (`renderFlatMeshFaceGroup`, 26, NEW function), `funcs_4.c:14889`
   (`renderLitMeshFaceGroup`, 26, NEW function -- note `renderLitMeshFaceGroup` already carries the older
   `RENDER_LIT_MESH_R2`-`R8_GUARD` lineage under a DIFFERENT name/idiom from s496-519, check this isn't a
   duplicate of one of those before assuming new), `funcs_3.c:34504` (`renderLitTexturedMeshFaces`, 25, a
   THIRD site in this function -- check its reg/off before assuming it's genuine and not another r4/off0X0
   mismatch). Re-verify the fresh ranking first -- do not assume this exact ordering survives the regen.
3. **Pull all raw reload addresses feeding the target write line** (filter the raw JSON report,
   `scratch/agent/s494_item317_step3_report.json`, by `func==<name>` and hits containing the target write
   line -- Python one-liner pattern: `[e for e in data if e['func']==name and any(h['kind']=='write' and
   h['line']==target_line for h in e['hits'])]`, then print `e['guest_addr']` for each match).
4. **Cross-check EVERY raw address against `fixup_game_funcs.py` directly** (the actual path is
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, NOT under a `tools/`
   subdirectory). **Caution**: `submitSceneNodeRender` now carries FOUR guards (R1-R4), `emitColorFillRect`
   carries TWO (R1 at `0x8000A538`, R2 at `0x8000A3C4`), `drawSubtitleText` carries one (R1 at
   `0x80016B58`), `renderLitTexturedMeshFaces` carries one (R1 at `0x8000FE14`) -- check the new
   candidate's write address isn't one of those (or one of THEIR OWN load addresses) before assuming it's
   genuinely uncovered.
5. **Read the generated source** around any zero-hit write address to confirm the exact vulnerable shape
   AND confirm the dereferenced register is actually a reload of the `+0x63B0`-offset global-table idiom,
   not a function argument or other already-validated value (check this BEFORE the reachability
   cross-check, not after -- the s535 lesson).
6. **Fix the first genuine candidate** using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` -- bump `N` if the function already has
   guards from this campaign.
7. **Regen** (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`, all four steps,
   fixup is NOT optional; delete `RecompiledFuncs/funcs_*.c` first per the standing item -20 rule --
   `python3 -c` a `glob.glob` + `os.remove` loop, `find -delete` is blocked in this sandbox). Exact
   commands (validated s537):
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
   **Gotcha (s533)**: the CMake build directory that actually links `RogueSquadron64Recomp` is
   `RogueSquadron64Recomp/build`, NOT `N64Recomp/build`.
   **Sandbox note (s535)**: redirecting `python3 fixup_game_funcs.py` output to `/tmp` is blocked by the
   session's directory allowlist -- redirect to a file inside one of the three allowed repos instead, then
   delete it after auditing.
8. **1st live-verify, manual, foreground** -- copy the most recent guard's manual script from
   `scratch/agent/soak_queue/done/` (`s537_render_lit_textured_mesh_faces_r1_manual_20260809-020000.sh` is
   the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed env-var list
   (append, do not remove any existing ones -- batch-instrumentation rule), point the output dir at a new
   `scratch/agent/soak_results/s538_..._manual` path, run it with `Bash run_in_background: true`, then use
   `TaskOutput` with `block: true` and a `timeout` of 300000 on that task ID to synchronously wait for it.
9. **Read the run.log directly** (grep for the new guard's fire count, `hangarbay-entry` count, and any
   crash/signal markers) -- do not trust a stale cached read. **Standing lesson: before trusting ANY
   0-fires result, first confirm `hangarbay-entry` (or another armed positive control) actually appears in
   the log with a non-trivial count.** A full-duration rc=0 completion is not itself proof the guarded code
   ran -- an s536 attempt completed the full 300s with rc=0 and ZERO hangar-prefixed diagnostics anywhere,
   because the scripted key sequence evidently diverged onto a different scene path that run (same script,
   same binary, different outcome -- `PROBE_KEYS_FROM_PHASE` timing does not guarantee an identical
   playthrough). If the positive control is weak (single digits) or absent, discard the run and re-run
   rather than recording it. If clean with a real positive control, queue a 2nd independent confirm to
   `scratch/agent/soak_queue/s538_..._confirm.sh` (loop-queued, same recipe, new output dir -- a `sed`
   rename of the manual script's guard-family env-vars and output path works well) and record the
   1st-verify result in `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard
itself would be the first actual confirmation this idiom class fires in practice (none of the 38 guards
fixed so far have ever fired) -- treat that as a genuinely new, high-priority finding, not routine.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source.
- **Never trust a 0-fires result without confirming the positive control (`hangarbay-entry` or
  equivalent) actually appears in the run.log with a non-trivial count.** A full-duration rc=0
  completion, or even a crash, is NOT itself evidence the guarded scene was reached -- grep for the
  positive control explicitly every time before recording a result.
- One build/run carries every armed guard's env var (batch-instrumentation rule) -- never spend a
  build-run cycle isolating just the newest guard.
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan` or dedupe
  silently ranks against stale data (s521 gotcha).
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- The `fixup_game_funcs.py` used by this campaign lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- NOT under a `tools/`
  subdirectory.
- The build that actually matters is `RogueSquadron64Recomp/build`, not `N64Recomp/build` (s533 gotcha).
- `make_elf.py` lives at `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py` (a
  THIRD repo, not under `RogueSquadron64Recomp` or `N64Recomp`) -- run it from that repo's root.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, AND output redirection
  to `/tmp` in a single Bash call fairly often -- prefer single simple commands; delete generated files
  with a small `python3 -c` one-liner (`glob.glob` + `os.remove`); redirect script output only to paths
  inside the three allowed repo directories.
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) on the returned task ID to synchronously wait for it to finish before
  doing anything else.
- `docs/CURRENT-TRUTH.md` is 62762 bytes at s537's end -- do the maintenance pass FIRST next iteration,
  per Step 0 above.
