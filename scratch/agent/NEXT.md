# Next work unit: classify the next M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-census

Run the paired retail/port candidate-writer harness with its three candidate
PCs set to `0x800050CC`, `0x800050D0`, and `0x800050D4`. Build the Debug
target first; retain whole-RDRAM, title-1024, hangar-512, oracle-completion,
and passive M5 controls.

Competing hypotheses:

- H1: at least one candidate writes the qualified retail hangar payload.
- H2: candidates execute in the target phase but produce no post-target row or
  scalar sample; this bounded class is not the payload writer.
- H3: candidates do not execute in the qualified target phase; this bounded
  class is not the payload writer.
- H4: a positive control or paired port arm fails, so the census is unevaluable.

Discriminator: all three candidate PCs must be measured in one retail run with
the positive controls passing. Target-phase execution, post-target rows, and
scalar samples split H1/H2/H3; any missing control or port hangar phase selects
H4 and invalidates the census.

Exact preparation and run:

    apply_patch <<'PATCH'
    *** Begin Patch
    *** Update File: scratch/agent/run_s3941_m5_candidate_writers.sh
    @@
    -  --post-value-pc 0x800050C0,0x800050C4,0x800050C8 --post-value-pc-detail \\
    +  --post-value-pc 0x800050CC,0x800050D0,0x800050D4 --post-value-pc-detail \\
    @@
    -grep -a -E '0x800050C0|0x800050C4|0x800050C8|post-store-scalar|post-value|oracle] done|positive-control|origin=0x00(790400|6ab400)' "$OUT/retail.log" | tail -120 > "$OUT/retail_provenance_tail.txt" || true
    +grep -a -E '0x800050CC|0x800050D0|0x800050D4|post-store-scalar|post-value|oracle] done|positive-control|origin=0x00(790400|6ab400)' "$OUT/retail.log" | tail -120 > "$OUT/retail_provenance_tail.txt" || true
    *** End Patch
    PATCH
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3941_m5_candidate_writers.sh
