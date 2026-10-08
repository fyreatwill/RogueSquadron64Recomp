# Next work unit: M5 Step 10c - fresh-save crashes in audio code (nonzero PCM) and drive the pilot-create menu

HYPOTHESIS-ID: m5-audio-destub-sequence

s4227: fresh save -> first-run SELECT GAME / ARE YOU SURE? menu (title 47.6 s). "No hangar" in s4226 was input mismatch. Fresh-save runs crash at varying audio sites: fillSampleStreamRange+8136 (pc 0x8000b650, 30 s) and last-guest-pc 0x80001b08 (s4226). Stale (zero-volume) save never hits these in the first 24 s.
Hypotheses: (a) crashes are real nonzero-audio-path defects (sample stream/voice array) exposed by volume 0x7F; (b) crashes are run-timing noise unrelated to volume.
Discriminator: 4+ fresh-save runs with keys shifted to the pilot menu (Start at 48, A at 56 on YES...) and tally crash sites/times; compare with stale-save runs of equal length. Control: stale arm must reach 512 at ~24 s.
Then classify the fillSampleStreamRange crash (name the writer of the bad pointer before guarding).
