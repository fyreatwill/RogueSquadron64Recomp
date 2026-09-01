# M5 Session 3496 — real-audio route failed before title

Ran one fresh direct-PID port arm from `build/` with the prescribed
real-audio/LLE/spin-yield, phase, task-writer, selector, and audio-return
controls. The process exited with SIGSEGV after 11 seconds; the watchdog did
not need to kill it.

The capture produced no title or selector controls and no usable selector
rows. The last guest PC was `0x8000B650` (`fillSampleStreamRange`), and the
host crash stack was in RT64 framebuffer writeback. The route did not qualify
for an animated selector comparison. This is a fresh route failure, distinct
from Session 3495's `0x8000834C` failure.

The discriminator selects neither selector parity nor source divergence. It
rules out only a qualified-route interpretation of the null selector rows;
the route-failure family remains unresolved. Evidence is the full capture at
`scratch/agent/s3496_m5_real_audio_route_20260831-184412.log`.

ORIGIN: diagnostic-only route, phase, selector, audio-return, and crash
observations; no audio state, selector value, task field, or route behavior
was rewritten, skipped, or validated.
