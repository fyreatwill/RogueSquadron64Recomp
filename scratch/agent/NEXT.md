# NEXT work unit — attribute the retail M5 VI origin writer

HYPOTHESIS-ID: m5-retail-vi-origin-attribution

Session 3230 selected distinct edges: both port arms stopped at
640/`0x0066A500`, while retail's ordered route PCs fired at 640/`0x00790A00`.
Do not add more port route fields until the retail buffer writer/commit is
attributed.

## Competing hypotheses

- `H-RetailRouteWriter`: the retail `0x00790A00` origin is legitimately
  published by the watched reapply/VI-commit path and its physical buffer can
  be identified at the VI-swap edge.
- `H-RetailOtherWriter`: another display-buffer writer produces
  `0x00790A00`; the watched route PCs are consumers or adjacent bookkeeping.
- `H-PortOriginSelection`: the port's `0x0066A500` commit is the same logical
  route but selects a different legitimate buffer because its commit/VI-swap
  ordering differs.

## Discriminator

Run the independent retail oracle first with a whole-RDRAM write positive
control, the existing route and title gate, and a phase-gated execution watch
on the VI-swap/commit routine already reported by the oracle (`0x80035500`).
Record each `0x00790A00` transition's VI-swap physical argument, previous PC,
and immediately preceding/following VI origin. `H-RetailRouteWriter` is
selected if the watched route sequence and VI-swap writer/argument form one
ordered publication of `0x00790A00`; `H-RetailOtherWriter` if another PC writes
or commits it; `H-PortOriginSelection` if retail and port show the same writer
and ordering but different legitimate buffer selection. A whole-RDRAM control
must reach its callback threshold in the same run.

## Exact commands

Use the oracle command documented in `tools/oracle/README.md`, preserving the
validated Rice/input route and title gate. Add the `0x80035500` VI-swap watch
and the existing four route-PC watches, plus the whole-RDRAM watch. Capture to
`scratch/agent/s3231_m5_retail_vi_origin/` and do not build port
instrumentation until the oracle result is positive-controlled.

Do not add audio/task counters until this writer/commit discriminator selects
one outcome.
