# NEXT work unit

## s406 recap

Continued the bisection of s405's 10-name crash suspect set (`submitCameraTrackedObjectToRender` ...
`loadEffectModelInstancePool`, all parked in `main_overlay.txt` from s405's revert) per that session's
Option A plan, split into two file-order quarters of 5.

**Quarter 1** — `submitCameraTrackedObjectToRender`, `emitEffectParticlesAlongPath`,
`getEffectModelPoolHandle`, `beginCameraViewTransition`, `requestCameraSnapToTrackedAnchor` — applied,
regen'd (positive control: unmapped-functions-skipped 707→702), rebuilt clean (295 warnings, matches
baseline), `nm`-confirmed, live-verified: **0 crashes**, reached `vi_width=512`→`640` (88.5s, matching
clean baseline). **This quarter stays applied** — item -249 is now at **101/778 done, ~677 remain**.

**Quarter 2** — `beginCameraTrackedTransition`, `advanceCameraTransitionOnCue`, `isCameraTransitionIdle`,
`initPlayerCraftTrailBuffers`, `loadEffectModelInstancePool` — applied on top (702→697), rebuilt clean,
all 10 `nm`-confirmed present, live-verified: **reproduced the s404/s405 crash byte-identically**
(`playerXwingInit+2068`, `last-guest-pc=0x80011088`, crash 2.1s after reaching `vi_width=512`). The
culprit is somewhere in this 5. Quarter 2 was surgically reverted (`scratch/agent/s406_revert_q2.py`)
back to `main_overlay.txt` (marked `s406:`), and the repo was rebuilt with quarter 1 alone applied to
leave a clean, buildable, source-matching state (positive control re-confirmed: back to 702, 295
warnings, rc=0). Full detail: `docs/CURRENT-TRUTH.md` item -255, `PORTING-STATE` Session 406.

## Next work unit: continue bisecting quarter 2 (5 names) at n=2/3

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 13 under this slug — iterations 9-12
were all genuine discriminating results, no stall, iron rule 8 does not trigger a pivot).

The 5 crash-implicated names, currently in `main_overlay.txt` marked `s406:`:
```
beginCameraTrackedTransition   0x800ae358   CONFIRMED:mission
advanceCameraTransitionOnCue   0x800ae390   WEAK:mission
isCameraTransitionIdle         0x800ae3bc   WEAK:mission
--- split A ends (3) ---
initPlayerCraftTrailBuffers    0x800ae3f0   CONFIRMED:mission
loadEffectModelInstancePool    0x800ae138   CONFIRMED:mission
--- split B ends (2) ---
```
(Tags carried over from `scratch/agent/s404_batch1_apply.txt` — no need to re-probe destinations.)
5 names is small enough that per-name isolation (n=1, 5 separate apply+build+verify cycles) may
actually be *faster* than another binary split, since each cycle is only ~2-3 minutes. Consider going
straight to n=1 this iteration instead of a 3/2 split, if time allows — either is a valid discriminating
design.

### Recipe (same as s405/s406, repeat for each split)
1. Write a `scratch/agent/s407_a_apply.txt`-style file (name/addr/tag, 3 columns — see
   `scratch/agent/s400_apply_batch.py`'s expected format) with just that split's names.
2. `python3 scratch/agent/s400_apply_batch.py <file>` — moves them main→mission.
3. Regen: `cd rogue_squadron64 && python3 tools/make_elf.py` (expect unmapped-functions-skipped to
   drop by exactly the split size from 702), then `cd N64Recomp && ./build/N64Recomp
   rogue_squadron.toml`, then `python3 N64Recomp/fixup_game_funcs.py`.
4. Build: `cmake -S . -B build && cmake --build build -j8` (rc=0, still 295 warnings, no new ones).
5. `nm`-confirm the split's names present (pattern: see `scratch/agent/s406_check_names.sh`).
6. Live-verify:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   PASS = reaches `vi_width=512` (~88.5s) and continues to `vi_width=640` with 0 crashes, `run.log` has
   no `[CRASH]`/`Bus error` lines. FAIL = `playerXwingInit+2068` Bus error firing within a few seconds
   of the 512 reach (matches s404/s405/s406's signature exactly — watch `process gone at Ns after N
   frames` in the probe.sh output, it fires around 2s after phase-reach).
7. If a split crashes and it's down to a single name: STOP relocating it. Add it to a new
   `scratch/agent/m4_known_bad.txt` (parallel to `m4_known_skip.txt`, but semantically distinct — this
   one caused a live crash, not an ambiguous probe) with a one-line note pointing at this session's
   writeup, and move on to a fresh n=20 slice of the main candidate list (item -249 continues from
   677 remaining, skipping this one known-bad name going forward). If a split of >1 crashes, keep
   bisecting narrower until a single name is isolated.
8. If a split is clean: leave it applied, apply the next split on top and repeat, same logic as
   s405/s406 (each independently-verified-clean split doesn't need re-checking once the full set is
   isolated to the crashing remainder).
9. Once isolated: rebuild with only the proven-safe names applied (not the known-bad one) to leave the
   repo in a clean, buildable, matching-source state before ending the session — same as s406 did.

### Do NOT this iteration
- Re-apply all 5 of quarter 2 at once without finishing the split.
- Move on to a fresh n=20 slice of the main candidate list before this thread is resolved, UNLESS a
  single culprit name has just been isolated (see step 7) — then it's fine and expected to pivot back
  to bulk relocation with the bad name on the new skip/bad list.
- Patch around `playerXwingInit` without first isolating which name causes the corruption — per the
  standing rule, revert-then-investigate, not patch-same-iteration.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each bisection step gets its own live-verify run inline (they're phase-gated
and cheap enough, ~2-3 minutes each including build).

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 13. Four consecutive discriminating
results (s404 iteration 9, s405 iterations 10-11, s406 iteration 12) — this is genuine narrowing
progress on a real regression, not a stall. Continue the n=2/3 (or n=1) bisection of the final 5.
