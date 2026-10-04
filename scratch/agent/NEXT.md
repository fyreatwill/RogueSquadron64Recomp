# Next work unit: classify the next retail candidate-span writer class

HYPOTHESIS-ID: m5-image-task-output-edge

Session 3895 qualified the new candidate arm. Retail whole-RDRAM, title-1024,
hangar-512, and shutdown controls passed. `0x80004AE8`, `0x80004AF0`, and
`0x80004BE8` each had 166 qualified writer-PC rows but no post-store scalar
attribution or post-target rows. Port reached 2,254 image-DMA joins and 2,259
ABI events with zero crash/abort markers. This selects H2 for these PCs only.

The current arm to run is `0x80004C74`, `0x80004C88`, and `0x80004C8C`.

Competing hypotheses and the discriminating measurement:

- H1: one of `0x80004C74`, `0x80004C88`, or `0x80004C8C` writes legitimate
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

    zsh scratch/agent/run_s3895_m5_remaining_candidate_writers.sh

Expected outcomes: H1/H2/H3 as defined above.
