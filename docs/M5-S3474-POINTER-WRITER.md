# M5 Session 3474 — pointer-span writer census

The independent retail preflight used a whole-RDRAM positive control and the
physical span `0x00110000:0x00112000`. The control recorded 2,255,979 writes,
the candidate span was active, and the run reached 3,269 VI. Sampled span
values included `0x80110000`, `0x80110770`, and `0x8010FF70`; this validates the
physical span but does not identify an ordinal-specific state writer.

The regeneration-safe port capture reached title origin `0x00790400` at width
1024 and later hangar width 512 without crash or abort. Existing positive
controls fired: `m5-output-state-fields-positive` and
`m5-state-pointer-checkpoint-positive`. The capture emitted 2,048 table rows,
1,024 producer rows, and 2,048 output/state rows. The new title-scoped store
witness emitted 1,024 pointer-valued stores in the physical span.

The first pointer-valued rows were initialization/chain construction at
`0x800027C4`, `0x800027D0`, `0x800027DC`, and then repeated stores at
`0x80003C28` (for example `0x80110E4C <- 0x80111150` and
`0x80110EC0 <- 0x80111178`). No row joins these stores to the later `s1`
consumer ordinal, and the witness did not instrument loads. Therefore this
session narrows the candidate writer set but does not select
`H-InterveningPointerWriter` or `H-AlternateDispatch`. The next discriminator
must capture selected addresses/loads at the consumer path, or join the
candidate stores to the producer ordinal.

The first two port attempts were invalid instrument placements: one helper
returned before the witness, and the next helper did not cover all stores.
They are retained as failed measurement attempts; only the final filtered run
supports the result above.
