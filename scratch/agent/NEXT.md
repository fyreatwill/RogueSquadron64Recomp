# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4923: s4796-style driver gated on origin 0x006AB400, never seen; unprompted 512/0x00690400 phase at ~97 s; alive 240 s, 0 crashes, vi-fs stalled=1 at end.

Completed s4924 with `scratch/agent/s4924_phase_origin_x3.sh`: three sequential current-binary runs selected first 512 origin `0x00690400` (all 3/3), with later `0x00620400` also present (3/3), positive controls in all runs, and zero crash/abort markers.

Competing hypotheses and discriminator:

1. H-stable-label: the first 512 phase is consistently `0x006AB400`; outcome: all three runs' first-512 rows have that origin, so the prior miss was route timing and the hangar gate remains valid.
2. H-mission-label: the first 512 phase is consistently `0x00690400`; outcome: all three runs select that origin, so the driver must key on width rather than the old hangar address.
3. H-route-variable: first-512 origins vary across runs; outcome: both origins occur in the three-run table, so origin cannot identify the press trigger and the next driver must use width plus an explicit post-key phase transition.

Positive control: each run must emit a 512-wide phase row and continue advancing `update_screen`; a run without that control is invalid and cannot select a hypothesis.

Next work unit: make one bounded edit to `scratch/agent/s4923_mission_longevity.sh` so its wait changes from `vi_width=512.*origin=0x006AB400` to `vi_width=512`, then run `zsh scratch/agent/s4923_mission_longevity.sh`. Press Start/A only after the first 512-wide row, and inspect `scratch/agent/s4923_mission_longevity/driver.log` plus the phase rows in `run.log`. H-post-key: a new phase within the six Start/A pairs selects the mission trigger. H-no-post-key: no phase change but counter/control stays live, so width is only a press trigger and the route needs a different entry condition. Invalidate the run if there is no 512-wide positive-control row or no advancing update-screen counter.
