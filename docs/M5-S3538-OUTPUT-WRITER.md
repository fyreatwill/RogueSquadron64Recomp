# M5 Session 3538 — output-writer/order boundary

The independent retail arm passed its whole-RDRAM control (7,175,370 writes),
reached title VI `0x00790400/1024` and hangar VI `0x006AB400/512`, and wrote
nonzero bytes to the PCM ring: `12115/12288`, `760/768`, and `757/768` bytes
were nonzero in the three watched ranges. Retail's target-phase attribution
anchors were live: `0x800078EC` in title and `0x80018F5C`/`0x80018F60` in
hangar.

The same-build real-audio port reached title and hangar with positive phase,
source, consumer, image-stage, and completion controls. It produced 1,024
phase-qualified `[pcm-writer]` rows and 5,104 image-stage joins. Every sampled
output write was an RSP DMA (`kind=2`, `pc=0`) with zero source and destination
payload (`fnv=F59C39C5`, `nz=0`); there were no guest/CPU writer rows. The
joins were `classification=stage-only`, with no source/consumer event and no
ordering violation.

This selects `H-PortMissingWriter` at the nonzero payload-producer edge. The
port does have a DMA write mechanism, but its RSP source is already zero, so
the result is not evidence for a later overwrite. It rules out missing task
completion, an absent target phase, and an invalid retail comparison. No
output state was changed.
