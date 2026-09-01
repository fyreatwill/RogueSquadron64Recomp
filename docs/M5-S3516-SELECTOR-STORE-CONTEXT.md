# M5 Session 3516 — live selector-store context boundary

The independent retail oracle first ran the corrected selector watch at
physical `0x00149758..0x00149760`, together with a whole-RDRAM positive control
and phase-gated execution watches at `0x8008F228` and `0x8008F264`. The control
reached 10,000 callbacks, the selector span recorded 10 writes, and both writer
PC watches recorded five executions in the hangar bucket. A prior candidate
reload at `0x8009192C` recorded zero executions in the same qualified route,
so it is not a valid predecessor boundary. The oracle field-dump mode emitted
no register rows despite the positive PC watches; retail register parity is
therefore not claimed.

Added `rs64_m5_selector_store_context` through
`tools/apply_s3516_m5_selector_store_context.py`, inserted at both generated
selector stores. The port Debug build passed. Its validated silent
LLE/spin-yield/autopilot capture reached 512 VI origin `0x006AB400`; the new
control fired at both PCs and captured `s0=0x12`, `s1=0x5622`, values
`0x80171E70` and `0x80173CB0`, matching the existing store witness. The run
had no crash or abort marker.

This qualifies the live store boundary and rules out `0x8009192C` as a
phase-observable predecessor on this route. It does not select parity,
divergence, or later mutation because the independent oracle did not expose a
comparable register tuple. No audio, selector, table, task, or output value
was rewritten, skipped, or validated.

ORIGIN: diagnostic-only independent oracle watches and port execution-context
witness; the selector stores and all observed values remained untouched.

Evidence: `scratch/agent/s3516_selector_context_oracle_fixed.log`,
`scratch/agent/s3516_selector_writer_context_oracle.log`,
`scratch/agent/s3516_selector_writer_context_oracle_fields.log`, and
`scratch/agent/s3516_selector_writer_context_port/run.log`.
