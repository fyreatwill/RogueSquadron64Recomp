# Next work unit: join source-read ordering to the published task route

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3680 found that all 3,698 stage rows used the current generation and
current route publication, while source rows split 250 exact route matches and
774 generation-only rows. Do not repeat the generation/thread instrument.

Competing hypotheses:

- H-SourceBeforePublish: source DMA reads occur before `rs64_audio_route_prepare`
  publishes the route, then the same task reaches the current stage callback.
- H-SourceWrongTask: source reads carry a route/task identity different from
  the stage task, so the stage's current publication is not the source owner.
- H-DmaPublicationRace: source rows are current but the input-DMA event is
  published or consumed out of order relative to the route publication.

Discriminating measurement: add one publication sequence snapshot to each
source input-DMA row and join each source event to the next stage row by task
generation plus route ordinal/row. Classify source rows as pre-publication,
same-task exact, or different-task, and report source-event-to-stage-event
ordering. Pre-publication rows that join the same task select H-SourceBefore-
Publish; different task identity selects H-SourceWrongTask; current identity
with reversed event ordering selects H-DmaPublicationRace. Require the same
positive controls: oracle whole-RDRAM, descriptor, title, hangar, and type-2
controls plus port phase/source-hook/ABI/DMA/source/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3681_m5_source_publication_join.sh

Use one qualified concurrent capture and SIGKILL cleanup. Parse
`[m5-source-range-reader]` and `[audtask-image-stage-row]` from the new run
directory. Do not alter guest state or add a mitigation.
