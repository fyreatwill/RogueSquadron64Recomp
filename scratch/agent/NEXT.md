# Next work unit

HYPOTHESIS-ID: m5-shutdownaudio-return-boundary

Add a regeneration-replayable, phase-scoped post-body/return marker for
`shutdownAudioEngine`, preserving the existing `s4771-cb` entry and
`s4700-cb` callback-table probes. Rebuild once and run one capture on the
qualified real-audio/LLE/ungated/solo/spin-yield route with title, hangar, SP,
PCM, audio-return, and crash/abort controls. Do not repeat the completed A12
or synth-dedup A/B.

Competing hypotheses:

- H1: the existing helper is misbound or incomplete; a direct return row
  appears after entry and table deregistration.
- H2: teardown reaches an internal non-return path; no direct return row
  appears despite downstream controls.
- H3: the new marker is on an unreachable/generated path; it remains absent
  while the positive controls pass.

Discriminator: ordered entry -> callback-table deregistration -> direct return
rows in one phase-gated run, independently qualified by task/SP, PCM,
title/hangar, and crash/abort controls. H1 selects the return boundary; H2
requires internal-path analysis; H3 requires marker-placement repair. The
prior A12 result is route-neutral and is not repeated.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_S4700_CB=1 ROGUESQ_LOG_S4782=1 ROGUESQ_LOG_M5_CALLBACK_ENTRY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh <shutdown-return-recipe>

Do not start the generated-symbol sweep while this M5 unit is applicable.
