# Next work unit: qualify image versus silent audio with stable arm controls

HYPOTHESIS-ID: m5-paired-qualification-arm-stability

The s3799 same-build SP-yield validation is complete: both arms reached phase
640 and passed their positive controls. Default preserved the pending request;
request-only consumed it once. Neither reached title or hangar, so the
remaining blocker is elsewhere and the SP-yield contract is not the next
discriminator.

Competing hypotheses and discriminator:

- H1: the image-stage difference is caused by the audio/image arm itself. Both
  image and silent arms reach title 1024 and hangar 512 with positive shared
  task/route/PCM controls; only image produces image-stage/DMA rows.
- H2: the silent arm is unstable before paired target coverage. Image reaches
  target phases and silent misses a required positive control or crashes before
  target; the pair is invalid and no route/audio conclusion is allowed.
- H3: both arms are stable and share target coverage, but image-stage rows are
  absent in both. This moves the boundary upstream of the audio-mode choice.

The discriminating measurement is one same-build image/silent run with
phase-gated shared controls, title/hangar transitions, and image-stage/DMA
rows. A valid result requires positive controls in both arms; otherwise select
H2 and redesign stability rather than comparing route totals.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_paired_qualification.sh

The first command in that work unit is to write the self-contained
`scratch/agent/run_m5_paired_qualification.sh` recipe from the qualified
s3789 image/silent setup, then execute it once; the script must launch both
arms, preserve the independent retail control, phase-gate the comparison, and
SIGKILL all children on exit.

Use SIGKILL cleanup, run from `build/`, and preserve the independent retail
control. Do not revisit launch-order variants or alter the SP-yield contract.
