# NEXT work unit — watch the target-phase display-mode store

HYPOTHESIS-ID: retail-pretitle-route-state-writer

Session 3252 established that the watched `reapplyDisplayMode` triplet is live
but executes only after the target boundary. Do not repeat that watch or add
port instrumentation. The next single work unit is an independent retail
oracle watch of the target-phase display-mode store at `0x8008EC88`, gated to
1024 origins `0x00790400` and `0x00790800`, with the whole-RDRAM positive
control and title gate retained.

## Competing hypotheses

- `H-TargetStoreLive`: `0x8008EC88` writes at target width/origin with a
  value/order relation that can be compared to the port boundary.
- `H-TargetStoreAbsent`: controls pass but no target-phase store occurs;
  this candidate is ruled out.
- `H-TargetStoreMisaligned`: the store fires, but its value or ordering is not
  the target route relation; keep the port unchanged and redesign the watch.

## Discriminator

One oracle run with a whole-RDRAM positive control and title 1024 gate must
capture the `0x8008EC88` store, its value and PC, live 1024 VI origin, and
ordering relative to the transition. A target-phase hit with a comparable
value selects `H-TargetStoreLive`; zero hits with valid controls selects
`H-TargetStoreAbsent`; otherwise select `H-TargetStoreMisaligned`. No result
authorizes a port or audio change by itself.

## Exact commands

1. Read `tools/oracle/README.md` and use its existing route-watch recipe; do
   not build a new instrument before the oracle control is armed.
2. Run one retail capture with `--watch-write 0x0:0x800000`,
   `--watch-pc 0x8008EC88`, `--pc-phase-log-width 0x00790400:1024`, and
   `--pc-phase-log-width 0x00790800:1024`, plus the documented Start schedule.
3. Compare only against the existing port row; if no like-for-like relation
   exists, record the boundary as unevaluable and leave source unchanged.
