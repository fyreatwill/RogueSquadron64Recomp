# NEXT work unit (classify the Factor 5 triangle map discrepancy)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one bounded source audit of the installed Factor 5 triangle path and
the regeneration/fixup source that produces it. Do not build, run, or change
behavior.

Competing hypotheses and discriminator:

- H-map-intentional: the consume-only map is an intentional temporary contract
  and another path emits the geometry.
- H-map-regression: the installed map contradicts the reference and the
  consume-only override is the load-bearing defect.
- H-generated-source: a fixup or generated-source step rewrites the intended
  triangle handler/map, so editing the checked-in RT64 map would be the wrong
  fix location.

Discriminator: trace the complete map-to-handler path and every source/fixup
definition for 0xB4/0xBF, then compare its intended command length and geometry
side effects with the independent reference. A deliberate alternate geometry
producer selects H-map-intentional; an unreferenced consume-only override that
contradicts the reference selects H-map-regression; a regeneration rewrite
selects H-generated-source. No behavior change or mitigation is allowed in
this audit.

Evidence from s844/s845: the phase-gated run reached VI 1024 and produced 392
positive E9 provenance rows. It recorded 112 candidate rows (37 B4, 75 BF;
54 textured), zero draw rows, and zero copy-assert rows. The reference maps
both opcodes to geometry with conditional 8/24-byte totals, while RT64 maps
both to unconditional consume16. The run later hit slotDispatcherIter+872 at
202.8s. No writer/legitimacy claim exists.

Exact execution: use `rg` and bounded `sed` windows to enumerate every
0xB4/0xBF map, handler, fixup, and generated-source definition; compare the
call graph and command-length behavior with `docs/F5-UCODE-REFERENCE.md`.
