# NEXT work unit (s2670) — qualify the Step 0 control with the stable driver

HYPOTHESIS-ID: m5-audio-step0-control-qualification

## Work unit

Make one bounded control-only repair: replace the failing isolated-arm launch
path with the repository's known stable phase-driver recipe, while retaining
the oracle gate, the same input schedule, and all phase/probe settings. Run
silent and default controls in one build/run and collect both summaries. Do
not alter runtime behavior, audio routing, gates, or guards.

## Competing hypotheses and discriminator

- `H-stable-driver-qualifies`: both arms reach title and hangar with the
  oracle control intact; the prior wrapper path was the invalid component.
- `H-port-crash-persists`: the stable driver still loses one or both arms
  before hangar; the port-side control remains unevaluable.
- `H-driver-control-invalid`: the replacement loses the oracle/title positive
  controls or fails to launch one arm; the driver comparison is invalid.

The discriminator is the same-build table of oracle positive-control rows,
independent title/hangar phase rows, and terminal host/guest crash attribution
for both arms. Both hangar rows select `H-stable-driver-qualifies`; pre-hangar
loss with intact oracle/title selects `H-port-crash-persists`; missing oracle,
title, or arm-launch controls selects `H-driver-control-invalid`.

## Exact commands

1. Edit only the control-driver entry point with `apply_patch` to invoke the
   known stable phase-driver recipe, preserving SIGKILL cleanup and marker
   categories.
2. `zsh scratch/agent/run_s2277_m5_step0_ground_truth.sh`
3. Inspect only its `driver.log` and bounded `grep -c`/`tail -50` slices of
   the arm logs.

Expected: the oracle positive control remains present. Both arms either reach
hangar, qualifying the M5 contract table for the next step, or fail before
hangar and leave audio behavior unchanged.
