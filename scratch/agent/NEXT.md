# NEXT work unit

## s414 recap

`HYPOTHESIS-ID: m4-item249-bulk-relocation-n75` (ordinary bulk relocation, resumed per s413's handoff).
Regenerated the candidate list fresh (`s414_gen_candidates.py`): 439 total, 433 actionable after
filtering `m4_known_skip.txt` (4) + `m4_known_bad.txt` (2) — both counts matched the docs' prior
estimate exactly. Took the next 75, probed all 75 (57 CONFIRMED + 18 WEAK, 0 NONE/AMBIGUOUS, all
`mission`-destined), applied, regenerated, built — all clean, `nm`-verified all 75 present.

**Live-verify hit a NEW, deterministic crash**, reproduced 2/2 byte-identically:
`[CRASH] pc-symbol=loadDatFile+21884`, `last-guest-pc=0x800290d4`. This matches neither existing
`m4_known_bad.txt` signature. Note: `0x800290d4` is BELOW `overlay_start` (`0x800A5130`) — the fault
site is in core `.text`, not inside any of the 75 relocated functions' own bodies, so the mechanism (if
this batch really is the cause) is indirect: a newly-real (no-longer-stubbed) function calling into core
code with bad state — same class as the s404/s412 crashes.

**Same-run positive control**: reverted the 75-name batch (`s414_revert.py`), rebuilt, live-verified
once — CLEAN (88.6s to phase, 19 frames, 0 crash markers, `lastW=640`). Crash present 2/2 with the batch
applied, absent 1/1 with it reverted — the batch (not environment/nondeterminism) is confirmed
responsible. Per NEXT.md's own contingency instruction, did NOT guess which of the 75 names is at
fault — deferred to a proper halves bisection.

**Repo state end-of-session: back to 359/778 (unchanged from s413).** The 75-name suspect batch is
preserved at `scratch/agent/s414_crash_batch_needs_bisection.txt`.
Full detail: `PORTING-STATE` Session 414, `docs/CURRENT-TRUTH.md` item -249..-258.

## Next work unit: bisect s414's 75-name crash batch

HYPOTHESIS-ID: m4-item249-s414batch-badfunc-isolation

Same playbook as s404-407 (20→10→5→1) and s412-413 (100→50→25→12/13→6→1) — halves bisection until the
specific bad function(s) are isolated. Do NOT re-attempt the full 75 as one batch; do NOT guess a name
without testing.

### Recipe
1. Start from the CURRENT (clean, 359/778) baseline — verify `git -C
   ~/Documents/Tools/rogue_squadron64 diff --stat` (or equivalent) shows `main_overlay.txt` /
   `mission_overlay.txt` back to the s413 state before beginning (s414 already reverted its batch, but
   confirm fresh rather than trusting this note).
2. Split `scratch/agent/s414_crash_batch_needs_bisection.txt` (75 names) into two halves (e.g. 37/38).
3. For EACH half in turn: apply via `s400_apply_batch.py`-style move (need `name addr TAG` lines — the
   original probe tags are in `scratch/agent/s414_probe1.txt`, filter to the half's names), clear
   `RecompiledFuncs/funcs_*.c`, regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py`), build,
   `nm`-verify, live-verify:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   CLEAN = phase reached (~88s), 19ish frames, 0 `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/
   dmem-race/defer-drop/assert. CRASH = check `[CRASH][pc-symbol]`/`[CRASH][last-guest-pc]` — a match to
   `loadDatFile+21884`/`0x800290d4` confirms this half carries the bad function(s); a DIFFERENT signature
   is a FOURTH bad function — stop and record separately, don't conflate.
4. Revert the half tested (`s414_revert.py`-style, or write a fresh surgical revert script for the
   specific half) before testing the next split — same discipline as s412/s413's bisection (each split
   tested in isolation against the clean baseline, not cumulatively).
5. Recurse on whichever half crashed until you reach a single name that reproduces the crash alone.
6. Record the isolated bad function(s) in `scratch/agent/m4_known_bad.txt` (same format as the existing
   2 entries — name, addr, tag, session, crash signature, note).
7. Apply the REMAINING 74 (or however many are left after removing the bad one(s)) as one batch on top
   of the clean baseline, full regen+build+nm-verify+live-verify — this should land clean and gets
   the item -249 tally back to 359+N/778.
8. Commit (this repo's `scratch/agent/*` + docs only — sibling-repo symbol edits stay uncommitted per
   item -3, ask the user first).

### Do NOT this iteration
- Re-attempt the full 75-name batch in one shot.
- Guess a bad-function name without testing (the earlier s413 "named lead" trick failed there too —
  test, don't infer from function names).
- Conflate a differently-signatured crash with the `loadDatFile+21884`/`0x800290d4` one — if a bisection
  split produces a NEW signature, that's evidence of a second bad function in this same batch; track
  both.

### Budget note (iron rule 8)
This will be the 2nd consecutive iteration on the item -249 M4 thread if counting s414 and this one as
the same overall hypothesis-family; s414 changed `HYPOTHESIS-ID` to a bisection-specific slug so the
loop's 3-strikes counter starts fresh here. If bisection itself takes 3+ iterations without a
discriminating narrowing, escalate per iron rule 8 (write the hypothesis/evidence table, pick the
highest-information probe, or go BLOCKED).

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).
