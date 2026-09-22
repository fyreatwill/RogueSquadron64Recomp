# Next work unit: generation-first source/stage diagnostic join

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3681 found 784 source rows one publication behind the route and before
the same-generation stage, but 240 source rows had no same-generation stage
row. The current matcher requires route ordinal/row equality before falling
back to task-pointer history, so it cannot classify that minority.

Competing hypotheses:

- H-SourceSameGeneration: the 240 rows belong to the same task generation and
  only route ordinal publication drift prevents the current exact join.
- H-SourceWrongTask: the 240 rows have a task generation that does not match
  any stage row, so the source belongs to another task.
- H-SourcePublicationRace: generation matches, but source and stage event order
  is reversed or publication is observed out of order.

Discriminating measurement: add a diagnostic-only generation-first matcher in
`audio_image_match_source_locked`, retaining the existing exact route match and
pointer fallback as separate classes. Report source generation, stage
generation, source event, stage event, and route identities for the new class.
Generation match with source event before stage selects H-SourceSameGeneration;
no generation match selects H-SourceWrongTask; a reversed event order selects
H-SourcePublicationRace. Require the same positive controls: oracle
whole-RDRAM, descriptor, title, hangar, and type-2 controls plus port
phase/source-hook/ABI/DMA/source/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3682_m5_generation_first_join.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation.
