# Next work unit (s4412): map the retail hangar selector source path

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4411's qualified oracle run passed the whole-RDRAM and VI controls and
reached title and hangar. It observed title-only `0x80091CB8` and
`0x80029E78` rows, no `0x80091BAC` rows, and live phase-specific task payload
identities including hangar `0x80171E70`. The missing hangar selector row is
now the boundary to repair.

Competing hypotheses:

- H-retail-hangar-selector-live: the qualified hangar source path reaches the
  selector entry or an equivalent callsite, so the prior zero is a watch gap.
- H-retail-hangar-source-only: `0x8009C904`/`0x8009C950` remain live with task
  publication, but no selector entry is reached in hangar.
- H-retail-route-boundary: the source/task arm is absent despite live controls,
  so the comparison remains unevaluable.

Discriminating measurement: one retail-oracle run with whole-RDRAM and VI
positive controls, phase-gated watches for `0x8009C904`, `0x8009C950`,
`0x80029E78`, both direct edges, and `0x80033FCC` task publication. A hangar
source row plus selector row selects H-retail-hangar-selector-live; a hangar
source/task row with no selector row selects H-retail-hangar-source-only; a
missing source/task arm with controls live selects H-retail-route-boundary.

Exact commands:

1. Run one capture following `tools/oracle/README.md` with
   `--watch-write 0x0:0x800000`, Rice, the verified press schedule, `--vi-trace`,
   `--watch-pc 0x8009C904,0x8009C950,0x80029E78,0x80091BAC,0x80091CB8,0x80033FCC`,
   phase buckets `0x00790400:1024` and `0x006AB400:512`, and
   `--pc-task-dump 0x80033FCC --pc-task-type 2`.
2. Inspect bounded counts and first/last rows with `grep -n`; do not interpret
   a null unless whole-RDRAM, both VI buckets, and the source/task arm fired.

Do not repeat caller enumeration or the completed port phase-latch run.
