# Next work unit: isolate the M5 census load that destabilizes image startup

HYPOTHESIS-ID: m5-diagnostic-load-startup

s3805 confirmed the image-only full census is also invalid for a payload join:
the independent oracle passed its whole-RDRAM control and completed, while the
image arm crashed at guest PC `0x8000834C` after the 320-wide phase, before any
target VI or M5 row. The no-census silent control from s3804 reached title and
hangar, so do not repeat another full-census silent arm or another retail join
until the image startup discriminator is qualified.

Competing hypotheses and discriminator:

- H1: a specific M5 census category destabilizes startup; removing that
  category restores the image arm's target phase.
- H2: the common probe/launch path is the cause; all image diagnostic bundles,
  including the no-census control, crash before target.
- H3: the crash is nondeterministic or unrelated to census load; all bundles
  have mixed outcomes without a stable bundle-specific split.

The discriminating measurement is one same-build image-only matrix with three
bundles launched under the same recipe: no M5 census, source/input census only,
and the full M5 census, plus the independent retail oracle. Every arm must
retain phase and crash controls. H1 predicts one bundle reaches title/hangar
while the full bundle crashes; H2 predicts every bundle crashes; H3 predicts
mixed outcomes without a stable bundle-specific split. The oracle whole-RDRAM
control and target-VI controls must fire independently.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_census_startup_matrix.sh

The recipe must keep the existing M5 census variables, phase gate, oracle watch
ranges, positive controls, and SIGKILL cleanup. It must launch all three image
bundles through `tools/probe.sh` from the same build, and must not infer a
writer or retail payload parity from a missing target phase.
