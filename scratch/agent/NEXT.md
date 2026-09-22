# Next work unit: classify the qualified DMEM predecessor table

HYPOTHESIS-ID: m5-dmem-predecessor-classification

S3696 fixed the omitted `ROGUESQ_LOG_M5_SOURCE_WRITER` gate and ran the real
audio and silent arms concurrently from one binary. Both reached VI 1024 and
512. The real arm emitted 2,048 DMEM rows and 512 source-range rows; every
sampled DMEM value and source/post-write payload was zero, all source rows had
predecessor sequences, and 139/512 predecessors overlapped the output range.
The silent arm emitted no target DMEM/source rows. The s3695 pre-320 stall is
therefore intermittent, not a stable route gate.

Competing hypotheses:

- `H-ZeroDMEMProducer`: the qualified DMEM writer class legitimately writes
  zero data, so the zero output payload follows directly from that writer.
- `H-DMEMWriterWrongWindow`: the latest predecessor is an unrelated or
  non-overlapping store, and the producer for the output window is elsewhere.
- `H-RetailSourceDifferent`: the port's qualified DMEM path is not the retail
  source path even though its route controls and output writer are live.

Discriminator: obtain independent retail ground truth before any new build,
then run the existing port hooks with `ROGUESQ_LOG_M5_RSP_SOURCE=1` and
`ROGUESQ_LOG_M5_SOURCE_WRITER=1`. The single table must join every sampled
source-range row to predecessor sequence/address/length/kind/value/nonzero/
overlap and payload fields, with both RSP and DMEM positive controls visible.
Stable matching zero writers select `H-ZeroDMEMProducer`; unrelated or
non-overlapping predecessors select `H-DMEMWriterWrongWindow`; a qualified
port table that cannot account for the retail writer/source contract keeps
`H-RetailSourceDifferent` open. Do not add another diagnostic field.
