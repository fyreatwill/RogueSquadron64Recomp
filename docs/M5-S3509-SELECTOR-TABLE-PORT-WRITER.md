# M5 Session 3509 — corrected selector-table port writer

The independent retail preflight used the whole-RDRAM positive control first,
reached title origin `0x00790400` at width 1024, and kept the corrected
physical span `0x00149758..0x00149760` armed. It recorded 8 span writes and
four executions at each selected writer PC. The post-store values were
`0x80171E70` at `0x8008F228` and `0x80173CB0` at `0x8008F264`.

The matching real-image/LLE/spin-yield/autopilot port arm reached title and
hangar, fired the existing selector-load positive control, and fired the new
selector-table-store control. It captured two corrected stores:
`0x8008F228` wrote `0x80171CE0` to `0x80149758`, and `0x8008F264` wrote
`0x80173B20` to `0x8014975C`.

These are two independent lines of evidence for a first value divergence at
the corrected table-writer boundary. `H-PortWriterDivergence` is selected;
`H-PortWriterAbsent` and `H-CaptureInvalid` are rejected at this scope. The
next unresolved edge is the writer input/initializer or selector-index source
that produces the differing values. The port witness is diagnostic-only and
does not rewrite, skip, or validate selector/table state.

Evidence: `scratch/agent/s3509_selector_retail_natural.log` and
`scratch/agent/s3509_selector_port.log`.

ORIGIN: the new witness observes the two guest stores and their register
contexts; it does not alter the table or selector values.
