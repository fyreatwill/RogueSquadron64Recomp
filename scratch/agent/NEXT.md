# NEXT work unit (stability-oriented post-sec2 parser-chain capture)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s792 writer-attribution repeat selected independent known writers for the
wild-writeback path, but both attempts died before the parser target phase.
The next unit is one bounded run that obtains a post-sec2 parser-chain sample;
do not interpret another VI-640 null.

## Competing hypotheses

- H-authoritative-advance-loss: aligned E9 commands reach the task stream but
  are lost before authoritative dispatch. Prediction: post-sec2 controls show
  aligned E9 > authoritative E9, with authoritative E9 still dispatching to
  `State::fullSync`.
- H-parser-handler-loss: authoritative dispatch is reached but the handler or
  state accounting loses FULL_SYNC. Prediction: authoritative E9 and dispatch
  counts advance, but `State::fullSync` does not match them.
- H-postsec2-co-gate: parser loss is downstream of a post-sec2 presentation or
  recovery gate. Prediction: parser-chain counts correlate with the gate and
  change when the existing recovery-active recipe is used.

## Discriminating measurement

One stability-oriented, phase-gated post-sec2 run carrying all existing
provenance, parser, free-list, and writeback telemetry. Positive control is
four same-run records with `emit=1`, `raw=1`, `dispatch=1`, and `match=1`.
The discriminating sample is one VI-1024/post-sec2 window containing aligned
E9 count, authoritative parser E9 count, dispatch count, and
`State::fullSync` count. A pre-gate death is unevaluable and requires its
fixed repeat immediately.

## Exact command

Run `zsh scratch/agent/s790_postsec2_reachability.sh` once. This is the
existing phase-gated recipe with `PROBE_PHASE_WIDTH=1024`, the phase-relative
key schedule, `PROBE_LEAVE_OK=1`, and all passive telemetry. Build only if the
working tree/build manifest is stale; otherwise use the existing build and
capture the generated `run.log` under `scratch/agent/soak_results/`.

Expected outcomes: aligned E9 much greater than authoritative E9 selects
H-authoritative-advance-loss; authoritative E9 without matching fullSync
selects H-parser-handler-loss; gate-correlated changes select
H-postsec2-co-gate. No mitigation is allowed from this capture.
