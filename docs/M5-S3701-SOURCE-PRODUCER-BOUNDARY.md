# M5 s3701 — source producer boundary

Date: 2026-09-21

The retail preflight passed its whole-RDRAM positive control, reached title
VI `0x00790400` width 1024 and hangar VI `0x006AB400` width 512, and recorded
1,125 writes in `0x1798B0..0x179A48`. Its hangar writer census included
`0x80007670`, `0x8001E2C0`, the `0x8001F...` family, and `0x800078EC`.

The qualified real-audio/LLE-ungated/LLE-solo/spin-yield/autopilot port run
reached hangar and fired the RSP and source/DMEM controls without a crash or
abort. Its first 512 qualified hangar rows joined the expected
RDRAM-to-DMEM source DMA at `0x1798B0`, length `0x198`, DMEM `0xCB0`. The
source FNV was `762B22A5` with `nz=0`, and the post-DMA output was also zero.
The paired input/source records had no current scalar writer
(`prev_writer_pc=0`); the only prior writer snapshot remained the title
`0x800078EC` zero-fill.

This selects `H-RetailSourceDifferent` and refutes `H-PortSourceProducer` and
`H-InputDescriptorWrong` at this boundary. The descriptor and DMA range are
correct; the next boundary is the producer/layout of the zero RDRAM source
before that DMA. No mitigation or guest/RDRAM state change was made.
