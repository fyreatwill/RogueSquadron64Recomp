# M5 session 3734 — retail-to-port source boundary

The batched capture ran the independent retail oracle and the qualified real/silent
port arms from the existing validated schedules. The oracle reached the whole-
RDRAM positive-control threshold, title `0x00790400`, and hangar
`0x006AB400`. The real port arm reached both target phases and fired its RSP
control; the silent arm also reached both phases but emitted no image joins.

The real port arm emitted 1,819 phase-5 image-DMA joins. The
`0x1798B0..0x179A48` source descriptor and its stage-3 DMEM payload were zero
in every sampled join: `762B22A5`, zero nonzero bytes, with matching zero
output and destination payloads. The retail oracle independently sampled
189/256 nonzero positions in `0x1797B0..0x1798B0` and 106/256 in
`0x1798B0..0x179A48` during hangar, with writer families `0x80007670`,
`0x8001E2C0`, and `0x8001F...` present. Its target-phase source writes also
included the later `0x800078EC` clear.

This selects `H-RetailOnlyProducer` at the measured source boundary and makes a
port source-layout error less likely: the same retail source spans are populated
while the port's corresponding source-DMA handoff is all zero. The capture does
not provide exact retail byte offsets or a retail FNV, so it cannot formally
refute a shifted layout. The next discriminator is an oracle-side exact byte
position/FNV export joined to the port's per-subrange payload table.

ORIGIN: independent retail oracle watches plus the port's phase-gated source-DMA
join; no port or guest behavior changed.
