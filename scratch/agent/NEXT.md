# Next work unit: audit the A11 wait-for-any-audio-slot idiom class

Session 4121 selected H-A8-trap-live at the qualified title/hangar scope.
Execute exactly one complete A11 census/capture next; do not remove the wait
cap, replace the wait, or force a slot state.

HYPOTHESIS-ID: m5-step9-wait-for-any-audio-slot-class

Competing hypotheses and discriminator:

- H-A11-return-live: the wait entry/return path is live and slot writers reach
  the required terminal states; the guard cap does not fire on qualified work.
- H-A11-suppresses-valid: the cap fires or a qualified valid slot transition
  is lost at the wait path, while retail independently reaches the matching
  wait/slot behavior.
- H-A11-route-invalid: a required positive control or title/hangar phase is
  missing, so wait and guard nulls are unevaluable.

The single discriminating measurement is one complete regeneration-safe A11
source census plus one same-build retail/port phase-gated capture. Enumerate
every `waitForAnyAudioSlot` / `anyAudioSlotActive` entry, loop, cap, return,
and slot `01/02/00` writer. Ask the retail oracle first with whole-RDRAM and
wait/slot execution controls. Retail must reach title and hangar; port must
reach both phases, fire its positive controls, and report task completion.
Any missing control or phase selects H-A11-route-invalid. A cap fire or a
missing qualified terminal transition with retail-valid wait evidence selects
H-A11-suppresses-valid; otherwise select H-A11-return-live. Do not alter the
wait or cap.

Before building, use bounded `rg` searches in the generated tree, fixup
script, and oracle watch configuration to enumerate the full idiom. Use the
qualified route parameters from s4120/s4121:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_M5_C88_VALUE=0 ROGUESQ_AUDIO_UCODE=1`.

Required build:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Required run properties: oracle first, whole-RDRAM positive control, exact
title/hangar VI phase gates, port positive controls, and SIGKILL cleanup.
