# Next work unit: classify the immediate retail zero writer

HYPOTHESIS-ID: m5-source-writer-census

The concurrent process-topology matrix selected H1 for the M5 route. The
`0x800C825C` predecessor was then unevaluable: retail controls and both port
target phases passed, but the predecessor had zero target-phase rows. The same
run showed `0x800078EC` making 816 source-span scalar stores, all zero with
`mismatch=0`; classify that immediate writer next. Use the qualified
declared-real port arm only; do not infer anything from legacy-real.

Competing hypotheses:

- H1: `0x800078EC` is the legitimate target-phase source writer and its zero
  stores explain the port zero payload; retail scalar rows pair with the
  source-span phase and port source-stage rows.
- H2: it writes zero only in metadata/adjacent context; its scalar rows are
  real but do not overlap the target source span or target phase.
- H3: the apparent writer is not target-phase-equivalent; the scalar rows are
  from another phase/route and cannot explain the port source span.

Discriminator: one same-build run with the retail oracle whole-RDRAM positive
control, title/hangar VI controls, and declared-real port arm. Arm
`0x800078EC` as the primary post-store PC and retain `0x800C825C/0x800078E0`
for context. H1 requires phase-gated scalar zero stores overlapping the retail
source span plus matching port source-stage activity; H2 requires stores
outside that span/phase; H3 is selected if the retail rows and port route are
not phase-equivalent.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s3941_m5_candidate_writers.sh
grep -nE 'positive-control|origin=0x00790400|origin=0x006ab400|writer-pc-phase|post-store-scalar|pc-task-join|CRASH|ABORT' \
  scratch/agent/s4057_m5_predecessor_census/{driver.log,retail_provenance_tail.txt} | tail -240
```

Retain phase-gated budgets and the retail controls. If the selected class is
not target-phase-equivalent, record it as unevaluable and choose the next
bounded class; do not turn a pre-target failure into a source-writer null.
