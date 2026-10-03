# s3819 result

The independent retail oracle completed normally. The whole-RDRAM positive
control fired 11,125 times; hangar VI `0x006AB400` at width 512 was reached;
the source-span watch recorded 1,125 writes.

In the hangar phase, `0x800078EC` made 816 scalar stores into
`0x1798B0..0x179A48`; all stored values were zero (`mismatch=0`,
`unsupported=0`). The final 408-byte snapshot nevertheless had 12 nonzero
bytes and `FNV=0x0726A645`; other writer PCs were present. This refutes
complete retail/port zero-span parity while selecting the legitimate zero
writer as only one part of the retail chain.
