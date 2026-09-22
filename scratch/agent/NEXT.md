# Next work unit: distinguish absent-source no-consumer from publication gap

HYPOTHESIS-ID: m5-audio-source-ownership

S3684 classified the source-centric minority without changing guest state:
hangar had 512 source rows, 220 generation-absent, and 0 distinct task
pointers: every absent row used 0x80171E70, which also occurs in the stage
stream. The next unit must distinguish a later publication from a source row
that is never consumed by an image stage.

Competing hypotheses:

- H-AbsentNoStageConsumer: the source row has no corresponding stage task or
  input-DMA consumer in the target phase.
- H-AbsentPublicationGap: the source generation is present in a later stage
  or task publication, but the current census window misses the join.
Discriminating measurement: retain every source row's generation, source event,
task pointer, and route ordinal; compare each absent row against all later
stage generations and all later task publications for the same pointer, then
report later-publication versus no-stage-consumer classes. A later same-pointer
generation selects H-AbsentPublicationGap; no later stage/publication selects
H-AbsentNoStageConsumer. Require
the same positive controls: retail whole-RDRAM, descriptor, source-span,
title, hangar, and type-2 controls plus port phase/source-hook/ABI/DMA/source/
stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3685_m5_absent_publication_join.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation.
