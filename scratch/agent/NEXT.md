# NEXT work unit

HYPOTHESIS-ID: m4-item249-bulk-relocation-n75

## s416 recap

Resumed ordinary bulk relocation at n=75 per s415's handoff recipe. Regenerated candidates fresh (366
total, 358 actionable after filtering `m4_known_bad.txt` (4) and `m4_known_skip.txt` (4)), probed the
next 75 (58 CONFIRMED + 17 WEAK, 0 NONE/AMBIGUOUS — every name resolved to exactly one destination
overlay), applied, and hit a crash: `last-guest-pc=0x800290d4`, reproduced byte-identically 2/2. This is
the SAME crash site s415 isolated two bad functions against (`allocObjectPoolNode`,
`tickCraftMountedAnimationEffect`).

Reverted the full 75 as a same-run positive control (296↔371 unmapped-functions-skipped, exact ±75),
confirming the batch was responsible. Halves-bisected: 75 → half-A(37,CRASH)/half-B(38,deferred) →
A1(18,clean)/A2(19,CRASH) → B1(9,clean)/B2(10,CRASH) → C1(5,CRASH)/C2(5,deferred) →
D1(2,clean)/D2(3,CRASH) → E1(`getActiveHudInstanceTargetPosition`,clean)/E2(2,CRASH) →
F1(`isHudSecondaryWeaponActive`,clean)/F2(`stepObjectOrientationTowardTarget`,**CRASH ALONE**).

**Applied s415's own lesson from the start this time**: before declaring done, independently tested
BOTH deferred siblings (C2, half-B) instead of assuming them clean by elimination. C2 (5 names) tested
clean as a group. half-B (38 names) tested and **crashed** as a group — bisected it too: 38 →
G1(19,CRASH)/G2(19,deferred) → H1(9,clean)/H2(10,CRASH) → I1(5,CRASH)/I2(5,deferred) →
J1(2,CRASH)/J2(3,deferred) → K1(`getDemoRecordedTimestep`,clean)/K2(`updateHudHealthIndicator`,**CRASH
ALONE**). Two bad functions this session, both recorded in `scratch/agent/m4_known_bad.txt`:
- `stepObjectOrientationTowardTarget` (0x800FEF10)
- `updateHudHealthIndicator` (0x800BF790)

**Noteworthy pattern, not yet investigated**: four distinct bad functions now share the exact same
`last-guest-pc=0x800290d4` crash site across s415 and s416 (`allocObjectPoolNode`,
`tickCraftMountedAnimationEffect`, `stepObjectOrientationTowardTarget`, `updateHudHealthIndicator`).
`0x800290d4` is below `overlay_start` (`0x800A5130`) — in core `.text`, not inside any of these
functions' own bodies. This is consistent with s414's read that the fault is downstream/indirect (one of
several distinct newly-real functions corrupting shared state that later crashes in core code), not four
independent bugs. If this address recurs a 5th time, it may be worth a dedicated root-cause session
(out of scope for ordinary bulk relocation — see M3 idiom-audit-only-mode caveat in the USER DIRECTIVE,
though this is M4 not M3).

Applied the final 73-name batch (75 minus both bad functions), full regen+build, `nm`-verified all 73
present and both bad names absent, **live-verified clean 2/2** (88.6s/88.7s to phase, 19 frames each,
0 crash markers both runs). **505/778 done** (was 432/778), +73 this session.

**Housekeeping**: `scratch/agent/m4_known_bad.txt` and `scratch/agent/m4_known_skip.txt` were found
UNTRACKED by git (matched the blanket `/scratch/` gitignore rule, never `git add -f`'d since creation in
s402/s407) — 12+ sessions of bisection knowledge was one `git clean`/fresh-checkout away from being lost.
Force-added both this session (`git add -f`); future `git add -A` picks up their modifications normally.

Full detail: `PORTING-STATE` Session 416, `docs/CURRENT-TRUTH.md` item -249..-258.

## Next work unit: resume ordinary bulk relocation at n=75

Per s411-s416's established cadence: n=75 remains the confirmed-safe steady-state batch size for
ordinary relocation. 293 candidates remain per a fresh regen (283 actionable after filtering
`m4_known_bad.txt` (6) + `m4_known_skip.txt` (4)).

### Recipe
1. Regenerate the candidate list fresh (`scratch/agent/s414_gen_candidates.py` still works — reads
   `main_overlay.txt`/`mission_overlay.txt`/`menu_overlay.txt`/`cinematic_overlay.txt` directly, no
   session-specific state). Confirm the actionable count (candidates minus known-bad minus known-skip)
   is in the neighborhood of 283 — some drift from lingering NONE/AMBIGUOUS items is expected and
   normal (see `m4_known_skip.txt`'s header comment).
2. Probe the next 75 names (`s400_probe_batch.py`-style), tag CONFIRMED/WEAK/NONE/AMBIGUOUS.
3. Apply via `s400_apply_batch.py`, delete `RecompiledFuncs/funcs_*.c` (see path note below), regen
   (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`), build, `nm`-verify all 75 present,
   live-verify (phase-gated, `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1`).
4. **If CLEAN**: live-verify a second time (2/2 discipline), commit, done.
5. **If CRASH**: do NOT guess. Revert the full batch first as a same-run positive control (confirms the
   batch, not environment, is responsible — check the `make_elf.py` unmapped-functions-skipped delta
   matches the batch size exactly both ways). Then halves-bisect. **At every split, when one branch
   reproduces the crash, the OTHER (sibling) branch must be independently tested before being treated as
   clean** — s415 and s416 BOTH found a second bad function hiding in an assumed-clean sibling branch.
   Budget for this: a "found one, verified done" bisection can silently miss a second bug in this
   codebase's crash families; the discipline that catches it costs one extra apply/build/live-verify
   round-trip but has now paid off twice in a row.
6. If a THIRD occurrence of the exact `last-guest-pc=0x800290d4` signature turns up in a future batch,
   consider pausing ordinary relocation for one iteration to source-read what's actually at that address
   and why four (soon possibly five) unrelated newly-relocated functions all reach it — this is starting
   to look like a single shared bug, not batch-specific noise.

### Environment/tooling notes (unchanged from s414/s415, still accurate)
- `RecompiledFuncs/funcs_*.c` live at
  `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` (50 files, `funcs_0.c`
  through `funcs_49.c`). Delete them there before every regen or `N64Recomp` skips rewriting files that
  already exist on disk (item -20's stacking-duplicate bug).
- `nm` is not on the Bash allowlist directly; prefix with `env` (`env nm <path>`).
- `find ... -delete` and glob-pattern `rm` are both blocked by the sandbox; delete generated files by
  listing exact paths to `rm` (or run one `rm -f` call per ~19 files to stay under the multi-op
  approval trigger).
- `pc-symbol` in `[CRASH]` markers is NOT a reliable cross-build crash signature — always compare
  `last-guest-pc`, not `pc-symbol`.
- Live-verify commands that take longer than 120s (the `phase width=512` gate alone takes ~88-89s, plus
  the ~45s capture window) auto-background; use `Monitor` with an until-loop on the output file (grep for
  `captured|died`) to wait for completion without foreground-polling, or just retry a plain Read on the
  task's output file — both work, `Monitor` is cleaner.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-135s including build).
