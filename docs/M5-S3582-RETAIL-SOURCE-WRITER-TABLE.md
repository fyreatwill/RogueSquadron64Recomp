# M5 session 3582 — retail source-span writer table

The prescribed single retail-oracle capture ran for 60 seconds using the
whole-RDRAM and `0x1797B0..0x179930` write watches, phase-gated PC watches,
field dumps, writer histogram, and post-value capture. Complete output:
`/tmp/rs64_next_oracle.log`.

The whole-RDRAM positive control reached 10,674 writes and the source-span
watch reached 674 writes. The target phase was VI 2803 at 47.4 s, width 1024
to 512, origin `0x006AB400`. The phase-scoped writer histogram recorded 384
target-phase writes by `0x800078EC` (with other source-span writers also
present). Field rows joined `0x800052C4 -> 0x800078E0 -> 0x800078EC`; one
target tuple had source buffer `0x8065E0A0` and length `0x1C`.

Post-value rows at the preceding 1024-wide VI (2801, origin `0x006AB800`)
showed nonzero stored words in the watched range, including `0x00941376` at
`0x001797B0`, `0x008317BD` at `0x001797B4`, and `0x0042154D` at
`0x001797B8`. This independently qualifies a nonzero retail store, rather
than merely proving that a branch ran.

This selects the immediate retail producer/context and nonzero-value
divergence at the writer boundary. The earlier construction of the source
words remains unresolved. No independent DMA event identifier was emitted,
so exact DMA ordering remains open. This is one capture with two independent
qualified observation lines (writer-PC histogram and post-value rows), not a
cross-run comparison.
