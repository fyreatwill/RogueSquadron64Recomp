# Next work unit: restore the producer-object join through the fixup path

HYPOTHESIS-ID: m5-source-clear-handoff

S3705 confirmed the clear-to-DMA ordering: the real arm joined the clear at
ordinal 525 and later zero source/output rows at ordinals 669–670. Both arms
reached hangar. The intended writer-setup probe was absent from generated
`funcs_23.c`, so object identity was not measured.

Competing hypotheses:

- `H-DifferentProducerObject`: the pre-clear producer writes a different
  object from the one handed to the source DMA.
- `H-ClearTooEarly`: the expected object is cleared before the producer's
  output is consumed or copied.
- `H-ProducerAfterClear`: a later nonzero producer exists but remains missed.

Discriminator: repair the missing writer-setup injection in the fixup path,
then retain the retail writer census, RSP/DMEM controls, and output rows in
one phase-gated paired run. Join the `0x8008F2CC` allocation result and source
producer stores to the first output-DMA ordinal. A producer pointer different
from `0x801797B0` selects `H-DifferentProducerObject`; a same-object producer
overwritten before consumption selects `H-ClearTooEarly`; a later nonzero
same-object writer selects `H-ProducerAfterClear`.

Before building, inspect the generated-function fixup that should inject
`rs64_m5_writer_setup_state` and verify the retail matching writer PCs. Build
once with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through a self-contained paired driver based on
`scratch/agent/run_s3692_m5_input_payload_writer.sh`, preserving all controls.
Kill with SIGKILL after the qualified hangar rows are captured. Expected
splits are different producer object, same-object early clear, or a missed
post-clear writer.
