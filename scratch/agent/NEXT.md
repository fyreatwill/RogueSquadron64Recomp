# NEXT work unit (s2579) — M5 audio de-stubbing design

HYPOTHESIS-ID: m5-audio-destub-design

## Single work unit

Create `docs/M5-AUDIO-PLAN.md`. Survey every audio stub, trap, gate, and
default-off arm currently in force, then define an incremental de-stubbing
sequence. For each step specify the code surface, expected contract, positive
controls, phase-gated soak recipe, and promotion/rollback criterion. Do not
change runtime behavior in this design-only unit.

## Competing hypotheses and discriminator

- `H-complete-audio-gate-map`: all behavior-changing audio stubs and gates can
  be located in the current tree and classified by contract.
- `H-hidden-audio-gate`: at least one active gate is outside the obvious audio
  callback/task paths and needs a broader call/queue search.
- `H-contract-uncertain`: a stub is visible but its data-flow is not sufficient
  to define a safe promotion checkpoint.

The discriminator is one inventory table covering each stub/trap/gate, call
site, current default, data contract, and independent positive control. A
complete table plus staged validation sequence selects the design; any
unclassified active path selects a broader source/queue audit before code.

## Exact commands

```sh
rg -n -i 'audio|aspMain|M_AUDTASK|MusyX|MORT|queue_audio|audio_data|waitForAnyAudioSlot|audio.*stub|Broke' src lib tools patches
rg -n -i 'audio|aspMain|M_AUDTASK|MusyX|MORT|queue_audio|audio_data|waitForAnyAudioSlot|audio.*stub|Broke' docs/CURRENT-TRUTH.md docs/PROJECT-OVERVIEW.md
```
