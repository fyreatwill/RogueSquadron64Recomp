# M5 Session 3709 — caller and allocator route qualification

The independent retail oracle was run first with a whole-RDRAM positive
control. It recorded 10,000 control callbacks and, after phase-gating title
and hangar origins in the same run, executed both `0x80091934` and
`0x8008F0A0` in the target route. Retail reported `a1=0x561F`, `a2=0`,
`s0=0x12`, and `s2=1`; the allocator entry received `a0=0x12` from the
caller's delay-slot handoff and the same `a1` value. The first oracle attempt
armed only at the 512 phase and returned zero PC rows; that was an instrument
timing failure, not a phase execution result, and was discarded.

The one-build paired port run fired the caller-route control and two
phase-controls in both arms. The active real-audio rows at the caller and
allocator entry had `a1=0x561F`, `a2=0`, `s0=0x12`, `s2=1`, and `s3=0`; the
silent arm had the same tuple and the same caller-to-entry handoff. The
route identity was `ordinal/seq=525/526` in real audio and `519/520` in the
silent arm, reflecting arm-local route publication counts. No selector or
mixer input differed between the arms, and no later route state was needed to
enter the allocator.

This selects `H-CallerSelectorRoute`: the clear's allocator route is entered
with the retail-matching selector tuple. It refutes `H-CallerStateDivergence`
and does not support `H-CallerOrdering` as an explanation at this boundary.
The next boundary is the writer/source of `MEM_W(0x80165ED0)`, which is loaded
at `0x8009192C` before the caller.

This is two independent evidence lines: the retail oracle and the paired
port arms, each with a positive control.

ORIGIN: diagnostic-only caller/entry argument and route tracing. No clear,
selector, audio, task, or payload behavior was changed.

Evidence: `scratch/agent/s3709_oracle_caller_route_fixed.log` and
`scratch/agent/s3709_m5_caller_route/{real,silent}.log`.
