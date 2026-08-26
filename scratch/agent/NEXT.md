# NEXT work unit (s2400) — identify the accepted-preparation clear edge

HYPOTHESIS-ID: m5-image-stage-route-order-perturbation

## Work unit

Use one ground-truth-first, bounded capture to distinguish where the accepted
route identity is cleared between `rs64_audio_route_prepare` and
`rs64_audio_image_stage`. Keep the qualified LLE/image route,
`ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=1024`, and the existing
route/stage probes. Do not change task data, audio, gate, fallback, dispatch,
VI, output behavior, or mitigation.

Before building, arm the retail oracle's whole-RDRAM positive control and the
target-origin control; only trust a null after both controls fire. In the port,
add one complete phase-keyed clear-edge table covering the accepted preparation
sequence, stage entry, route-valid state, and every host/guest clear or reset
edge already present in the route identity path. Run all A/B arms from the same
build and kill with SIGKILL.

## Competing hypotheses and discriminator

- H-HostClearBetweenPrepareStage: the host-side route identity is explicitly
  cleared between preparation and stage entry.
- H-GuestClearBeforeHostStage: a guest-side edge clears the source state before
  the host stage callback observes it.
- H-SeparateIdentityRead: the accepted identity remains live, but stage entry
  reads a different identity source.

The discriminator is a single phase-keyed table with one row per retained stage
call and columns for preparation sequence, clear-edge sequence/PC/source,
stage sequence, route-valid state, route ordinal/row, and arm. A clear event
between equal preparation and stage sequence selects the corresponding clear
edge; no clear with invalid stage identity selects separate-source use.

## Exact command shape

`cmake --build build -j2`

Run the two same-build arms with the controls from
`scratch/agent/s2399_identity_join_run.sh`, plus the oracle control recipe in
`tools/oracle/README.md`; use `env ... zsh ...` for env-prefixed commands.
Reduce logs with `python3 scratch/agent/s2399_identity_join.py LOG` only after
the positive controls and target title origin are present.

Expected outcomes: host clear rows select `H-HostClearBetweenPrepareStage`;
guest clear rows select `H-GuestClearBeforeHostStage`; no clear rows with
persisting accepted identity select `H-SeparateIdentityRead`. If the route
control fails in either arm, reject the capture and fix the driver in the same
iteration.
