# NEXT (s5687): G2 audio fidelity - locate where the noise layer enters
Hypotheses: H1 noise is in ucode PCM (ADPCM/resample/envelope output); H2 AI ring/rate/format (byte order, sample-rate mismatch) ; H3 host sink (SDL resample/format).
Discriminator: capture title-music AI PCM from port and from retail oracle (tools/oracle) in the same phase; compare noise floor (high-band energy), spectrum, rate, byte order. Port PCM dumped pre-sink vs post-sink: if noise already in pre-sink dump -> H1/H2; if only post-sink -> H3. Positive control: inject a known tone / confirm dump is non-silent.
First step: grep docs/M5-AUDIO-PLAN.md and src for existing PCM dump flags (ROGUESQ_*PCM*, s5669_pcm soak) and reuse; do not build a new instrument if one exists.
HYPOTHESIS-ID: g2-audio-fidelity
