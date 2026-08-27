# NEXT work unit (s2516) — M5 Step 3: implement one proven image contract edge

HYPOTHESIS-ID: m5-contract-edge

## Single work unit

Choose one proven missing image task/output contract edge from Step 3 of
`docs/M5-AUDIO-PLAN.md`, after naming the guest writer, destination span,
legitimacy, and independent retail/port controls. Build old/new arms together
and run one phase-gated validation capture. If no edge is proven, document that
finding and leave the image arm opt-in; do not add more stage/DMA join fields.

## Competing hypotheses and discriminator

- `H-proven-edge`: a legitimate selected edge closes the task/output/PCM
  boundary when enabled.
- `H-no-edge`: current evidence does not name a legitimate missing edge, so no
  behavior change is authorized.
- `H-route-only`: apparent downstream movement is route/stability drift and
  does not close the output contract.

The discriminator is one phase-scoped old/new table containing selected writer
PC, destination/span, task completion, SP completion, service/slot progress,
and PCM source/consumer identity. A matching legitimate writer plus new
downstream contract selects `H-proven-edge`; unchanged controls select
`H-no-edge`; route-only movement selects `H-route-only`.

## Exact commands

```sh
rg -n "data_ptr|output_buff|yield_data_ptr|rs64_m5_pcm_writer|queue_audio_buffer" \
  src/main/main.cpp lib/N64ModernRuntime/librecomp/src/rsp.cpp
rg -n -C 4 "Step 3|Implement exactly one missing" docs/M5-AUDIO-PLAN.md
```

Any mitigation-shaped change requires an `ORIGIN:` line naming a legitimate
writer. The s2514 observer-contract result is not evidence for a new writer.
