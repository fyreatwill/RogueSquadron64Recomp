# NEXT: distinguish rasterizer no-fill from a later table overwrite
HYPOTHESIS-ID: g1c-dd8-limit
s6498: the existing instrument captured 25 dd4 EMPTY stream rows. They had
seq==ret, in-range bounds and in-range first/last store addresses, but an
all-127 table sample. Both arms reached mission and held cleanly.

Hypotheses:
- H-bin: the rasterizer's in-range integer loop writes no meaningful span bytes
  (or only the 127 sentinel) despite valid polygon bounds.
- H-writer: a later clear/overwrite changes a populated table back to all 127
  before stream consumption.
- H-order: the stream consumer observes the table before rasterizer completion;
  this is expected to be weakened if the post-return sample differs from the
  stream sample in the same synchronous call chain.

Do exactly one build/run: add a regeneration-safe probe that counts every
span-table store and records the first/last stored byte, plus a table sample at
rasterizer return, then build Debug and run
`zsh scratch/agent/s6492_forface.sh` (pinned dd1/dd4, 150 s). Do not change
the arm recipe. Positive controls: dd1 nonempty rows, nonzero store counts,
and a post-rasterizer sample that matches its nonempty stream row.
Discriminator: dd4 EMPTY with zero meaningful stores and all-127 post-return
sample selects H-bin; a non-127 post-return sample followed by all-127 at
stream selects H-writer; a mismatch before stream with no intervening writer
selects H-order. If the post-return sample is unavailable, call the result
unevaluable rather than infer a null.
