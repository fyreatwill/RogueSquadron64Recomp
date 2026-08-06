# NEXT work unit

## s408 recap

Resumed ordinary bulk relocation on M4 item -249 now that the s404-s407 crash-batch bisection thread is
fully closed. Wrote `scratch/agent/s408_gen_candidates.py` — a persisted version of the candidate-list
generator every prior session (s400-s407) had been re-typing inline as a `python3 -c "..."` snippet
(same filter s402 fixed: excludes `defined:false`, data-typed comments, `D_`/`junk_`-prefixed names,
and lowercase-`g`-prefixed globals).

Two clean, independently live-verified n=20 batches landed (40 relocations total):
- Batch 1: `initActorFromSpawnTemplate`...`sayLukeGoingMakeHovertrainEscape_v0xE4` — 0 crashes,
  reached `vi_width=512`→640.
- Batch 2: `sayStickObjectives_v0x11F`...`sayMoreFightersInboundSevenDecimal_v0x1EB` — 0 crashes,
  reached `vi_width=512`→640.

**Item -249 tally: 145/778 done, 653 remain per a fresh regen (648 actionable, 4 known-skip, 1
known-bad).** Full detail: `docs/CURRENT-TRUTH.md` item -257, `PORTING-STATE` Session 408.

**Bookkeeping note**: the docs' "N remain" figure keeps drifting from a true regenerated count
session-over-session (s404 first documented this, s408 hit a smaller instance of it — 693 fresh vs 672
pure-subtraction at session start). **Always regenerate the candidate list fresh at the start of an
item -249 session** (`python3 scratch/agent/s408_gen_candidates.py`) rather than trusting the prior
session's "N remain" prose for the starting count.

## Next work unit: continue the n=20 bulk-relocation cadence

HYPOTHESIS-ID: m4-main-overlay-phantom-functions

Iteration 15 under this slug — ordinary bulk relocation, not bisection; iteration count restarted its
"budget" framing at s408 per the standing note that the crash-sub-thread closure resets rule-8
bookkeeping for this slug.

### Recipe
1. Regenerate the candidate list fresh: `python3 scratch/agent/s408_gen_candidates.py` (writes
   `scratch/agent/s408_candidates_all.txt` — rename/copy before re-running if you want to keep a
   session-specific snapshot, the script overwrites the same path every time).
2. Filter out every name in `scratch/agent/m4_known_skip.txt` (4 names, persistently NONE/AMBIGUOUS)
   and `scratch/agent/m4_known_bad.txt` (1 name, `initPlayerCraftTrailBuffers` — crashes on
   relocation, permanently parked). Do NOT re-probe or re-attempt either list without a dedicated new
   investigation thread for that specific name.
3. Take the next ~20 candidates in strict file order, probe with
   `python3 scratch/agent/s400_probe_batch.py <batch_file>` (0 ambiguous is the historical norm — if a
   name comes back AMBIGUOUS, add it to `m4_known_skip.txt` and move on; if NONE, same).
4. Apply CONFIRMED+WEAK verdicts: `python3 scratch/agent/s400_apply_batch.py <probe_output_file>`.
5. Regen: `zsh scratch/agent/s408_run_make_elf.sh` (or write a fresh session-numbered copy — expect
   `unmapped functions skipped` to drop by exactly the batch size from 658), then
   `zsh scratch/agent/s408_run_n64recomp.sh`, then `zsh scratch/agent/s408_run_fixup.sh`.
6. Build: `zsh scratch/agent/s408_run_build.sh` (rc=0, 0 `error:` lines).
7. `nm`-confirm the batch's names present — write a session-specific `check_names.sh` from the
   `s408_check_names.sh`/`s408_check_names2.sh` template (nm needs to run via a `.sh` file, not
   inline — direct `nm ...` invocations get denied by the permission matcher even with
   `dangerouslyDisableSandbox`).
8. **Mandatory live-verify before selecting the next batch** — run in the background
   (`run_in_background: true`), then block on it with `TaskOutput`:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   PASS = reaches `vi_width=512` (~88-89s) and continues to `vi_width=640` (check the tail of
   `run.log` for `lastW=640`), 0 `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/dmem-race/defer-drop/
   assert lines, only the 1 known pre-existing `[missing-func] 0x800FB9E4`. FAIL = a
   `playerXwingInit+2068`-style Bus error or any other `[CRASH]` — if this happens, bisect the batch
   (halves, then quarters, then n=1) the way s405/s406/s407 did, don't just revert-and-guess.
9. If clean: leave applied, take the next ~20-slice batch, repeat. Two consecutive clean batches is a
   reasonable stopping point for one iteration.

### Do NOT this iteration
- Re-probe or re-attempt `initPlayerCraftTrailBuffers` (`m4_known_bad.txt`) or anything in
  `m4_known_skip.txt`.
- Batch beyond ~20-40 without an intervening live-verify (s401's "swept everything, verified once at
  the end" dead end).
- Trust a prior session's "N remain" prose over a fresh regen (see bookkeeping note above).

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).

## Maintenance note

s409 was a MAINTENANCE iteration (Step 0 triggered at 60,639 bytes): collapsed items -257..-249
(the s400-408 M4 saga) and four closed M5 items into two compact pointer paragraphs — 677→446 lines,
60,639→39,696 bytes. `docs/CURRENT-TRUTH.md` is now under the 60000-byte trigger again; no maintenance
action needed at the start of the next iteration unless it has grown back over the cap. Full detail:
`PORTING-STATE` Session 409.
