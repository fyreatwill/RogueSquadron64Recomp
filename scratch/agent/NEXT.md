# Next work unit (s4414): locate the title-side selector family path

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4413's qualified oracle run passed the whole-RDRAM and VI controls and
retained 629/628/691 type-2 task rows in the two title buckets and hangar.
The exact selector `0x80029E78` executed twice only in hangar, with one
retained field row (`branch_selector=0x561F`, `object=0x5622`); it had no
title field row. The title task publication witness remained live, so the
shared-input comparison is blocked by a title-side selector-path boundary.

Competing hypotheses:

- H-title-selector-alternate: title reaches a different PC in the selector
  family, while hangar reaches `0x80029E78`.
- H-title-selector-absent: title task publication bypasses this selector
  family or stops before it, despite live title task rows.
- H-retail-route-boundary: the range/source/task controls fail, so the null
  cannot distinguish an alternate path from an instrument boundary.

Discriminating measurement: one retail-oracle run with whole-RDRAM and VI
positive controls, `--watch-pc-range 0x80029D20:0x80029F20`, the two source
PCs, both direct edges, and `0x80033FCC`, plus phase-keyed task dumps. A
title-range hit at a PC other than `0x80029E78` selects the alternate path;
live title task rows with no title-range hit selects the bypass/absence arm;
missing source/task controls selects the route-boundary arm.

Exact commands:

1. Run one 75-second Rice capture with `--watch-write 0x0:0x800000`,
   `--vi-trace`, phase buckets `0x00790400:1024`, `0x00790800:1024`, and
   `0x006AB400:512`, the verified Start schedule, the range watch above,
   `--watch-pc 0x8009C904,0x8009C950,0x80091BAC,0x80091CB8,0x80033FCC`, and
   `--pc-task-dump 0x80033FCC --pc-task-type 2`.
2. Inspect bounded range-hit and task counts; do not interpret a null unless
   whole-RDRAM, all VI buckets, and source/task controls fired.

Do not repeat caller enumeration or the completed port phase-latch run.
