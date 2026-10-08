# Next work unit: name the residual audio stall at t≈22-30 with private DMEM on (s4258)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4257 showed private DMEM raises t=18-30 audio from ~8/s to 25-36/s, but dips of 0-17/s remain at t≈22-30 (default arms).
Hypotheses: (H1) another lock on the gfx/audio path (e.g. g_lle_task_mutex still taken elsewhere); (H2) RT64 copyToRAM / gfx task blocking the scheduler thread; (H3) game-side wait (waitForAnyAudioSlot-style), not host.
Discriminator: one build logging per-task wait breakdown (existing s4248 lock_wait_us plus scheduler queue wait) in the 22-30 s window, 3 default arms vs 3 with gfx tasks skipped. Audio dip vanishes without gfx -> H2; lock_wait_us nonzero -> H1; neither -> H3.
Reuse scratch/agent/s4257_ctrl.sh as the runner.
