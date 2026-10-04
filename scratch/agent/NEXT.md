# Next work unit: classify the next retail candidate-span writer class

HYPOTHESIS-ID: m5-image-task-output-edge

Session 3891 completed the M5 Step 1 same-build silent/image qualification.
The retail whole-RDRAM, title-1024, and hangar-512 controls passed. Both port
arms reached hangar without crash/abort. The silent arm had no image DMEM/DMA;
the image arm changed DMEM, reached break `0x1328`, and issued two
DMEM-to-RDRAM DMAs, but their payloads and the PCM source/consumer joins were
zero. This selects H-ContractGap over H-AudioDegeneracy at this scope.

Competing hypotheses and the discriminating measurement:

- H1: one of the next retail candidate PCs writes legitimate nonzero data into
  the candidate span. The oracle's phase-gated writer/post-value row selects
  H1 only when the same PC has a nonzero post-value sample.
- H2: the candidate PC writes the span but only zero/unchanged data. A
  qualified writer row with zero post-value samples selects H2 for that PC.
- H3: the candidate PC is not a candidate-span producer in title/hangar. No
  qualified writer row or post-value sample, with controls passed, selects H3
  for that PC only.

Discriminator: independent retail whole-RDRAM, title-1024, hangar-512, and
shutdown controls plus phase-gated writer and post-value attribution for the
three PCs in the recipe. Do not infer a global producer absence from one arm.

Exact command:

    zsh scratch/agent/run_s3890_m5_remaining_candidate_writers.sh

Expected outcomes: H1/H2/H3 as defined above. The recipe must use SIGKILL for
cleanup and no mitigation or writeback guard may be added from a zero result.
