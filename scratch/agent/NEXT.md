# Next work unit: validate the DMEM task-data boundary fix

HYPOTHESIS-ID: m5-audio-dmem-task-boundary

The runtime now stages the complete declared DMEM task-data window through
`0x0F7F`; the previous length `0xF80 - 1` omitted the final byte immediately
before the OSTask area at `0x0FC0`.

Competing hypotheses and discriminator:

- H1: the missing final DMEM task-data byte is part of the audio task contract;
  the corrected image arm changes the audio task's DMEM/DMA or downstream
  service/PCM row without losing the validated route.
- H2: the byte is padding or otherwise unused; image and silent controls retain
  identical downstream behavior and the corrected byte is never consumed.
- H3: the build/runtime change destabilizes task staging; the corrected image
  arm fails before the qualified title/hangar phases.

The discriminating measurement is one same-build validation run with the
default image and explicit silent control. Require the existing phase, task,
SP-completion, route, and no-crash controls. Select H1 only if the corrected
image reaches title/hangar and shows a task-contract or downstream difference;
select H2 if it is route-equivalent with the positive controls; select H3 on a
pre-target crash or abort.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_M5_TASK_CONTRACT=1 zsh scratch/agent/run_m5_step1_validation.sh
