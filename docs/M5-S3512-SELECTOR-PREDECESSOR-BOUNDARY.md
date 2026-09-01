# M5 Session 3512 — selector predecessor boundary

The independent retail oracle was run with a whole-RDRAM positive control and
the corrected selector-table physical watch. The control reached 10,010
callbacks, the selector span recorded 10 writes, and the writer histogram
identified five stores each at `0x8008F228` and `0x8008F264` during the
hangar-qualified run.

The first candidate predecessor arm watched function entry `0x8008F0A0` and
the pre-store boundary `0x8008F1F0`, with a 512-wide `0x006AB400` phase gate.
Both exact watches and a corrected whole-function PC range produced zero
execution rows, while the two store PCs remained live. The second candidate
watched caller `0x80091934`, the static callsite that loads `a1` before
entering `0x8008F0A0`; it also produced zero phase-gated execution rows. The
port run independently passed the host positive control, reached title and
hangar, and captured the existing pre-allocate row with `a1/s1=0x00005622`,
plus the title stores. It did not re-enter this initializer in hangar, so no
cross-runtime predecessor join is valid.

This selects `H-CaptureInvalid` for the proposed predecessor measurement, not
for the retail store observation: the store control is positive, but the
candidate predecessor callbacks are absent in the same qualified retail run.
It rules out treating the zero predecessor rows as evidence for parity,
divergence, or a later mutation. The upstream producer of the differing writer
context remains unresolved. Evidence: `scratch/agent/s3512_selector_oracle.log`,
`scratch/agent/s3512_selector_oracle_range.log`,
`scratch/agent/s3512_selector_oracle_caller.log`, and
`scratch/agent/s3512_selector_port.log`.

ORIGIN: diagnostic-only oracle and port predecessor/store observations; no
selector, table, audio, task, or output value was rewritten, skipped, or
validated.
