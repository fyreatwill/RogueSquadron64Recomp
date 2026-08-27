# s2673 M5 ring-writer ground truth

The independent retail oracle passed its whole-RDRAM positive control (`23,087`
watch hits) and reached the target phase (`512`, `0x006AB400`). Exact watches
completed with `12,288` writes to `0x166450:0x169450`, `717` writes to
`0x1798B0:0x179A48`, and `82` writes to `0x141AD0:0x141AF0`. The watched
execution at `0x800078EC` was live in phase; its predecessor histogram was
`0x8002BEEC:507`, `0x800078EC:22,363`, `0x800078F8:9,057,029`, and
`0x800078E8:27,216`. The completed watch table supplied no same-event writer
PC/value row for the ring, so execution of `0x800078EC` does not prove it wrote
the ring.

The port image arm reached hangar with 9,272 image-stage rows, 4,609
DMA-range rows, 72 PCM-source rows, and 72 PCM-consumer rows, with zero crash
or abort markers. Every observed target-phase stage-2 row in the ring was
zero-valued. The only target-phase nonzero image payloads were outside the ring
at `0x168850` (`nz=621`) and `0x168B50` (`nz=639`). Stage 3 at
`0x1798B0` was zero-valued.

| source | target-phase span | writer/event | payload/value | order evidence | result |
|---|---|---|---|---|---|
| retail oracle | `0x166450:0x169450` | exact watch: 12,288 writes; `0x800078EC` executed | value/payload not retained in completed watch table | no same-event writer/order row | writer unresolved |
| retail oracle | `0x1798B0:0x179A48` | exact watch: 717 writes | value/payload not retained | no same-event writer/order row | secondary writer unresolved |
| port image | rotating `0x166xxx`, `0x300` windows | Factor 5 stage 2 DMA | all observed ring rows `source_nz=0`, `capture_nz=0`, `retained_nz=0` | stage/PCM rows live but zero | no image-ring join |
| port image | `0x168850`, `0x168B50` | Factor 5 stage 2 DMA | `nz=621`, `nz=639`; retained `nz=0` | source/consumer rows present | non-ring output |
| port image | `0x1798B0:0x179A48` | Factor 5 stage 3 DMA | `nz=0` | stage rows live; PCM join absent | no stage-3 join |

The positive controls prove both phase drivers were live, but no row supplies a
legitimate named writer plus destination, payload polarity, and completion-to-
consumer order. This selects `H-ring-unmapped` and leaves the CPU-side MORT
publication edge as the next M5 target. No writeback, remap, gate, or
mitigation is authorized by this result.
