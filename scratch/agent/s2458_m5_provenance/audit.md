# s2458 M5 image-consumer provenance

The retail oracle ran first with a whole-RDRAM positive control, exact image
ranges, the hangar origin `0x006AB400`, and execution watches for
`0x8002BEEC`, `0x800078EC`, and `0x8008F2CC`. It recorded 12,661 whole-RDRAM
writes, 1,536 writes in `0x167650..0x167C50`, 1,125 writes in
`0x1798B0..0x179A48`, and 594 hangar-phase `0x8002BEEC` predecessors to the
`0x800078EC` block. The retail `0x8008F2CC` execution count was 6.

The paired qualified port run used one build and concurrent stub/image arms.
The image arm reached 1024-wide title and 512-wide hangar phases, emitted
8,351 image-stage rows and 4,149 completed image joins, all classified
`stage-only`; no PCM consumer or image consumer-only rows were emitted. Its
phase-scoped static `rs_memset` table retained 1,024 rows. In the hangar, the
first row was the generated alternate callsite `0x8008F2CC`, with
`dst=0x801797B0`, `len=0x298`, and active Factor 5 route identity; subsequent
rows were dominated by `0x800052C4`. The image arm therefore selects
`H-PortGeneratedAlternate` at static-callsite scope, not
`H-PortSecondRangeEquivalent`; the active image/task path has no bounded
second-range consumer join.

The stub arm did not reach the target phase and crashed in the VI retrace
thread after width 640, so its missing target-phase rows are a non-result.
The port alternate selection is consequently single-source at the live port
boundary, independently paired with the retail ground truth; it does not
authorize an output remap, task-data change, gate change, or guard.
