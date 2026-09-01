# M5 session 3550 — HMT tuple roles

The generated body establishes the `parseHmtMaterials` entry contract:
`a0` is a scalar material index, `a1` is the output material-record pointer,
`a2` is a nullable material-entry pointer, and `a3` is an 8-bit mode/control
value. The body branches on a null `a2` before reading the material entry.
The earlier provisional classifier was false-positive: it treated ordinary
indices and the nullable input as malformed pointers.

The host probe now reports those roles, decodes entry fields at
`+0x28/+0x2A/+0x2C/+0x2D/+0x2E` only for a mapped non-null `a2`, and marks
`bad` only when a required role pointer is unmapped. This is diagnostic-only;
no game value or write was changed.

The rebuilt canonical real-audio/LLE/spin-yield/autopilot run passed the HMT
positive control and emitted 1,557 rows. It reached the 640-wide pre-title
origin `0x0066A500`; all sampled `parseHmtMaterials` rows had a mapped `a1`
and either a mapped or null `a2`, producing zero role-contract violations.
The run later crashed in `heapFreeListDequeue` with
`last-guest-pc=0x8000D704`, before title or hangar. The role-mapped HMT input
is valid at this discriminator; the next boundary is the heap failure, not an
HMT malformed-input producer.

Evidence: `scratch/agent/s3550_m5_hmt_role_table/run-final2.log`.

ORIGIN: diagnostic-only role and field observation; no input, heap, audio,
PCM, image-task, output, or texture-record state was suppressed or rewritten.
