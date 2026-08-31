# M5 Session 3422 — retail target writer-state join

The independent retail oracle passed whole-RDRAM, target-span, producer-PC,
and both explicit target VI controls. It recorded 11,166 whole-RDRAM writes,
1,166 target-span writes, 1,291,783 producer-PC executions, and 664
phase-qualified target stores from `0x800078EC`. The joined retail state was:

    a0=0x801797B0 a1=0 a2=0x298 ra=0x8008F2D4
    s0=0x00000012 s1=0x0000561F
    t0=0x2000FF01 t1=0x8010FEF8

The fresh-build port pair reached title 1024 and hangar 512 in both silent and
Factor 5 image arms. Route, audio-ABI/DMA, and non-target writer controls were
live; image-stage rows were present only in the image arm (4,874), and neither
arm crashed or aborted. Both port arms had target rows with:

    a0=0x801797B0 a1=0 a2=0x298 ra=0
    s0=0x00000012 s1=0x00005622
    t0=1 t1=0

The port `v0`/`v1` sequence advanced normally. Thus
`H-RetailTargetStateDiffers` is selected; `H-RetailTargetStateMatches` is
refuted. `H-RetailTargetOtherWriter` is also refuted for this phase because
all 664 retail target rows were attributed to `0x800078EC`. The result names a
state/setup divergence, not yet its cause or the zero PCM explanation.

The first two oracle attempts were instrument-invalid: one used the
execution-only field dump, and one used watch index 2 although the target was
zero-based index 1. The corrected command used
`--store-field-dump 1:0x800078EC` with both phase buckets.

Evidence: `scratch/agent/s3422_retail_writer_state_join/retail-correct.log`,
`scratch/agent/s3421_m5_writer_state/{silent,image}.log`, and the successful
Debug build.
