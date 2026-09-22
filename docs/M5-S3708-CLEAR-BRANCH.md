# M5 Session 3708 — clear-caller branch qualification

The independent retail oracle was run first with a whole-RDRAM positive
control and phase-gated execution watches at `0x8008F108`, `0x8008F168`,
`0x8008F1C4`, and `0x8008F2CC`. The control recorded 10,021 hits; all four
candidate PCs executed in the `0x006AB400:512` target phase. Retail showed the
same 18-iteration loop shape as the port: `0x8008F168` had `v0=1` for 17
iterations and `v0=0` on the terminating iteration, followed by a not-taken
`0x8008F1C4` and the clear caller with `a0=0x801797B0`.

The paired port run used one build and real/silent arms. All target controls
fired in both arms. Each arm emitted the same branch/state table: one
`0x8008F108` row with `v1=0x12`, 18 loop rows at `0x8008F168`, a terminating
`v0=0`, a not-taken `0x8008F1C4`, and the same allocator state
(`s0=0x12`, `s1=0x561F`, matching loop arguments). The clear caller was on the
same branch route in both arms; the real arm had producer sequence state before
the call, while the silent arm did not, but neither arm showed a producer
sequence after the clear and before the qualified zero source DMAs.

This selects `H-ClearBranchRoute`: the clear is scheduled by the stable
allocator route, not by a real-versus-silent caller-state difference. It
refutes `H-ClearCallerState` at the measured branch inputs and
`H-ClearCallOrdering` at the measured clear-to-source boundary. This is two
lines of evidence (retail oracle and paired port), each with a positive
control.

ORIGIN: diagnostic-only branch and route tracing. No game logic, clear, or
payload behavior was changed.

Evidence: `scratch/agent/s3708_oracle_branch.log` and
`scratch/agent/s3707_m5_source_clear_input/{real,silent}.log`.
