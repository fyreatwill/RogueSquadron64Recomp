# NEXT: attribute post-bin table changes to a concrete writer
HYPOTHESIS-ID: g1c-dd8-limit

One bounded experiment: extend the passing s6506 invocation-key census with
per-site counts and a post-table diff. Keep DB4, DC0, EBC, and EC4 separate;
for each keyed stream invocation record the four interval counts and the table
bytes at the stream return. Preserve the dd1 nonempty and dd4 EMPTY controls in
one build and one run. Do not change game behavior or add a mitigation.

Competing hypotheses and discriminator:

- H-DB4/DC0: the keyed interval's DB4/DC0 stores explain the matching table
  change; the changed table bytes must overlap the bytes written by those sites.
- H-EBC/EC4: EBC or EC4 writes outside the stream interval explain the change;
  a widened keyed interval or a post-return writer snapshot will show EBC/EC4
  activity tied to the same key.
- H-uninstrumented: none of the four sites accounts for the diff; the post-table
  diff remains nonzero while all keyed site counts are zero, proving a missing
  writer path.

The result must include a positive key-match control, dd1 nonempty rows, and
dd4 EMPTY rows. Build with `cmake --build build --config Debug --target
RogueSquadron64Recomp`, then run `zsh scratch/agent/s6492_forface.sh`.
