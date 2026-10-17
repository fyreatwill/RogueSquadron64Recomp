# Session 5274 symbol audit: `__osCurrentHandle`

The bounded companion-symbol helper scanned `0x80039150..0x80039180`, made
zero edits, and reported `__osCurrentHandle`, `__osPiAccessQueueEnabled`, and
`__osSiAccessQueueEnabled` as already synchronized.

Independent checks found `__osCurrentHandle = 0x80039150` in the companion
libultra map as `OSPiHandle*` data of size `0x8`. The generated tree has no
callable body, placeholder symbol, header declaration, overlay record, or
direct generated caller at that address. The bytes are shown only as `lb` and
`nop` entries in the surrounding data/fragment decode.

This rules out callable placeholder propagation. Preserve the existing data
name; no build or soak is needed. The next candidate is
`__osPiAccessQueueEnabled = 0x80039160`.
