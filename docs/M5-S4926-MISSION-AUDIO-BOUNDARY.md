# M5 s4926 — mission-origin audio boundary

The corrected width-gated driver reached the first 512-wide phase, accepted
one Start/A pair, and observed `0x00690400` as the post-key origin. The
update-screen counter advanced from 6656 to 13888 over 120 seconds; crash and
abort markers stayed at zero.

The same run carried route-order, audio-task contract, PCM source/consumer,
and PCM sanity controls. Their global controls were positive, but every
mission-origin row was zero: route-order 0, audio-route 0, audio-task 0, PCM
source 0, PCM consumer 0, and PCM sanity 0. The run therefore selects the
current route-boundary hypothesis: the visible `0x00690400` phase is not the
phase in which the instrumented audio work executes. It does not authorize a
guard or skip.

The next discriminator must retain the post-key origin witness while joining
audio-task/PCM rows against the immediately following 512-wide origin
(`0x00620400`) or an origin-transition latch; a null based only on the current
VI origin would otherwise conflate a phase handoff with route absence.

ORIGIN: no mitigation or game-behavior change; only phase gates and the
width-gated capture summary were extended for measurement.
