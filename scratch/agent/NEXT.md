# NEXT work unit (M3 post-sec2 reachability stability preflight)

HYPOTHESIS-ID: m3-full-sync-parser-control-flow

Session 784 could not reach the parser audit phase. Two attempts reached VI
640 and fired the positive control, then died before VI 1024/post-sec2: the
verbose attempt hit a `viRetraceHandlerThread` SIGBUS and the low-noise fixed
attempt aborted. Session 783 compared the stock Mupen64Plus CLI with the oracle. The stock CLI
fresh config lacked `Input-SDL-Control1` and fell back to `InputAutoCfg.ini`,
but a fresh 130-second oracle run using the attached SDL input path and the
verified eleven Start schedule still stayed 320-only: 21,618,871 whole-RDRAM
writes, 7,793 VI, all presses verified. The oracle runtime/configuration
thread is closed for this concrete difference.

## Discriminating measurement

First establish whether the low-noise recipe can reach VI 1024/post-sec2 at
all, while retaining only the existing positive-control/provenance marker.
The split is: reaching 1024 with controls live permits the parser-chain audit
next; two more VI-640 early deaths select a deterministic pre-target crash
blocker and require a new systematic audit target; a clean run that reaches
1024 but has no post-sec2 provenance is an instrumentation/phase-latch fault.

## Competing hypotheses for the next iteration

- H-640-transient: the two early deaths are unrelated timing-sensitive crash
  families. Prediction: the low-noise recipe reaches 1024 in the next run.
- H-640-deterministic: the current product/runtime state deterministically
  dies during the 640 phase. Prediction: another low-noise run reaches 640,
  fires controls, and dies before 1024 with the same class of marker.
- H-phase-latch: the game reaches the target work but the phase marker fails
  to publish 1024. Prediction: logs show post-sec2 provenance or equivalent
  task activity despite no `[phase] vi_width=1024` line.

Once reachability is established, retain the prior chain hypotheses:
`emitted/raw E9 -> authoritative fetch/match -> RDP dispatch -> State::fullSync`.

The single discriminating measurement is the phase-scoped chain
`emitted/raw E9 -> authoritative fetch/match -> RDP dispatch -> State::fullSync`,
with the existing control-task markers proving every arm is live. A positive
chain through a stage rules out all hypotheses upstream of that stage; a
break between two adjacent counters selects the corresponding class.

## Controls

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting command boundaries.
- Write the competing hypotheses and this discriminating measurement into this
  file before building; do not run a counter-only null.
- Use one build/run for all parser, aligned-E9, authoritative-dispatch, and
  State::fullSync counters; scope budgets to the post-sec2 phase.
- Do not productize a mitigation without naming the writer and legitimacy.

## Exact run

Build once, then run the existing 1024-gated leave recipe without the noisy
dispatch/full-sync print streams:

`cmake --build build --config Debug --target RogueSquadron64Recomp -j8`

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/soak_results/s785_m3_reachability 300 2`

Expected split: controls must fire before interpreting a null. Do not interpret
the parser chain until the 1024 gate is reached; if it is reached, run the
chain audit with one batched build/run in that same iteration.
