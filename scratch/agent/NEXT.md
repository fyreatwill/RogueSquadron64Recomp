# NEXT (s5926): G2 audio fidelity - where does the fuzzy noise enter?

HYPOTHESIS-ID: g2-audio-fidelity

Rung G2 (ITERATION.md 3c) has never been run; G1 bolt-damage thread is closed by s5925.
Hypotheses for the noise layer: (A) ucode PCM output itself noisy (bad ADPCM decode/resample/reverb in the ported ucode); (B) AI ring/rate/format (byte order, sample-rate mismatch, dropped/duplicated frames); (C) host sink (SDL resample/format).
Discriminator: dump port AI DMA PCM (at the AI register write, before the host sink) for the title music over a fixed VI-phase window, and dump the same window to a WAV via the host sink path; analyze offline (spectrum, noise floor, ratio of high-band energy, sample rate from AI_DACRATE). If the pre-sink dump is already noisy -> A or B (check byte order/rate by spectrum of a known tone); if clean pre-sink but noisy after -> C. Retail oracle (tools/oracle/README.md) AI PCM of the same title music is the reference for the noise floor if the pre-sink dump is noisy.
First: grep the port for an existing AI PCM dump flag (grep -rn "AI_PCM\|DUMP_AI\|ai_dump" src tools) before building a new one. Capture once, analyze many.
