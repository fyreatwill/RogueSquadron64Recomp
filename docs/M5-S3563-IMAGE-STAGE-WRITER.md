# M5 Session 3563 — image-stage writer census

The retail oracle could not run: this checkout still lacks the documented
debugger core. No retail null is used as evidence.

The existing image-stage and DMA writer census was run on the validated
standalone real-audio/LLE/spin-yield/autopilot route after a clean build. The
run reached title VI `0x00790400`/1024 at 14.9 seconds and hangar VI
`0x006AB400`/512 at 24.1 seconds. Positive controls were live: image-stage,
image completion, RSP DMA, PCM source/consumer, audio return, downstream
store, and both phase transitions. There was no crash marker before the game
was SIGKILLed.

| phase | image-stage rows | stage-2 rows | stage-3 rows | nonzero stage rows | completion rows | DMA-task rows |
|---|---:|---:|---:|---:|---:|---:|
| title 1024 | 2,131 | 534 | 529 | 16 | 529 | 529 |
| hangar 512 | 4,152 | 1,039 | 1,035 | 0 | 1,048 | 1,035 |

The stage-2 and stage-3 destination rows showed the same zero-valued source
DMEM hashes and zero-valued DMA payload hashes. The corresponding RSP
`dmem_to_rdram` rows were the only observed writer mechanism for the stage
destinations; their payload `nz` was zero. The 16 nonzero title destination
rows were retained preexisting bytes in the destination before the zero DMA,
not output produced by the task. No CPU/guest writer rows fired.

This selects `H-StageWriterMissing` at the current discriminator: the image
task reaches its legitimate DMA writer, but its producer payload is empty.
It refutes a wrong-destination explanation for this run because the DMA
destination agrees with the stage destination and the zero hashes agree at
DMEM, DMA payload, and RDRAM destination. This is single-source port evidence;
the independent retail writer line remains unavailable until the oracle core
is restored.

ORIGIN: diagnostic-only stage, DMA, hash, completion, and PCM observations;
no game state, task field, output, gate, slot, PCM, or writeback behavior was
changed.
