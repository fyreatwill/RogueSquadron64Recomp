# NEXT work unit (capture the VI-640 transition boundary)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s799 audit verified that the s798 launcher passed the intended 1024 gate,
240-second timeout, phase-relative keys, and low-volume diagnostics. Both logs
reached VI 640 and never reached 1024. Run one stability-oriented capture gated
at VI 640 with `PROBE_LEAVE_OK=1`, retaining the existing parser controls, so
the run observes whether the transition occurs after the 640 phase without
waiting on the unreachable 1024 gate.

## Competing hypotheses

- H-runtime-transition: the port reaches VI 640 but a runtime transition blocks
  the 1024 mode. Prediction: the 640-gated run remains at 640 and emits no
  parser positive controls.
- H-late-transition: the 1024 transition is merely later than the prior gate.
  Prediction: the 640-gated run reaches 1024 and then emits the four controls.
- H-gate-observer: the prior 1024 gate hid a transition already occurring after
  640. Prediction: the 640-gated run reaches 1024 but controls remain absent,
  or the phase log reveals a non-1024 transition that explains the mismatch.

## Discriminating measurement

Run the 640-gated recipe once. Reaching 1024 with controls selects
H-late-transition; staying at 640 with no controls selects
H-runtime-transition; reaching 1024 without controls selects H-gate-observer.
Any crash before the transition is unevaluable and must not be used as parser
evidence.

## Exact commands

```sh
OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/soak_results/s799_transition_640
env ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 \
  PROBE_PHASE_WIDTH=640 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
  PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start' \
  zsh tools/probe.sh "$OUT" 300 2
grep -n -E '\[phase\]|unified|provenance|callback|authoritative|CRASH|last-guest-pc' \
  "$OUT/run.log" | tail -80
```
