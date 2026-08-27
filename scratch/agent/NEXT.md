# NEXT work unit (s2582) — M5 Step 1 image/control contract checkpoint

HYPOTHESIS-ID: m5-audio-contract-gap

## Single work unit

Run the existing same-build silent/image Step 1 contract pair, with the
independent retail oracle control, now that the first-task boundary is proven
live. Do not change runtime behavior or task, output, gate, or wait values.
Compare the complete phase-keyed row for silent versus image at title and
hangar.

## Competing hypotheses and discriminator

- `H-AudioDegeneracy`: the real image adds a downstream service, slot, voice,
  or PCM edge relative to the silent control.
- `H-ContractGap`: image DMEM/DMA/return completes but the task/output/PCM
  contract remains unclosed relative to the silent control and retail rows.
- `H-RouteOnly`: image and silent differ only in route reachability or shared
  phase behavior; no image-owned downstream edge appears.

The discriminator is one same-phase table containing dispatch, task fields,
DMEM/DMA, image return/SP completion, service, slot/status, voice/reap, PCM
source/consumer, and route phase for both arms. A new image-only downstream
edge selects `H-AudioDegeneracy`; equal image/stub completion with an open
output/PCM join selects `H-ContractGap`; equal complete rows with only route
variation selects `H-RouteOnly`. Missing oracle whole-RDRAM/title/hangar or
port autopilot/route controls makes the capture unevaluable.

The independent retail whole-RDRAM control must first report at least 10,000
write callbacks and nonzero VI. The port capture is valid only if its table
has the autopilot key presses, an image-dispatch row, and at least one boundary
row; otherwise classify it as unevaluable and do not promote any ABI or gate
interpretation.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2582_m5_step1_contract_pair
```

Use the existing retail oracle positive-control recipe before adding any new
probe. Record the first-task row in `PORTING-STATE.md`; no promotion or
mitigation is authorized from a `Broke` return alone.
