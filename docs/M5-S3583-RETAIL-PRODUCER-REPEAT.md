# M5 session 3583 — retail producer discriminator remains open

The prescribed 60-second retail-oracle capture ran from `build/` with the
complete output at `/tmp/rs64_next_oracle.log`.

Both positive controls fired: the whole-RDRAM watch recorded 10,674 writes
and the `0x1797B0..0x179930` source-span watch recorded 674 writes. The target
phase reached 512-wide origin `0x006AB400` at VI 2813 (48.5 seconds), with
subsequent target VIs through the end of the run. The run completed normally
after 1,305,471 execution-watch hits and 3,026 VIs.

The phase-scoped source-span writer histogram recorded 384 writes by
`0x800078EC`. Joined execution rows again showed
`0x800052C4 -> 0x800078E0 -> 0x800078EC`; at the target phase one tuple was
source `0x8065FA30`, length `0x1C`, with source word `0x59050000`. The
writer's post-value sample retained 384 values, including nonzero
`0x00941376`, `0x008317BD`, and `0x0042154D`.

This independently repeats the immediate producer/context and nonzero
retail-value evidence. It does not expose a stable earlier constructor
beyond `0x800052C4`, nor a separate DMA event identifier. Therefore the
earlier construction boundary and exact DMA-versus-writer ordering remain
open; the field-table discriminator did not move them.

ORIGIN: diagnostic-only retail producer qualification. No mitigation was
added.
