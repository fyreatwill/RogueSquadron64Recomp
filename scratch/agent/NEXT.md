# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s539 recap (read this first)

Folded in s537's queued `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD` 2nd confirm: CLEAN (0 fires on the
guard, 0 fires on any other armed guard family, `hangarbay-entry n=31` positive control), marking it
FULLY CLOSED 2/2 — 38/38 guards fully closed (100%, zero open guards) for the sixth time this
campaign. That confirm's crash (`heapFreeListDequeue+29152`/`last-guest-pc=0x8000d688`,
`local-symtab`-tagged) was a genuinely NEW single-occurrence signature — NOT a 3rd occurrence of item
-330 (different function, Dequeue not Insert) — filed as **item -331**, not chased.

Re-scanned fresh and found a genuine SECOND candidate in `renderLitTexturedMeshFaces` itself
(`funcs_3.c:34094`/`0x8000FCF4`, an EARLIER site than R1's `0x8000FE14`), fixed as
**`RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD`** (39th guard in the campaign), regenerated, built clean.
1st live-verify (`s539_render_lit_textured_mesh_faces_r2_manual`) is CLEAN: 0 fires on the new guard,
0 regressions, `hangarbay-entry n=34` positive control, full 300s duration, zero crashes at all — the
cleanest possible verify class. 2nd independent confirm already queued to
`scratch/agent/soak_queue/s539_render_lit_textured_mesh_faces_r2_confirm.sh` — **the loop should pick
this up between iterations; check `scratch/agent/SOAK-RESULTS.md` for its result at the top of next
iteration** (read list #3 in ITERATION.md already covers this).

## This iteration's work unit

**Step 1 — fold in the queued confirm result (do this FIRST, before picking a new work unit).**
`scratch/agent/SOAK-RESULTS.md` should have a line for `s539_render_lit_textured_mesh_faces_r2_confirm`
once the loop has run it. Read the run.log directly (the actual diagnostics live in a `run.log` file
INSIDE the soak's own results directory, e.g.
`scratch/agent/soak_results/s539_render_lit_textured_mesh_faces_r2_confirm_<timestamp>/run.log` if the
loop names it as a directory, or check the exact path in the SOAK-RESULTS.md line — **s537's confirm
had a top-level `.log` driver file that was NOT the real diagnostics log; the real one was inside
`scratch/agent/soak_results/<name>/run.log`, a subdirectory with the SAME base name minus `.log`. Check
both and grep the one with actual `[guard-name]`/`hangarbay-entry` lines, not just the probe.sh driver
output**). Grep for:
- `render-lit-textured-mesh-faces-r2-guard` fire count (expect 0 for a clean result)
- fires on any OTHER armed guard family (regression check) — sibling-guard `n=0` dumps at crash time
  are diagnostic snapshots, not fires; only count lines that look like an actual increment (`n=1+`)
- `hangarbay-entry` count — must be non-trivial (double digits+) or the run is vacuous per iron rule 1
- the crash signature this run hit (pc-symbol + last-guest-pc) — check against items -320 through -331
  in `docs/CURRENT-TRUTH.md` Next-steps; if it's a genuinely new signature, file it as item -332

If 0 fires on the guard AND a real positive control: mark `RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD`
FULLY CLOSED 2/2 in `docs/CURRENT-TRUTH.md` item -317 (39 fixed, 39 fully closed — 100% closed on
everything fixed so far, for the SEVENTH time this campaign) and add row 39 to
`docs/PROJECT-OVERVIEW.md` §25's table (matching the existing rows' format — see row 38 for the most
recent example, added s539). Fold the summary into `PORTING-STATE.md`.

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
   pair gated by `beq $v0,$zero,...`). At the s539 scan the tier after `renderLitTexturedMeshFaces`'s
   two now-fixed sites (`34094`→R2, `34329`→R1) ran: `funcs_3.c:34517` (`renderLitTexturedMeshFaces`,
   count=27, a THIRD site — check reg/off before assuming genuine, don't assume it survives a fresh
   scan), `funcs_4.c:7648` (`renderFlatMeshFaceGroup`, count=26, NEW function), `funcs_4.c:14889`
   (`renderLitMeshFaceGroup`, count=26, NEW site — note this function already carries the
   `RENDER_LIT_MESH_R2`-`R8_GUARD` lineage under a DIFFERENT idiom from s496-519, check this isn't a
   duplicate/already-covered idiom before assuming new). Re-verify the fresh ranking; do not assume
   this list survives a fresh session's re-scan.
4. Pull all raw reload addresses feeding the target write line (filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>` and hits containing the target
   write line, print `guest_addr` for each match — see s539's Python one-liner in PORTING-STATE.md
   Session 539 for the exact recipe).
5. Cross-check EVERY raw address against `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory). `submitSceneNodeRender` now carries R1-R4,
   `emitColorFillRect` R1-R2, `drawSubtitleText` R1, `renderLitTexturedMeshFaces` R1-R2 — check the new
   candidate isn't one of those or their own load addresses.
6. Read the generated source around any zero-hit write address to confirm the exact vulnerable shape
   AND that the dereferenced register is actually a reload of the `+0x63B0`-offset global-table idiom
   (not a function argument or other already-validated value) — check this BEFORE the reachability
   cross-check (the s535 lesson).
7. Fix the first genuine candidate using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` — bump `N` if the function already
   has guards from this campaign.
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
   `scratch/agent/soak_queue/done/` (`s539_render_lit_textured_mesh_faces_r2_manual_20260809-030000.sh`
   is the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't
   remove any existing ones — batch-instrumentation rule), point output at a new
   `scratch/agent/soak_results/s540_..._manual` path, run with `Bash` (it will auto-background if it
   exceeds the foreground timeout), then `TaskOutput` with `block: true` and `timeout: 300000` to wait
   synchronously.
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial count.** If weak/absent, discard and re-run.
    If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s540_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard
itself would be the first actual confirmation this idiom class fires in practice (none of the 39
guards fixed so far have ever fired) — treat that as a genuinely new, high-priority finding.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source.
- Never trust a 0-fires result without confirming the positive control appears with a non-trivial
  count.
- One build/run carries every armed guard's env var (batch-instrumentation rule).
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan`.
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- `fixup_game_funcs.py`: `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` — NOT
  under a `tools/` subdirectory.
- The build that matters: `RogueSquadron64Recomp/build`, not `N64Recomp/build`.
- `make_elf.py`: `/Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py` (a THIRD
  repo) — run it from that repo's root.
- **Soak result diagnostics gotcha (s539)**: a soak's real per-guard diagnostics can live in a `run.log`
  file INSIDE a same-named results subdirectory, not in the top-level `.log` driver file next to it —
  check both, grep the one with actual `[guard-name]` lines.
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp` fairly often — prefer single simple commands.
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
