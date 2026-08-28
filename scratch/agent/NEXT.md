# NEXT work unit (s2876) — m5-state-arbiter-port-equivalence

HYPOTHESIS-ID: m5-state-arbiter-port-equivalence

## Work unit

Use the newly established retail writer `0x8006E4B4` as the next bounded
port-side discriminator. First rerun the retail oracle with the same
whole-RDRAM control and a phase-qualified execution watch for `0x8006E4B4` plus
the `0x80130B40:0x80130B80` write histogram. Only if that control again reaches
title and hangar, add one batch of port probes for the generated equivalent of
the `0x8006E4B4` call/store site and the same state span, then run the matching
image/silent pair. Do not change behavior or interpret downstream audio nulls.

## Competing hypotheses and discriminator

- H-writer-missing: the retail `0x8006E4B4` writer is phase-qualified but the
  matching port writer/store is absent before or during its target phases.
- H-writer-equivalent: retail and port both show the writer and state-span
  sequence in matching target phases, ruling out this writer class at scope.
- H-route-invalid: the retail positive control fails or the matching port pair
  does not reach title and hangar, making writer rows unevaluable.

The discriminator is one retail-vs-port phase table: positive-control count,
title/hangar reachability, `0x8006E4B4` phase rows, and state-span writer/value
histograms. Each outcome selects one hypothesis above; no downstream audio
counter is interpreted on H-route-invalid.

## Exact command

    sed -n '1,220p' tools/oracle/README.md
    # Run the retail preflight first; use the exact command in the prior
    # artifact, replacing --watch-pc with 0x8006E4B4 and retaining both phase
    # buckets and the whole-RDRAM control.

Record the phase table under `scratch/agent/s2876_m5_state_arbiter/`; use
SIGKILL, run from `build/`, and run `git diff --check` before committing.
