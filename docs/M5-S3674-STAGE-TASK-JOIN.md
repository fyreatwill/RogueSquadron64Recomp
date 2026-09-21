# M5 Session 3674 — joined image stages to live audio task pointers

The stage witness was extended with the live `s_pending_audio_task` data
pointer and size. The corrected concurrent 55-second route used the same LLE,
spin-yield, real-audio, autopilot, and oracle controls as s3671.

Controls passed: the oracle whole-RDRAM watch and title/hangar VI rows fired;
the port reached title `1024 @ 0x790400` and hangar `512 @ 0x6AB400`, emitted
the RSP-source control, 1,041 type-2 ABI/DMA rows, 1,024 source-span reader
rows, 2,024 bounded stage rows, and no crash or abort marker.

For stages 2 and 3, title rows carried `0x80171CE0` in 467/469 and 463/465
rows respectively. The remaining two rows in each stage carried the
interleaved `0x80173B20`. Hangar rows carried `0x80171E70` in 796/797 rows
for both stages; one row per stage carried `0x80171CE0`. The source-span
reader independently carried `0x80171CE0` in title and `0x80171E70` in
hangar, while the retail task dump reported those same dominant phase
pointers.

This selects phase-dominant `H-StageSameTask` and `H-HangarZeroStable` for the
observed stage stream, while refuting a universal stable-selector rule because
the sparse `0x80173B20` title and `0x80171CE0` hangar rows remain. The exact
per-row source-reader join was not established: stage ordinals and source
reader route ordinals were not aligned in this capture. No mitigation or
guest-state change was made.

Evidence: `src/main/main.cpp` and
`scratch/agent/s3674_m5_stage_task_join/{oracle.log,port.log}`.
