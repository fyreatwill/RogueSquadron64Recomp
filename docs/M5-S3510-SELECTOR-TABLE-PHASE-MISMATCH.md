# M5 Session 3510 — selector-table input join phase mismatch

The independent retail oracle passed the whole-RDRAM positive control with
10,010 callbacks and reached 632–633 title VIs. The corrected table span was
live, but both observed stores occurred later at width 1024, origin
`0x006AB400` (hangar): `0x8008F228` stored `0x80171E70` at `0x00149758`, and
`0x8008F264` stored `0x80173CB0` at `0x0014975C`. The oracle writer-field
dump produced zero rows because its phase bucket was not active at those
stores; post-store PC rows provide the independent value/PC evidence.

The rebuilt real-image/LLE/spin-yield/autopilot port reached title origin
`0x00790400`, fired its selector controls, and captured the two stores as
`0x80171CE0` and `0x80173B20`. Its producer, caller, and predecessor controls
also fired. Retail hangar stores and port title stores are not a valid join,
so this run selects no input, initializer, index, or route hypothesis.

The next measurement must phase-match the port store witness to retail origin
`0x006AB400` before comparing writer inputs.

ORIGIN: diagnostic-only oracle and port observations; no table, selector,
audio, task, or output value was rewritten, skipped, or validated.
