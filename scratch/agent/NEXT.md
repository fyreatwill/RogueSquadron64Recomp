# NEXT work unit — requalify M5 audio after a route change

HYPOTHESIS-ID: m5-route-after-vi-edge

## Single work unit

Do not repeat the exhausted VI-edge probe unchanged. After an upstream route
change produces a new target-phase control, run the paired phase-keyed M5
Step 1 qualification with image and silent arms in one build/run. If no route
change is available, stop and ask for the specific route-change direction;
do not infer target-phase audio behavior from pre-title rows.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent arm suppresses downstream task/service/slot/
  voice/PCM progress once target phases are reachable.
- `H-ContractGap`: the image arm completes DMEM/DMA but fails a named guest or
  output contract edge, while the silent control does not.
- `H-RouteOnly`: image and silent arms have the same complete downstream row;
  the prior failure was solely route reachability.

## Discriminating measurement

One build must run both arms concurrently with whole-RDRAM/port phase controls.
The decisive row is dispatch → task fields → DMEM/DMA → image exit → SP
completion → service → slot/status → voice/reap → MORT → PCM source/consumer
→ title `1024` / hangar `512`. A same-phase image-only downstream edge selects
`H-AudioDegeneracy` or `H-ContractGap` by the first missing contract join; an
identical complete row selects `H-RouteOnly`. Any row before target phase is
unevaluable.

## Exact commands after the route change

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 zsh scratch/agent/run_s3028_m5_step1_contract_pair.sh
```

Retain the same-run positive controls and SIGKILL cleanup. No gate, wait,
voice, destination, or output change is authorized by a missing row alone.
