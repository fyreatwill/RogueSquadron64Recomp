# NEXT work unit (s875)

HYPOTHESIS-ID: m3-coalesce-phase-driver

Run one phase-gated value-origin experiment for the coalescer globals and
free-list head. Preserve whole-RDRAM, PIF, and VI positive controls. Record
exact writer PC/value in the port for `0x801163E4`, `0x801163E8`,
`0x801163F8`, and `0x8010FF18`; arm matching retail physical watches only
after controls are live. Do not change game behavior or add a mitigation.

Competing hypotheses:

- H-port-writer: the port partition writer produces a stale or malformed value.
- H-retail-writer: retail reaches the same writer/value transition, but the
  current oracle schedule has not crossed the required phase.
- H-legitimate-transition: matched values are legitimate state-machine output
  and the defect is downstream.

Discriminating measurement: positive controls plus matched writer/value
transitions select H-retail-writer; a port-only or malformed port value selects
H-port-writer; matched legitimate values with divergent downstream behavior
select H-legitimate-transition. If retail remains at width 320, classify the
run as phase-unreachable, not as a null.

Exact source anchors: `partitionFramebufferMemory` stores at 0x80000ED8,
0x80000FFC/0x80001010, and 0x80001024/0x80001038; the normal tick calls it
at 0x800013F0 and coalescer at 0x80001430.
