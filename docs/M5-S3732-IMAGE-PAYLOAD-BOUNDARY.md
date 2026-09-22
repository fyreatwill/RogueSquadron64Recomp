# M5 session 3732 — image payload boundary recheck

The prescribed same-build oracle/real/silent pair was attempted twice. The
oracle passed its whole-RDRAM positive control and reached the 512 target. The
silent arm reached the 512 target on both attempts and fired its RSP control,
but the real arm was invalid before the target phase: the first attempt hit a
VI-retrace bus error at width 640 and the retry hit the known scheduler/audio
boundary at guest PC `0x8000834C`.

A fixed real-audio-only capture with the identical environment was then valid.
It reached VI 1024 at 13.2 seconds and VI 512 at 24.4 seconds, fired the RSP
positive control, and emitted 2,557 phase-5 output-DMA joins, 2,561 completion
calls, and 528 PCM-consumer rows. Among 1,903 phase-5 output joins, every row
had `source_dmem_nz=0`, `nz=0`, and `destination_nz=0`; the repeated payload
hash was `762B22A5`.

This requalifies `H-ImageProducerZero` for the port's measured image stream,
but it does not provide a same-run real/silent A/B or retail payload parity.
The two paired failures are recorded as reachability failures, not payload
evidence. Existing independent retail evidence remains the second evidence
line for the port-versus-retail source discrepancy.

ORIGIN: diagnostic-only paired image/source/consumer capture and one fixed
real-audio-only recheck. No guest, RSP, task, audio, selector, clear,
writeback, or consumer behavior changed.

Evidence: `scratch/agent/s3732_m5_image_payload/`.
