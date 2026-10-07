# M5 Session 4150 — source-construction setup state matched

The rebuilt port and independent retail oracle were run together for 75
seconds with a whole-RDRAM positive control and title `0x00790400/1024` plus
hangar `0x006AB400/512` phase gates. All five controls passed; the port had no
crash or abort.

The port's regeneration-safe setup probe fired in both target phases. Its
title clear tuple was `destination=0x801797B0`, `length=0x298`,
`s0=0x12`, `s1=0x561F`, `t0=1`, `t1=0`. Retail's setup-PC rows independently
showed the same destination and state family at the `0x8008F2A8/BC/C0/C4/C8`
chain, with predecessor `0x80001C90`.

The new hangar probe fired at `0x800AB68C/690 -> 0x800AB694`. Its dominant
tuple was `a0=0x80165E50`, `length=0xC`, `s0=0`, `s1=0x800D0000`,
`t0=t1=4`. Retail independently showed the same tuple at
`0x800AB694`, with predecessor `0x800AB690`, across the hangar phase.

H-shared-source-state is selected at the measured setup boundary. This rules
out the repaired setup-state probe as the explanation for the zero source
payload; it does not explain the later `0x800078EC` producer divergence.
The source span remains zero on the port, so the next boundary is the
source-construction producer/call-context join.

ORIGIN: setup arguments and state are legitimate guest values observed by the
port probe and the retail oracle; no guest behavior, audio wait, cap,
predicate, slot state, or writeback mitigation changed.

Evidence: `scratch/agent/s4150_m5_source_setup/`.
