# NEXT work unit (one more stable post-sec2 reachability before parser-chain audit)

HYPOTHESIS-ID: m3-full-sync-parser-control-flow

The s786 repeat reached VI 1024 with positive controls and section-2 latch,
then crashed 50.4s into the run after 15 frames in
allocAndInitGridCellArray+624 (guest PC 0x80001c94). The parser chain was not
sampled. Run one more stability-oriented repeat with the same phase gate and
provenance controls; do not interpret E9 counters unless the post-sec2 capture
survives. If the next run dies again before a usable sample, pivot to a
systematic allocation/grid crash-idiom audit rather than another reactive
single-crash chase.

## Competing hypotheses

- H-prechain-transient: pre-chain failures are timing-sensitive across
  unrelated crash families. Prediction: the repeat reaches 1024 and survives
  long enough to capture post-sec2 provenance.
- H-prechain-deterministic: the current post-sec2 workload deterministically
  fails before chain capture, though the fault site may vary. Prediction: the
  repeat reaches 1024 with controls live and dies before chain data again.
- H-phase-latch: the phase gate fired but the capture window is not aligned
  with the parser work. Prediction: a surviving run has post-sec2 task/E9
  provenance without the expected chain counters.

## Discriminating measurement

One phase-gated run measuring: VI 1024 reached, control task
emit/raw/dispatch/match positive, capture survival past the 9-frame window,
and post-sec2 E9 provenance. Reaching 1024 and surviving selects
H-prechain-transient and permits the batched parser-chain audit next. A third
pre-chain death, regardless of exact fault site, selects
H-prechain-deterministic and requires a systematic allocation/grid crash-idiom
audit. A surviving run with no post-sec2 provenance selects H-phase-latch.

## Exact run

Build once:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j8

Run from build/ with the same low-noise controls:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/soak_results/s787_m3_stable_reachability 300 2

Keep the existing positive-control requirement. Do not add a mitigation or
change runtime code on a crash-only result.
