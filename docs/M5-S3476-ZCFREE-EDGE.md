# M5 Session 3476 — audited the sole `zcfree` state edge

The independent retail oracle used a whole-RDRAM positive control, title-phase
execution controls, and field dumps at `0x80029CFC`, `0x80005268`, and
`0x80001C98`. The positive control reached 10,000 callbacks; title 1024
appeared; and the exact retail edge executed 825 times. Retail transferred
from `zcfree` at `0x80029CFC` through `rs_zcfree`/`0x80005268` to `rs_free`,
with the edge carrying a live `$s1` value into the consumer.

The generated census found one `rs_zcfree` caller and one direct
`0x80005268 -> rs_free` edge. A regeneration-safe port witness at that sole
edge emitted 827 title rows, including its positive control. The existing
consumer witness emitted 512 rows; 477 had the same `$s1` as the most recent
sole-edge row. The 35 nonmatches are other `rs_free` callers, for which the
sole-edge latch is intentionally stale. No caller-side `$s1` assignment or
load exists inside `rs_zcfree` between the edge and `rs_free`.

This selects `H-UninstrumentedWriter` only in the bounded sense that the
caller-side inherited state is the source for the `zcfree` edge; it rules out
an uninstrumented assignment between `0x80005268` and `rs_free`. It does not
explain the earlier port-versus-retail value divergence, because retail's
edge carries `0x80110xxx` state while the downstream port consumer can later
observe `0x80194Fxx`/`0x801Bxxxx` state.

Evidence: `scratch/agent/s3476_m5_oracle/driven/oracle.log`,
`scratch/agent/s3476_m5_port_fixed/run.log`, and the generated caller census
under `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`.

ORIGIN: the witness only observes the inherited register and consumer value;
it does not rewrite, skip, or validate any pointer or state value.
