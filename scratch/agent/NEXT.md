# Next work unit: classify remaining retail candidate-span writers

HYPOTHESIS-ID: m5-retail-candidate-span-payload

Session 3861 selected the bounded result that `0x80015BC8` and `0x8000F3A0`
are not phase-gated writers of physical `0x165000..0x16C000`: controls passed,
but neither PC appeared in the candidate-span writer table or scalar rows.
Other candidate-span writer PCs remain open; do not infer that the image edge
is absent.

Competing hypotheses and discriminator:

- H1: the remaining dominant candidate-span PCs emit legitimate nonzero
  construction payloads in hangar; scalar rows identify the writer and value.
- H2: the remaining candidate-span writes are zero/metadata construction and
  no nonzero scalar writer exists in the qualified phase.
- H3: whole-RDRAM, title/hangar VI, or post-store controls fail; the run is
  invalid and no writer conclusion is allowed.

The discriminator is one same-run table using the existing positive controls,
phase-gated candidate-span writer-PC histogram, and scalar rows for the top
phase writer PCs from the previous run (`0x80022BB0`, `0x80022BC8`,
`0x80022A04`, plus the highest-count PCs if the harness exposes them). H1
requires nonzero scalar stores with zero mismatches; H2 requires valid controls
and no such rows; H3 is selected if any control is absent. Keep the port arm in
the same script and do not add a writeback guard.

Preparation and run:

    cp scratch/agent/run_s3861_m5_candidate_span_scalar.sh scratch/agent/run_s3862_m5_remaining_candidate_writers.sh
    # change only --post-value-pc to the selected remaining PCs and OUT to s3862
    zsh scratch/agent/run_s3862_m5_remaining_candidate_writers.sh

Use the script's SIGKILL watchdog and inspect bounded summaries, not full logs.
