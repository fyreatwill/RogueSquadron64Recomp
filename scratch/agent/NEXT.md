# Next: M5 audio de-stubbing survey (docs/M5-AUDIO-PLAN.md) — the regen-discriminator thread is parked
HYPOTHESIS-ID: m5-audio-destub
s5091: pristine-regen discriminator was unevaluable (s4204-fresh tree fails vendored fixup at s4938 before replay). s5090's post-condition already guards the s4296 marker; do not spend more on this unless regen output can be redirected to a scratch dir.
Work unit: write docs/M5-AUDIO-PLAN.md — grep-survey every audio stub/trap/gate in force, then an incremental de-stub sequence with a validation soak per step (strategic priority 2). Discriminating outcome: a ranked step list whose step 1 is executable with an existing soak recipe.
