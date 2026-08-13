# NEXT work unit (audit the phase-gated transition boundary)

HYPOTHESIS-ID: m3-postsec2-parser-chain

The s798 lower-volume repeat also stopped at VI 640 in both arms after the
240-second phase timeout. It emitted no provenance or join controls, so the
parser join remains untested. Before another parser capture, audit the probe
recipe and transition boundary in one bounded, read-only work unit; do not
add instrumentation or infer a parser result from a pre-1024 timeout.

## Competing hypotheses

- H-recipe-gate: the probe recipe never reaches the transition that enables the
  1024 phase. Prediction: inspection finds a key/phase or launcher mismatch.
- H-runtime-transition: the port reaches VI 640 but a runtime transition blocks
  the 1024 mode. Prediction: recipe inputs and env propagation are correct, but
  the run log shows the expected pre-transition state without the gate.
- H-instrumentation-interference: the diagnostics or launcher alter stability.
  Prediction: the audit finds an unintended enabled category, stale process,
  or logging path beyond the requested low-volume set.

## Discriminating measurement

Read-only audit of `tools/probe.sh`, its argument/env handling, the two s798
launcher logs, and the captured phase lines. The discriminating result is
whether the requested phase gate and key schedule were actually propagated:
an argument/env mismatch selects H-recipe-gate; correct propagation plus
explicit VI-640/no-1024 evidence selects H-runtime-transition; an unintended
diagnostic/process path selects H-instrumentation-interference. If all three
remain possible, stop and ask for ground truth rather than rerunning the join.

## Exact commands

```sh
rg -n 'PROBE_PHASE|PROBE_KEYS|ROGUESQ_LOG_E9|probe.sh|launch|env' tools/probe.sh scratch/agent/soak_results/s798_join_a_launcher.log scratch/agent/soak_results/s798_join_b_launcher.log
grep -n -E '\[phase\]|1024|640' scratch/agent/soak_results/s798_join_a/run.log scratch/agent/soak_results/s798_join_b/run.log | tail -40
```

No build or run. This audit must name one corrected, falsifiable next capture
or leave the investigation blocked; any pre-1024 death remains unevaluable for
the join.
