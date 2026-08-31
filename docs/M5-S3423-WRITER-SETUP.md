# M5 Session 3423 — writer setup versus host entry

The fresh Debug build included a regeneration-safe witness immediately before
the target `jal 0x800078E0` in `allocateSongChannelArray` and at `rs_memset`
entry. It was phase-gated to hangar 512 and retained non-target setup rows as
a positive control.

The first concurrent pair was invalid: both arms hit the known early
`spTaskSchedulerThread+9536` / guest `0x8000834c` crash before M5 controls.
Same-build single-arm retries reached hangar 512 with no crash or abort. Both
silent and Factor 5 image retries fired the setup control and a target row.
Their target setup tuple was:

    edge=0x8008F2CC ra=0 a0=0x801797B0 a2=0x298
    s0=0x12 s1=0x5622 t0=1 t1=0

The corresponding `rs_memset` entry and writer-loop rows retained the same
tuple. Thus the divergence from retail's `s1=0x561F`,
`t0=0x2000FF01`, `t1=0x8010FEF8`, and `ra=0x8008F2D4` is already present at
the guest caller/setup edge. This selects `H-PortSetupStateDiffers` and
refutes `H-HostWrapperStateDiffers` for the observed target call. It does not
identify the earlier producer or explain zero PCM output.

Evidence: `scratch/agent/s3423_m5_writer_setup/image_retry.log`,
`scratch/agent/s3423_m5_writer_setup/silent_retry.log`, and the initial pair
logs in the same directory.
