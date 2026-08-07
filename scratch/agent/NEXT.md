# NEXT work unit

## s413 recap

Closed `HYPOTHESIS-ID: m4-item249-q2-badfunc-isolation` (opened s412 for the 25-name suspect group
carved from the crashing n=100 batch's second quarter). Tested the named lead
(`npcTickEffectChannelWithSlotDispatch`, referencing "slot dispatch" like the crash's `slotDispatcherIter`
frame) alone first — **CLEAN**, lead was wrong. Fell back to standard halves bisection on the remaining
24, testing each split on top of the fixed 100-relocation baseline (batch-1 75 + q1 25, per s412):

- h1 (12) → CLEAN
- h2 (12) → CRASH (`slotDispatcherIter+1404`, `last-guest-pc=0x80065e94`)
- g1a (6, first half of h2) → CLEAN
- g1b (6, second half of h2) → CRASH (same signature)
- single name from g1b (`transformCraftAnchorsApplySubFx3`, 0x800E71D0) → **CRASH alone**, same exact
  signature at every depth

`transformCraftAnchorsApplySubFx3` reproduces the crash byte-identically with nothing else relocated —
recorded in `scratch/agent/m4_known_bad.txt` (2nd entry). Reverted it, applied the other 24 of q2's 25
names (including the false-lead, confirmed clean alone) as a group on top of the 100-baseline — live-
verified CLEAN (19 frames, `lastW=640`, 0 crash markers).

**Landed this session: +24 net new relocations. Repo now has 124 relocations from the s412+s413 arc
(100 + 24). Tally: 359/778 done (was 335/778), 439 remain (433 actionable, 4 known-skip, 2 known-bad).**
Full detail: `PORTING-STATE` Session 413, `docs/CURRENT-TRUTH.md` item -249..-258.

## Next work unit: resume ordinary bulk relocation at n=75 cadence

HYPOTHESIS-ID: m4-item249-bulk-relocation-n75

New slug — the q2 bad-function isolation thread is CLOSED. This is back to ordinary bulk relocation,
not root-causing, using the confirmed-safe n=75 cadence settled s412 (n=100 remains closed per s412's
discriminating result — specific-function bugs are the dominant failure mode at that size, not batch
size itself, but n=75 is still the validated steady-state until/unless a fresh discriminating probe
justifies scaling further).

### Recipe (unchanged from s408/s410/s412's ordinary-relocation steps)
1. Regenerate the candidate list fresh — do NOT trust any prior session's "N remain" prose (iron rule).
   Use whatever script s408-412 used to enumerate `main_overlay.txt` phantom-overlay candidates
   (`scratch/agent/s408_gen_candidates.py` or equivalent — check `scratch/agent/s4*.py` for the exact
   generator and probe classifier).
2. Filter OUT both `scratch/agent/m4_known_skip.txt` (4 entries, NONE/AMBIGUOUS probe results) and
   `scratch/agent/m4_known_bad.txt` (2 entries: `initPlayerCraftTrailBuffers`,
   `transformCraftAnchorsApplySubFx3` — do NOT re-probe or re-attempt either without a dedicated
   root-cause session).
3. Take the next 75 candidates in file order (CONFIRMED or WEAK tag, single destination overlay).
4. Apply via `python3 scratch/agent/s400_apply_batch.py <batch-file>` (moves entries from
   `main_overlay.txt` to the destination overlay file).
5. Clear `RecompiledFuncs/funcs_*.c` (`zsh scratch/agent/s410_clear_recompiledfuncs.sh` or equivalent),
   regen: `make_elf.py` → `N64Recomp` (`zsh tools/agent/regen_n64recomp.sh`) → `fixup_game_funcs.py`.
6. Build: `cd build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
7. `nm`-verify all names present in the built binary (positive control — every name must show up).
8. Live-verify:
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   Run in background, block with TaskOutput. PASS = reaches `phase width=512` (~88-89s), no "process
   gone" line, continues to `lastW=640` in `run.log`, 0 `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/
   dmem-race/defer-drop/assert lines. FAIL = a `[CRASH]` Bus error — check
   `grep -n "\[CRASH\]\[pc-symbol\]\|\[CRASH\]\[last-guest-pc\]" run.log`; if the signature is new (not
   `slotDispatcherIter+1404`/`0x80065e94` or `playerXwingInit+2068`/`0x80011088`), this is a THIRD bad
   function/family — defer bisection to the next iteration rather than guessing, same as s404 and s412
   did.
9. If clean: commit the symbol-file moves are in the SEPARATE `rogue_squadron64` repo — do NOT commit
   there autonomously (item -3 rule, ask the user first). This repo's commit only covers
   `scratch/agent/*` and the docs.

### Do NOT this iteration
- Re-attempt n=100 — closed per s412's discriminating result.
- Re-probe or re-relocate either of the 2 `m4_known_bad.txt` entries without a dedicated root-cause
  session.
- Trust a prior session's "N remain" prose over a fresh regen (`make_elf.py`'s own
  unmapped-functions-skipped counter is the ground truth).

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).
