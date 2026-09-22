# Next work unit: join generation-absent source rows to input DMA and task

HYPOTHESIS-ID: m5-audio-source-ownership

S3683 classified the source-centric minority without changing guest state:
title 512/512 same-generation; hangar 282/512 same-generation, 230
generation-absent, 0 reversed. The next unit must identify whether those 230
hangar rows are attached to a distinct selected task or are source records
that never feed an image stage.

Competing hypotheses:

- H-AbsentDistinctTask: a generation-absent source row's input-DMA event
  carries a task pointer/object different from the stage stream's current
  task, selecting a distinct producer/object.
- H-AbsentNoStageConsumer: the source row has no corresponding stage task or
  input-DMA consumer in the target phase.
- H-AbsentPublicationGap: the source generation is present in a later stage
  or task publication, but the current census window misses the join.

Discriminating measurement: retain every source row's generation, task
pointer, source event, and phase; join each generation-absent row to the exact
input-DMA event and live task object in the same run, then report distinct-task,
no-consumer, and later-publication classes. Distinct task selects
H-AbsentDistinctTask; no input-DMA/stage record selects H-AbsentNoStageConsumer;
a later same-generation publication selects H-AbsentPublicationGap. Require
the same positive controls: retail whole-RDRAM, descriptor, source-span,
title, hangar, and type-2 controls plus port phase/source-hook/ABI/DMA/source/
stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3684_m5_absent_source_dma_join.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation.
