# Next work unit: leave object-path parity qualification; pick the next M5 de-stub step

HYPOTHESIS-ID: m5-step4-object-entry-body

s4191: caller continuation 0x8008F4C0 matched retail in the hangar (v0/v1/a0/a2/
s0/s1/s2 equal). With s4187-s4190 the whole initSampleStreamBlockCache object
path is register-parity clean in the hangar; six consecutive qualification
sessions found no divergence. Do NOT add another parity witness on this path.

Next: read docs/M5-AUDIO-PLAN.md, choose the next not-yet-done de-stub step
(a stub/gate still in force whose removal could be soaked), and land it with a
validation soak. Hypotheses: H-destub-dissolves-guard (crash family disappears),
H-destub-neutral (no change), H-destub-regresses (new crash). Discriminator: the
same hangar soak recipe with the gate off vs on, built as two arms in one iteration
(iron rule 13). If the plan has no remaining safe step, go BLOCKED with a
specific question.
