# NEXT: apply the qualified safe regeneration repair harness to a fresh copy
HYPOTHESIS-ID: regen-repair-harness

This iteration checked every available image artifact and found no retail
hangar pixel/reference capture. The PNGs are port soak outputs (including the
hangar AB directories); retail/oracle artifacts are logs, tables, or memory
watches. Therefore the M4 H-source thread is closed as unevaluable, not as a
port-vs-retail visual conclusion. The s4649 reconstruction remains valid:
both controls pass and 515 complete triplets / 4,120 lanes have zero
post-VMADH mismatches. See `scratch/agent/s4649_m4_join.md`.

Next work unit: run the already-qualified fixer against a fresh generated
copy, then compare the five behavioral arms and the five known diagnostic-only
tag differences. Do not regenerate over the live external tree.

Competing hypotheses and discriminator for the next unit:

- H1: the vendored fixer is behaviorally equivalent; all five live-only arms
  and the expected diagnostic drift match the s4648 classification.
- H2: the fixer repairs the E088 failure but changes a live arm; at least one
  behavior-changing tag differs from the classification.
- H3: the fresh generation itself is incomplete or malformed; the fixer
  fails, or the target functions/tags are absent before comparison.

The discriminating measurement is one fresh-copy fixer return code plus the
single five-arm tag comparison from `scratch/s4648/classification.md`.
