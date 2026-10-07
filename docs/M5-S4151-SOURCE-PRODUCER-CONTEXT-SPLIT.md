# M5 Session 4151 — source-producer context split

The rebuilt port and independent retail oracle ran together for the planned
75-second capture. The oracle whole-RDRAM positive control fired, and both
retail and port reached title `0x00790400/1024` and hangar
`0x006AB400/512`. The port had no crash or abort.

The port source-context control fired in both target phases. Its title rows
used `0x8008F2CC` with `a0=0x80178C80`, `a2=0x298`, and zero values. Hangar
rows used the same clear path and the setup path at `0x800AB694`; the latter
had `a0=0x80165E50`, `a2=0xC`, and zero values. The generated hook reported
`ra=0`, which is not usable caller evidence.

Retail independently recorded 796 writes to the watched source span and
phase buckets for both target origins. Its execution histogram attributed
`0x800078EC` to predecessor `0x8002BEEC` 253 times and attributed the
`rs_memset` entry `0x800078E0` to predecessor `0x800052C4` 1,693 times.

H-producer-context-split is selected at this boundary: the phase-qualified
retail predecessor family differs from the port's regeneration-safe callsite
and argument tuples. This identifies a context divergence, not its cause;
the next probe must join the caller's state fields without treating `ra=0`
as a port caller. ORIGIN: the legitimate guest `rs_memset` store loop and the
retail execution predecessor witness; no guest behavior, audio wait, cap,
predicate, slot state, or writeback mitigation changed.

Evidence: `scratch/agent/s4140_m5_source_context/`.
