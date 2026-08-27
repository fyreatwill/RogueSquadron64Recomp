# NEXT work unit (s2669) — isolate the pre-hangar control crash

HYPOTHESIS-ID: m5-audio-step0-control-qualification

## Work unit

Make one bounded control-only change to the Step 0 driver: retain the oracle
gate and all phase/probe settings, but run the silent/default arms in separate
isolated launches with the same input schedule and collect both summaries in
one iteration. Do not alter runtime behavior, audio routing, gates, or guards.
The purpose is to determine whether the shared `slotDispatcherIter+3508`
failure is caused by paired-process interference or is intrinsic to each arm.

## Competing hypotheses and discriminator

- `H-shared-process-interference`: isolated arms reach hangar; the paired
  concurrent control is invalid because two instances contend for a host-side
  resource.
- `H-common-prehangar-crash`: isolated arms reproduce the same crash before
  hangar; the failure is intrinsic to the current control route and the
  contract remains unevaluable.
- `H-isolation-driver-invalid`: an isolated arm loses title or its positive
  control; the recipe cannot discriminate the crash and needs driver repair.

The discriminator is the same-build, oracle-qualified table with independent
title/hangar phase rows and terminal host/guest crash attribution for both
arms. Hangar reach in isolation selects interference; repeated pre-hangar
crashes select the common crash; missing controls select driver invalidity.

## Exact commands

1. Edit only `scratch/agent/run_s2288_m5_audio_default_step2.sh` with
   `apply_patch` to use isolated bounded arm launches while preserving
   SIGKILL cleanup and all existing marker categories.
2. `zsh scratch/agent/run_s2277_m5_step0_ground_truth.sh`
3. Inspect only `scratch/agent/s2277_m5_step0_ground_truth/driver.log` and
   bounded `grep -c`/`tail -50` slices of its logs.

Expected: the oracle positive control remains present. Both isolated arms
  either reach hangar or reproduce the common crash; do not change audio
  behavior based on a control-invalid result.
