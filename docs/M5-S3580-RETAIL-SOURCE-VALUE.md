# M5 s3580 — retail source value qualification

Date: 2026-09-01

Ran the prescribed retail oracle capture with whole-RDRAM and source-span
positive controls, `0x800078EC`/`0x800078E0`/`0x800C825C` PC watches,
target-phase VI gating, and post-value sampling. The complete log is retained
at `/tmp/rs64_next_oracle.log` (218,125,140 bytes).

The whole-RDRAM control fired 10,674 times and the source-span watch fired 674
times. The target phase occurred at VI 2803, 47.4 s, width 512, origin
`0x006AB400`; `0x800078EC` wrote 384 source-span locations at that time.
Post-value rows contained nonzero words including `0x00941376`, `0x008317BD`,
and `0x0042154D`, followed by byte-lane rows whose final low-byte observations
were zero. The target-phase span is therefore not an all-zero store.

Earlier source-span activity occurred at 7.0–7.2 s. The capture exposed no
separate DMA event identifier, so exact DMA-versus-writer ordering remains
only phase/timestamp ordered. This selects `H-RetailValueNonzero` at the
writer boundary and rules out a target-phase all-zero store. It is
single-source oracle evidence; the producer and parity against the port's
stored words remain open.
