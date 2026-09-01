# M5 Session 3501 — pre-call selector state

The independent retail preflight used the debug mupen core, Rice video, the
whole-RDRAM write control, title-driving Start presses, and an execution range
watch from `0x80091280` through `0x80091330`. The control reached its 10,000-hit
cap, title origin `0x00790400` was live, and the predecessor range executed in
the title phase. At the post-`lw a0` boundary (`0x80091320`), retail showed
`a0=0x801772F0` in all 628 sampled rows.

The first port attempt used an invalid Windows-style `build/Debug` path and
launched no process. The corrected route was rebuilt once and run from `build/`
with `ROGUESQ_STUB_MISSING_FUNCS=1`, the canonical autopilot schedule,
real-image/LLE/spin-yield settings, and the caller/producer/pre-call controls.
It reached title origin `0x00790400` and emitted 2,048 pre-call rows, 1,024
caller rows, and 1,024 producer rows, with each positive-control marker live.

Port post-load rows split at the `0x8009131C` `a0` load: 511 rows loaded
`0x80175960` from `0x80150000` (index 0), 512 loaded `0x801772F0` from
`0x80150004` (index 1), and one additional `0x80195190` row. The stage-1
`0x8009132C` rows and adjacent caller rows preserved these classes. The two
independent lines therefore agree that the first measured divergence is in the
pre-call selector table/state feeding `a0`, not in the caller wrapper or the
producer below `0x80091330`.

This selects `H-PreCallState`, refutes `H-PreCallObservationFailure`, and
narrows the next boundary to the writer/initializer of the `0x80150000` table
entries or their selector index. It does not establish whether the differing
port table values are legitimate; no mitigation or value rewrite was added.

ORIGIN: the new witness observes post-load register/table context at
`0x8009131C` and `0x8009132C`; it does not rewrite, skip, or validate selector
state.
