# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4927 selected an internal mission-audio boundary: the corrected driver
reached post-key `0x00690400` and later `0x00620400`, with `update_screen`
6720 -> 13696 and zero crash/abort markers. Global route/audio-task/PCM
controls were positive, but both mission-origin buckets were empty.

Next work unit: add one transition-window join that labels every global
audio-task/PCM event between the post-key `0x00690400` commit and the
following `0x00620400` commit, independent of the current origin bucket. Run
`zsh scratch/agent/s4923_mission_longevity.sh` once with the first-512 gate and
one Start/A pair unchanged. Do not add a guard or skip.

Competing hypotheses and discriminator:

1. H-stale-origin: task/PCM events occur in the transition window but are
   reported under another current origin; transition-window rows select an
   attribution defect.
2. H-before-publication: no task/PCM events occur in the transition window,
   while same-run global controls remain positive; this selects a boundary
   before mission task/PCM publication.
3. H-route-invalid: the first-512, post-key `0x00690400`, following
   `0x00620400`, advancing counter, or global controls fail; the capture is
   unevaluable.

Positive controls: first `vi_width=512`, post-key origin `0x00690400`, later
origin `0x00620400`, advancing `update_screen`, and nonzero global
route/audio-task/PCM rows. The transition-window event count is the
discriminator: nonzero selects H-stale-origin; zero with controls positive
selects H-before-publication; missing controls selects H-route-invalid.
