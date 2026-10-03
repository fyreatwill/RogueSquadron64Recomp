# M5 s3776 — writer-setup probe split

## Work unit

The s3775 image-only capture crashed before target after adding the writer-setup
witness. This run compared two image arms from the same Debug build: control
with `ROGUESQ_LOG_M5_WRITER_SETUP=0`, and probe with it enabled, beside the
retail oracle.

## Result

The oracle whole-RDRAM positive control fired (`callbacks=10000`). Both port
arms fired all six family-store controls and the writer-setup input control.
The control arm recorded 5,953 title-VI rows and 679 hangar-VI rows; the probe
arm recorded 5,968 title rows and 729 hangar rows. Thus both reached title
`0x00790400` and hangar `0x006AB400`. Neither emitted a family-edge control,
so that join remains open; this is not a null result for the edge. Neither log
contained a crash or `last-guest-pc` marker before harness SIGKILL cleanup.

This selects H3: the prior pre-target crash was not reproduced in either arm,
so enabling the writer-setup witness is not sufficient to explain it. The
witness is qualified for the next clear-object/I-edge join using the image
arm. This does not establish alternate-object legitimacy or explain the
missing family-edge row.

ORIGIN: the witness only observes existing writer setup; no game value, clear,
allocation, route, or audio gate changed. Evidence is the oracle positive
control plus independent target reach and control rows in both A/B arms.
