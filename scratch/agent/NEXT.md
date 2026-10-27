# RESUME: identify the exact stream writer for a dd4 EMPTY row
HYPOTHESIS-ID: g1c-dd8-limit

Checkpoint close-out: s6500 already ran and selected H-writer. Its same-sequence
dd4 EMPTY row had meaningful post-bin bytes but an all-127 stream sample;
cumulative counts narrowed activity to 0x80042DB4 and 0x80042DC0 without naming
the writer for that return. No rerun was performed during this retry.

Resume with exactly one build/run. Extend the regeneration-safe s6500 probe with
per-stream-return writer deltas and last values for all four sites
0x80042DB4, 0x80042DC0, 0x80042EBC, and 0x80042EC4; print them on the matching
`[streamdump] EMPTY` row. Keep the pinned recipe and run
`zsh scratch/agent/s6492_forface.sh` after a Debug build.

Discriminator:

- A delta at one site on the matching row selects that writer as the source of
  the post-bin mutation.
- No delta at any site, with post and stream still differing, selects H-order
  (an uninstrumented writer or call boundary) and requires a new site census.

Positive controls remain mandatory: dd1 nonempty rows and nonzero meaningful
post stores, plus dd4 EMPTY rows with a same-sequence post snapshot. Missing
either control makes the run unevaluable.
