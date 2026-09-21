# M5 session 3660 — audio task/source ownership join

The independent retail oracle and same-build port were compared at the
phase-gated audio-task boundary. The initial retail command omitted
`--watch-pc`, so its task dump had zero rows despite 10,000 whole-RDRAM
callbacks. The fixed command registered `0x80033FCC` as both `--watch-pc` and
`--pc-task-dump`; it reached title and hangar, recorded 10,000 whole-RDRAM
callbacks, 1,786 task-PC phase hits, and 1,126 type-2 rows with zero invalid
task pointers.

The port was rebuilt and run with the qualified LLE/spin-yield route. It
reached title `0x00790400`/1024 and hangar `0x006AB400`/512, and emitted 2,171
`audtask-abi`/`audtask-dma-row` rows, 1,024 bounded RSP-source rows, and 39
audio-object frame samples. Every sampled real-arm task used type 2, ucode
`0x80099FE0`, zero output/yield fields, and exited at break PC `0x1328`.

Retail's target task pointer stayed `0x80149470`; its title source descriptor
was `data_ptr=0x80171CE0`, and its hangar descriptor was
`data_ptr=0x80171E70`. The port reproduced those target source pointers in the
corresponding phases, but also interleaved other live descriptors: title rows
used `0x80173B20` and hangar rows used `0x80173CB0`. Port source hashes,
nonzero counts, and DMA source ranges vary by logical task; physical address
alone is not an ownership key. For example, target-phase port rows include
`0x80171CE0` with `data_size=1`, FNV `050C5D40`, and `0x80173B20` with
`data_size=3`, FNV `16638FC0`; hangar rows include `0x80171E70` with FNV
`050C5D73` and `0x80173CB0` with FNV `050C5D67`.

This selects `H-SameLogicalObject` for matching target descriptor rows: the
shared task identity/phase contract is live and the same target object
addresses recur, while interleaved objects have distinct payload/source-DMA
identities. It does not establish that the differing payload is wrong or
identify its writer. `H-CaptureInvalid` is refuted by the retail whole-RDRAM,
title, hangar, and type-2 controls plus the port title/hangar/task controls.
`H-DifferentObject` remains applicable to the interleaved helper rows, not the
matching target rows.

Artifacts: `scratch/agent/s3660_audio_ownership/retail-fixed.log` and
`port.log`. No runtime behavior or mitigation changed.

ORIGIN: diagnostic-only task/source identity comparison; no value was skipped,
rewritten, or guarded.
