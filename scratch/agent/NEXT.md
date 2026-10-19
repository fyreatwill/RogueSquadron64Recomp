Single next unit: implement the missing M4 normalized-boundary schema for one
arm (phase epoch, ucode image identity, mapped IMEM PC, and task-local
progress/end observations), then self-test it against the existing retail
capture before any new accumulator comparison.

Competing hypotheses and discriminator:

1. H1: adding image identity and task-local progress makes the port/retail
   accumulator records joinable and the boundary remains stable.
2. H2: the records become joinable but the accumulator diverges only for one
   image/phase/progress class, identifying a live writer boundary.
3. H3: records remain structurally unjoinable or the normalized boundary is
   absent in one arm; no writer or mitigation follows.

Discriminating measurement: one self-test and one existing-capture run must
report nonzero image-identity, mapped-PC, and task-progress rows in both the
retail and port schemas, then either produce normalized joins or explicitly
select H3. Whole-RAM, VI, and mapped-PC positive controls must fire before a
null is interpreted.

Ground-truth gate: use the retail oracle's image/PC/task watches before adding
a port runtime instrument; the runtime cannot witness its own writer.

Read `docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md` and
`tools/analyze_m4_normalized.py` first. Do not build until the oracle schema
and positive controls are identified.

HYPOTHESIS-ID: m4-normalized-boundary-schema
