# Next work unit: retail-grounded source-writer census, next candidate class

HYPOTHESIS-ID: m5-source-writer-census

The concurrent process-topology matrix selected H1 for the M5 route: both
declared-real and declared-silent reached title VI 1024 and hangar VI 512,
while legacy-real still crashed before target phases. Use the newly qualified
declared-real arm for the next bounded retail-grounded candidate class. Do not
infer anything from the legacy arm's pre-target crash.

Competing hypotheses:

- H1: the next candidate class is a legitimate nonzero source writer and will
  be attributed by the retail oracle in a target phase, with a corresponding
  port-side marker.
- H2: the class executes in the target phase but writes zero/metadata only;
  retail attribution will show target-phase stores whose values remain zero or
  whose destination is not the image source span.
- H3: the class is not target-phase-equivalent; retail and/or port will show no
  paired target-phase rows, making the class unevaluable rather than absent.

Discriminator: one same-build run with the retail oracle whole-RDRAM positive
control, title/hangar VI controls, and declared-real port arm. Arm one bounded
candidate class from the next unqualified writer batch using the oracle's
physical watch plus PC attribution and the port's phase-scoped source marker.
H1 requires a retail target-phase writer and matching port-side activity; H2
requires a retail target-phase store with zero/metadata semantics and matching
route phase; H3 is selected if either side lacks target-phase equivalence.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s3941_m5_candidate_writers.sh
grep -nE 'positive-control|origin=0x00790400|origin=0x006ab400|writer-pc-phase|post-store-scalar|pc-task-join|CRASH|ABORT' \
  scratch/agent/s3955_m5_candidate_writers/{driver.log,retail_provenance_tail.txt} | tail -240
```

Retain phase-gated budgets and the retail controls. If the selected class is
not target-phase-equivalent, record it as unevaluable and choose the next
bounded class; do not turn a pre-target failure into a source-writer null.
