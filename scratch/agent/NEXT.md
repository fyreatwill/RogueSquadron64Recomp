# NEXT work unit

## s412 recap

Continued `HYPOTHESIS-ID: m4-item249-cadence-scaleup` (opened s411, n=50 confirmed clean). This
session: n=75 landed CLEAN (55 CONFIRMED + 20 WEAK, live-verified to `lastW=640`, 0 crash markers).
Pushed to n=100 next (per NEXT.md's own "one more step up" instruction) — **crashed**: Bus error,
`pc-symbol=initHudStruct+12304`, `last-guest-pc=0x800290d4`, call chain
`mainGameLoop→initMission→spawnHudNpc→spawnNpcOfType→slotDispatcherIter→initHudStruct`.

Reverted the 100-batch (wrote `scratch/agent/s412_revert_batch2.py`, mirrors `s400_apply_batch.py`),
confirmed the revert restored the exact batch-1-only unmapped-count (493), then bisected on top of the
clean n=75 baseline (s405-407 halves playbook, but testing each half/quarter ON TOP of a known-clean
baseline rather than in isolation, so every live-verify state is real):

- first 50 of the 100 → CRASH (`slotDispatcherIter+1404`, `last-guest-pc=0x80065e94`)
- first 25 of that 50 (q1) → CLEAN (live-verified, 0 crash markers, reached `lastW=640`)
- last 25 of that 50 (q2) → CRASH, **byte-identical signature to the 50-batch's crash**
  (`slotDispatcherIter+1404`, `last-guest-pc=0x80065e94` exact match)

Two independent bisection branches (the 50-batch and the isolated 25-batch) converging on the exact
same PC/symbol is strong evidence this is a specific bad function within q2, not a batch-size artifact
— matching the s404-407 `initPlayerCraftTrailBuffers` precedent (single bad function in an otherwise-
clean batch).

**Final repo state (committed): batch-1 (75) + q1 (25) = 100 net new relocations, live-verified clean.
Item -249 tally: 335/778 done (was 235/778), 463 remain per a fresh regen (458 actionable once q2's 25
are set aside, 4 known-skip, 1 known-bad).** q2's 25 names are saved at
`scratch/agent/s412_bisect_q2.txt` — NOT yet in `m4_known_bad.txt`, only isolated as a GROUP so far.

**Cadence decision: n=75 is the confirmed-safe steady-state** (not n=100) until q2's specific bad
function(s) are found and parked — full detail: `PORTING-STATE` Session 412, `docs/CURRENT-TRUTH.md`
item -249..-258.

## Next work unit: sub-bisect q2's 25-name suspect group to find the specific bad function(s)

HYPOTHESIS-ID: m4-item249-q2-badfunc-isolation

New slug — this is root-causing a specific crash (the s404-407 model), not scaling cadence, which is
CLOSED for now (steady state = n=75, use it for ordinary relocation once this thread resolves).

### A promising lead before blind bisection
`scratch/agent/s412_bisect_q2.txt`'s last entry is `npcTickEffectChannelWithSlotDispatch`
(`0x800d3240`) — its NAME directly references "slot dispatch," and the crash backtrace's deepest
N64Recomp-side frame is `slotDispatcherIter`. Worth testing this ONE name in isolation FIRST (n=1, on
top of the clean batch-1+q1 baseline) before a blind halves bisection — if it alone reproduces the
crash, this sub-thread closes in one cycle instead of 3-4 (25→12/13→6/7→1).

### Recipe (if the lead doesn't pan out, standard halves bisection)
1. Current repo state is ALREADY the correct baseline (batch-1 + q1 = 100 relocated, confirmed clean) —
   do not re-apply or re-verify it, just extend from here.
2. Test `npcTickEffectChannelWithSlotDispatch` alone: apply via
   `python3 scratch/agent/s400_apply_batch.py <single-line-file>` (grep its line out of
   `scratch/agent/s412_bisect_q2.txt`), clear `RecompiledFuncs/`, regen (make_elf → N64Recomp → fixup),
   build, `nm`-confirm, live-verify (same recipe as s412, see below).
   - CRASH with the same signature → found it. Add to `m4_known_bad.txt` (format matches existing
     entries — name, addr, tag, session, signature, note). Revert it. Apply the OTHER 24 of q2's names
     (all but this one) on top of the clean 100-baseline, live-verify — if clean, that's +24 more net
     relocations landed this session, tally becomes 359/778.
   - CLEAN → the lead was wrong; revert it, fall back to standard bisection: split q2's 25 into
     12/13, apply each half on top of the clean 100-baseline, live-verify, recurse into whichever half
     crashes (same playbook as s404-407 and this session's h1/q1/q2 split).
3. Live-verify command (unchanged from s411/s412):
   ```
   env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
     PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
     zsh tools/probe.sh <outdir> 45 2
   ```
   Run in background, block on it with TaskOutput. PASS = reaches `phase width=512` (~88-89s), no
   "process gone" line in the driver's own stdout, continues to `lastW=640` in `run.log`, 0
   `[CRASH]`/SIGBUS/SIGSEGV/UnhandledJumpTarget/dmem-race/defer-drop/assert lines. FAIL = a `[CRASH]`
   Bus error, check `grep -n "\[CRASH\]\[pc-symbol\]\|\[CRASH\]\[last-guest-pc\]" run.log` — if it
   matches `slotDispatcherIter+1404`/`0x80065e94` exactly, that confirms it's the same bug, not a new
   one.
4. Once q2's bad function(s) are isolated and parked in `m4_known_bad.txt`, resume ordinary bulk
   relocation at the confirmed-safe **n=75** cadence (not n=100 — that thread is closed per s412) using
   the standard recipe: regenerate candidates fresh (`s408_gen_candidates.py`), filter both known-skip
   and known-bad lists, take the next 75 in file order, probe/apply/regen/build/nm-verify/live-verify.

### Do NOT this iteration
- Re-attempt n=100 batches — closed per s412's discriminating result (specific-function bug, not size).
- Skip all 25 of q2's names into `m4_known_bad.txt` without isolating the actual culprit(s) — the
  s404-407 precedent found only 1 bad function out of 20 candidates; blanket-skipping wastes ~24 good
  relocations.
- Trust a prior session's "N remain" prose over a fresh regen.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued — each batch's live-verify is inline (phase-gated, ~90-120s including build).
