# NEXT work unit (s989)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Run one bounded macOS target-page write-fault census for phase-6 VTXCOLOR
range `0x732A10..0x73E3B0`, retaining phase 4
`0x726200..0x726C50` as the positive control and retaining the s988 DMA
census. Protect only the pages covering both ranges after RDRAM is captured;
recover each write fault and record fault PC/LR, phase, and overlap.

## Competing hypotheses and discriminating measurement

- H-game-dynamic: generated CPU stores fault on the target pages.
- H-renderer-state: no target-page faults occur after payload capture.
- H-watch-gap: faults occur but cannot be safely recovered or attributed.

Discriminating measurement: phase-gated target-page fault records plus the
existing all-DMA and F5/shade controls. A generated-code fault PC selects
H-game-dynamic; zero target faults with controls firing selects
H-renderer-state only for this process's writable target pages; handler loss
or unrecoverable faults selects H-watch-gap. Land no mitigation.

## Exact commands

`rg -n -C 3 'SIGSEGV|mprotect|RDRAM|rdram|DMA|do_dma|write' src/main/main.cpp src/main/upstream_compat.cpp lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp`

Build once, then run the existing isolated ungated-LLE capture with the s986
F5-state/shade controls and `ROGUESQ_FIX_ZERO_SHADE=0`. Phase-gate every fault
record; do not use a stopwatch or add a guard.
