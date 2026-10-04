# Next work unit: M5 declared audio ucode-data staging qualification

HYPOTHESIS-ID: m5-audio-task-contract-staging

The route prerequisite is qualified only for image/LLE-on. Validate the s3977
runtime change that replaces the audio task's unconditional `0xF80` DMEM DMA
with its declared `ucode_data_size` (`0x800` on the qualified task). Run both
arms from one build; keep the legacy arm as rollback, not as a new binary.

Competing hypotheses:

- H1: declared-size staging preserves the image task and route, then changes a
  downstream contract join (DMA/slot/PCM) relative to legacy staging.
- H2: declared-size staging preserves route and task completion but changes no
  downstream join; the over-copy was real but not the missing audio edge.
- H3: declared-size staging loses a positive control or route; the task relies
  on bytes beyond its declared image and the change must be rolled back.

Discriminator: one build and one batched driver must pass the independent
whole-RDRAM positive control, reach VI 1024 and VI 512, and report for both
arms the task fields, exact staging span, image exit/SP completion, DMA ranges,
slot/voice activity, PCM source/consumer joins, and route controls. H1 is
selected only by a downstream join difference with controls intact; H2 by
identical downstream rows with controls intact; H3 by any lost control/route.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3977_m5_task_staging.sh

The recipe must be self-contained, use SIGKILL cleanup, phase-gated
title/hangar controls, and passive M5 markers. It must run the declared-size
arm and `env ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` arm from the same binary.
