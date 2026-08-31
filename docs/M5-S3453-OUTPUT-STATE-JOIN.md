# M5 session 3453 — output/state schema join

The existing controlled port logs were joined to the independent retail
oracle log `scratch/agent/s3450_oracle_fixed.log`. Both are title-phase
captures at origin `0x00790400` and width 1024, with positive controls: the
oracle reached its whole-RDRAM threshold and the port emitted its four-PC
schema marker.

The key was phase, PC, and ordinal within each PC. The oracle contributes
460/511/511/458 rows for `0x80001C98`/`0x80001CB8`/`0x80001CC8`/`0x80001F84`;
the port contributes 514/510/510/514 rows in each arm. Comparing common
prefixes, the first joined row diverges in `s0` at every target PC in both
port arms:

| PC | oracle `s0` | port `s0` | joined rows | exact six-field rows |
|---|---:|---:|---:|---:|
| `0x80001C98` | `0x801A8840` | `0x00006C20` | 460 | 0 |
| `0x80001CB8` | `0x801A8890` | `0x80195190` | 510 | 0 |
| `0x80001CC8` | `0x801A8890` | `0x80195190` | 510 | 0 |
| `0x80001F84` | `0x801A8840` | `0x00006C20` | 458 | 0 |

The two port arms have the same selected result; the oracle is an independent
second evidence line. This selects `H-FirstFieldDivergence`: the target
functions execute, but the first output/state context supplied to them is
already different. It rules out `H-PortAbsent` and does not identify the
writer of `s0`. This is a strict ordinal join, not a claim that sequential
silent/image arms are a valid animated A/B.

Evidence: `scratch/agent/s3449_m5_state_tuple_context/{silent,image}.log` and
`scratch/agent/s3450_oracle_fixed.log`.
