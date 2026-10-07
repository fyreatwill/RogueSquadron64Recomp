# Next work unit: M5 Step 9 — why is hangar PCM all-zero at the AI source, and is title's fully-nonzero PCM real?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4201: source==consumer (124/124 FNV). Hangar 81/81 source buffers all-zero; title 19 buffers 768/768 nonzero bytes (17 distinct hashes), 24 zero.
Hypotheses: H-title-garbage (title nonzero is a fill/uninit pattern, not audio); H-title-real (genuine loud PCM); H-hangar-no-voices (no active voices/music started at hangar so ucode mixes silence); H-hangar-mix-broken (voices active but ucode output zero).
Discriminator (one build, one run, title+hangar, s4200_drain_tick_ab.sh single default arm): in the pcm-boundary-source row also print the first 16 int16 samples and min/max; at hangar entry also log the MusyX active-voice count/slot status per buffer. Title min/max/sample pattern splits garbage vs real; hangar voice count splits no-voices vs broken mix. Positive control: the title nonzero buffers must show non-trivial samples in the same run.
