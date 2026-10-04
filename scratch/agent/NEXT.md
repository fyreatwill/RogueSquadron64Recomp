# Next work unit: classify the next three M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

The M3 validation prerequisites remain unavailable, so the next runnable
bounded M5 arm is `0x80001AD0`, `0x80001AD8`, and `0x80001AE0`. Keep the retail
oracle and port arms in one run, with title/hangar phase controls and all
passive breadcrumbs. Do not infer an image producer from a writer-PC hit alone.

Competing hypotheses and discriminator:

- H1: at least one candidate is a nonzero producer; its phase-gated writer
  rows have post-store scalar values in `0x165000..0x16C000`.
- H2: candidates write the span but never produce a qualified nonzero scalar;
  they are not the image producer at this scope.
- H3: candidate rows are absent despite positive controls, so these PCs do not
  own the retail target edge; this does not classify other writers.

The discriminator is one paired run using the existing runner pattern:
whole-RDRAM oracle control, title VI 1024, hangar VI 512, oracle shutdown,
phase-gated candidate-span writer rows, and post-value scalar samples for all
three PCs. H1 requires a qualified nonzero post-value sample; H2 requires
writer rows with zero post-value samples; H3 requires zero writer rows after
all controls pass. The positive controls must visibly fire before a null result
is accepted.

Preparation and run:

    cp scratch/agent/run_s3872_m5_remaining_candidate_writers.sh \
      scratch/agent/run_s3873_m5_remaining_candidate_writers.sh
    sed -i '' \
      -e 's#s3872_m5_remaining_candidate_writers#s3873_m5_remaining_candidate_writers#g' \
      -e 's#0x80085898,0x8008589C,0x80066450#0x80001AD0,0x80001AD8,0x80001AE0#g' \
      -e 's#0x80085898|0x8008589c|0x80066450#0x80001ad0|0x80001ad8|0x80001ae0#g' \
      scratch/agent/run_s3873_m5_remaining_candidate_writers.sh
    zsh scratch/agent/run_s3873_m5_remaining_candidate_writers.sh

Record the arm outcome in PORTING-STATE.md and update the candidate list from
the measured result. Kill both processes with SIGKILL as the runner requires.
