# NEXT work unit (s2580) — M5 Step 1 image/control contract checkpoint

HYPOTHESIS-ID: m5-audio-destub-step1-contract

## Single work unit

Run the existing paired contract checkpoint from one current build, comparing
the silent `M_AUDTASK` control (`ROGUESQ_AUDIO_UCODE=0`) with the current
default Factor 5 image arm (`ROGUESQ_AUDIO_UCODE=1`). Do not change runtime
behavior or task/output fields.

## Competing hypotheses and discriminator

- `H-AudioDegeneracy`: the silent task arm suppresses a downstream service,
  slot, voice, or PCM transition that the image arm restores.
- `H-ContractGap`: the image task performs DMEM/DMA work and completes but its
  task/output ABI does not close a downstream join.
- `H-RouteOnly`: both arms have the same audio contract rows and any observed
  difference is only route or phase reachability.

The discriminator is one phase-keyed table from the existing script containing
dispatch and exit, task fields/source hash, DMEM changes, DMA/readback ranges,
SP completion, service return, slot/status transitions, voice/reap rows, PCM
source/consumer joins, and title/hangar route phases. Image-only downstream
progress selects `H-AudioDegeneracy`; image DMEM/DMA without a downstream join
selects `H-ContractGap`; equal rows with route differences select
`H-RouteOnly`. Missing oracle or port positive controls makes the row
unevaluable.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2580_m5_step1_contract_pair
```

The paired driver must pass its whole-RDRAM oracle control before launching
the port arms, gate on `PROBE_PHASE_WIDTH=1024`/`PROBE_KEYS_FROM_PHASE=1`, and
use SIGKILL cleanup. Record the row in `PORTING-STATE.md`; no promotion or
mitigation is authorized from a `Broke` return alone.
