# M5 s3675 — sparse image-stage task exceptions

The qualified concurrent 55-second run passed the oracle whole-RDRAM,
source-span, descriptor, title, hangar, and type-2 controls plus the port
source-hook, phase, ABI, and stage controls. It emitted 1,024 source-span
reader rows and 3,939 bounded stage rows, with no crash or abort marker.

Title stage-2/3 alternate pointer `0x80173B20` occurred at route ordinals 1,
460, and 463. Their stage-2 destinations varied across `0x80167350`,
`0x80166A50`/`0x80166D50`, and `0x80167650`; stage 3 used `0x80178D80`.
Hangar's alternate `0x80171CE0` occurred at ordinal 464, with stage-2
destination `0x80167950` and stage-3 destination `0x80178D80`.

This favors `H-ExceptionRoute` over `H-ExceptionDestination`: title
exceptions occur at distinct route ordinals and do not map to one destination
window. It does not yet distinguish route selection from a stale callback
pointer, because the source-reader and stage witness do not share an exact
event key in this capture. No value was skipped, guarded, or rewritten.

Evidence: `scratch/agent/s3674_m5_stage_task_join/{oracle.log,port.log}` and
`src/main/main.cpp`.

ORIGIN: diagnostic-only stage/task witness; no mitigation was added.
