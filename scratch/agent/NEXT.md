# NEXT work unit (s2770) — M5 Step 1 phase-qualified audio-arm re-baseline

HYPOTHESIS-ID: m5-step1-image-vs-silent-contract

## Work unit

Retry the phase-qualified Step 1 pair from the same checked-in build using the
fixed recipe `scratch/agent/s2769_m5_step1/run.sh`, after removing its
`ROGUESQ_M5_C88_VALUE=0` entry so the compiled C88 default is exercised. Keep
the retail oracle whole-RDRAM control and launch silent
(`ROGUESQ_AUDIO_UCODE=0`) and Factor 5 image (`ROGUESQ_AUDIO_UCODE=1`) arms
concurrently with the in-process AUTOPILOT. Do not add instrumentation or a
contract change.

## Competing hypotheses and discriminator

- H-AudioDegeneracy: the silent arm is the cause of downstream failure. The
  image arm must add task completion plus service, slot/voice, or PCM progress
  after the same title/hangar route; a route-only difference rejects this.
- H-ContractGap: the image path does real work but its task/output contract is
  incomplete. The image arm will show nonzero DMEM/DMA and image completion,
  while task-field, service/slot, or PCM joins remain absent or divergent.
- H-MixedPipelines: Factor 5 image audio and CPU MORT speech are independent.
  Image task controls can differ while MORT descriptor/voice and PCM controls
  remain independently unchanged; no single global audio result explains
  both.
- H-GateArtifact: a current gate or safety hatch suppresses legitimate work.
  This is not selected by a counter alone; it requires a same-run writer/value
  and downstream transition, so the Step 1 result should leave it unresolved
  unless those controls appear.

The discriminating measurement is the complete phase-keyed arm row:
`dispatch → task fields/source → DMEM/DMA → image exit → SP completion →
service → status/slot → voice/reap → MORT class → PCM source/consumer →
title/hangar phase`. The oracle whole-RDRAM threshold, title 1024 phase, and
hangar 512 origin are mandatory positive controls. If the controls are absent,
the result is invalid and the experiment must not be interpreted as a null.

## Exact commands

1. `sed -i '' '/ROGUESQ_M5_C88_VALUE=0/d' scratch/agent/s2769_m5_step1/run.sh`
2. `env zsh scratch/agent/s2769_m5_step1/run.sh s2770_m5_step1`
3. Inspect only bounded summaries: `sed -n '1,220p' scratch/agent/s2770_m5_step1/driver.log` and marker counts/tails from the two arm logs.

Expected outcomes: the oracle gate must pass. The silent arm should show
dispatch/return but no image DMEM/DMA activity; the image arm should show
nonzero image DMEM/DMA and `Broke` completion. Downstream differences select
H-AudioDegeneracy or H-ContractGap; identical downstream rows keep the
publication edge unresolved and close this re-baseline without authorizing a
contract change. No build is needed unless the checked-in executable is
missing or stale.
