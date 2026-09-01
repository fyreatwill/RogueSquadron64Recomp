# M5 session 3581 — retail source producer qualification

The retail oracle ran for 60 seconds with whole-RDRAM and
`0x1797B0..0x179930` write controls, watched PCs `0x800078EC`,
`0x800078E0`, and `0x800C825C`, the 512-wide phase bucket, VI tracing, and
post-store sampling. The capture is at `/tmp/rs64_next_oracle.log`.

Both positive controls fired: whole-RDRAM had 10,674 writes and the source
span had 674 writes. Retail changed from 1024 to 512 width at 47.4 seconds
(VI 2792, origin `0x006AB800`) and first displayed the target origin
`0x006AB400` at 48.5 seconds (VI 2825).

At the target transition, the execution table joined `0x800052C4` to
`0x800078E0` with `a0=0x80656010`, `a2=0x18`, followed by
`0x800078EC` on that buffer. A later call used `a0=0x80656040`, `a2=0x3C`.
The separate `0x8002BEEC` predecessor reached `0x800078EC` with
`a0=0x80656090`, `a2=0x8000`. Post-store rows for the target-gated writer
included nonzero values such as `0x00941376`, `0x008317BD`, and
`0x0042154D`.

This qualifies nonzero retail target-phase values and the `0x800078EC`
writer family. It does not identify a distinct DMA event or prove whether
DMA precedes or follows the writer, and it does not identify which earlier
producer constructed the nonzero words. Those boundaries stay open. This is
single-source oracle evidence; no runtime behavior was changed.

ORIGIN: diagnostic-only retail producer/value qualification. No mitigation
was added.
