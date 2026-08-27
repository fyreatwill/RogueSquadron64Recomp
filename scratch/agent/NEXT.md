# NEXT work unit (s2517) — M5: obtain a new independent contract boundary

HYPOTHESIS-ID: m5-contract-edge

## Single work unit

Do not change runtime behavior or add another stage/DMA join field. The s2516
title-phase A/B proved image execution but no legitimate missing edge. Identify
one genuinely new retail-visible contract boundary (writer PC plus destination
span and ordering) that can be paired with an existing port control; if none
is available, stop M5 Step 3 rather than repeating the unresolved observer.
The image arm remains opt-in.

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
writer. The s2514 observer-contract and s2516 title-phase no-edge results are
not evidence for a new writer.
