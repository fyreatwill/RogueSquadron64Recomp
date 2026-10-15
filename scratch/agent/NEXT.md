# Next work unit

HYPOTHESIS-ID: m5-aux-store-ab

s4945: the s4944 "11x synth frames per VI" was a witness artifact (the cap resets per origin flip; rows/flip 32.8 image vs 30.8 silent).
Aux-store arms are equivalent per flip, so this A/B line is closed.
Next: take the next unfinished step in docs/M5-AUDIO-PLAN.md (de-stub sequence) and run it with a validation soak.
If none is unblocked, run one solo image-arm flips/sec counter (solo vs 2-concurrent) to separate CPU-bound from AI-drain gating.
