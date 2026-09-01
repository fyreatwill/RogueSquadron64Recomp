# M5 Session 3569 — zero-DMEM-payload producer census

The first two attempts were invalid: one stopped at VI 640 because the
validated route flags were incomplete, and the next omitted `ROGUESQ_LOG_ALL=1`
so route-gated census rows were absent. The final run used
`ROGUESQ_AUTOPILOT=1`, `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`,
LLE-solo, and `ROGUESQ_LOG_ALL=1`, from `build/`, then was killed with SIGKILL.

Positive controls fired: title VI 1024 at `0x00790400`, hangar VI 512 at
`0x006AB400`, two RSP-source controls, two DMEM-store controls, 512
source-range writebacks, 1,355 source-window store rows, and 6,995
source-window DMA rows. No crash marker appeared before deliberate kill.

For hangar ordinals 668 onward, each image-task sequence performed vector
stores overlapping DMEM `0xCB0` and `0x6F0`, but the exact DMEM window hashes
stayed zero. The corresponding `dmem_to_rdram` writebacks to
`0x1797B0..0x179930` had `payload_nz=0` and `post_nz=0`. No target-phase
preclear or static `rs_memset` rows fired. The ordering is therefore a
nonproductive store path followed by a zero writeback, not a productive
CPU/vector producer.

This selects `H-DmemPayloadClearOrStale` at the current discriminator and
refutes `H-DmemPayloadCpuStore` and `H-DmemPayloadVectorStore` as productive
producers. The remaining boundary is the source DMA's upstream RDRAM
writer/data source; this detailed result is port-only.

The independent retail oracle passed its whole-RDRAM positive control
(10,674 writes) and observed 674 writes in the watched source span, including
384 from guest PC `0x800078EC`. This independently establishes live retail
source-span activity, but does not attribute the port's zero payload.

ORIGIN: diagnostic-only census; the existing image-task DMA writeback carries
zero bytes and is not legitimate content for this contract. No game state,
output, PCM state, or DMA behavior was rewritten.
