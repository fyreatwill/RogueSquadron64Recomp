# NEXT work unit — capture retail VI context at the route boundary

HYPOTHESIS-ID: m5-retail-vi-origin-attribution

Session 3233 showed that the repaired route join is live: it produced a
target row at `0x00790A00`, but route `$a0` is `0x8014090E`, not a framebuffer.
The existing VI-context join also filters out the target origin and cannot yet
provide the framep/mode candidates needed for writer attribution.

## Competing hypotheses

- `H-RetailRouteWriter`: the target route's VI context contains the
  framebuffer selected by the route publication.
- `H-RetailOtherWriter`: the target VI context points to a different writer or
  commit path than the watched route.
- `H-PortOriginSelection`: retail exposes a legitimate target framebuffer that
  differs from the port's selected buffer.

## Discriminator

Add an any-next-VI arm to the context join, then run the independent retail
oracle with the whole-RDRAM control and validated full Start schedule,
watching `0x80091D38` and using `--vi-context-table-pc 0x80091D38`.
Require the positive control, the target `0x00790A00` route hit, and a
`vi-context-row` containing context/framep/mode candidates. A candidate equal
to the route's legitimate framebuffer selects `H-RetailRouteWriter`; a valid
different candidate or no matching route context selects `H-RetailOtherWriter`;
the same valid retail candidate compared with the port's selected buffer
selects `H-PortOriginSelection`. A zero context join after the controls means
the context filter/join remains unevaluable; do not add port counters.

## Exact command

First add `--vi-context-any-vi` to the oracle's context join and rebuild with
`bash tools/oracle/build.sh`. Then use the Session 3233 fixed oracle command,
replacing the post-swap options with
`--vi-context-table-pc 0x80091D38 --vi-context-any-vi`, and capture to a new
`scratch/agent/s3234_m5_retail_context_join/` directory. Do not build port
instrumentation until the oracle result is positive-controlled.
