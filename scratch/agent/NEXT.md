# Next work unit: implement the normalized M4 boundary sampler
HYPOTHESIS-ID: m4-shared-boundary-revisit

The offline design is in `docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md`.
Implement one regeneration-surviving, batched sampler in both arms, then run
the retail oracle and port concurrently on the keyed hangar route. Do not use
raw framebuffer origin or implementation-local task serial as a join key.

Competing hypotheses:

* H1: normalized `(phase_epoch, ucode_overlay_id, mapped_imem_pc,
  progress_bucket)` rows match, including transient lane distribution and zero
  task-end masks.
* H2: at least 20 shared rows per mapped PC exist but lane or writer-PC
  distributions differ repeatedly; then identify the exact writer.
* H3: any required normalized field or positive control is absent, or fewer
  than 20 shared rows exist; keep the thread parked.

Discriminator: one run must pass whole-RDRAM, VI, and mapped-PC controls and
produce at least 20 rows per mapped PC in both arms. A row joins only on the
four normalized fields above. H1/H2 are selected by the explicit distribution
rules in the design document; missing controls or rows selects H3.

Before building, inspect the existing cxd4 record format and Factor 5 generated
task-end hook so the new fields are real observations, not stage labels.
