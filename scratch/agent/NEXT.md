# Next: identify audio descriptor writers

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3660 qualified the shared type-2/task/phase contract and found the
target retail descriptors at `0x80171CE0` (title) and `0x80171E70` (hangar).
The port also uses those objects but interleaves `0x80173B20` and
`0x80173CB0` objects with different source hashes and DMA ranges. The source
writer and ownership boundary are still open. Do not compare a reused
physical address without joining the logical task row first. Do not add a
writeback, zero-fill, guard, or game-state forcing.

Next unit: one phase-gated writer-PC census for the four descriptor ranges,
using the retail oracle's task dump as the ground-truth object selector and
the existing port `audtask-abi`, `audio-objects`, and `m5-rsp-source` rows as
the comparison arm. Register `0x80033FCC` with `--watch-pc` and
`--pc-task-dump`; add bounded writer histograms for physical ranges covering
`0x171CE0`, `0x171E70`, `0x173B20`, and `0x173CB0`, plus the whole-RDRAM
positive control. Use title/hangar phase buckets, not elapsed time. Run the
port from `build/` with the qualified LLE/spin-yield/autopilot recipe and the
existing source/object logs.

Competing hypotheses and discriminator:

- H-SameWriter: matching logical task rows and interleaved objects are written
  by one shared producer. Expected: the same writer PC dominates each selected
  physical range within a phase.
- H-PerObjectWriter: descriptor identity selects different producers or
  allocator paths. Expected: writer-PC histograms separate by range/object,
  with the task rows still valid.
- H-CaptureInvalid: range watches or logical selectors fail. Expected: the
  whole-RDRAM control, title/hangar controls, or task rows fail; discard the
  census rather than infer ownership.

Discriminating outcome: a valid run with task rows and positive controls that
shows one writer family versus separated writer families. If the writer
histograms are saturated or no longer phase-selectable, stop and redesign the
table; do not add another isolated counter. M3 `rs_zcfree` remains parked
because its stream+0x24 indirect consumers still need a separate census.
