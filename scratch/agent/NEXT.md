# NEXT: join post-bin snapshots to dd4 EMPTY stream rows
HYPOTHESIS-ID: g1c-dd8-limit

The s6499 census selected a later stream-path writer for the dd1 EMPTY control,
but the first dd4 EMPTY was seq 268, beyond the 33-row post snapshot budget.
The dd4 arm also emitted 37 crash markers, so its 151 s hold is diagnostic only.

Do exactly one build/run. Extend the regeneration-safe s6499 probe with a
bounded ring of post-bin snapshots keyed by `s6497_seq` (retain at least the
last 64 rows), and log the matching post table when `[streamdump] EMPTY` is
emitted. Add per-PC counts/first-last values for the four stream writers
`0x80042DB4`, `0x80042DC0`, `0x80042EBC`, and `0x80042EC4`. Keep the pinned
recipe and run `zsh scratch/agent/s6492_forface.sh` after a Debug build.

Competing hypotheses and discriminator:

- H-bin: the matching dd4 post snapshot is all 127/sentinel with no meaningful
  bytes. This proves the rasterizer returned no usable span data.
- H-writer: the matching dd4 post snapshot has a meaningful byte, but the
  stream sample is all sentinel/clear; a per-PC writer count identifies the
  responsible stream site.
- H-order: post and stream samples differ without any intervening writer count.
  This would indicate the consumer observes a different call/order boundary.

Positive controls are mandatory: dd1 must produce nonempty rows and nonzero
meaningful post stores; dd4 must produce EMPTY rows with a same-sequence post
snapshot. If either control is absent, call the result unevaluable.
