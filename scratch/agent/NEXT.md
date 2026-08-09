# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s531 recap -- read this first

s531 was a fold-in-then-pick iteration (matching the s521-s531 pattern).

1. **Folded in `BEGIN_FRAME_DL_CHUNK_R9_GUARD`/`R10_GUARD`'s 2nd confirm** (`s530_begin_frame_dl_chunk_r9_r10_confirm`,
   rc=0, 347s): 0 fires on either guard, 1 benign already-catalogued `hangarmenu-a0-guard` co-fire,
   `hangarbay-entry n=35` positive control, full 347s duration with NO crash at all. Both marked FULLY
   CLOSED 2/2 -- this closes out the entire `beginFrameDLChunk` 36-site tier (R1-R10, all ten guards
   now disposed, s521-530).
2. **Re-scanned for the next tier** per the mandatory s529/s530 cross-check methodology (fresh
   `--scan` + `s506_dedupe.py`, no custom `--out`). Top of the table: `funcs_3.c:11625`
   (`emitColorFillRect`, 30-reachability write) and `funcs_4.c:4457` (`submitSceneNodeRender`,
   30-reachability write), tied. Cross-checked all 30 `emitColorFillRect` raw reload addresses directly
   against `tools/fixup_game_funcs.py` (N64Recomp repo) -- **0 hits**, none pre-covered (unlike the
   beginFrameDLChunk tier, where most of the raw 36 were already guarded). Read the actual generated
   source around the shared downstream write (`funcs_3.c` line 11625, guest `0x8000A538`) and confirmed
   it matches the exact idiom: load pair `0x8000A528`/`0x8000A52C` (`lui $v0,0x8011` / `lw
   $v0,0x63B0($v0)` -- the same `+0x63B0`-offset cached-pointer idiom as the whole beginFrameDLChunk
   lineage, reused in a different function), `beq $v0,$zero,L_8000A53C` at `0x8000A530` gates one arm
   safely (delay slot write at `0x8000A534` harmless), non-null fallthrough dereferences the reloaded
   `ctx->r2` unconditionally at `0x8000A538` with no range check.
3. **Fixed `EMIT_COLOR_FILL_RECT_R1_GUARD`** -- the first guard in this campaign outside
   `beginFrameDLChunk` -- patched in `tools/fixup_game_funcs.py`, full regen/build applied cleanly.
4. **1st live-verify the cleanest possible class**: 0 `emit-color-fill-rect-r1-guard` fires, 0
   regressions on any other armed guard family, `hangarbay-entry n=33` positive control, full 300s
   scheduled duration completed with NO crash at all (118 frames captured). 2nd independent confirm
   queued: `scratch/agent/soak_queue/s531_emit_color_fill_rect_r1_confirm.sh`.
5. Tally: item -317 step 3 now 32/~150 fixed, 31 fully closed 2/2, `EMIT_COLOR_FILL_RECT_R1_GUARD`
   pending its 2nd confirm. ~114 sites remain across further tiers (`submitSceneNodeRender` next,
   tied at 30, unaudited).

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 531.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s531_emit_color_fill_rect_r1_confirm`**: read
its directory's own `run.log` (`scratch/agent/soak_results/s531_emit_color_fill_rect_r1_confirm/run.log`
-- NOT just the flat top-level summary file). If 0 fires on `emit-color-fill-rect-r1-guard` and a strong
`hangarbay-entry` positive control, mark `EMIT_COLOR_FILL_RECT_R1_GUARD` FULLY CLOSED 2/2 in
`docs/CURRENT-TRUTH.md` item -317 (32 fixed, 32 fully closed -- item -317 step 3 would then be 100%
closed on everything fixed so far) and fold the result into `PORTING-STATE.md`. Then continue to the
next step below in the SAME iteration (fold-in-then-pick pattern, s521-s531).

**Then (or if no confirm result is queued yet), audit the `submitSceneNodeRender` tier**
(`funcs_4.c:4457`, 30-reachability write at this session's scan) using the SAME cross-check
methodology -- do NOT skip it and trust the raw tracer count:

1. **Re-run the tracer fresh** (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. **Pull all `submitSceneNodeRender` reload addresses** feeding the top-ranked write line (same
   technique as s531 -- filter the raw JSON report by `func=='submitSceneNodeRender'` and hits
   containing the target write line; see s531's python one-liners in this session's transcript /
   `PORTING-STATE.md` Session 531 for the exact commands).
3. **Cross-check EVERY raw address against `tools/fixup_game_funcs.py` (N64Recomp repo) directly**
   (grep each address). **Caution**: `ROGUESQ_LOG_SUBMIT_SCENE_NODE_RENDER_R1_GUARD` already exists as
   an armed env var in the soak scripts -- an EARLIER, unrelated guard in this same function from a
   prior session. Check its actual guest address/site before assuming the new candidate is genuinely
   uncovered; if the new top-ranked write happens to BE that existing guard's site, skip it and take the
   next-ranked candidate instead.
4. **Read the generated source** around any zero-hit address in `RecompiledFuncs/funcs_4.c` to confirm
   the exact vulnerable shape (null check proves non-null only, unconditional deref follows with no
   `0x80000000`-`0x80800000` range check, downstream reload feeds an existing guard).
5. **Fix the first genuine candidate** as `SUBMIT_SCENE_NODE_RENDER_R2_GUARD` (bump the suffix if `R1`
   turns out to be a different, already-taken name) using the same `fixup_game_funcs.py` template as
   `EMIT_COLOR_FILL_RECT_R1_GUARD` (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr
   report, `U32()` range check `< 0x80000000u || >= 0x80800000u`).
6. **Regen** (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`, all four steps,
   fixup is NOT optional).
7. **1st live-verify, manual, foreground** -- copy `scratch/agent/soak_queue/done/s531_emit_color_fill_rect_r1_manual_*.sh`,
   add the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed env-var list (append, do not remove any
   existing ones -- batch-instrumentation rule), point the output dir at a new
   `scratch/agent/soak_results/s532_..._manual` path, run it in the foreground (background the Bash
   call and wait for the game process to exit -- do NOT foreground-sleep-poll).
8. **Read the run.log directly** (grep for the new guard's fire count, `hangarbay-entry` count, and any
   crash/signal markers) -- do not trust a stale cached read. If clean (0 fires on the new guard, 0
   regressions, strong positive control), queue a 2nd independent confirm to
   `scratch/agent/soak_queue/s532_..._confirm.sh` (loop-queued, same recipe, new output dir) and record
   the 1st-verify result in `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, with a same-run `hangarbay-entry` positive control each time, is what promotes a
guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard itself would be the first actual
confirmation this idiom class fires in practice (none of guards R1-R10 or `EMIT_COLOR_FILL_RECT_R1` have
ever fired) -- treat that as a genuinely new, high-priority finding, not routine.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without the address-by-address cross-check against
  `fixup_game_funcs.py` AND a direct read of the generated source -- the s528/s529 lesson (most raw
  counts in a shared-downstream-write tier are already covered by other guard families).
- One build/run carries every armed guard's env var (batch-instrumentation rule) -- never spend a
  build-run cycle isolating just the newest guard.
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan` or dedupe
  silently ranks against stale data (s521 gotcha).
- Kill runs with SIGKILL only; capture paths must not start with `.`; run from `build/` with the ROM
  present.
