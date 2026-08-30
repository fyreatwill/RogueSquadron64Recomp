# NEXT work unit — watch the alternate target-boundary writer

HYPOTHESIS-ID: retail-pretitle-route-state-writer

Session 3253 established that `0x8008EC88` is live but executes only at the
1024-to-512 transition. Do not repeat that watch or add port instrumentation.
The next single work unit is an independent retail oracle watch of the other
named writer `0x8008ED48`, gated to 1024 origins `0x00790400` and
`0x00790800`, with the whole-RDRAM positive control and title gate retained.

## Competing hypotheses

- `H-ED48TargetLive`: `0x8008ED48` executes at target width/origin with a
  value/order relation that can be compared to the port boundary.
- `H-ED48Absent`: controls pass but no target-phase execution occurs; this
  candidate is ruled out.
- `H-ED48Misaligned`: it fires only outside the target phase, or its value or
  ordering is not the target route relation; keep the port unchanged.

## Discriminator

One oracle run with a whole-RDRAM positive control and title 1024 gate must
capture `0x8008ED48`, its value/PC, live 1024 VI origin, and ordering relative
to the transition. A target-phase hit with a comparable value selects
`H-ED48TargetLive`; zero hits with valid controls selects `H-ED48Absent`;
otherwise select `H-ED48Misaligned`. No result authorizes a port or audio
change by itself.

## Exact commands

1. Read `tools/oracle/README.md` and use its existing route-watch recipe; do
   not build a new instrument before the oracle control is armed.
2. Run one retail capture with `--watch-write 0x0:0x800000`,
   `--watch-pc 0x8008ED48`, `--pc-phase-log-width 0x00790400:1024`, and
   `--pc-phase-log-width 0x00790800:1024`, plus the documented Start schedule.
3. Compare only against the existing port row; if no like-for-like relation
   exists, record the boundary as unevaluable and leave source unchanged.
