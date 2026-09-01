# M5 Session 3567 — DMEM payload producer

The retail oracle passed its whole-RDRAM positive control and independently
observed 674 writes in physical `0x1797B0:0x179930`, including writes from
`0x800078EC` and the expected texture-record PCs. This establishes that the
retail source range is active independently of the port.

The standalone port image arm used the validated real-audio/LLE-solo/
spin-yield/autopilot route. It reached title width 1024 and hangar origin
`0x006AB400` at width 512 with phase, source-DMA, DMEM-store, image-stage,
join, and audio-return controls live, and no crash before deliberate SIGKILL.

In target hangar tasks, RDRAM-to-DMEM DMAs from `0x1797B0`/`0x1798B0` into
`0x6F0`/`0xCB0` carried zero hashes and zero nonzero counts before the
corresponding zero writebacks. No CPU/RSP DMEM-store row overlapped the
payload window. This selects `H-DmemPayloadRdramDma`; CPU/RSP-store production
and stale-DMEM explanations are not supported at this boundary.

This is single-source port evidence for ordering and payload contents, paired
with independent retail evidence that the watched source range is genuinely
written. No game-state change was made. The next boundary is the producer of
the source-range RDRAM bytes before the image-task DMA.
