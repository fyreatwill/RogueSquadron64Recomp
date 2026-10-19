Single next unit: implement the matching M4 normalized-boundary schema in the
port capture (phase epoch, ucode image identity, mapped IMEM PC, and task-local
progress/end observations), then compare one new port capture with the new
retail RSM2/RSD2 capture. Do not reuse the legacy port log as if it had an image
identity.

Competing hypotheses and discriminator:

1. H1: the matching port fields produce at least 20 shared normalized rows per
   mapped PC and the lane distributions agree.
2. H2: the fields produce shared rows but a repeated lane or writer-PC mismatch
   remains in one image/phase/progress class.
3. H3: the port arm cannot provide an independent image, task progress/end, or
   positive control; no writer or mitigation follows.

Discriminating measurement: one new port run plus the qualified retail capture
must report nonzero image-identity, mapped-PC, and task-progress rows in both
schemas, then either produce normalized joins or explicitly select H3.
Whole-RAM, VI, and mapped-PC positive controls must fire before a null is
interpreted.

Ground-truth gate: use the retail oracle's image/PC/task watches before adding
a port runtime instrument; the runtime cannot witness its own writer.

Read `docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md`,
`tools/oracle/patches/cxd4-m4-normalized-schema.md`, and
`tools/analyze_m4_normalized.py` first. The port arm must expose the same
wire-level fields and pass its own positive controls before comparison.

HYPOTHESIS-ID: m4-normalized-boundary-schema
