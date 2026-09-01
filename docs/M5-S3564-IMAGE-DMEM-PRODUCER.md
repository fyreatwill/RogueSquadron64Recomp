# M5 session 3564 — image-task DMEM producer census

## Work unit

The target-valid standalone image arm was run with one phase-keyed census of
scalar/vector RSP DMEM stores and RDRAM-to-DMEM DMAs overlapping
`0x6F0..0x9F0` and `0xCB0..0xE48`. The retail oracle preflight was unavailable
because this checkout has neither the retail ROM nor its debugger core.

## Result

The arm reached title (`0x00790400`, VI width 1024) and hangar
(`0x006AB400`, VI width 512), with 2,131 title and 4,152 hangar image-stage
rows, 2,048 bounded DMEM writer rows, 4,096 bounded source-window rows, 530
audio returns, and 196 PCM rows. No crash marker appeared before the
deliberate end-of-window SIGKILL.

The DMEM writer census was not empty. It observed vector stores in both target
phases, including stores overlapping both target windows; the sampled broad
DMEM span had nonzero contents during that staging sequence. The source-window
table also observed repeated RDRAM-to-DMEM DMAs overlapping the target
windows. Several copied from the `0x178C80`/`0x178D80` source family with zero
post-copy payload, including the exact `0xCB0..0xE48` stage-3 span and a
`0x6F0` stage-2 span. Later stage-2/3 observations still reported zero DMEM,
zero DMA payload, and matching zero destination hashes.

## Discrimination

This refutes `H-DmemProducerMissing`: legitimate vector stores and DMAs do
reach the target windows. It does not establish that those stores are the
correct image payload; the zero-valued staging DMAs are legitimate observed
writers whose source formation is still unexplained. The active result is
`H-DmemProducerWrong` at the staging/clear boundary, with the next probe
focused on the source and ordering of the zero DMAs. `H-DmemPayloadValid` is
not selected because zero state is observed at both the stage input and its
DMA/destination endpoints. This remains single-source port evidence.

No game state, task field, output, PCM, gate, slot, or writeback behavior was
changed.

The build completed with `cmake --build build --config Debug --target
RogueSquadron64Recomp`. The run log is
`scratch/agent/NEXT_IMAGE_STAGE_WRITER/run.log`.
