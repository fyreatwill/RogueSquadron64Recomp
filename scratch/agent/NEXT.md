# NEXT work unit (s2515) — M5 Step 3: implement one proven image contract edge

HYPOTHESIS-ID: m5-contract-edge

## Context

s2514 audited the stage/DMA mismatch. The stage hook runs before the shared
writeback helper and the generic DMA observer does not retain stage identity.
Ordinal 606 therefore cannot prove same-DMA versus later overwrite. The
image-stage, task, and PCM controls are positive; no mitigation is authorized.

## Single work unit

Choose one proven missing image task/output contract edge from M5 plan Step 3,
using existing source/task-field evidence. Before changing code, name the
guest writer, destination span, legitimacy, and independent retail/port
controls that select it. Build old/new arms together and run one phase-gated
validation capture. If no edge is proven, stop and document why; do not add
more stage/DMA join fields.

## Competing hypotheses and discriminator

- `H-proven-edge`: one selected image contract edge is legitimate and closes
  the task/output/PCM boundary when enabled.
- `H-no-edge`: current evidence does not name a legitimate missing edge, so the
  image arm remains opt-in.
- `H-route-only`: an apparent downstream change is only route/stability drift
  and does not close the task/output contract.

The discriminator is one phase-scoped old/new table containing the selected
writer PC, destination/span, task completion, SP completion, service/slot
progress, and PCM source/consumer identity. A matching legitimate writer and
new downstream contract selects `H-proven-edge`; unchanged controls select
`H-no-edge`; route-only movement selects `H-route-only`.

## Exact commands

```sh
rg -n "data_ptr|output_buff|yield_data_ptr|rs64_m5_pcm_writer|queue_audio_buffer" \
  src/main/main.cpp lib/N64ModernRuntime/librecomp/src/rsp.cpp
rg -n -C 4 "Step 3|Implement exactly one missing" docs/M5-AUDIO-PLAN.md
```

Do not infer a writer from the unresolved stage/DMA observer. Any
mitigation-shaped change requires an `ORIGIN:` line naming a legitimate
writer.
