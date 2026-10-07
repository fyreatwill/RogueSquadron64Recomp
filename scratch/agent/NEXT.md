# Next work unit: execute the next bounded M5 audio de-stubbing step

HYPOTHESIS-ID: m5-audio-destub-step

Session 4163 closed the earlier-writer census: `pi_rom_to_rdram` is the
legitimate nonzero host writer before the hangar clear, while generated guest
scalar/non-scalar rows remain zero. Do not repeat that census.

Competing hypotheses and discriminator:

- H-audio-stub-artifact: one bounded audio de-stub removes a degenerate path;
  its arm reaches title/hangar with the targeted stub signature absent and no
  new crash family.
- H-audio-real-route-defect: the same de-stub causes a new pre-target failure
  or changes the existing route signature.
- H-unrelated-state-defect: the de-stub leaves the target source and route
  signature unchanged.

Exact work: read `docs/M5-AUDIO-PLAN.md`, select its first not-yet-qualified
incremental step, implement only that step, and run its phase-gated validation
capture. Build every required control arm in this iteration. Expected outcome:
title/hangar controls and unchanged route markers with the targeted stub
signature removed supports H-audio-stub-artifact; a new pre-target failure or
unchanged route supports the other hypotheses.
