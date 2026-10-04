# Next work unit: classify the next retail candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

Run the paired retail/port candidate-span driver for writer PCs
`0x80004BE8`, `0x80004E74`, and `0x80004E8C`.

Competing hypotheses and discriminator:

- H1: at least one selected PC is a legitimate nonzero producer for the
  candidate image span; its phase-gated post-store scalar sample is nonzero
  with zero mismatch/unsupported evidence.
- H2: selected PCs write the candidate span but are not nonzero producers;
  qualified writer rows exist while all post-target scalar samples are zero.
- H3: selected PCs do not own the candidate edge at this scope; no qualified
  phase-gated writer rows or post-target scalar samples occur.

The discriminator is one paired run containing the whole-RDRAM, title-1024,
hangar-512, oracle-shutdown, port image-DMA, writer-histogram, and post-store
scalar controls. Classify each PC independently; do not promote a per-PC H2 or
H3 result to the remaining candidate set. The same-run positive controls must
show title/hangar phase transitions, oracle completion, and port image-DMA
joins before any zero result is interpreted.

Exact command:

    env PCS=0x80004BE8,0x80004E74,0x80004E8C OUT_NAME=s3880_m5_remaining_candidate_writers zsh scratch/agent/run_s3876_m5_remaining_candidate_writers.sh

The driver must SIGKILL both arms after its watchdog. Captures are written
under `scratch/agent/s3880_m5_remaining_candidate_writers/`.
