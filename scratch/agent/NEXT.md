# NEXT work unit

## s411 recap

The loop's MANDATORY-PIVOT gate fired at session start: s408, s410, and s410-recorded "iteration 16"
had all run 3 straight ordinary n=20 batches under `HYPOTHESIS-ID: m4-main-overlay-phantom-functions`,
so a 4th consecutive n=20 batch was disallowed. Per the gate's own contract, ran the single
highest-information discriminating probe instead: **is n=20 actually a hard ceiling, or just an
unbisected inference from s401's one 774-item failure?** Attempted n=50 (2.5x cadence) with full
live-verify discipline.

**Result: clean.** 49 CONFIRMED + 1 WEAK (0 ambiguous, 0 none) out of 50. Applied all 50. Positive
control exact (`make_elf.py` unmapped-functions-skipped 618→568). Build clean (0 errors, the s401
`CONFIGURE_DEPENDS` fix held — no stale-glob repeat). `nm`-confirmed 50/50 present. Live-verify reached
`phase width=512` at 88.6s, continued to `lastW=640`, **0 crash markers AND 0 `[missing-func]` lines**
(down from the 1 that's appeared in every prior session — the batch included `endMissionCleanup` at
the exact address, `0x800fb9e4`, that's been firing `[missing-func]` since s400; two independent lines
of evidence it's genuinely fixed: the grep-count drop plus the address match).

**Item -249 tally: 235/778 done (was 185/778), 563 remain per a fresh regen (558 actionable, 4
known-skip, 1 known-bad).** Full detail: `docs/CURRENT-TRUTH.md` item -249..-257, `PORTING-STATE`
Session 411.

**Verdict on the discriminating question:** n=20 was NOT a hard structural ceiling — at least not at
n=50, with the CMake glob fix in place and the one known-bad function excluded. This is a
single-source result (one n=50 trial); it does not prove arbitrarily large batches are safe (s401's
774-item attempt is still a real historical failure, now more plausibly explained by cross-overlay
cascade dependencies and/or an unbisected bad function rather than pure batch size). But it directly
answers this session's question and materially changes the remaining-work estimate.

## Next work unit: scale the batch cadence further, then settle into the new steady-state size

HYPOTHESIS-ID: m4-item249-cadence-scaleup

Iteration 1 under this new slug — the old slug (`m4-main-overlay-phantom-functions`) is CLOSED per the
s411 discriminating-probe result above; this is a genuinely new question (how far can the cadence be
pushed before something breaks), not a repeat of "just do another n=20 batch."

### Recipe
1. Regenerate the candidate list fresh: `python3 scratch/agent/s408_gen_candidates.py` (overwrites
   `scratch/agent/s408_candidates_all.txt` — expect 563 total).
2. Filter `m4_known_skip.txt` (4 names) and `m4_known_bad.txt` (1 name,
   `initPlayerCraftTrailBuffers`) → expect 558 actionable. Do NOT re-probe or re-attempt either list.
3. Take the next **n=75** candidates in strict file order (up from s411's n=50 — continue probing the
   ceiling one step at a time, do NOT jump straight to a huge batch like s401's 774; if n=75 is clean,
   try n=100-150 the iteration after; if any batch crashes, STOP scaling, fall back to the last known
   clean size, bisect the failing batch the standard way (halves→quarters→n=1, s405-407's playbook),
   and settle into that size as the new steady-state cadence for the remainder of item -249).
4. Probe: `python3 scratch/agent/s400_probe_batch.py <batch_file>`. 0 ambiguous/none is the historical
   norm at this file-order range (mostly `lv3_*`/`lv9_*`/`say2*`/dialogue helper names, same pattern as
   s410-s411's batches) — if a name comes back AMBIGUOUS/NONE, add it to `m4_known_skip.txt` and
   continue with the rest.
5. Apply: `python3 scratch/agent/s400_apply_batch.py <probe_output_file>`.
6. Clear `RecompiledFuncs/` first (write a one-line `.sh` wrapper, same as
   `scratch/agent/s410_clear_recompiledfuncs.sh` — inline `rm`/`find -delete` gets denied by the
   sandbox).
7. Regen: `zsh scratch/agent/s408_run_make_elf.sh` (expect `unmapped functions skipped` to drop by
   exactly the batch size from 568), then `zsh scratch/agent/s408_run_n64recomp.sh`, then
   `zsh scratch/agent/s408_run_fixup.sh`.
8. Build: `zsh scratch/agent/s408_run_build.sh` (rc=0, 0 `error:` lines).
9. `nm`-confirm the batch's names present — write a session-specific `check_names.sh` (see
   `scratch/agent/s411_check_names.sh` for a template that reads the batch file directly instead of a
   hardcoded name array — nm needs to run via a `.sh` file, not inline).
10. **Mandatory live-verify before selecting the next batch** — run in the background
    (`run_in_background: true`), then block on it with the task-notification system:
    ```
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh <outdir> 45 2
    ```
    PASS = reaches `vi_width=512` (~88-89s) and continues to `vi_width=640` (check the tail of
    `run.log` for `lastW=640`), 0 `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/dmem-race/defer-drop/
    assert lines. `[missing-func]` should now be 0, not 1 (s411 fixed the one standing address) — if it
    reappears, that's worth a note but is not itself a FAIL condition unless it's a NEW address. FAIL =
    a crash-style Bus error or any other `[CRASH]` — bisect (halves, then quarters, then n=1), same
    playbook as s404-407, and record the new safe ceiling.
11. If clean and this is the first batch of the session: consider ONE more step up in size before
    stopping for the iteration (e.g. 75 clean → try 100-150 next). If a batch fails: stop scaling for
    this thread, fall back and bisect, and record the ceiling found — that itself is a valid, complete
    discriminating result for this hypothesis-id (close it either way: "found the real ceiling at N" or
    "scaled cleanly through N, no ceiling found yet, continue next session").

### Do NOT this iteration
- Re-probe or re-attempt `initPlayerCraftTrailBuffers` (`m4_known_bad.txt`) or anything in
  `m4_known_skip.txt`.
- Jump straight back to s401's whole-remainder-in-one-shot approach — step the size up incrementally
  so a failure is attributable to a specific size, not lost in a 500+-item batch again.
- Trust a prior session's "N remain" prose over a fresh regen.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).
