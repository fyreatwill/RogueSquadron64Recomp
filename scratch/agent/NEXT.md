# Next work unit: trace the legitimate clear into the producer handoff

HYPOTHESIS-ID: m5-source-clear-handoff

S3704 selected `H-ClearLegitimateButEarly`: both qualified port arms joined
caller `0x8008F2CC` to the expected `0x801797B0`/`0x298` zero-fill before the
later source/output route ordinals. The real arm's source-DMA payload remained
zero.

Competing hypotheses:

- `H-DifferentProducerObject`: the pre-clear producer writes a different
  object from the one handed to the source DMA.
- `H-ClearTooEarly`: the expected object is cleared before the producer's
  output is consumed or copied.
- `H-ProducerAfterClear`: a later nonzero producer exists but remains missed.

Discriminator: retain the retail writer census, RSP/DMEM controls, and output
rows in one phase-gated port run. Join the `0x8008F2CC` caller's source object
pointer, producer stores, and first output-DMA route ordinal to the clear's
`ordinal=523` snapshot. A producer pointer different from `0x801797B0` selects
`H-DifferentProducerObject`; a same-object producer overwritten before
consumption selects `H-ClearTooEarly`; a later nonzero same-object writer
selects `H-ProducerAfterClear`.

Before building, inspect the existing `0x8008F2CC` caller and the retail
oracle's matching writer PCs. Build once with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through a self-contained paired driver based on
`scratch/agent/run_s3692_m5_input_payload_writer.sh`, preserving all controls.
Kill with SIGKILL after the qualified hangar rows are captured. Expected
splits are different producer object, same-object early clear, or a missed
post-clear writer.
