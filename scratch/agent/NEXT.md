# Next work unit: classify the next three M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

The M3 validation prerequisites remain unavailable, so the next runnable
bounded M5 arm is the ranked candidate list from CURRENT-TRUTH:
`0x800331D4`, `0x80033414`, and `0x8003326C`. Keep the retail oracle and port
arms in one run, with title/hangar phase controls and all passive breadcrumbs.
Do not infer an image producer from a writer-PC hit alone.

Competing hypotheses and discriminator:

- H1: at least one candidate is a nonzero producer; its phase-gated writer
  rows have post-store scalar values in `0x165000..0x16C000`.
- H2: candidates write the span but never produce a qualified nonzero scalar;
  they are not the image producer at this scope.
- H3: the candidate rows are absent despite positive controls, so these PCs do
  not own the retail target edge; this does not classify other writers.

The discriminator is one paired run using the existing runner pattern:
whole-RDRAM oracle control, title VI 1024, hangar VI 512, oracle shutdown,
phase-gated candidate-span writer rows, and post-value scalar samples for all
three PCs. H1 requires a candidate with a qualified nonzero post-value sample;
H2 requires writer rows with zero post-value samples; H3 requires zero writer
rows after all controls pass. The positive controls must visibly fire before a
null result is accepted.

Preparation and run:

    cp scratch/agent/run_s3865_m5_remaining_candidate_writers.sh \
      scratch/agent/run_s3867_m5_remaining_candidate_writers.sh
    sed -i '' \
      -e 's#s3865_m5_remaining_candidate_writers#s3867_m5_remaining_candidate_writers#g' \
      -e 's#0x80085564,0x8009785C,0x8008556C#0x800331D4,0x80033414,0x8003326C#g' \
      -e 's#0x80085564|0x8009785c|0x8008556c#0x800331d4|0x80033414|0x8003326c#g' \
      scratch/agent/run_s3867_m5_remaining_candidate_writers.sh
    zsh scratch/agent/run_s3867_m5_remaining_candidate_writers.sh

Record the arm outcome in PORTING-STATE.md and update the candidate list from
the measured result. Kill both processes with SIGKILL as the runner does.
