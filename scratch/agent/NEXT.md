# NEXT: G2 audio fidelity — oracle vs port AI PCM on title music

HYPOTHESIS-ID: g2-audio-noise
FIX_ZERO_SHADE flip closed (s5976). Take G2: capture retail-oracle AI PCM and port AI PCM in the title phase; compare noise floor, spectrum, sample rate, byte order. H1 noise in ucode PCM; H2 AI ring/rate/format; H3 host sink. Discriminator: does port PCM (pre-sink dump) already show the broadband noise vs oracle? Positive control: inject a known tone. No aim/steer work.
