# M5 session 3703 — final source writer is the zero-fill

The independent retail preflight passed its whole-RDRAM positive control at
10,000 callbacks, reached title and hangar, and recorded 674 writes to
`0x1797B0..0x179930`. This establishes that the target phase and watch were
live outside the port.

The paired port run used real-audio and silent arms, RSP/DMEM controls, and a
512-row output-DMA budget. Both arms reached title and hangar and each
recorded 652 source-range scalar stores. The real arm recorded 512 qualified
output DMAs; the silent arm recorded none, as expected.

The port source-store census was identical in both arms: 172 stores at
`0x80007670`, 11 at `0x8001E2C0`, 64 in the `0x8001F...` family, and 384 at
`0x800078EC`. The first groups included nonzero values and occurred before
target-route publication. The final 384-store group was zero-valued
`0x800078EC` stores at the end of the monotonic sequence. The first and last
qualified output-DMA rows both carried zero source and post-DMA payloads; the
predecessor snapshot remained `0x800078EC`, with no later source-range writer.

This selects `H-ClearIsFinal` and refutes `H-ProducerAfterClear` and
`H-DescriptorOrdering` for the measured range. Retail source-span writes and
the port's independent phase/control rows provide two evidence lines. This is
provenance evidence only; no mitigation or guest/RDRAM state change was made.

Next discriminator: join the `0x800078EC` zero-fill call's destination,
length, route/task identity, and ordering to the first output DMA. A different
destination/length or unrelated task selects `H-ClearWrongObject`; the
expected `0x801797B0`, length `0x298`, on the same route selects
`H-ClearLegitimateButEarly`; a later nonzero producer reopens
`H-ProducerAfterClear`.
