# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s535 recap -- read this first

s535 was a fold-in-then-pick iteration (matching the s521-s535 pattern).

1. **Folded in `SUBMIT_SCENE_NODE_RENDER_R4_GUARD`'s 2nd confirm** (`s534_submit_scene_node_render_r4_confirm`,
   rc=0, 346s): 0 fires, 0 fires on any other armed guard family, `hangarbay-entry n=32` positive control,
   full 346s duration, no crash at all. Marked FULLY CLOSED 2/2 -- this closes item -317 step 3's 35
   guards to 35/35 fully closed (zero open guards) for the THIRD time this campaign.
2. **Re-scanned for the next tier** (fresh `--scan` + `s506_dedupe.py`, no custom `--out`). Top of the
   table (`funcs_3.c:34419`, `renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`, count=27) was investigated
   and **correctly REJECTED**: the write dereferences `ctx->r4`, the function's own `$a0` argument
   (already written through twice earlier in the same freelist-insert block, provably non-null by
   construction) -- NOT a reload of the `+0x63B0` global-table idiom this campaign guards. This is the
   campaign's FIRST genuine false-positive top candidate in ~15 consecutive picks -- the raw tracer count
   is reachability, not dataflow, and this is the first time that distinction actually mattered. Correctly
   skipped, no guard written for it.
3. **Moved to the next-ranked shape-matching entry**: `funcs_4.c:25609` (`drawSubtitleText`, count=27,
   reg=`r2`/off=`0X4` -- the exact guarded shape). A NEW function for this campaign. Cross-checked all 22
   raw reload addresses feeding that write line directly against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- none present anywhere in it,
   genuinely uncovered (neither the write's own address `0x80016B58` nor its load pair
   `0x80016B48`/`0x80016B4C`). Read the generated source and confirmed the exact idiom shape.
4. **Fixed `DRAW_SUBTITLE_TEXT_R1_GUARD`** in `fixup_game_funcs.py`, full regen/build applied cleanly
   (patched exactly x1, no duplicate-stacking).
5. **1st live-verify clean**: 0 `draw-subtitle-text-r1-guard` fires, 0 fires on ANY other armed guard
   family at all (no benign co-fires this run -- unusually clean), `hangarbay-entry n=31` positive
   control. Full 300s scheduled duration completed with NO crash at all (117 frames, rc=0) -- the cleanest
   possible verify class. 2nd independent confirm queued:
   `scratch/agent/soak_queue/s535_draw_subtitle_text_r1_confirm.sh`.
6. Tally: item -317 step 3 now 36/~150 fixed, 35 fully closed 2/2, `DRAW_SUBTITLE_TEXT_R1_GUARD` pending
   its 2nd confirm. ~110 sites remain across further tiers, unaudited.

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 535.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s535_draw_subtitle_text_r1_confirm`**: read its
directory's own `run.log` (`scratch/agent/soak_results/s535_draw_subtitle_text_r1_confirm/run.log` -- NOT
just the flat top-level summary file, which only has probe.sh's own stdout, not the game's guard-fire
lines). If 0 fires on `draw-subtitle-text-r1-guard` and a strong `hangarbay-entry` positive control, mark
`DRAW_SUBTITLE_TEXT_R1_GUARD` FULLY CLOSED 2/2 in `docs/CURRENT-TRUTH.md` item -317 (36 fixed, 36 fully
closed -- item -317 step 3 would then be 100% closed on everything fixed so far, for the FOURTH time this
campaign) and fold the result into `PORTING-STATE.md`. Then continue to the next step below in the SAME
iteration (fold-in-then-pick pattern, s521-s535).

**Then (or if no confirm result is queued yet), re-scan and audit the next-ranked tier** using the SAME
cross-check methodology -- do NOT skip it and trust the raw tracer count. **s535 lesson: always verify
the write's register/offset is `reg=r2, off=0X4` (the guarded shape) before investigating further -- the
raw top count can now be a genuine shape mismatch (first happened s535), not just "already covered by
another guard family" (the s528-534 failure mode). Read the actual write instruction's operands before
doing the reachability cross-check, not after.**

1. **Re-run the tracer fresh** (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. **Identify the top-ranked write line NOT already fixed AND matching the exact shape** (`reg=r2,
   off=0X4`, i.e. the generated source shows `MEM_W(0X4, ctx->r2) = ctx->r3;` fed by a `lui
   $v0,0x8011`/`lw $v0,0x63B0($v0)` load pair gated by a `beq $v0,$zero,...`). At the s535 scan (line
   numbers will shift after this session's regen, re-check), the table after `drawSubtitleText:25609`
   (27, now fixed as `DRAW_SUBTITLE_TEXT_R1_GUARD`) ran: `funcs_3.c:11253` (`emitColorFillRect`, 26 --
   check against R1's own site `0x8000A538` first, this may already be covered), `funcs_3.c:34316`
   (`renderLitTexturedMeshFaces`, 26 -- a DIFFERENT write line from the rejected r4/off0X0 one, check its
   reg/off before assuming it's genuine), `funcs_4.c:7648` (`renderFlatMeshFaceGroup`, 26, NEW function),
   `funcs_4.c:14889` (`renderLitMeshFaceGroup`, 26, NEW function). Re-verify the fresh ranking first --
   do not assume this exact ordering survives the regen, and do not assume the raw top-of-list pick is
   automatically the right shape (s535 lesson).
3. **Pull all raw reload addresses feeding the target write line** (filter the raw JSON report,
   `scratch/agent/s494_item317_step3_report.json`, by `func==<name>` and `hits` containing the target
   write line -- Python one-liner pattern: iterate entries, check `h['kind']=='write' and
   h['line']==<target>` for each hit).
4. **Cross-check EVERY raw address against `fixup_game_funcs.py` directly** (the actual path is
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, NOT under a `tools/`
   subdirectory). **Caution**: `submitSceneNodeRender` now carries FOUR existing guards (R1 at
   `0x80010F38`, R2 at `0x80010E10`, R3 at `0x80010AAC`, R4 at `0x80010BF0`), `emitColorFillRect` carries
   one (R1 at `0x8000A538`), `drawSubtitleText` carries one (R1 at `0x80016B58`) -- check the new
   candidate's write address isn't one of those (or one of THEIR OWN load addresses) before assuming it's
   genuinely uncovered.
5. **Read the generated source** around any zero-hit write address to confirm the exact vulnerable shape
   (null check proves non-null only, unconditional deref follows with no `0x80000000`-`0x80800000` range
   check, downstream reload feeds an existing guard) -- AND confirm the dereferenced register is actually
   a reload of the `+0x63B0`-offset global-table idiom, not a function argument or other already-validated
   value (the s535 lesson: check this BEFORE the reachability cross-check, not after).
6. **Fix the first genuine candidate** using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` -- bump `N` if the function already
   has guards from this campaign.
7. **Regen** (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`, all four steps,
   fixup is NOT optional; delete `RecompiledFuncs/funcs_*.c` first per the standing item -20 rule --
   `python3 -c` a `glob.glob` + `os.remove` loop, `find -delete` is blocked in this sandbox). Exact
   commands (validated s535):
   ```
   cd /Users/williambuckley/Documents/Tools/N64Recomp
   python3 -c "import glob, os; [os.remove(f) for f in glob.glob('RecompiledFuncs/funcs_*.c')]"
   cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
   cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
   python3 fixup_game_funcs.py   # audit report for exactly the expected xN counts, no duplicate-stacking
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build && \
     DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
   ```
   **Gotcha (s533)**: the CMake build directory that actually links `RogueSquadron64Recomp` is
   `RogueSquadron64Recomp/build`, NOT `N64Recomp/build`.
   **Sandbox note (s535)**: `python3 fixup_game_funcs.py` output redirection to `/tmp` is blocked by the
   session's directory allowlist -- redirect to a file inside one of the three allowed repos instead
   (e.g. `fixup_report.txt` in `N64Recomp/`, then delete it after auditing).
8. **1st live-verify, manual, foreground** -- copy the most recent guard's manual script from
   `scratch/agent/soak_queue/done/` (`s535_draw_subtitle_text_r1_manual_20260808-193000.sh` is the latest
   full env-var list), append the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed env-var list (append, do
   not remove any existing ones -- batch-instrumentation rule), point the output dir at a new
   `scratch/agent/soak_results/s536_..._manual` path, run it with `Bash run_in_background: true` (it will
   auto-background past the 120s tool timeout regardless), **then use `TaskOutput` with `block: true` and
   a `timeout` of 300000 on that task ID to synchronously wait for it to actually finish** -- this is more
   reliable than the old pgrep-loop-plus-Monitor pattern (s535: worked, but needed both a Monitor AND a
   blocking TaskOutput call after a Stop-hook rejection; TaskOutput alone with a generous timeout is
   simpler and sufficient).
9. **Read the run.log directly** (grep for the new guard's fire count, `hangarbay-entry` count, and any
   crash/signal markers) -- do not trust a stale cached read. If clean (0 fires on the new guard, 0
   regressions, strong positive control), queue a 2nd independent confirm to
   `scratch/agent/soak_queue/s536_..._confirm.sh` (loop-queued, same recipe, new output dir -- a `sed`
   rename of the manual script's guard-family env-vars and output path works well) and record the
   1st-verify result in `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, with a same-run `hangarbay-entry` positive control each time, is what promotes a
guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard itself would be the first actual
confirmation this idiom class fires in practice (none of the 36 guards fixed so far have ever fired) --
treat that as a genuinely new, high-priority finding, not routine.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without BOTH the shape check (reg/off match the guarded
  idiom) AND the address-by-address cross-check against `fixup_game_funcs.py` AND a direct read of the
  generated source -- s535 added a NEW failure mode (shape mismatch: the top count can be a CFG-
  reachability artifact through a function argument, not a genuine reload) on top of the s528-534 lesson
  (raw counts often partly covered by other guard families).
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
  doing anything else -- confirmed working s535 (a Stop-hook rejection mid-run showed that ending the turn
  before the notification lands does NOT keep the gate satisfied; blocking on `TaskOutput` after the
  rejection got a clean completed result immediately).
