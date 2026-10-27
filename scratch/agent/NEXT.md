# NEXT: identify the exact stream writer for a dd4 EMPTY row
HYPOTHESIS-ID: g1c-dd8-limit

The s6500 ring joined dd4 EMPTY seq 269 to a meaningful post table, while the
stream sample was all 127. This selects H-writer, but cumulative counts only
show activity at 0x80042DB4 and 0x80042DC0; they do not identify the writer for
the matching return.

Do exactly one build/run. Extend the regeneration-safe s6500 probe with
per-stream-return writer deltas and last values for all four sites
0x80042DB4, 0x80042DC0, 0x80042EBC, and 0x80042EC4; print those values on the
matching `[streamdump] EMPTY` row. Keep the pinned recipe and run
`zsh scratch/agent/s6492_forface.sh` after a Debug build.

Competing hypotheses and discriminator:

- H-bin: the matching dd4 post snapshot is all 127/sentinel with no meaningful
  bytes. This would prove the rasterizer returned no usable span data.
- H-writer: the matching dd4 post snapshot has a meaningful byte, but the
  stream sample is all sentinel/clear; a per-PC delta identifies the site.
- H-order: post and stream samples differ without any intervening writer delta.
  This would indicate the consumer observes a different call/order boundary.

Positive controls are mandatory: dd1 must produce nonempty rows and nonzero
meaningful post stores; dd4 must produce EMPTY rows with a same-sequence post
snapshot. If either control is absent, call the result unevaluable.
