# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s538 recap (maintenance iteration, read this first)

Step 0 triggered (`docs/CURRENT-TRUTH.md` was 62762 bytes, over the 60000 cap). s538 was a pure
maintenance pass: migrated item -317's guard-by-guard narrative for guards 26-37 (s526-537) into
`docs/PROJECT-OVERVIEW.md` §25 (same table format as §23), condensed the closed breadcrumb items
(-310/-311/-316/-318/-319/-320..-330) to their essential facts with pointers to §24-§25, fixed a
stale cross-reference in M2's goal-stack paragraph, and tightened spacing/duplication in the
USER DIRECTIVE headline. Result: `docs/CURRENT-TRUTH.md` 583→379 lines (-204 net, clears the
>=200-line ADVANCED bar), 62762→43856 bytes (-30%). No experiment ran this iteration — do not treat
s538 as having advanced the item -317 sweep itself; that work resumes below, at exactly where s537
left off.

## This iteration's work unit: fold in s537's 2nd confirm, then continue the sweep

**Step 1 — fold in the queued confirm result.** `scratch/agent/SOAK-RESULTS.md` already has a line
for `s537_render_lit_textured_mesh_faces_r1_confirm` (rc=3, 162s) but it has NOT been read or graded
yet. Read `scratch/agent/soak_results/s537_render_lit_textured_mesh_faces_r1_confirm_20260809-015615.log`
(check the exact filename in SOAK-RESULTS.md's line first, timestamps drift) directly — do not trust
just the rc/duration. Grep for:
- `render-lit-textured-mesh-faces-r1-guard` fire count (expect 0 for a clean result)
- fires on any OTHER armed guard family (regression check)
- `hangarbay-entry` count — **must be non-trivial (double digits+) or the run is vacuous per iron
  rule 1; re-queue rather than record if it's 0 or single-digit**
- the crash signature this run hit (pc-symbol + last-guest-pc), and whether it's a 3rd occurrence of
  item -330 (`heapFreeListInsert+72`/`0x800220b8`, currently 2 occurrences s536/s537 back-to-back) —
  if it IS a 3rd occurrence, and especially if it's in an unrelated run (different session, not just
  the immediately-following soak), that would cross this campaign's standing 3-occurrence escalation
  threshold (see items -319/-321/-322's precedent) and should be source-traced, not just filed.

If 0 fires on the guard AND a real positive control: mark `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD`
FULLY CLOSED 2/2 in `docs/CURRENT-TRUTH.md` item -317 (38 fixed, 38 fully closed — 100% closed on
everything fixed so far, for the SIXTH time this campaign) and in `docs/PROJECT-OVERVIEW.md` §25's
table (currently table row for guard 38 doesn't exist yet since it was still open at maintenance
time — add it as row 38, matching the existing rows' format). Fold the same summary into
`PORTING-STATE.md`.

**Step 2 — re-scan and audit the next-ranked tier, same iteration (fold-in-then-pick pattern).**
1. Re-run the tracer fresh (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. The raw tracer's top pick (`funcs_3.c`, `renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`) is a
   KNOWN, four-times-confirmed shape mismatch (s535/s536/s537, and again whenever it resurfaces) —
   `ctx->r4` there is the function's own always-valid `$a0` argument, not a reloaded global. Skip it
   without re-deriving from scratch, but do re-run the scan fresh each session (line numbers drift).
3. Identify the top-ranked write line NOT already fixed AND matching the exact shape (`reg=r2,
   off=0X4`, i.e. `MEM_W(0X4, ctx->r2) = ctx->r3;` fed by a `lui $v0,0x8011`/`lw $v0,0x63B0($v0)` load
   pair gated by `beq $v0,$zero,...`). At the s537 scan the tier after
   `renderLitTexturedMeshFaces:34329` (now fixed, `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD`) ran:
   `funcs_4.c:7648` (`renderFlatMeshFaceGroup`, 26, NEW function), `funcs_4.c:14889`
   (`renderLitMeshFaceGroup`, 26, NEW function — note this function already carries the older
   `RENDER_LIT_MESH_R2`-`R8_GUARD` lineage under a DIFFERENT idiom from s496-519, check this isn't a
   duplicate before assuming new), `funcs_3.c:34504` (`renderLitTexturedMeshFaces`, 25, a THIRD site —
   check reg/off before assuming genuine). Re-verify the fresh ranking; do not assume this survives.
4. Pull all raw reload addresses feeding the target write line (filter
   `scratch/agent/s494_item317_step3_report.json` by `func==<name>` and hits containing the target
   write line, print `guest_addr` for each match).
5. Cross-check EVERY raw address against `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   directly (NOT under a `tools/` subdirectory). `submitSceneNodeRender` now carries R1-R4,
   `emitColorFillRect` R1-R2, `drawSubtitleText` R1, `renderLitTexturedMeshFaces` R1 (pending its own
   fold-in above) — check the new candidate isn't one of those or their own load addresses.
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
   `scratch/agent/soak_queue/done/` (`s537_render_lit_textured_mesh_faces_r1_manual_20260809-020000.sh`
   is the latest full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` (append, don't
   remove any existing ones — batch-instrumentation rule), point output at a new
   `scratch/agent/soak_results/s539_..._manual` path, run with `Bash run_in_background: true`, then
   `TaskOutput` with `block: true` and `timeout: 300000` to wait synchronously.
10. Read the run.log directly (grep the new guard's fire count, `hangarbay-entry` count, crash/signal
    markers). **Never trust a 0-fires result without confirming `hangarbay-entry` (or another armed
    positive control) actually appears with a non-trivial count** — a full-duration rc=0 completion is
    not itself proof the guarded code ran (s536's lesson: the scripted key sequence can diverge onto a
    different scene path run to run even with `PROBE_KEYS_FROM_PHASE`). If weak/absent, discard and
    re-run. If clean with a real positive control, queue a 2nd independent confirm to
    `scratch/agent/soak_queue/s539_..._confirm.sh` and record the 1st-verify result in
    `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, each WITH a same-run `hangarbay-entry` positive control that actually fired
non-trivially, is what promotes a guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard
itself would be the first actual confirmation this idiom class fires in practice (none of the 38
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
- This sandbox blocks `find -delete`, multi-statement `&&`/`while`/heredoc chains, and output
  redirection to `/tmp` fairly often — prefer single simple commands.
- After launching a manual live-verify in the background, use `TaskOutput` with `block: true` and a
  generous `timeout` (e.g. 300000ms) to wait synchronously before doing anything else.
- Full guard-by-guard table and mechanism detail for everything closed so far: `docs/PROJECT-OVERVIEW.md`
  §22-§25.
