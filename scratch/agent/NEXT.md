# NEXT work unit (s2673) — obtain the next independent M5 writer/order edge

HYPOTHESIS-ID: m5-audio-step3-ring-writer-ground-truth

## Work unit

Use the existing independent retail oracle and the qualified port capture to
map the rotating stage-2 PCM ring (`0x166450:0x169450`) to a named writer and
ordering edge. Prefer a ground-truth oracle watch/callsite mapping for the
exact nonzero retail/port addresses; do not change runtime behavior, add
writeback, or repeat the zero task-field census. If the oracle cannot drive the
target phase, record that limitation and do not interpret a narrow null.

## Competing hypotheses and discriminator

- `H-ring-writer`: a named CPU/MORT writer legitimately produces the rotating
  `0x166xxx` PCM payload before the port consumer, and its retail PC/value/order
  can be joined to image completion.
- `H-image-ring-writer`: the Factor 5 image's stage-2 DMA is the legitimate
  writer, with retail and port destination/payload/order agreement.
- `H-ring-unmapped`: neither independent source can provide a legitimate named
  writer plus destination, payload polarity, and completion-to-consumer order.

The discriminator is one table covering every target-phase nonzero/zero ring
window observed in the qualified port arm and every corresponding retail watch
row: address span, writer PC, value/payload polarity, MORT descriptor/type (if
any), image completion event, PCM source/consumer event, and ordering. A
complete CPU writer join selects `H-ring-writer`; a complete image-DMA join
selects `H-image-ring-writer`; otherwise select `H-ring-unmapped`. The oracle
whole-RDRAM watch must fire first as the positive control.

## Exact commands

1. Inspect `tools/oracle/README.md` and the existing qualified driver/recipe
   used for s2671; grep the oracle watch configuration and phase keys before
   changing anything.
2. Use `rg -n "166450|166D50|167050|queue_samples|MORT|mort|pcm" tools/oracle
   src docs scratch/agent/s2671_m5_step1_contract_rebaseline` and read only
   bounded windows.
3. Run one batched oracle/port capture only if the existing ground-truth
   driver can arm the whole-RDRAM positive control and target phase; otherwise
   write the blocker and stop without a runtime build.

Expected: the positive control remains live. Either a named independent writer
and complete order join closes one ring hypothesis, or the ring remains
explicitly unmapped. Do not promote a mitigation from address overlap.
