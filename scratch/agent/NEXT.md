# Next work unit: qualify the image source census against retail ground truth

HYPOTHESIS-ID: m5-single-arm-source-ground-truth

s3804 showed that the paired full census is not a valid source-writer setup:
the probe-launched image arm reached title/hangar, but the full-census silent
arm crashed before title at guest PC `0x8000B650`. A same-build silent arm with
all M5 census variables removed reached title and hangar without a crash. The
independent retail oracle's whole-RDRAM control also fired. Do not repeat a
full-census silent arm.

Competing hypotheses and discriminator:

- H1: the port zero-DMEM chain is an artifact not shared by retail; retail
  source bytes are nonzero while the image arm's joined DMEM/source payload is
  zero.
- H2: retail and port source payloads are both zero at the qualified hangar
  route; the apparent retail difference came from an unjoined phase or range.
- H3: the image census cannot reach the qualified route alone, so the source
  writer remains unevaluable and the next unit must be a narrower probe.

The discriminating measurement is one same-build image-only full census plus
the independent retail oracle, both phase-gated. H1 predicts nonzero retail
source bytes versus the image arm's zero DMEM/RDRAM source payload. H2
predicts zero payload on both sides. H3 predicts no valid image target phase;
the whole-RDRAM and both retail target-VI controls must fire.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_image_source_ground_truth.sh

The recipe must keep the existing M5 census variables, phase gate, oracle
watch ranges, positive controls, and SIGKILL cleanup, but launch only the
image arm through `tools/probe.sh`. Do not add a silent arm or infer a writer
from a missing retail target phase.
