# Session 3374 — independent retail PCM writer qualification

The retail oracle was run with Rice for 75 seconds using the canonical Start
schedule. The whole-RDRAM positive control fired 12,496 writes. VI tracing
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, so the target
phase was valid.

| range | total writes | hangar-phase writer |
|---|---:|---|
| `0x166450..0x166750` | 768 | `0x800078EC`, 768 |
| `0x169150..0x169450` | 768 | `0x800078EC`, 768 |
| `0x168E50..0x169150` | 768 | `0x800078EC`, 768 |
| `0x16A000..0x16A300` | 192 | `0x80022B1C/20/24/28`, 48 each |

Post-store snapshots were nonzero: respectively 744/768, 754/768, 747/768,
and 340/768 bytes, with FNV values `A222DCFE`, `E71AD8A6`, `A3C7EF13`, and
`CC4746FB`. The port's corresponding PCM rows were phase-live but reported
`nz=0` and `F59C39C5` for 768-byte samples.

This selects `H-PortPCMWriterGap`: retail has a guest-side writer/value
transition for the observed PCM spans, while the qualified port path presents
the same spans as zero-valued output. It refutes `H-RetailZeroPCMIsLegitimate`
for these spans and makes `H-PortPCMJoinMisattribution` unlikely for the
three ranges that match the port rows. The fourth range has a separate retail
writer family and remains secondary. No output substitution or mitigation is
authorized.

Raw captures: `s3374_m5_retail_pcm_writer/oracle.log` and
`s3374_m5_retail_pcm_writer_values/oracle.log`.
