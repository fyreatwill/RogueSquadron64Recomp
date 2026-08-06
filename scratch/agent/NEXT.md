# NEXT work unit

## s405 recap

Continued the bisection of s404's 20-name crash batch (`scratch/agent/s404_crash_batch_needs_bisection.txt`),
per that session's Option A plan. Split into two file-order halves of 10 from the clean revert
checkpoint (confirmed all 20 names still present in `main_overlay.txt`, sibling-repo diff unchanged
from s403).

**Half 1** — `submitCameraTrackedObjectToRender`, `emitEffectParticlesAlongPath`,
`getEffectModelPoolHandle`, `beginCameraViewTransition`, `requestCameraSnapToTrackedAnchor`,
`beginCameraTrackedTransition`, `advanceCameraTransitionOnCue`, `isCameraTransitionIdle`,
`initPlayerCraftTrailBuffers`, `loadEffectModelInstancePool` — applied, regen'd (positive control:
unmapped-functions-skipped 717→707), rebuilt clean, `nm`-confirmed, live-verified: **reproduced the
s404 crash byte-identically** (`playerXwingInit+2068`, `last-guest-pc=0x80011088`, same fault address,
same ~89.2s timing). The culprit is somewhere in this 10.

**Half 2** — `freeEffectModelInstancePool`, `computeCraftSelectTurnFromInput`,
`populateCutsceneSubtitleTextIds`, `playRandomCutsceneVoiceLine`, `integrateCraftVelocityAndCollide`,
`playCutsceneObjectImpactSound`, `tickCutsceneObject`, `findNearestSceneObjectToPoint`,
`resetEffectSequenceState`, `findNearestNpcWithinRange` — half 1 was surgically reverted
(`scratch/agent/s405_revert_half1.py`), half 2 applied on top, regen'd (717→707 again), rebuilt clean,
`nm`-confirmed, live-verified: **0 crashes**, reached `vi_width=512`→`640` (89.2s→118.1s), matching the
clean baseline almost exactly, only the 1 known pre-existing `[missing-func] 0x800FB9E4`. **This half
stays applied** — item -249 is now at **96/778 done, ~682 remain**.

Half 1 (the 10 crash-reproducing names) was reverted back to `main_overlay.txt`, marked with an
`s405:` comment block, and is NOT in the done count. Full detail: `docs/CURRENT-TRUTH.md` item -254,
`PORTING-STATE` Session 405.

## Next work unit: continue bisecting half 1 (10 names) at n=5

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 12 under this slug — iterations 9-11
were all genuine discriminating results, no stall, iron rule 8 does not trigger a pivot).

The 10 crash-implicated names, in file order (currently in `main_overlay.txt`, marked `s405:`):
```
submitCameraTrackedObjectToRender   0x800add5c   WEAK:mission
emitEffectParticlesAlongPath        0x800adf2c   CONFIRMED:mission
getEffectModelPoolHandle            0x800ae280   WEAK:mission
beginCameraViewTransition           0x800ae290   WEAK:mission
requestCameraSnapToTrackedAnchor    0x800ae320   CONFIRMED:mission
--- quarter 1 ends ---
beginCameraTrackedTransition        0x800ae358   CONFIRMED:mission
advanceCameraTransitionOnCue        0x800ae390   WEAK:mission
isCameraTransitionIdle              0x800ae3bc   WEAK:mission
initPlayerCraftTrailBuffers         0x800ae3f0   CONFIRMED:mission
loadEffectModelInstancePool         0x800ae138   CONFIRMED:mission
--- quarter 2 ends ---
```
(Tags carried over from `scratch/agent/s404_batch1_apply.txt` — no need to re-probe destinations.)

### Recipe (same as s405, repeat for each quarter)
1. Write a `scratch/agent/s406_q1_apply.txt`-style file (name/addr/tag, 3 columns — see
   `scratch/agent/s400_apply_batch.py`'s expected format) with just quarter 1's 5 names.
2. `python3 scratch/agent/s400_apply_batch.py <file>` — moves them main→mission.
3. Regen: `cd rogue_squadron64 && python3 tools/make_elf.py` (expect unmapped-functions-skipped
   717→712, exactly −5), then `cd N64Recomp && ./build/N64Recomp rogue_squadron.toml`, then
   `python3 N64Recomp/fixup_game_funcs.py`.
4. Build: `cmake -S . -B build && cmake --build build -j8` (rc=0, no new warnings).
5. `nm`-confirm the 5 names present (see `scratch/agent/s405_check_names.sh` for the pattern).
6. Live-verify:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   PASS = reaches `vi_width=512` (~89s) and continues to `vi_width=640` (~118s) with 0 crashes. FAIL =
   `playerXwingInit+2068` Bus error firing right after the 512 reach (watch a few seconds past it, not
   just the reach itself).
7. If quarter 1 crashes: revert it, the culprit is among these 5 — bisect again at n=2/3 (or even
   probe them one at a time; 5 is small enough that n=1 per name may just be faster than another
   binary split). If quarter 1 is clean: leave it applied (+5 progress), apply quarter 2 on top and
   repeat; if quarter 2 then crashes, the culprit is isolated to quarter 2 alone (no further split
   needed to confirm quarter 1's safety — it was already independently verified clean).
8. Once a single culprit name is isolated: do NOT relocate it. Add it to a new
   `scratch/agent/m4_known_bad.txt` (parallel to `m4_known_skip.txt`, but semantically distinct — this
   one caused a live crash, not an ambiguous probe) with a one-line note pointing at this session's
   writeup. The remaining 4 (proven safe by elimination) get applied and folded into item -249's done
   count.

### Do NOT this iteration
- Re-apply all 10 of half 1 at once without finishing the quarter-level split first.
- Move on to a fresh n=20 slice of the main candidate list before this thread is resolved — it's a
  live discriminating investigation, finish it.
- Patch around `playerXwingInit` without first isolating which name causes the corruption — per the
  standing rule, revert-then-investigate, not patch-same-iteration.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each bisection step gets its own live-verify run inline (they're phase-gated
and cheap enough, ~2 minutes each including build).

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 12. Three consecutive discriminating
results (s404 iteration 9, s405 half-1/half-2 split iterations 10-11) — this is genuine narrowing
progress on a real regression, not a stall. Continue the n=5 bisection.
