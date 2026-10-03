# Next work unit: phase-gated scalar attribution in the candidate image span

HYPOTHESIS-ID: m5-retail-candidate-span-payload

Session 3860 established that the unresolved writer probe was aimed at
`0x141AD0..0x141AF0`, not the candidate image span, and therefore selected no
image-writer hypothesis. The next unit must watch the candidate span itself.
Create one self-contained script by copying the 3857 paired harness, retain
its whole-RDRAM/title/hangar controls, and change the retail arm to watch
`0x165000:0x16C000` with phase-gated post-store samples forced at
`0x80015BC8,0x8000F3A0`. Run both retail and port arms in that one script.

Competing hypotheses and discriminator:

- H1: a legitimate retail stage writer emits nonzero scalar payloads into the
  candidate span during hangar; its writer PC and source/value samples are
  the missing retail producer evidence.
- H2: the candidate-span writes are only zero/metadata construction, so both
  known writer PCs have zero scalar payloads or no hangar-phase stores; the
  image/output edge remains absent at this scope.
- H3: whole-RDRAM, title, hangar, or post-store controls fail; the run is
  invalid and no writer conclusion is allowed.

The discriminator is one same-run table containing positive-control counts,
VI phase counts, candidate-span writer-PC histograms, and scalar
`zero/nonzero/mismatch/unsupported` rows for both PCs. H1 requires nonzero
scalar stores with zero mismatches; H2 requires valid controls and no such
stores; H3 is selected if any control is absent. Do not add a writeback guard:
the observed writer is legitimate only if the payload and destination are
qualified together.

Preparation and run commands:

    cp scratch/agent/run_s3857_m5_retail_writer_provenance.sh scratch/agent/run_s3861_m5_candidate_span_scalar.sh
    # edit only the retail watch range and requested writer-PC list as above
    zsh scratch/agent/run_s3861_m5_candidate_span_scalar.sh

Use the script's SIGKILL watchdog; inspect bounded summaries, not full logs.
