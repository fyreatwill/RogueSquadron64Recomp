# Next work unit: classify the next retail candidate-span writer class

HYPOTHESIS-ID: m5-image-task-output-edge

Session 3896 qualified the retail side of the candidate arm. Retail whole-RDRAM,
title-1024, hangar-512, and shutdown controls passed. `0x80004C74`,
`0x80004C88`, and `0x80004C8C` each had 12 title and 29 hangar qualified
writer-PC rows but no post-store scalar attribution or post-target rows. The
paired port crashed before ABI/image-DMA controls at
`spTaskSchedulerThread+9556`, guest PC `0x8000834C`. This selects H2 for these
PCs as single-source retail evidence only.

The current arm to run is `0x80004C90`, `0x80004D00`, and `0x80004D60`.

Competing hypotheses and the discriminating measurement:

- H1: one of `0x80004C90`, `0x80004D00`, or `0x80004D60` writes legitimate
  nonzero data into the candidate span. A qualified writer row plus a
  nonzero post-value scalar sample from the same PC selects H1.
- H2: a tested PC writes only zero/unchanged data. A qualified writer row with
  zero post-value scalar samples selects H2 for that PC.
- H3: a tested PC is not a candidate-span producer in title/hangar. No
  qualified writer row or post-value sample, with controls passed, selects H3
  for that PC only.

Discriminator: one paired run with independent retail whole-RDRAM, title-1024,
hangar-512, and shutdown controls, plus phase-gated writer and post-value
attribution for all three PCs. Do not infer a global producer absence from one
arm. Do not add a writeback guard or other mitigation from a zero result.

Exact command:

    zsh scratch/agent/run_s3896_m5_remaining_candidate_writers.sh

Expected outcomes: H1/H2/H3 as defined above.
