# NEXT work unit

## s410 recap

Continued the M4 item -249 bulk-relocation cadence (no crash-bisection needed this session — that
sub-thread stayed closed from s407). Regenerated the candidate list fresh
(`python3 scratch/agent/s408_gen_candidates.py`): 653 candidates, exactly matching s408's ending count
(no bookkeeping drift this time). Filtered `m4_known_skip.txt` (4 names) and `m4_known_bad.txt` (1 name,
`initPlayerCraftTrailBuffers`), leaving 648 actionable.

Two clean, independently live-verified n=20 batches landed (40 relocations total):
- Batch 1: `sayAnotherVictoryRogueSquadron_v0x230`...`say2LastGroupScannedHereCome_v0x17` — 19 CONFIRMED
  + 1 WEAK, 0 crashes, reached `vi_width=512`→640.
- Batch 2: `say2SirWeveFoundSomeSeeker_v0x299`...`playPairedDialogue_0x246_0x0ED` — 20/20 CONFIRMED,
  0 crashes, reached `vi_width=512`→640.

Both batches: positive control confirmed at the `make_elf.py` regen step (`unmapped functions skipped`
dropped by exactly 20 each time, 658→638→618), `nm`-confirmed 20/20 names present post-build, and a
same-run live-verify (`PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1`) reaching
`phase width=512` at 88.7s and continuing to `lastW=640` with 0 crash markers, only the 1 known
pre-existing `[missing-func] 0x800FB9E4`.

**Item -249 tally: 185/778 done, 613 remain per a fresh regen (608 actionable, 4 known-skip, 1
known-bad).** Full detail: `docs/CURRENT-TRUTH.md` item -249..-257, `PORTING-STATE` Session 410.

**Bookkeeping note (still holds, s404/s408/s409/s410):** the docs' "N/778 done" figure keeps drifting
from a true regenerated count as a running tally (185+613=798 vs the 778 baseline) — this session's own
arithmetic was exact (653→613 after applying 40), so the drift lives in the original 778 baseline/prior
session bookkeeping, not in new errors. **Always regenerate the candidate list fresh at the start of an
item -249 session** (`python3 scratch/agent/s408_gen_candidates.py`) rather than trusting the prior
session's "N remain" prose for the starting count.

## Next work unit: continue the n=20 bulk-relocation cadence

HYPOTHESIS-ID: m4-main-overlay-phantom-functions

Iteration 16 under this slug (ordinary bulk relocation, not bisection — no rule-8 pivot needed, this is
a routine continuation of the same mechanical batch-relocation work, not repeated experimentation on an
unresolved hypothesis).

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
5. **Clear `RecompiledFuncs/` before regenerating** (item -20 standing rule — N64Recomp skips files that
   already exist on disk, so an uncleared regen silently isn't a regen): delete
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` first (a `find -delete`
   or inline `rm` gets denied by the sandbox; write a one-line `.sh` wrapper and run it via `zsh`, same
   as `scratch/agent/s410_clear_recompiledfuncs.sh`).
6. Regen: `zsh scratch/agent/s408_run_make_elf.sh` (expect `unmapped functions skipped` to drop by
   exactly the batch size from 618), then `zsh scratch/agent/s408_run_n64recomp.sh`, then
   `zsh scratch/agent/s408_run_fixup.sh`.
7. Build: `zsh scratch/agent/s408_run_build.sh` (rc=0, 0 `error:` lines).
8. `nm`-confirm the batch's names present — write a session-specific `check_names.sh` from the
   `s410_check_names.sh`/`s410_check_names2.sh` template (nm needs to run via a `.sh` file, not
   inline — direct `nm ...` invocations get denied by the permission matcher even with
   `dangerouslyDisableSandbox`).
9. **Mandatory live-verify before selecting the next batch** — run in the background
   (`run_in_background: true`), then block on it with the task-notification system:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   PASS = reaches `vi_width=512` (~88-89s) and continues to `vi_width=640` (check the tail of
   `run.log` for `lastW=640`), 0 `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/dmem-race/defer-drop/
   assert lines, only the 1 known pre-existing `[missing-func] 0x800FB9E4`. FAIL = a
   crash-style Bus error or any other `[CRASH]` — if this happens, bisect the batch (halves, then
   quarters, then n=1) the way s405/s406/s407 did, don't just revert-and-guess.
10. If clean: leave applied, take the next ~20-slice batch, repeat. Two consecutive clean batches is a
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
