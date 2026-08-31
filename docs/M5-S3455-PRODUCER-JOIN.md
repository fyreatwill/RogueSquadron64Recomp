# M5 Session 3455 — producer/input boundary run

The independent retail preflight used the whole-RDRAM write watch as its
positive control and reached title VI origin `0x00790400` at width 1024. It
reported 18,497 control callbacks, 781 executions of `0x80005268` followed by
`0x80001C98`, and 2,570 executions each of `0x80001CB8` and `0x80001CC8`.

The batched port run reached the same title phase. Its four-PC schema control
fired, and it emitted 1,024 phase-scoped callsite rows, 514 `0x80001C98`
rows, 514 `0x80001CB8` rows, and 510 `0x80001CC8` rows. The callsite rows
contain nonconstant caller-side `s0` values before the target calls; examples
include `0x00000000`, `0x801B2950`, and `0x801B26F8` at caller
`0x80005268`.

The retail execution watch independently shows the same caller-to-target edge
and varied caller-side `s0` values in the title phase. Session 3454's
regeneration-safe pre-call witness showed that port `rs_free` preserves its
caller-side `s0` at `0x80001C98`. Together these lines select the
upstream-producer/input boundary over wrapper/ABI clobber. This run does not
name the writer of `s0`; the callsite row is an input witness, not a producer
attribution. No waits, slots, dispatch, clear behavior, or PCM writeback
changed.

Sources: `scratch/agent/s3455_oracle_ground_truth.log`,
`scratch/agent/s3455_port_upstream.log`, and
`docs/M5-S3454-STATE-POINTER-CALLSITE.md`.
