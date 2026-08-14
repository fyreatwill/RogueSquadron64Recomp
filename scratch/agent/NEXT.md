# NEXT work unit (s988)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Run one bounded runtime write-origin census for the phase-6 VTXCOLOR payload
range `0x732A10..0x73E3B0`, retaining phase-4 `0x726200..0x726C50` as the
positive control. Instrument the existing RDRAM write/DMA-origin hooks in one
build, phase-gate every record, and run the isolated ungated-LLE recipe with
the established F5-state and shade controls. Land no mitigation.

## Competing hypotheses and discriminating measurement

- H-dma-copy: a DMA or copy path changes the sampled payload.
- H-game-dynamic: a register-relative game store changes the sampled payload.
- H-renderer-state: neither writes after the sampled payload, so zero begins in
  renderer conversion.

Discriminating measurement: phase-gated write-origin records for sampled
addresses, plus the existing F5/shade positive controls. A DMA/copy origin or
guest-PC origin selects its writer class; no post-payload write with controls
firing selects H-renderer-state.

## Exact commands

`rg -n -C 3 'RDRAM|rdram|DMA|do_dma|write' src/main/main.cpp src/main/upstream_compat.cpp`

Build once, then run the existing isolated ungated-LLE capture with the s986
F5-state and shade controls. Phase-gate every new write record; do not use a
stopwatch or add a guard.
