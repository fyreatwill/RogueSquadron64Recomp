# Next work unit: separate image-stage source from output/consumer boundary

HYPOTHESIS-ID: m5-image-stage-source-vs-consumer

The s3800 same-build image/silent qualification is complete. Retail passed its
whole-RDRAM control and reached title/hangar. Both port arms reached title
1024 and hangar 512, each passed exact-route and family-edge controls, and
neither crashed or aborted. Image emitted 5,570 image-stage rows; silent
emitted zero. Shared task/return/PCM controls were active in both arms.

Competing hypotheses and discriminator:

- H1: image-stage input/source production is absent or zero before the stage;
  the image-stage consumer is functioning and records the zero payload.
- H2: the image-stage producer runs, but its output/consumer path is the gap;
  source-side rows are valid while destination/consumer publication is absent.
- H3: the apparent difference is instrumentation scope; a same-build control
  shows the stage rows are not arm-specific after joining by task generation.

The discriminating measurement is one same-build image/silent run, phase-gated
at title/hangar, joining each image-stage row by task generation to its source
DMA/input FNV, destination FNV/nz, and consumer-only row. H1 predicts zero or
constant input payload with valid stage/consumer publication; H2 predicts
valid nonzero source rows but missing/invalid destination or consumer rows; H3
predicts equal joined rows after generation alignment. Both arms must pass the
existing exact-route and family-edge controls or the run is invalid.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_image_stage_boundary.sh

The next iteration must first obtain ground truth for the source and
destination ranges from the retail oracle, then write the self-contained
recipe and batch all join fields in one build/run. Preserve the independent
retail control, use SIGKILL cleanup, and do not alter the SP-yield contract.
