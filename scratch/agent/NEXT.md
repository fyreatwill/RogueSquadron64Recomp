# NEXT work unit (s2231) — write the M5 audio de-stubbing plan

HYPOTHESIS-ID: m5-audio-plan

## Work unit

Create `docs/M5-AUDIO-PLAN.md`. Survey every audio stub, trap, gate, early
return, task-field assumption, and MORT boundary currently in force, then
turn the inventory into an ordered incremental de-stubbing sequence. Each
proposed step must name its one behavior change, its positive control, its
phase-gated validation soak, its expected downstream signal, and its rollback
condition. Do not change code, flip `ROGUESQ_AUDIO_UCODE`, enable C88 by
default, or start a soak in this work unit.

Competing hypotheses and the discriminating measurement:

- H-AudioDegeneracy: the silent `M_AUDTASK`/`Broke` path and related gates
  create the recurring wait, slot, PCM, and voice failures. A one-edge change
  should produce a new downstream control (service completion, nonzero PCM,
  or voice-slot progress) without merely changing route reachability.
- H-ContractGap: the dominant defect is an incomplete MusyX task/DMEM/DMA
  contract, so de-stubbing a host return alone will not produce valid output;
  the plan must keep the image arm opt-in until task/output parity is proven.
- H-MixedPipelines: Factor 5 image audio and CPU-side MORT speech are separate
  pipelines, so each requires its own positive control and soak; no single
  audio default can explain both.
- H-GateArtifact: a current gate or trap, rather than a missing implementation,
  suppresses legitimate work. This remains unselected unless an inventory row
  identifies the gate's writer, input, and legitimate retail behavior.

The discriminator is an inventory-to-soak matrix: for every proposed step,
record `M_AUDTASK` dispatch/exit, task-field identity, DMA/readback activity,
service status transition, slot `0x01/0x02/0x00` cycle, PCM source/consumer
join, voice-array/reaping activity, MORT entry, and route phase. A step is
supported only if its same-recipe soak passes the whole-RDRAM/route positive
controls and changes the predicted downstream field; unchanged fields select
H-ContractGap or H-MixedPipelines, while a new control plus the predicted
status/PCM/slot change selects H-AudioDegeneracy. A gate is an actionable
H-GateArtifact candidate only with independent retail writer evidence. A
route-only change is not a de-stubbing result.

## Exact commands

Survey bounded source/doc locations without building or reading large logs:

~~~sh
rg -n -i 'M_AUDTASK|AUDIO_UCODE|aspMain|MusyX|MORT|audtask|RspExitReason::Broke|waitForAnyAudioSlot|voice|PCM|audio|DMA' \
  src lib docs tools | head -400
rg -n 'real_ucode|audtask-dispatch|audio|M5|PCM|voice|slot|service|image|MORT' \
  docs/CURRENT-TRUTH.md docs/PROJECT-OVERVIEW.md | head -300
rg -n 'M_AUDTASK|RspExitReason::Broke|AUDIO_UCODE|MORT|MusyX' \
  src/main src/rsp lib/N64ModernRuntime lib/rt64 | head -300
~~~

Write the new plan with one inventory row per distinct stub/trap/gate and one
validation recipe per de-stubbing step. If a site is only diagnostic or is
already opt-in, label it rather than treating it as a default behavior. The
plan must leave the current default silent path unchanged.
