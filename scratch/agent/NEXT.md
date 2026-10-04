# Next work unit: classify the next retail candidate-span writer class

HYPOTHESIS-ID: m5-retail-candidate-span-payload

Session 3864 completed the paired arm. Retail controls passed and the
candidate PCs `0x800076A0`, `0x80085890`, and `0x800852D8` had hangar
candidate-span writer rows but no post-target samples. This selects H2 only for
those PCs; the paired port reached hangar with 2,892 image-DMA joins and no
crash/abort.

Competing hypotheses and discriminator:

- H1: the next dominant candidate-span PCs emit legitimate nonzero
  construction payloads in hangar; scalar rows identify the writer and value.
- H2: the next candidate-span writes are zero/metadata construction and no
  nonzero scalar writer exists in the qualified phase.
- H3: whole-RDRAM, title/hangar VI, or oracle shutdown controls fail; the run
  is invalid and no writer conclusion is allowed.

The discriminator is one same-run table using the existing positive controls,
phase-gated candidate-span writer-PC histogram, and scalar rows for the next
dominant PCs from s3864: `0x80085564`, `0x8009785C`, and `0x8008556C`.
H1 requires nonzero scalar stores with zero mismatches; H2 requires valid
controls and no such rows; H3 is selected if any control is absent. Keep the
port arm in the same script and do not add a writeback guard.

Preparation and run:

    # Add run_s3865_m5_remaining_candidate_writers.sh by applying the same
    # bounded runner template as s3864, set OUT to s3865, and replace
    # --post-value-pc with 0x80085564,0x8009785C,0x8008556C.
    zsh scratch/agent/run_s3865_m5_remaining_candidate_writers.sh

The s3863 runner is a reusable baseline; retain its removal of the high-volume
`--watch-pc` stream so the oracle can complete and write its bounded summary.
