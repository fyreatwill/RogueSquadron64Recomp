# M5 Session 4157 — pre-clear writer census

The regeneration-safe `s2190` writer-parity fixup was extended to include
physical `0x1797B0..0x179A48`, title and hangar phase buckets, and the actual
scalar store value. A target-phase writer-control row was also added. The
generated tree rebuilt successfully.

The corrected retail oracle arm passed the whole-RDRAM control (11,830 writes),
title and hangar phase gates, and the target-span watch (1,830 writes). Its
hangar phase recorded 664 writes by `0x800078EC`; the broader writer set also
included `0x80007670`, `0x8001E2C0`, and the `0x8001FAxx` family. The hangar
post-phase snapshot remained zero (`664` bytes, `FNV=0xC0EFD6A5`).

Both paired port retries were route-invalid: each crashed before title in
`spTaskSchedulerThread+9772`, with last guest PC `0x8000834C`. Neither emitted
the target-phase port writer control or target-7 rows. No provenance split is
selected. The retail writer identity is independently qualified, but the
port-side legitimate-versus-mismatching comparison remains open.

ORIGIN: retail target-span writes and the generated scalar-store census; no
guest, audio, wait, cap, predicate, slot, or writeback behavior changed.

Evidence: `scratch/agent/s4157_m5_preclear_writer_census/`.
