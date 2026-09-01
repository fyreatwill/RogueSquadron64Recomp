# M5 session 3579 — retail source writer

The retail oracle ran for 60 seconds with whole-RDRAM and source-span
positive controls, watched PCs `0x800078EC`, `0x800078E0`, and `0x800C825C`,
and the `0x006AB400:512` phase bucket.

Controls were live: whole-RDRAM recorded 10,674 writes and the source span
`0x1797B0..0x179930` recorded 674 writes. The target VI first appeared at
48.5 s. Target-phase source-span writes began at 47.4 s from PC `0x800078EC`,
before that VI. The run recorded 1,289,615 executions of `0x800078EC`,
3,165 of `0x800078E0`, and 2,260 of `0x800C825C`; `0x800078E0` was entered
from `0x800052C4` 866 times and from `0x800C825C` 2,260 times.

This selects H-RetailWriterSame for target-phase writer identity and
pre-target ordering. Earlier setup writes came from `0x8001E2C0`,
`0x80007670`, and `0x8001FAxx..0x8001FDxx`, and are separate initialization
activity.

The ordinary write-hit rows report address, PC, and time but not stored-word
values. Value parity against the port's zero-fill remains open; the next
capture must use post-value sampling and retain the first source-DMA boundary.

Capture: `/tmp/rs64_next_oracle.log` (555,695 lines).
