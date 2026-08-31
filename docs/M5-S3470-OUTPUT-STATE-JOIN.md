# M5 Session 3470 — port selection/output join audit

The prescribed join used the qualified port capture
`scratch/agent/s3469_m5_port_pointer/run_autopilot.log` and the corrected
retail capture `scratch/agent/s3468_m5_retail_post_value/oracle-fixed.log`.

The port capture passed its four-PC output/state schema control and emitted
2,048 ordered output/state rows at `0x80001C98`, `0x80001CB8`,
`0x80001CC8`, and `0x80001F84`, plus 2,048 ordered table-selection rows at
`0x800644DC` and `0x80064524`. Its title phase was origin `0x00790400`.
The selected-family counts include 128 `0x801B4F00`, 129 `0x801B5E70`,
128 `0x801B4EC0`, 129 `0x801B5E30`, and 123 `0x801B50C0` at each selection
PC.

The retail capture also passed its independent controls and retained 2,261
ordered post-value rows at the title origins (`1,145` at `0x00790400` and
`1,116` at `0x00790800`). However, those rows are keyed by VI ordinal,
writer PC, store address, and stored value. They do not contain the port
table `entry`, selected pointer, or a shared invocation ordinal. The retail
rows therefore cannot be joined to the port selection/output rows by title
phase, selected entry, and per-entry ordinal. The controls firing and the
nonempty ordered rows rule out `H-PortObservationInvalid`; the missing
cross-runtime identity is a schema limitation, not a runtime null.

Result: `H-OutputStateContract` and `H-LaterTableSelection` remain
unevaluable. The aggregate `0x801Bxxxx` family overlap is descriptive only
and cannot select either hypothesis. The next discriminator is a
phase-scoped port witness carrying the oracle tuple
`(pc,s0,s1,source_word,branch_selector,source_byte,branch_state)` at the
four target PCs, followed by an ordinal join to the existing port
consumer/output rows.
