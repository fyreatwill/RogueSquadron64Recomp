# Next work unit (s4413): compare retail selector inputs and payload families

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4412's qualified oracle run passed the whole-RDRAM and VI controls and
reached title and hangar. Hangar source PCs `0x8009C904` and `0x8009C950`,
selector entry `0x80029E78`, direct edge `0x80091CB8`, and task publication
`0x80033FCC` all fired; `0x80091BAC` remained absent. The next boundary is
the selector's phase-keyed inputs and returned/published payload identity.

Competing hypotheses:

- H-retail-selector-multiplex: selector input stays shared while the selected
  or published payload family changes by phase.
- H-retail-selector-phase-split: selector input/arguments change with phase,
  identifying an upstream phase-specific selector path.
- H-retail-route-boundary: the source/task arm or selector rows are absent
  despite live controls, so the comparison remains unevaluable.

Discriminating measurement: one retail-oracle run with whole-RDRAM and VI
positive controls, phase-gated execution watches for the two source PCs,
`0x80029E78`, both direct edges, and `0x80033FCC`, plus field dumps at the
selector and task PCs. Shared selector input with phase-specific task data
selects H-retail-selector-multiplex; phase-specific selector arguments/data
select H-retail-selector-phase-split; missing source/task rows with controls
live select H-retail-route-boundary.

Exact commands:

1. Run one capture following `tools/oracle/README.md` with
   `--watch-write 0x0:0x800000`, Rice, the verified press schedule, `--vi-trace`,
   `--watch-pc 0x8009C904,0x8009C950,0x80029E78,0x80091BAC,0x80091CB8,0x80033FCC`,
   `--pc-field-dump 0x80029E78,0x80033FCC`, both phase buckets, and
   `--pc-task-dump 0x80033FCC --pc-task-type 2`.
2. Inspect bounded counts and phase-keyed field/task rows with `grep -n`; do
   not interpret a null unless whole-RDRAM, both VI buckets, and source/task
   controls fired.

Do not repeat caller enumeration or the completed port phase-latch run.
