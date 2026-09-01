# M5 Session 3508 — selector-table writer boundary

The first retail capture used the stale `0x00150000..0x00150008` watch. Its
whole-RDRAM control and title predecessor range were positive, but that span
had zero writes and zero post-store samples. The port retry also used a
non-autopilot script and crashed before title in `fillSampleStreamRange`; its
selector result was unevaluable.

The corrected port route used real audio, forced LLE, spin-yield, the validated
autopilot, and `ROGUESQ_STUB_MISSING_FUNCS=1`. It reached title origin
`0x00790400`, fired the selector-load and selector-writer controls, and emitted
1,024 rows at each site without a crash. The live table addresses in those rows
were `0x80149758` and `0x8014975C`, with source classes including
`0x8018DD30`, `0x80171CE0`, and `0x80173B20`.

The corrected independent retail capture kept the whole-RDRAM control positive,
reached 633 title VIs, and recorded 12 writes to physical
`0x00149758..0x00149760`. Post-store sampling saw two values,
`0x80171E70` and `0x80173CB0`; the writer-PC post-value split was
`0x8008F228` and `0x8008F264`. The predecessor range remained live with 30,624
hits. Thus the first measured selector-table boundary is an active retail
writer/value path at `0x80149758`, not the previously assumed `0x80150000`
region.

This selects `H-TableWriterDivergence` at the corrected address and rejects
`H-CaptureInvalid` for the fixed retail and port captures. It does not yet
establish whether the port table is written by a corresponding route, because
the current port witness observes the later table use rather than stores to
`0x80149758`.

Evidence: `scratch/agent/s3508_m5_selector_retail.log`,
`scratch/agent/s3508_m5_selector_retail_fixed.log`,
`scratch/agent/s3508_m5_selector_port.log`, and
`scratch/agent/s3508_m5_selector_port_fixed.log`.

ORIGIN: diagnostic-only oracle memory/PC watches and port selector witnesses;
no table, selector, audio, task, or output value was rewritten, skipped, or
validated.
