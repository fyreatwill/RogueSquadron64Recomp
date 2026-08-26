# NEXT work unit (s2420) — run the complete same-build M5 contract checkpoint

HYPOTHESIS-ID: m5-step1-contract-checkpoint

## Work unit

Run the M5 plan's Step-1 same-build stub/image validation checkpoint. Keep the
new shared task-pointer witness and all existing phase, task, DMA, service,
slot, voice, MORT, and PCM observations unchanged. Build one binary, launch
the stub and image arms from the same build in one controlled capture sequence,
and do not change runtime behavior, task data, dispatch, gates, or output.

## Competing hypotheses and discriminator

- H-ImageContractProgress: image arm passes route, task, DMEM/DMA, SP
  completion, service, slot/voice, and PCM controls beyond the stub baseline.
- H-ContractGap: image arm performs task/DMEM/DMA work and exits, but a named
  downstream contract row remains absent while route controls pass.
- H-StubRouteOnly: stub and image differ only in route reachability or phase
  timing, with no image-specific downstream signal.
- H-CheckpointInvalid: either arm misses its route/dispatch positive control;
  no null is interpretable.

The discriminator is the complete phase-keyed validation row for both arms:
dispatch, task fields/source, DMEM/DMA, image exit, SP completion, service,
status/slot, voice/reap, MORT class, PCM source/consumer, and route phase. Both
arms must pass title and hangar controls, and the image arm must pass its task
and SP-completion controls. A missing control selects checkpoint-invalid, not
a missing writer; zero-valued payloads remain non-provenance.

## Exact commands

Use one build and the existing phase-gated driver with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1`, retaining title/hangar markers and the independent task
controls. Capture both `ROGUESQ_AUDIO_UCODE=0` and `=1` arms under
`scratch/agent/s2420_m5_contract/`, killing each game with SIGKILL. Expected
retail reference remains title `data_ptr=0x80173B20`, hangar
`data_ptr=0x80173CB0`, task pointer `0x80149470`; use observed port values.
