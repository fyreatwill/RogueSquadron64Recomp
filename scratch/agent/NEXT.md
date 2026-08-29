# NEXT work unit — repair the retail route-to-VI join

HYPOTHESIS-ID: m5-retail-vi-origin-attribution

Session 3232 showed that the four retail route PCs and `0x00790A00` VI
transition are live, but `--post-swap-table-pc 0x80035500` produced no
joined rows. Downstream target-phase qualification remains open.

## Competing hypotheses

- `H-RetailRouteWriter`: the `0x00790A00` transition is the watched route's
  legitimate publication.
- `H-RetailOtherWriter`: another writer or commit path owns that origin.
- `H-PortOriginSelection`: retail and port share writer/order but select
  different legitimate buffers.

## Discriminator

Run the independent retail oracle with the whole-RDRAM control and validated
full Start schedule, watching the four route PCs and using
`--post-swap-table-pc 0x80091D38` (the route execution, not the high-frequency
swap routine). Keep phase buckets for `0x00790A00`, `0x00790400`, and
`0x006AB400/800`, plus `--vi-trace`. A joined row with the route's physical
framebuffer and following VI origin selects `H-RetailRouteWriter`; another
writer or unmatched route selects `H-RetailOtherWriter`; matching writer/order
with a different legitimate port buffer selects `H-PortOriginSelection`.
Zero joined rows after a positive control means the join remains unevaluable
and requires no port instrumentation.

## Exact command

Use the Session 3232 oracle command, replacing only
`--post-swap-table-pc 0x80035500` with `--post-swap-table-pc 0x80091D38`, and
capture to a new `scratch/agent/s3233_m5_retail_route_join/` directory. Do not
build port instrumentation until the oracle result is positive-controlled.
