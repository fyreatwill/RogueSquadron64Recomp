# M5 session 3737 — retail writer-family join

The first batched capture was invalid because the existing executable was
stale: both port arms crashed before a target phase. Rebuilding
`RogueSquadron64Recomp` completed cleanly, and the identical capture was then
rerun with retail oracle, real-audio port, and silent port arms together.

The fixed oracle passed the whole-RDRAM positive control, reached title and
hangar, and ran 120 seconds / 7,181 VI. Its exact snapshots were unchanged:

| range | title nonzero / FNV | hangar nonzero / FNV |
|---|---:|---:|
| `0x1797B0..0x1798B0` | 105/256, `0x8611C3AF` | 0/256, `0xE6A1D1C5` |
| `0x1798B0..0x179A48` | 168/408, `0xD4E10CCC` | 0/408, `0x762B22A5` |

Retail writer histograms for the two source ranges include `0x80007670` and
`0x8001E2C0` in the title route, followed by the `0x800078EC` clear in the
hangar route. The qualified real port reached hangar and emitted 512
source-range reader rows, 512 source-range writer rows, and 4,082 image-DMA
joins. Every joined source/output/destination payload remained zero with
`FNV=0x762B22A5`; the input-writer positive-control row fired, but no
phase-gated input-writer row identified a nonzero store. The silent arm passed
title but emitted no source/image rows and had no crash.

This selects `H-RetailWriterEarlier` at the measured boundary: retail has an
earlier nonzero writer family that is absent from the qualified port source
path, while the later clear is common to the zero hangar payload. It does not
prove why that family is absent or authorize suppressing the clear.

Evidence: `scratch/agent/s3737_m5_retail_writer_join_fixed/oracle.log`,
`real.log`, `silent.log`, and `summary.txt`.

ORIGIN: independent retail writer-PC/snapshot watches plus phase-gated port
input/source/DMA rows. No guest or port behavior changed.
