# M5 s3738 — port source-span writer census

The same-build capture used the retail oracle, a real-audio port arm, and a
silent `ROGUESQ_AUDIO_UCODE=0` control. The oracle whole-RDRAM watch reached
its positive-control threshold and observed both title (`0x00790400`, width
1024) and hangar (`0x006AB400`, width 512). Both port arms reached those VI
transitions; the real arm emitted source-DMA rows and the silent arm emitted
none.

The phase-scoped scalar-store witness reported 664 title-span stores, all at
guest PC `0x800078EC`, all byte stores, and all zero-valued. It reported no
target-span scalar store after the hangar phase armed. Hangar source-DMA rows
still carried `prev_writer_pc=0x800078EC`, `prev_writer_value=0`, and zero
payload (`FNV=0x762B22A5` / `input_nz=0` for the second source range). The
existing control hook fired in both port arms.

This selects `H-PortEarlierWriterAbsent` for the measured port boundary and
refutes `H-PortWriterUnlogged` for the scalar-store class. It also refutes a
port nonzero-producer-then-clear explanation at this boundary. The writer
`0x800078EC` is a legitimate zero fill observed before the image DMA; this is
origin evidence, not a mitigation authorization. Retail's independent writer
census still shows earlier nonzero writer families (`0x80007670` and
`0x8001E2C0`) absent from this qualified port target-span census.

The instrumentation change resets the producer log budget per numeric VI
phase. The previous lifetime budget could exhaust during title and create a
false hangar null.

Evidence: `scratch/agent/s3738b_m5_port_writer_census/real.log`,
`silent.log`, and `oracle.log`; build completed with
`cmake --build build --config Debug --target RogueSquadron64Recomp`.
