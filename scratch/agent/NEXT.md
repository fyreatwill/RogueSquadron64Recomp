# Next work unit: classify coverage-aware DMEM producers

HYPOTHESIS-ID: m5-dmem-predecessor-classification

S3697 retail ground truth passed its positive control: the whole-RDRAM watch
reached 10,000 callbacks and was removed, while the target range produced
1,058 writes through the 512-width hangar phase. Retail's phase-gated writer
PCs were `0x800078EC` (768), `0x80007670` (172), `0x8001E2C0` (11), and the
`0x8001F...` family (107). The scalar samples at `0x800078EC` were zero with
zero mismatches. The independent contract is therefore a live retail writer
set, with a legitimate zero-valued scalar member and additional non-scalar or
vector members.

S3696 fixed the omitted `ROGUESQ_LOG_M5_SOURCE_WRITER` gate and ran the real
audio and silent arms concurrently from one binary. Both reached VI 1024 and
512. The real arm emitted 2,048 DMEM rows and 512 source-range rows; every
sampled DMEM value and source/post-write payload was zero, all source rows had
predecessor sequences, and 139/512 predecessors overlapped the output range.
The silent arm emitted no target DMEM/source rows. The s3695 pre-320 stall is
therefore intermittent, not a stable route gate.

S3697's port run selected `H-DMEMWriterWrongWindow` for the latest global
predecessor: 365/512 joined stores did not overlap the output window, while
147/512 overlapped only a two-byte edge. However, the same bounded DMEM census
contains earlier zero vector stores that do overlap the broader
`0xC30..0xE48` output-DMEM union, so the actual producer remains open.

Competing hypotheses:

- `H-ZeroDMEMProducer`: a stable coverage-aware DMEM writer legitimately
  writes zero data across the output-DMEM union, so the zero payload follows
  directly from that writer.
- `H-DMEMProducerAbsent`: no observed DMEM writer covers the bytes emitted by
  the source-range DMA; the zero comes from initialization or a missed DMA.
- `H-RetailSourceDifferent`: the port's qualified DMEM path is not the retail
  source path even though its route controls and output writer are live.

Discriminator: retail ground truth is now available from the positive-control
run above. Before the build, obtain the retail writer contract again if needed;
then add the coverage-aware table in one build and run the qualified
real-audio/LLE-solo/spin-yield/autopilot route with
`ROGUESQ_LOG_M5_RSP_SOURCE=1` and `ROGUESQ_LOG_M5_SOURCE_WRITER=1`. The one
table must cover every sampled source-range row and report, for each output
subrange, the covering predecessor sequence/address/length/kind/value/
nonzero/route plus source and post-write payload, with both positive controls
visible. A stable covering zero class selects `H-ZeroDMEMProducer`; no covering
writer selects `H-DMEMProducerAbsent`; a live class that cannot account for
retail's named writers keeps `H-RetailSourceDifferent` open.
