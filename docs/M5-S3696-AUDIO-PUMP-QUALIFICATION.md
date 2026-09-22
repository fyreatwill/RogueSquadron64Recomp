# M5 s3696 — qualified audio-pump route and predecessor table

The first paired run omitted `ROGUESQ_LOG_M5_SOURCE_WRITER`, so its missing
DMEM control was invalid. The fixed concurrent real-audio/silent run used the
same existing binary, LLE/ungated/solo/spin-yield route, autopilot, and phase
gate. Both arms reached VI widths `0`, `320`, `640`, `1024`, and `512`; both
RSP source-hook controls fired, with no crash or abort.

The real arm emitted the DMEM positive control in both target phases and 2,048
DMEM-store rows, plus 512 source-range DMA-to-RDRAM rows. All 2,048 sampled
DMEM writer values had zero nonzero bytes. All 512 source rows had zero
`payload_nz` and zero `post_nz`; every row carried a nonzero predecessor
sequence, and 139/512 predecessors overlapped the output DMA range. The silent
arm emitted no target DMEM or source-range rows, as expected for the `Broke`
control.

This refutes a stable audio-pump gate or route stall for the qualified arm:
the s3695 pre-320 stall is intermittent. It validates the existing DMEM
predecessor instrument and reopens producer classification. The result does
not yet distinguish a legitimate zero-producing DMEM writer from a
wrong-window join or a retail-only source path.

Evidence: `scratch/agent/soak_results/s3696_audio_pump_route_boundary_fixed_20260921/real/run.log`,
the paired silent log, and both phase-gated probe logs. ORIGIN: diagnostic
DMEM/DMA provenance witnesses; no guest or RDRAM state changed.
