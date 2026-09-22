# M5 session 3736 — exact retail byte join

The oracle gained `--phase-snapshot-watch N`, which captures the watched
physical range at the first VI callback for title (`1024`, `0x00790400`) and
hangar (`512`, `0x006AB400`). It emits the exact nonzero byte offsets and
values, plus a full-range FNV-1a and nonzero count. The implementation reads
aligned words and unpacks byte lanes so the phase callback remains bounded.

The final retail run used whole-RDRAM, both source subrange watches, and both
target phases. Controls were live: whole-RDRAM had 11,166 writes; the two
source watches had 449 and 717 writes. The snapshots were:

| range | phase / VI | bytes | nonzero | FNV-1a |
|---|---:|---:|---:|---:|
| `0x1797B0..0x1798B0` | title / 1015 | 256 | 105 | `0x8611C3AF` |
| `0x1797B0..0x1798B0` | hangar / 2281 | 256 | 0 | `0xE6A1D1C5` |
| `0x1798B0..0x179A48` | title / 1015 | 408 | 168 | `0xD4E10CCC` |
| `0x1798B0..0x179A48` | hangar / 2281 | 408 | 0 | `0x762B22A5` |

The exact `(offset,value)` exports are in
`scratch/agent/s3736_m5_exact_byte_join/retail-span.log`, emitted as
`[oracle] phase-snapshot-byte` rows. The first target-phase nonzero positions
therefore are now independently available for any future byte-level join;
the hangar snapshot is an all-zero control.

The same-iteration port arms reached title and hangar. The real-audio arm's
qualified source-DMA rows remained zero-valued (`FNV=0x762B22A5`, `nz=0`),
matching the silent arm's zero source payload. This selects
`H-RetailOnlyProducer` at the measured hangar boundary. It does not establish
that the retail and port nonzero title layouts are equivalent, because the
port source payload is already zero before a position comparison can succeed.

ORIGIN: the retail oracle writer/source watches and the phase-gated port
source-DMA rows. No mitigation or guest behavior changed.
