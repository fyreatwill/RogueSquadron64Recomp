# M5 Session 3539 — image-task source-writer census

The first scalar-only build was capture-invalid for the source-writer
question: it reached both target phases and all existing controls fired, but
it saw zero scalar DMEM-source rows. Factor 5 can populate these ranges with
vector stores, so that null did not select an absent producer.

The fixed build added regeneration-safe hooks to the shared scalar and vector
RSP DMEM store helpers. In one real-audio LLE/spin-yield/autopilot run, the
whole-RDRAM/source-DMA/image-stage/PCM controls were live, with two target
phases and 2,048 bounded source-window store rows, all vector stores. Rows
covered both `0x6F0..0x9F0` and `0xCB0..0xE48`; the observed broad DMEM span
had nonzero contents during the vector-store sequence (`span_nz` ranged from
1454 down to 416/480/823 depending on route point), while the subsequent
image-stage snapshots still reported zero source payloads
(`F59C39C5`, `nz=0`) and zero PCM output.

The independent retail arm passed its whole-RDRAM control (10,674 writes),
reached the target run phases, and wrote 384 and 290 bytes in the two watched
source/state ranges. The port had 1,027 source-DMA rows, 11,518 image-stage
rows, 93 PCM-consumer rows, and no crash or abort.

This selects `H-PortSourceOverwritten` at the broad DMEM-span boundary: a
legitimate RSP vector producer is executing in the source-window address
class, but the image-stage source snapshot is zero afterward. It rules out a
missing RSP producer and the scalar-only coverage explanation. The exact
writer/clear ordering for the individual `0x6F0..0x9F0` and
`0xCB0..0xE48` windows remains open because this census records broad
post-store hashes rather than a per-window snapshot at every event. No audio,
PCM, or output state was changed.

Capture logs:

- `scratch/agent/s3539_m5_source_writer_fixed/port.log`
- `scratch/agent/s3539_m5_source_writer_fixed/retail.log`
