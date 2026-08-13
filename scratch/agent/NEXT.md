# NEXT work unit (stable post-sec2 reachability before parser-chain audit)

HYPOTHESIS-ID: m3-full-sync-parser-control-flow

The s785 recipe reached VI 1024 with positive controls, then crashed 30.2s
into the 9-frame capture in MetalCommandList::barriers+436. The parser chain
was not sampled. Run one stability-oriented repeat with the same phase gate
and provenance controls; do not interpret E9 counters unless the post-sec2
capture survives.

## Competing hypotheses

- H-renderer-transient: the Metal barrier crash is timing-sensitive.
  Prediction: the repeat reaches 1024 and survives long enough to capture
  post-sec2 provenance.
- H-renderer-deterministic: the current post-sec2 workload deterministically
  crashes in the renderer barrier path. Prediction: the repeat reaches 1024
  with controls live and dies in the same barrier family before chain data.
- H-phase-latch: the phase gate fired but the capture window is not aligned
  with the parser work. Prediction: a surviving run has post-sec2 task/E9
  provenance without the expected chain counters.

## Discriminating measurement

One phase-gated run measuring: VI 1024 reached, control task
emit/raw/dispatch/match positive, capture survival past the 9-frame window,
and post-sec2 E9 provenance. Reaching 1024 and surviving selects
H-renderer-transient and permits the batched parser-chain audit next.
Two barrier-family deaths select H-renderer-deterministic and require a
systematic renderer-barrier idiom audit. A surviving run with no post-sec2
provenance selects H-phase-latch.

## Exact run

Build once:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j8

Run from build/ with the same low-noise controls:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/soak_results/s786_m3_stable_reachability 300 2

Keep the existing positive-control requirement. Do not add a mitigation or
change runtime code on a crash-only result.
