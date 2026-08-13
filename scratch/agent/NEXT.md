# NEXT work unit (classify the observed Factor 5 candidate dispatch population)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one bounded source-and-reference audit of the s844 0xB4/0xBF dispatch
rows against docs/F5-UCODE-REFERENCE.md and the installed Factor 5 handler map.
Do not build, run, or change behavior.

Competing hypotheses and discriminator:

- H-legitimate-tri: the rows are valid Factor 5 triangle commands whose
  handler should consume payload and emit geometry elsewhere.
- H-garbage-candidate: the rows are non-triangle bytes reached by the parser;
  classify them against command boundaries and source provenance.
- H-misclassified-opcode: the installed map or reference labels 0xB4/0xBF
  differently from the current consume-only interpretation.

Discriminator: every observed opcode/operand pattern must map to the exact
Factor 5 command length and handler, and the reference must agree on whether
it is a geometry command. Agreement selects H-legitimate-tri; boundary or
provenance evidence selecting non-command bytes selects H-garbage-candidate;
map/reference disagreement selects H-misclassified-opcode. No mitigation
without an ORIGIN writer/legitimacy claim.

Evidence from s844: the Debug build passed; the phase-gated run reached VI
1024 and produced 392 positive E9 provenance rows. It recorded 112 candidate
dispatch rows (0xB4/0xBF only), zero draw rows, and zero copy-assert rows,
then hit slotDispatcherIter+872 at 202.8s.

Exact execution: add one regeneration-safe, phase-scoped dispatch diagnostic;
build Debug; run the existing phase-gated recipe from `build/` with the E9
positive control and crash capture enabled; compare candidate dispatch rows to
the draw/assert rows.
