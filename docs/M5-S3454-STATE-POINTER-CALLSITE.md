# M5 Session 3454 — state-pointer callsite boundary

The independent retail oracle passed its whole-RDRAM positive control at
10,000 callbacks, reached title origin `0x00790400`, and reported 825
executions of caller `0x80005268` immediately before `rs_free` plus 825 target
entries at `0x80001C98`.

The corrected port witness reached title 1024, fired the four-PC control
marker, and emitted 1,024 callsite rows plus 514/510/510/514 target rows at
`0x80001C98`/`0x80001CB8`/`0x80001CC8`/`0x80001F84`. Every 1C98 row's
thread-local pre-call `s0` equaled target-entry `s0`, including all 480 rows
whose callsite was `0x80005268`.

This selects `H-ProducerInput`: the first `s0` divergence is already present
at the caller-side register context, not introduced by the `rs_free` wrapper
or ABI boundary. The upstream writer/input remains unidentified. No waits,
slots, dispatch, clear behavior, or PCM writeback changed.

The first attempt placed the witness after the call and was discarded; the
generator now places it before `rs_free`.

Evidence: `scratch/agent/s3454_oracle_caller.log` and
`scratch/agent/s3454_port_producer_final.log`.
