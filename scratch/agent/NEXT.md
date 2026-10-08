# Next work unit: M5 Step 10b - why is hangar (VI 512) not reached with the fresh 7F save?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4225: fresh save -> real PCM nonzero at title (nz~759/768). But no hangar in 200 s (s4224 also none); stale-save runs reached 512 at ~26 s.

Hypotheses:
- H-save-menu-flow: a fresh/blank save changes title->hangar flow (first-run screen) so the scripted Start/A no longer lands on SELECT LEVEL.
- H-audio-timing: nonzero audio changes a wait/countdown so title never advances.
- H-a12-regression: the s4192 A12 default (not the save) blocks hangar.
Discriminator (one iteration, arms built together): s4225_pcm_fresh.sh variants: (a) fresh save; (b) stale zero-volume save restored (must reproduce 512 at ~26 s = positive control); (c) fresh save + ROGUESQ_AUDIO_WAIT_NOPUMP=0. Per arm report: 512 reached?, pcm-sanity nonzero?, title frame dump. (b) reaches 512 and (a) not -> save/audio; (c) reaches 512 -> H-a12-regression.
