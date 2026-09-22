# Next work unit: source-centric generation census for unmatched rows

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3682 added a generation-first stage matcher. The qualified capture
passed controls and produced 442 generation-first stage matches (182 title,
260 hangar), but the stage-first report cannot classify source rows for which
no stage callback arrives. The prior 240-source-row minority therefore remains
source-centric and unevaluable.

Competing hypotheses:

- H-SourceSameGeneration: an unmatched source row's generation is present in a
  later/current stage record, but route/order drift hid the join.
- H-SourceWrongTask: an unmatched source generation is absent from all stage
  records in its phase bucket.
- H-SourcePublicationRace: generation matches, but source and stage event order
  is reversed or publication is observed out of order.

Discriminating measurement: add a source-centric bounded census at source
publication that records each source generation, then at stage publication
classify the source generation as matched, later-only, reversed-order, or
absent without replacing the existing report. A generation match with source
event before stage selects H-SourceSameGeneration; no generation match selects
H-SourceWrongTask; a reversed event order selects H-SourcePublicationRace.
Require the same positive controls: oracle
whole-RDRAM, descriptor, title, hangar, and type-2 controls plus port
phase/source-hook/ABI/DMA/source/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3683_m5_source_centric_generation_census.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation.
