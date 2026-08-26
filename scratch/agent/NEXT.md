# NEXT work unit (s2421) — discriminate the M5 image downstream contract gap

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run one observation-only, phase-keyed contract-gap table using the existing
validated eleven-Start driver and one build. Keep `ROGUESQ_AUDIO_UCODE=0` and
`=1` arms, the repaired shared task-pointer witness, and the retail oracle
whole-RDRAM/title/hangar controls. Join each image DMA completion to the named
service/SP return, slot/status, voice/reap, MORT, and PCM source/consumer rows
at title and hangar. Do not change task data, output ranges, gates, guards,
dispatch, or the image default.

## Competing hypotheses and discriminator

- H-MissingImageConsumer: image DMA/SP completion is real, but no downstream
  slot/voice/PCM row closes against the image task identity.
- H-SharedDownstreamPath: downstream rows exist, but their identity is shared
  or phase-transitioned; a bounded task/phase/event key closes them.
- H-ZeroPayloadLegitimate: zero payloads are legitimate and the downstream
  contract is present despite zero-valued bytes.
- H-ContractTableInvalid: any arm or retail control misses its route/dispatch
  positive control, so no null is interpretable.

The discriminating measurement is a complete row per arm, phase, task ordinal,
and DMA row containing dispatch, task pointer/data pointer, DMEM change, DMA
range, image break/SP return, service return, slot/status transition,
voice/reap, MORT class, and PCM source/consumer identity. A same-key downstream
join selects H-MissingImageConsumer only if the retail and port route controls
pass; a bounded phase-transition/shared key selects H-SharedDownstreamPath;
nonzero downstream completion with zero payload selects H-ZeroPayloadLegitimate.
Missing controls select H-ContractTableInvalid.

## Exact commands

1. `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run the validated driver, preserving its SIGKILL cleanup and oracle gate:
   `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2421_m5_contract`
   (retain the eleven-Start injector added for s2420).
3. Summarize only phase-gated rows from the two arm logs and the oracle log in
   `scratch/agent/s2421_m5_contract/`; do not interpret pre-title nulls.

Expected outcomes: both arms must pass title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and the oracle must pass whole-RDRAM plus both route
controls. If image DMA/SP rows exist but no bounded downstream join closes,
select H-MissingImageConsumer provisionally and leave behavior unchanged.
