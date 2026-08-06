# NEXT work unit

## s407 recap

Finished bisecting s406's quarter-2 5-name crash suspect set (`beginCameraTrackedTransition`,
`advanceCameraTransitionOnCue`, `isCameraTransitionIdle`, `initPlayerCraftTrailBuffers`,
`loadEffectModelInstancePool`). Split A (first 3) landed clean (+3). Split B (last 2) crashed
together; bisected at n=1 down to a single genuinely-buggy function: **`initPlayerCraftTrailBuffers`**
alone reproduces the byte-identical `playerXwingInit+2068`/`last-guest-pc=0x80011088` crash.
`loadEffectModelInstancePool` tested alone and is clean (+1). Final: 4 of the 5 relocated, 1
permanently excluded via new `scratch/agent/m4_known_bad.txt`.

**Item -249 tally: 105/778 done, 672 remain, 1 permanently excluded.** Full detail:
`docs/CURRENT-TRUTH.md` item -256, `PORTING-STATE` Session 407.

The s404-originated 20-name-batch crash thread is now FULLY CLOSED — 19/20 confirmed safe and
relocated, 1 real bug isolated and parked. This is the first time this hypothesis thread bisected all
the way to n=1 and found a genuinely buggy single function rather than a batch-size/boundary-slicing
artifact — worth keeping in mind for future crashes in this family: don't assume every M4
item -249 crash is a re-slicing artifact: it might be a real translation or dependency-ordering bug in
one specific function.

## Next work unit: fresh n=20 slice of the main candidate list

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 14 under this slug — iterations 9-13
were all genuine discriminating results, no stall; this pivots back to bulk relocation now that the
crashing thread from s404 is fully resolved, exactly as the standing plan anticipated).

The s404-s407 crash-batch bisection thread is closed. Resume the ordinary per-batch-verify workflow
(s400/s402/s403 recipe) on the remaining ~672 real candidates.

### Recipe
1. Regenerate the candidate list with `tools/overlay_symbol_probe.py`'s usual scan (the `is_data`
   filter from s402, per the standing lesson about lowercase-`g`-prefixed globals). **Exclude every
   name in `scratch/agent/m4_known_skip.txt` (persistently NONE/AMBIGUOUS) AND every name in
   `scratch/agent/m4_known_bad.txt` (crashes on relocation — currently just
   `initPlayerCraftTrailBuffers`)** — do not re-probe or re-attempt either list without a dedicated new
   investigation thread for that specific name.
2. Take the next ~20 candidates in strict file order (skipping both exclusion lists), probe them with
   `tools/overlay_symbol_probe.py` (0 ambiguous is the historical norm for this family — if a name comes
   back AMBIGUOUS, add it to `m4_known_skip.txt` and move on, don't re-probe in the same session).
3. Apply the CONFIRMED+WEAK verdicts via `scratch/agent/s400_apply_batch.py` (format: `name addr
   TAG` per line, TAG = `CONFIRMED:<overlay>` or `WEAK:<overlay>`).
4. Regen: `cd rogue_squadron64 && python3 tools/make_elf.py` (expect `unmapped functions skipped` to
   drop by exactly the batch size from 698), then `cd N64Recomp && ./build/N64Recomp
   rogue_squadron.toml`, then `python3 N64Recomp/fixup_game_funcs.py`.
5. Build: `cmake --build build -j8` (rc=0, no new warnings beyond the 295 baseline).
6. `nm`-confirm the batch's names present (pattern: `scratch/agent/s407_check_names.sh` as a template
   — regenerate the `names=(...)` array for the new batch).
7. **Mandatory live-verify before selecting the next batch** — do not accumulate unverified batches
   (s401's dead-end lesson):
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   Run this **in the background** (`run_in_background: true` on the Bash call) — it takes ~90-120s to
   reach phase width=512 alone, comfortably over the 120s foreground timeout. PASS = reaches
   `vi_width=512` (~88-89s) and continues to `vi_width=640`, 0 `[CRASH]` lines in `run.log`. FAIL =
   `playerXwingInit+2068`-style Bus error (or any other `[CRASH]`) firing within a few seconds of the
   512 reach — if this happens, bisect the batch the same way s405/s406/s407 did (halves, then
   quarters, then n=1) rather than reverting-and-guessing.
8. If clean: leave applied, take the next ~20-slice batch, repeat. Two consecutive clean batches with
   no crash is a reasonable stopping point for one iteration (matches s402/s403's pace of ~2
   batches/iteration).

### Do NOT this iteration
- Re-probe or re-attempt `initPlayerCraftTrailBuffers` (in `m4_known_bad.txt`) or anything in
  `m4_known_skip.txt`.
- Batch beyond ~20-40 without an intervening live-verify (s401's "swept everything, verified once at
  the end" dead end).
- Try to root-cause WHY `initPlayerCraftTrailBuffers`'s real code crashes — that's a separate,
  dedicated investigation thread if it's ever picked up (not blocking further item -249 progress since
  it's now permanently excluded).

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~2-3 min including build).

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 14. Five consecutive discriminating
results (s404 iteration 9 through s407 iteration 13), the crash-batch sub-thread that opened at s404 is
now fully closed. This iteration resumes ordinary bulk relocation, not bisection — a genuinely
different (and lower-risk) operation, so the "3 consecutive iterations on one hypothesis" budget rule
should be read as reset by this closure, not violated by continuing under the same top-level
HYPOTHESIS-ID (the slug names the overall item -249 effort, not just the crash sub-thread).

## Maintenance note

`docs/CURRENT-TRUTH.md` is at ~58.8 KB after this session's edit (cap is ~60 KB, Step 0 trigger). The
next iteration that finds it over 60000 bytes via `wc -c` should run a MAINTENANCE pass before any
further M4 work — likely close soon given the pace of item -249 session entries.
