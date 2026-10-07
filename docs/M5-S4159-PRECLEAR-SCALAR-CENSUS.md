# M5 s4159 pre-clear scalar-store census

The independent retail arm passed the whole-RDRAM positive control (11,830
writes), title VI 1024, and hangar VI 512. Its target span
`0x1797B0..0x179A48` recorded 1,830 writes; the hangar snapshot had 664 bytes
and the qualified earlier snapshot contained nonzero bytes. Retail writer PCs
included `0x80007670`, `0x800078EC`, and `0x8001E2C0`.

The rebuilt port reached both target phases and its census control fired. The
full-intersection scalar-store census captured all 664 stores intersecting the
hangar target span. Every row was a byte store from guest PC `0x800078EC`,
with value zero; no nonzero scalar store was observed. The census budget was
expanded from 512 to 4096 after the first valid run so the complete 664-row
clear loop was captured.

Selection: H-port-scalar-writer-omitted. This closes only the generated guest
byte/halfword/word-store class; it does not identify the earlier legitimate
port state seen by the pre-clear snapshot. The next discriminator must cover
host/DMA or another non-scalar RDRAM writer before `0x800078EC`.

ORIGIN: retail source-span writes and the guest scalar-store hook; zero port
values were observed, not suppressed, and no guest/audio/wait/cap/predicate/
slot/writeback behavior was changed by the probe.

Evidence: `scratch/agent/s4159_m5_preclear_span_census/`.
