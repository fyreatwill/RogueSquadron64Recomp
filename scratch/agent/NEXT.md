# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4925: the width-gated driver reached the mission phase after the first
Start/A pair and remained alive for 120 s of counter samples (6656 -> 13760),
with zero crash/abort markers. This is a longevity result, not an audio-path
qualification.

Completed s4925 with the corrected `scratch/agent/s4923_mission_longevity.sh`:
the first 512-wide row armed input, one Start/A pair produced
`vi_width=512 origin=0x00690400`, and the 120-second post-key counter stayed
live. Positive controls: first 512 row, post-key mission origin, advancing
counter, and zero crash/abort markers.

Competing hypotheses and discriminator:

1. H-mission-audio-live: mission phase emits nonzero phase-scoped M5 audio/task/PCM controls; outcome: the covered mission audio path is active and remaining nulls are not route-absence evidence.
2. H-mission-audio-absent: mission phase has positive route/counter controls but zero M5 audio controls; outcome: the remaining boundary is before the instrumented audio path and needs a new route discriminator.
3. H-mission-route-invalid: the width gate or post-key mission control fails; outcome: invalidate the audio null and repair the driver before interpreting it.

Positive controls: the run must emit a first `vi_width=512` row, a post-key
`origin=0x00690400` row, advancing `update_screen`, and nonzero route-order
controls. A missing phase or dead counter invalidates the run. The audio
discriminator is the phase-scoped M5 task/SP/PCM join; each possible result
selects one of the three hypotheses above.

Next work unit: add one phase-scoped M5 audio/task/PCM control bundle to the
width-gated driver, then run `zsh scratch/agent/s4923_mission_longevity.sh`
once. Keep the first-512 gate and one-pair input schedule. Record the joined
mission-phase controls and inspect `summary.txt` plus the phase rows. Do not
interpret an audio null unless the post-key origin and advancing counter are
present.
