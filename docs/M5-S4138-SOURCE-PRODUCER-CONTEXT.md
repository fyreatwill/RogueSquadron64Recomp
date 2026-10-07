# M5 session 4138 — source-producer context split

The rebuilt paired capture used an explicit oracle table: watch 0 was the
whole-RDRAM positive control, watch 1 was `0x178C80..0x178F18`, watch 2 was
`0x1798B0..0x179A48`, and watch 3 was task data. Both the retail oracle and
the port reached title `0x00790400/1024` and hangar `0x006AB400/512`; the
port had no crash or abort.

Retail watch 1 recorded 664 stores, 72 nonzero post-value bytes, zero
post-store scalar mismatches, and 29 distinct hangar-phase writer PCs. The
port emitted 1,854 target-phase image rows with zero source payload and 1,841
target-phase rows for the `0x1798B0` DMA payload with zero content. The
positive controls and route gates are therefore valid, and the result selects
H-port-writer-context-split rather than H-route-invalid.

This names a value/context split but does not yet identify the first divergent
caller or source-buffer constructor. No guest behavior, wait, cap, predicate,
slot state, or host writeback was changed. ORIGIN: retail guest source-span
stores and port image-stage/DMA rows; the zero fill is a measured port value,
not a mitigation target.

Evidence: `scratch/agent/s4138_m5_source_producer_context/driver.log`,
`retail_provenance_tail.txt`, `retail.log`, and `port.log`.
