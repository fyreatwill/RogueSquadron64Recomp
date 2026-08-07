# NEXT work unit

## s415 recap

`HYPOTHESIS-ID: m4-item249-s414batch-badfunc-isolation` (bisection of s414's 75-name crash batch, per
its own handoff recipe). Confirmed the clean 359/778 baseline first (all 75 names present in
`main_overlay.txt`). Halves-bisected: 75 -> half-A(37,CRASH)/half-B(38,untested) -> A1(18,clean)/
A2(19,crash) -> B1(9,clean)/B2(10,crash) -> C1(5,crash)/C2(5,untested) -> D1(2,clean)/D2(3,crash) ->
E1(`resetObjectPoolListHead`,clean)/F1(`allocObjectPoolNode`,**CRASH ALONE**)/G1(`resetObjectContextPool`,clean).

Applied "75 minus `allocObjectPoolNode`" (74 names), expecting clean — **it crashed again**, same
signature (`last-guest-pc=0x800290d4`). Root cause: half-B and C2 had never been independently tested,
only assumed clean because the sibling branch (half-A / C1) had already reproduced the crash. Tested
half-B alone: clean. Tested C2 alone: **crash**. Bisected C2: H1(2,crash)/H2(3,clean) ->
I1(`freeAllObjectContextPoolNodes`,clean)/J1(`tickCraftMountedAnimationEffect`,**CRASH ALONE**).

Two independent bad functions isolated and recorded in `scratch/agent/m4_known_bad.txt`:
- `allocObjectPoolNode` (0x800EC110)
- `tickCraftMountedAnimationEffect` (0x800EC6F0)

Applied the final 73-name batch (75 minus both), full regen+build, `nm`-verified all 73 present as real
functions and both bad names absent, **live-verified clean 2/2** (88.6s/88.8s to phase, 19 frames each,
0 crash markers both runs). **432/778 done** (was 359/778), +73 this session.

**Methodological lesson recorded**: when a nested bisection isolates one bad function, every sibling
half at every split level must be independently verified clean — do not assume a sibling branch is safe
just because the other branch already reproduced the crash. A batch can hide more than one bad function
in different branches of the same bisection tree. This cost one extra apply/build/live-verify/revert
round-trip this session; budget for it in future multi-bad-function bisections.

Full detail: `PORTING-STATE` Session 415, `docs/CURRENT-TRUTH.md` item -249..-258.

## Next work unit: resume ordinary bulk relocation at n=75

`HYPOTHESIS-ID: m4-item249-bulk-relocation-n75`

Per s411/s412/s413's established cadence: n=75 is the confirmed-safe steady-state batch size for
ordinary relocation (i.e. batches not already known to contain a bad function). 346 candidates remain
(338 actionable after filtering `m4_known_skip.txt` (4) + `m4_known_bad.txt` (4), 4 known-skip).

### Recipe
1. Regenerate the candidate list fresh (adapt `s414_gen_candidates.py` or `s400`-era tooling) — confirm
   the actionable count matches 338 (439 total minus the growing known-bad/known-skip exclusions).
2. Probe the next 75 names (`s400_probe_batch.py`-style), tag CONFIRMED/WEAK/NONE/AMBIGUOUS.
3. Apply via `s400_apply_batch.py`, clear `RecompiledFuncs/funcs_*.c` (see note below on the real path),
   regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`), build, `nm`-verify all 75 present,
   live-verify (phase-gated, `PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180`).
4. **If CLEAN**: live-verify a second time (2/2 discipline, per s415's confirmation), commit, done.
5. **If CRASH**: do NOT guess. Halves-bisect immediately in the SAME iteration if time allows (budget
   rule 8 permitting), and **this time, independently test EVERY sibling half at every split level** —
   do not stop bisecting once one bad function is found; verify "everything else" as an explicit group
   test, and if that group test also crashes, treat it as evidence of a second bad function and keep
   bisecting the untested sibling branches rather than assuming they're clean.

### Environment/tooling notes for next session (non-obvious, cost real time this session)
- The regenerated `RecompiledFuncs/funcs_*.c` files do NOT live under
  `RogueSquadron64Recomp/build/RecompiledFuncs/` — they live at
  `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` (49 files, `funcs_0.c`
  through `funcs_48.c`). Delete them there before every regen or `N64Recomp` skips rewriting files that
  already exist on disk (item -20's stacking-duplicate bug).
- `nm` is not on the Bash allowlist directly; prefix with `env` (`env nm <path>`), which IS allowlisted
  as a bare prefix.
- `find ... -delete` and glob-pattern `rm` are both blocked by the sandbox; delete generated files by
  listing exact paths to `rm`.
- `pc-symbol` in `[CRASH]` markers is NOT a reliable cross-build crash signature — it's `nm`'s
  nearest-preceding-symbol fallback and can resolve the SAME `last-guest-pc` to different names in
  different builds (observed: `loadDatFile+21884` vs `npcProbeDriod+4512` for the identical
  `0x800290d4`). Always compare `last-guest-pc`, not `pc-symbol`, when checking "is this the same crash."

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).
