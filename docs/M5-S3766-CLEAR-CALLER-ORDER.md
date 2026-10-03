# M5 s3766 — clear caller and ordering

The paired image/silent capture used the rebuilt static `rs_memset` caller
probe. Both arms passed the phase controls and reached title VI 1024 and
hangar VI 512. The probe's positive controls fired in both arms; the image
arm also produced image-stage rows.

The target clear was called from guest callsite `0x8008F2CC`, with destination
`0x801797B0`, fill `0`, and length `0x298`. The generated body shows the
caller allocating the buffer immediately beforehand (`0x8008F2B4`/
`0x8008F2B8`), storing the pointer, then issuing `jal 0x800078E0` at
`0x8008F2CC`; the next operation is the cache writeback at `0x8008F2DC`.
The runtime target row confirms the same callsite and arguments in both arms.

In the image arm, the clear-entry row precedes the phase-5 source-span rows
from `0x800078EC`, and those rows precede the `0x1798B0 -> DMEM 0xCB0`
input-DMA rows. All observed values remain zero. The silent arm has the same
clear caller/order, with the expected `musyx_stub` route.

This selects `H-M5-ClearIsExpected` for the caller/order question. It does not
show that the zero payload is correct for the retail game, and it does not
identify why the port has no nonzero producer after initialization. The
independent s3762 retail oracle control and target phases remain the second
evidence line; this port capture supplies the caller/order line. No guest
state or clear behavior was changed.
