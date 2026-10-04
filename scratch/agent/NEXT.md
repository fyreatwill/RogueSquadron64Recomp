# Next work unit: M5 Step 1 same-build audio baseline

HYPOTHESIS-ID: m5-audio-step1-baseline

The M3 patch checkpoint is blocked by configuration, not by the ordinary
host build: `PatchesLib` is absent and the Debug game target builds. Do not
add another M3 guard until a human supplies a configured patch target and MIPS
toolchain. The strategic next unit is the M5 design's Step 1 qualification:
compare the explicit silent audio arm with the default Factor 5 image arm in
one build and phase-gated run.

Competing hypotheses:

- H1: both audio arms reach the qualified title/hangar phases and the image
  arm closes the expected task/SP/service/slot/PCM chain.
- H2: both arms reach the route, but the image arm has a specific downstream
  contract gap after its positive DMEM/DMA and completion controls.
- H3: the route or positive controls fail before the target phase, making the
  comparison unevaluable rather than selecting an audio contract gap.

Discriminator: one phase-keyed row must contain, for each arm, M_AUDTASK
dispatch/exit, task fields, DMEM change and DMA ranges, image completion,
SP completion, service return, slot/status transitions, PCM source/consumer
joins, and title/hangar phase. The whole-RDRAM oracle control and port route
control must fire in the same run. H1 is selected only by the complete image
chain; H2 by a qualified route with a named missing downstream edge; H3 by
missing controls or pre-target termination.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s2968_m5_step1/run_fixed.sh

The driver launches silent and image arms concurrently with the same
phase-gated controls, positive M5 markers, and SIGKILL cleanup. Do not change
audio behavior or add another M3 guard in this unit; if the driver cannot
launch from the current build/ROM, record that concrete blocker and stop.
