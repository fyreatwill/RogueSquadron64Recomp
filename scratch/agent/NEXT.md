# NEXT work unit

## s374 picked Option A and ran its bounded source-only first pass — found a specific candidate mechanism

Full write-up: `docs/CURRENT-TRUTH.md` item -228, `PORTING-STATE.md` Session 374. One-paragraph
version: under the C88-reversed (audio gate durably on) state, `waitForAnyAudioSlot`
(`N64Recomp/RecompiledFuncs/funcs_15.c:7217`, called from `cinematicLoopBody`'s gate-independent
cutscene-teardown block, `funcs_27.c:108288`, which fires deterministically pre-title) reaches
`factor5MutexAcquire` for the first time ever via its per-iteration `tickMusyXIfActive` call. That
blocks on `osRecvMesg_recomp` against a single-token (`count=1`) message queue
(`initFactor5Mutex`, `funcs_24.c:5703-5745`) that is unconditionally destroyed and recreated EVERY
VIDEO FRAME by `reapplyAudioConfig`→`initFactor5Mutex` (`funcs_24.c:5070`), itself driven every
frame from `reapplyDisplayMode`→`runVideoFrameTick`. Under gate=0 (baseline) this per-frame churn
is inert; under gate=1 it's live for the first time in the project's history — a queue-recreation
race against a blocking receive. The existing `waitForAnyAudioSlot` 500000-iteration guard (s301)
cannot catch this: it only checks between full loop-body iterations, and a single blocking
`osRecvMesg_recomp` prevents even a second iteration.

## This iteration's work unit: build+soak instrumentation to confirm or refute the mechanism

This is the DISCRIMINATING measurement NEXT.md called for. Two competing outcomes:
- **Confirmed**: an entry/exit log around `factor5MutexAcquire`'s `osRecvMesg_recomp` call freezes
  (last log line = "entered `osRecvMesg_recomp`, never exited") at the exact wall-clock moment the
  soak's VI-width log sticks at 640.
- **Refuted**: the log keeps moving (enters and exits normally, repeatedly) well past the moment VI
  sticks at 640 — meaning `factor5MutexAcquire` is NOT where execution wedges, and item -227's
  original open question (what specifically drives VI 640→1024 in the gate=0 baseline; no such site
  was found in this session's source trace) becomes the only remaining thread. If refuted after one
  full try, this is 2/3 of the hypothesis-ID's iteration budget — the 3rd iteration should pivot to
  locating the VI-transition trigger directly rather than re-poking the same mutex theory a 3rd way.

### Instrumentation to add (batch it all in one build, per iron rule 1)
In `N64Recomp/fixup_game_funcs.py`, add a PATCH block (mirroring the existing
`[audio-drain-*]` style at `funcs_15.c:7220-7226`) that:
1. Wraps `factor5MutexAcquire`'s call to `osRecvMesg_recomp` (`funcs_24.c:5781`, inside
   `factor5MutexAcquire` at `funcs_24.c:5755`) with enter/exit `fprintf(stderr, "[f5mutex-acquire]
   enter/exit ...")` logs, env-gated `ROGUESQ_LOG_F5MUTEX=1`, unconditional (no sampling — this is a
   rare-event trace, not a hot-path histogram).
2. Same style around `factor5MutexRelease` (`funcs_24.c:5808` area) and `initFactor5Mutex`
   (`funcs_24.c:5703`, log both the `osCreateMesgQueue_recomp` and the `osSendMesg_recomp` calls) —
   the recreation-race needs both sides visible in one log.
3. Reuse the existing `[phase] vi_width=` instrument (already present, confirms VI-stuck-at-640
   timing) — do not add a new one.
4. This needs the C88 gate REVERSED to reproduce the hang (opposite of the shipped default) — do
   this as a temporary local build, NOT a change to the committed default. Confirm current gate
   state before touching it: `grep -n "0XF50" N64Recomp/RecompiledFuncs/funcs_23.c` should show the
   force-zero patch at the `reapplyDisplayMode` site (~line 9838 zero, ~line 10020 force-zero) —
   reverse ONLY the second (`0x8008EC88`) site for this soak, exactly as s342 did, then restore it
   before committing anything (the fixup script's default output must stay force-zeroed).

### Commands
```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # with the new f5mutex instrument + temporarily-reversed C88 site
cd build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
cd build && env ROGUESQ_LOG_F5MUTEX=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 timeout 300 ./RogueSquadron64Recomp 2>run_f5mutex.log &
# watchdog + SIGKILL per standing rules; capture run_f5mutex.log
```
After this soak: revert the C88 site back to force-zero, re-run `fixup_game_funcs.py`, confirm the
patch report shows the expected baseline before committing (regeneration reliability rule, item
-20). The f5mutex instrument itself can stay in the fixup script permanently (it's inert/env-gated
under the shipped gate=0 default) if useful for future audio work — reviewer's call next iteration.

## Iteration budget

HYPOTHESIS-ID: m5-audio-destub-c88-pretitle-hang (iteration 2 of budget — s374 was iteration 1,
source-only, no build). If this build+soak is also inconclusive (neither confirms nor cleanly
refutes), iteration 3 is the last before a mandatory pivot preamble per iron rule 8.
