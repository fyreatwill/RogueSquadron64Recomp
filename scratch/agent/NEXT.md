# Next work unit: classify the next adjacent retail candidate-writer class

HYPOTHESIS-ID: m5-retail-candidate-writer-class

The M3 active-queue guard remains source-only because this checkout lacks
`mips64-elf-gcc`/`mips64-elf-ld`; do not add another guard. Continue the
independent M5 writer census at the next bounded adjacent set.

Competing hypotheses:

- H1: one of `0x80004D7C`, `0x80004D84`, or `0x80004E74` writes a qualified
  nonzero target-phase payload in retail.
- H2: the PCs execute or touch unrelated spans, but none writes the qualified
  target buffer during title/hangar phases.
- H3: the port image-DMA route is not phase-equivalent to the retail target
  span, so a retail null is not comparable.

Discriminator: run the new candidate recipe below. Require the retail
whole-RDRAM positive control, title-1024 and hangar-512 VI gates, oracle
completion, and the port hangar gate. H1 requires a named candidate row with
nonzero post-value evidence; H2 is selected by zero candidate rows alongside
the positive controls; H3 is selected only if the port fails its phase gate or
its image-DMA join disappears.

Exact command:

    zsh scratch/agent/run_s3902_m5_remaining_candidate_writers.sh

Do not infer retail corruption from a null row and do not add a mitigation
without naming its writer and establishing value legitimacy.
