# M5 s3728 — image-task/output payload boundary

The first paired attempt was invalid because the real arm crashed before
title. The fixed retry removed only the unnecessary task-lifetime logger and
was control-valid. The independent retail oracle passed its whole-RDRAM
positive control with 10,000 writes, reached 1024-wide `0x00790400` and
512-wide `0x006AB400`/`0x006AB800`, and produced 1,148 phase-qualified type-2
task rows.

The valid port retry reached both target phases in both arms. The real arm
produced 1,820 hangar stage-2 rows, 1,818 stage-3 rows, 1,804 joined
output-DMA rows, and 1,830 completion calls. Every joined stage-3 row had
`source_dmem_fnv=762B22A5`, `source_dmem_nz=0`, `fnv=762B22A5`, and `nz=0`;
the destination was valid. Stage 2 was `F59C39C5`/zero in 1,818/1,820 rows;
two early rows had nonzero transform buffers but no matching nonzero stage-3
output. The 268 sampled hangar PCM consumers were all `F59C39C5`/zero. The
silent arm passed controls and emitted no image-stage or image-DMA rows.

This selects `H-ImageProducerZero` at the measured port boundary and refutes
`H-ImageWritebackGap` and `H-ConsumerPayloadGap` for the qualified hangar
stream: no nonzero image-task source/output payload was observed for a
writeback or downstream consumer to lose. The oracle line proves retail
reachability only; retail payload parity remains unmeasured.

ORIGIN: diagnostic-only source/DMEM/output/consumer hashes, route joins, task
completion, and oracle watches. No guest, RSP, task, audio, selector, clear,
writeback, or consumer behavior changed.

Evidence: `scratch/agent/s3728_m5_image_payload/{oracle,real,silent}.log`.
