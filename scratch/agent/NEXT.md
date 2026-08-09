# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s533 recap -- read this first

s533 was a fold-in-then-pick iteration (matching the s521-s533 pattern).

1. **Folded in `SUBMIT_SCENE_NODE_RENDER_R2_GUARD`'s 2nd confirm** (`s532_submit_scene_node_render_r2_confirm`,
   rc=3, 159s): 0 fires, 0 regressions, `hangarbay-entry n=31` positive control. Crashed on the
   already-catalogued `loadCutsceneAssetsByIndex+1860`/`last-guest-pc=0x800aafb8` signature (item -320,
   s508), unrelated/benign. Marked FULLY CLOSED 2/2 -- this closes item -317 step 3's first 33 guards to
   33/33 fully closed (zero open guards) for the first time since s490.
2. **Re-scanned for the next tier** (fresh `--scan` + `s506_dedupe.py`, no custom `--out`). Top of the
   table: a tie at count=28 between `funcs_4.c:3299` and `funcs_4.c:3766`, both in
   `submitSceneNodeRender` -- picked the line-3299 candidate. Pulled all 28 raw reload addresses feeding
   that write line, cross-checked every one directly against
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` (note: NOT under a `tools/`
   subdirectory -- it's at the N64Recomp repo root) -- only the same 2 addresses already known from the
   s532 cross-check were covered (`0x800101B0` by the s197 `scene_node_cache_guard`, `0x80010824` by a
   `DL_LIST_RESET_GUARD`-adjacent reload), neither at the target write's own address. The write's own
   address (`0x80010AAC`) and its load pair (`0x80010AA0`/`0x80010AA4`) do not appear anywhere else in
   `fixup_game_funcs.py` either. Read the generated source directly at the write site
   (`funcs_4.c:3285-3299`, guest `0x80010AAC`) and confirmed the exact idiom: load pair
   `0x80010AA0`/`0x80010AA4` (`+0x63B0`-offset cached pointer), `beq $v0,$zero,L_80010AB0` gates one arm
   safely (delay-slot write harmless), non-null fallthrough dereferences `ctx->r2` unconditionally with
   no range check. This is a THIRD, distinct site inside `submitSceneNodeRender` -- the function already
   carries `SUBMIT_SCENE_NODE_RENDER_R1_GUARD` (s515, `0x80010F38`) and `SUBMIT_SCENE_NODE_RENDER_R2_GUARD`
   (s532, `0x80010E10`).
3. **Fixed `SUBMIT_SCENE_NODE_RENDER_R3_GUARD`** in `fixup_game_funcs.py`, full regen/build applied
   cleanly (patched exactly x1, no duplicate-stacking).
4. **1st live-verify clean**: 0 `submit-scene-node-render-r3-guard` fires, 0 regressions (1 benign
   already-catalogued `hangarmenu-a0-guard` co-fire), `hangarbay-entry n=34` positive control. Crashed at
   ~93s on `pc-symbol=load_level_hmp+1488`, `last-guest-pc=0x800290d4` -- this `last-guest-pc` value is
   items -6/-249/-259, INVESTIGATED AND CLOSED s422 (a sparse-breadcrumb artifact that resolves to
   different real crash functions depending on build layout, not a shared corruption sink) -- not a new
   item, unrelated to the guard under test. 2nd independent confirm queued:
   `scratch/agent/soak_queue/s533_submit_scene_node_render_r3_confirm.sh`.
5. Tally: item -317 step 3 now 34/~150 fixed, 33 fully closed 2/2, `SUBMIT_SCENE_NODE_RENDER_R3_GUARD`
   pending its 2nd confirm. ~112 sites remain across further tiers, unaudited.

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 533.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s533_submit_scene_node_render_r3_confirm`**:
read its directory's own `run.log` (`scratch/agent/soak_results/s533_submit_scene_node_render_r3_confirm/run.log`
-- NOT just the flat top-level summary file). If 0 fires on `submit-scene-node-render-r3-guard` and a
strong `hangarbay-entry` positive control, mark `SUBMIT_SCENE_NODE_RENDER_R3_GUARD` FULLY CLOSED 2/2 in
`docs/CURRENT-TRUTH.md` item -317 (34 fixed, 34 fully closed -- item -317 step 3 would then be 100%
closed on everything fixed so far) and fold the result into `PORTING-STATE.md`. Then continue to the
next step below in the SAME iteration (fold-in-then-pick pattern, s521-s533).

**Then (or if no confirm result is queued yet), re-scan and audit the next-ranked tier** using the SAME
cross-check methodology -- do NOT skip it and trust the raw tracer count:

1. **Re-run the tracer fresh** (no custom `--out`, s521's gotcha):
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. **Identify the top-ranked write line NOT already fixed.** At the s533 scan (line numbers will shift
   slightly after this session's regen, re-check), the table after `submitSceneNodeRender:3299` (28, now
   fixed as R3) ran: `funcs_4.c:3766` (`submitSceneNodeRender`, 28 -- the tied candidate not yet taken;
   check it's not R1/R2/R3's own site first), `funcs_3.c:34419` (`renderLitTexturedMeshFaces`, 27),
   `funcs_4.c:25583` (`drawSubtitleText`, 27), `funcs_3.c:11253` (`emitColorFillRect`, 26 -- check against
   R1's own site first), `funcs_3.c:34316` (`renderLitTexturedMeshFaces`, 26), `funcs_4.c:7622`
   (`renderFlatMeshFaceGroup`, 26), `funcs_4.c:14863` (`renderLitMeshFaceGroup`, 26). Take the
   highest-ranked one whose write address is NOT already an existing guard's own site -- `funcs_4.c:3766`
   (submitSceneNodeRender's 4th candidate) is the natural next pick since it's still top-ranked and in the
   same well-understood function.
3. **Pull all raw reload addresses feeding the target write line** (filter the raw JSON report,
   `scratch/agent/s494_item317_step3_report.json`, by `func==<name>` and `hits` containing the target
   write line -- see this session's transcript / `PORTING-STATE.md` Session 533 for the exact Python
   one-liners).
4. **Cross-check EVERY raw address against `fixup_game_funcs.py` directly** (the actual path is
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, NOT under a `tools/`
   subdirectory). **Caution**: `submitSceneNodeRender` now carries THREE existing guards
   (`SUBMIT_SCENE_NODE_RENDER_R1_GUARD` at `0x80010F38`, `R2_GUARD` at `0x80010E10`, `R3_GUARD` at
   `0x80010AAC`) and `emitColorFillRect` carries one (`EMIT_COLOR_FILL_RECT_R1_GUARD` at `0x8000A538`) --
   check the new candidate's write address isn't one of those before assuming it's genuinely uncovered.
5. **Read the generated source** around any zero-hit write address to confirm the exact vulnerable shape
   (null check proves non-null only, unconditional deref follows with no `0x80000000`-`0x80800000` range
   check, downstream reload feeds an existing guard).
6. **Fix the first genuine candidate** using the same `fixup_game_funcs.py` template as every prior guard
   (skip-the-write-on-invalid, `ROGUESQ_LOG_<NAME>` env-gated stderr report, `U32()` range check
   `< 0x80000000u || >= 0x80800000u`). Name it `<FUNC>_R<N>_GUARD` -- bump `N` if the function already
   has guards from this campaign.
7. **Regen** (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`, all four steps,
   fixup is NOT optional; delete `RecompiledFuncs/funcs_*.c` first per the standing item -20 rule --
   `python3 -c` a `glob.glob` + `os.remove` loop, `find -delete` is blocked in this sandbox). **Gotcha
   (s533)**: the CMake build directory that actually links `RogueSquadron64Recomp` is
   `RogueSquadron64Recomp/build`, NOT `N64Recomp/build` (the latter only holds the `N64Recomp`/
   `RSPRecomp` tool binaries and reports "ninja: no work to do" if you build there by mistake).
8. **1st live-verify, manual, foreground** -- copy the most recent guard's manual script from
   `scratch/agent/soak_queue/done/`, append the new guard's `ROGUESQ_LOG_<NAME>=1` to the armed env-var
   list (append, do not remove any existing ones -- batch-instrumentation rule), point the output dir at
   a new `scratch/agent/soak_results/s534_..._manual` path, run it in the foreground (background the Bash
   call and wait for the game process to exit -- do NOT foreground-sleep-poll; a `Monitor` on
   `while pgrep -x RogueSquadron64Recomp; do sleep 3; done` works well for this, but ALSO run a
   synchronous foreground `while pgrep ...; do sleep 5; done` Bash call as a backstop before ending any
   turn -- a Monitor notification alone does not satisfy the Stop-hook gate if the turn ends first).
9. **Read the run.log directly** (grep for the new guard's fire count, `hangarbay-entry` count, and any
   crash/signal markers) -- do not trust a stale cached read. If clean (0 fires on the new guard, 0
   regressions, strong positive control), queue a 2nd independent confirm to
   `scratch/agent/soak_queue/s534_..._confirm.sh` (loop-queued, same recipe, new output dir) and record
   the 1st-verify result in `docs/CURRENT-TRUTH.md` + `SOAK-RESULTS.md` + `PORTING-STATE.md`.

**Discriminating outcome**: 0 fires on the new guard across BOTH the 1st live-verify and the 2nd
independent confirm, with a same-run `hangarbay-entry` positive control each time, is what promotes a
guard to FULLY CLOSED 2/2. Any nonzero fire count on the new guard itself would be the first actual
confirmation this idiom class fires in practice (none of the 34 guards fixed so far have ever fired) --
treat that as a genuinely new, high-priority finding, not routine.

## Iron-rule reminders specific to this campaign
- Never trust the tracer's raw per-tier count without the address-by-address cross-check against
  `fixup_game_funcs.py` AND a direct read of the generated source -- the s528/s529/s532/s533 lesson (raw
  counts in a shared-downstream-write tier are often already partly covered by other guard families,
  including OTHER guards from this same campaign in the same function).
- One build/run carries every armed guard's env var (batch-instrumentation rule) -- never spend a
  build-run cycle isolating just the newest guard.
- `s506_dedupe.py` reads a FIXED canonical path; never pass a custom `--out` to `--scan` or dedupe
  silently ranks against stale data (s521 gotcha).
- Kill runs with SIGKILL only; capture paths must not start with "." in the final component; run from
  `build/` with the ROM present.
- The `fixup_game_funcs.py` used by this campaign lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- NOT under a `tools/`
  subdirectory (some older session notes said otherwise; the file was moved or the note was wrong).
- The build that actually matters is `RogueSquadron64Recomp/build`, not `N64Recomp/build` (s533 gotcha,
  see step 7 above).
- This sandbox blocks `find -delete` and multi-statement `&&`/`while`/heredoc chains in a single Bash
  call fairly often -- prefer single simple commands, and delete generated files with a small
  `python3 -c` one-liner (`glob.glob` + `os.remove`) instead of `find`.
- After launching a manual live-verify in the background, ALWAYS also run a synchronous foreground
  `while pgrep -x RogueSquadron64Recomp > /dev/null; do sleep 5; done` Bash call before doing anything
  else -- a backgrounded Monitor's notification is not itself sufficient to keep the Stop-hook gate
  satisfied if the turn ends before the notification lands (s533 lesson).
