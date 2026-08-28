# NEXT work unit (s2976)

HYPOTHESIS-ID: m5-route-preparation-target-predicate

## Unit

Implement one bounded phase-aware oracle measurement for route preparation at
guest PC `0x80019CD8`. Retain a whole-RDRAM positive control, but avoid
breaking on the high-frequency boot loop and arm/log the route breakpoint only
after a target VI boundary. Do not change the port predicate until retail
target rows are available.

## Competing hypotheses and discriminator

- H-retail-target-predicate: retail calls route preparation only after the
  target VI width/origin is committed; target rows occur at
  `1024/0x00790400` or `512/0x006AB400`.
- H-retail-precommit-order: retail calls route preparation before VI commit;
  target identity is carried by a pending mode/buffer field, so a target row
  has a differing live VI.
- H-port-predicate-mismatch: retail and port agree on ordering, but accepted
  target identity differs.

The discriminator is one same-run table of route-PC executions joined to the
next target VI boundary, with live width/origin and GPR fields. The whole-
RDRAM control must fire. Target rows select one of the first two hypotheses;
matching retail target fields with the port's zero target rows selects
H-port-predicate-mismatch. No target phase is unevaluable.

## Commands

After implementing the phase-aware arm, run from the repo root with the local
debugger core and retail ROM:

    tools/oracle/build/rs64_oracle \
      --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom ../rogue_squadron64/rogue_squadron.z64 --secs 45 \
      --watch-write 0x0:0x800000 --watch-pc 0x80019CD8 \
      --pc-phase-log-width 0x00790400:1024 \
      --pc-phase-log-width 0x006AB400:512 \
      --press 8:start --press 14:start --press 20:start --press 26:start \
      --press 32:start --press 38:start --hit-cap 10000

Save output to `scratch/agent/s2976_m5_route_oracle/` and record the control
count, phases, route rows, and selected hypothesis.
