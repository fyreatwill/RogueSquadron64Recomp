# Next work unit: M5 de-stubbing Step 1 same-build re-baseline

Run one retail-gated, same-build comparison of the default Factor 5 image arm
and `ROGUESQ_AUDIO_UCODE=0` silent control, following Step 1 of
`docs/M5-AUDIO-PLAN.md`. Do not change the image, wait, cap, predicate, slot
state, or any guest behavior.

HYPOTHESIS-ID: m5-audio-destub-step1-rebaseline

Competing hypotheses and discriminator:

- H-image-contract-complete: the image arm reaches the full task → DMEM/DMA →
  `Broke` → SP completion → service/slot → PCM chain, while the silent arm
  remains a no-write control.
- H-contract-gap: the image arm dispatches and returns but a named downstream
  edge is absent or diverges from the silent control; that missing edge becomes
  the next bounded step.
- H-route-invalid: the retail positive control, either port arm, or
  title/hangar phase is absent; all nulls are invalid.

The single discriminating measurement is one phase-keyed row per arm joining
M_AUDTASK dispatch/exit, task fields and source hash, DMEM/DMA activity, SP
completion, guest service/slot progress, PCM source/consumer, and title/hangar
phase. A complete image chain plus silent no-write control selects
H-image-contract-complete; a qualified missing edge selects H-contract-gap;
missing controls selects H-route-invalid.

Before any build, verify the existing Step 1 switches and driver:

`rg -n 'ROGUESQ_AUDIO_UCODE|audtask-dispatch|audtask-abi|audio-return|PCM_BOUNDARY|AUTOPILOT' src tools scratch/agent --glob '!*.log'`

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the retail oracle first from the oracle recipe with whole-RDRAM positive
control, `--vi-trace`, and title/hangar phase watches. Then run both port arms
from `build/` using the canonical AUTOPILOT, phase gates, LLE/solo/spin-yield
settings, and all task/SP/service/slot/PCM logs; set
`ROGUESQ_AUDIO_UCODE=0` for the silent arm and `1` for the image arm.

Arm `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and
`ROGUESQ_LOG_PCM_BOUNDARY=1` plus the existing dispatch, ABI, DMA, service, and
slot traces. SIGKILL each game after hangar or the phase timeout. Report both
arms' complete rows; do not treat `Broke` alone as proof of contract
completion.
