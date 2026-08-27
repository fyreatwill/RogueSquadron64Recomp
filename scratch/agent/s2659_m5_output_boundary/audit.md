# s2659 M5 output-boundary mapping census

## Inputs and controls

This read-only census uses the qualified s2614 and s2619 artifacts. The retail
oracle passed its whole-RDRAM positive control with 23,005 writes, reached
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and recorded 12,288
writes in `0x166450:0x169450` plus 717 writes in `0x1798B0:0x179A48`. The
dominant retail writer for the first span was PC `0x800078EC`; secondary-span
writers included `0x800078EC`, `0x80007670`, `0x8001E2C0`, and
`0x8001FAcc..0x8001FD2C`.

The same-build port passed title and hangar route controls. The image arm had
live image completion and task joins; its DMEM/DMA controls were live. The
silent arm supplied the zero-work control. No behavior, writeback, remap, or
gate was changed.

## Phase/span table

| Phase | Retail writer evidence | Port image DMA destination and payload | Port PCM/MORT evidence | Ordering / interpretation |
|---|---|---|---|---|
| Title `1024 @ 0x00790400` | `0x166450:0x169450`: 12,288 writes overall, dominated by `0x800078EC`; secondary span has the mixed writer PCs above. Retail phase-specific histograms do not connect those PCs to a port object. | Repeated stage-2 DMA writes `0x166450..0x169450` in `0x300`-byte slots, FNV `F59C39C5`, `nz=0`; stage-3 writes `0x1798B0..0x179A48`, FNV `762B22A5`, `nz=0`. Image completion is live. | s2614 has 43 source and 43 consumer rows, with 19/43 nonzero at the evaluated endpoints; s2619's later title recheck has source/consumer rows but `nz=0`. No runtime MORT descriptor-class rows. | DMA completion and PCM joins are observed, but the payload is zero and no guest publication PC is attributed. The two port captures do not establish a stable nonzero source contract. |
| Hangar `512 @ 0x006AB400` | The same retail spans and writer family are observed in the oracle route; no port-equivalent writer PC is identified. | Repeated stage-2 `0x166xxx..0x169xxx` `0x300`-byte writes with FNV `F59C39C5`, `nz=0`; repeated stage-3 `0x1798B0..0x179A48` writes with FNV `762B22A5`, `nz=0`. Image joins classify both destinations as `stage-only`, with no source/consumer match. | s2614 has 43 source and 43 consumer rows, all zero at hangar. No runtime MORT descriptor-class rows. | The image task completes, but no nonzero PCM publication or MORT ordering edge closes. |

## Static/runtime cross-checks

- The image-stage records identify the port writer as Factor 5 image
  `dmem_to_rdram` DMA, not a guest CPU store. Stage 2 rotates through the
  `0x166450:0x169450` ring; stage 3 is fixed at `0x1798B0:0x179A48`.
- Every sampled image-stage payload for both spans has all-zero polarity
  (`nz=0`). This is a positive image/DMA control: the image arm changes DMEM,
  emits DMA, and reaches completion, while the silent arm emits no image
  stage rows.
- The port `pcm-writer` witness reports `kind=2`, `pc=0`, and zero values for
  the ring. This is a host/DMA observation and does not name a guest writer.
- `src/main/main.cpp` contains generic PCM source/consumer joins and task
  capture, but no CPU MORT descriptor-class event or direct static reference
  to the retail writer PC/destination contract. `tools/mort_probe.py` validates
  546 retail MORT descriptors independently; it is not a runtime publication
  witness.

## Hypothesis result

`H-Unmapped` selected. `H-ImageOutputEdge` is plausible because port DMA
destinations overlap the observed retail spans, but it fails the required
legitimate-value and writer-attribution fields. `H-CPU-MORT-Edge` remains
plausible because the retail PC writer is not mapped to the image task, but no
runtime MORT publication row closes that route. `H-ConsumerOnlyGap` is not
selected because the evaluated image payload is zero before the consumer
boundary; the nonzero s2614 title rows are not stable across the later s2619
title recheck and do not identify a producer.

This census rules out a complete retail-to-port mapping, not either pipeline.
It authorizes no writeback, remap, gate change, or mitigation. The next edge
must be a named Factor 5 task/output ABI or CPU-MORT publication boundary with
legitimate payload and ordering evidence.
