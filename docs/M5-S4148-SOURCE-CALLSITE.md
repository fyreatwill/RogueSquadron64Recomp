# M5 Session 4148 — source-construction callsite discriminator

The rebuilt port and independent retail oracle were run together with the
whole-RDRAM positive control, exact `0x800078EC` execution watch, and title
`0x00790400/1024` plus hangar `0x006AB400/512` phase gates. All five route
controls passed.

The regeneration-safe `s2240` fixup annotated all 88 generated `rs_memset`
callsites. Port source-context rows then reported `callsite=0x8008F2CC` in
title and `callsite=0x800AB694` in hangar. The existing generated `r31` field
remained zero and was not used as caller evidence.

The retail oracle independently recorded 7,163,165 executions at
`0x800078EC`, with predecessor rows including `0x8002BEEC`; its whole-RDRAM
control recorded 12,042 writes, the source-span watch recorded 2,042 writes,
and both target phase buckets were nonempty. This is a separate execution
predecessor line from the port's generated-callsite line.

H-retail-port-caller-split is selected at this boundary. The port's direct
callsite identity does not match the retail predecessor family measured by
the oracle, while both routes reach the target phases. This identifies a
caller-context split, not its source-state cause. No guest behavior, audio
wait, cap, predicate, slot state, or writeback mitigation changed.

ORIGIN: the guest `rs_memset` callsites and the retail execution predecessor
at `0x800078EC`; all observed zero stores remain legitimate memset behavior
at the measured port boundary.

Evidence: `scratch/agent/s4148_m5_source_callsite/`.
