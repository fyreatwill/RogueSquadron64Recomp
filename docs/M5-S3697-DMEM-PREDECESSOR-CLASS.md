# M5 s3697 — qualified DMEM predecessor classification

## Question

Does the latest host-observed DMEM writer explain the zero payload emitted by
the qualified hangar source-range DMA, or is it an unrelated predecessor?

## Independent retail ground truth

Before the port build, the retail oracle ran for 65 seconds with a whole-RDRAM
positive control and the target physical range `0x1797B0..0x179930`. The
whole-RDRAM watch reached 10,000 callbacks and was removed. Retail then
reported 1,058 target-range writes through the 512-width hangar phase. The
phase-gated writer histogram was:

| Retail writer PC | Writes |
|---|---:|
| `0x800078EC` | 768 |
| `0x80007670` | 172 |
| `0x8001E2C0` | 11 |
| `0x8001F...` family | 107 |

The oracle's `post-store-scalar` sample for `0x800078EC` was 256/256 zero,
with zero mismatches and zero unsupported stores. Thus a legitimate zero
scalar writer exists in retail, but it is not the complete retail writer
contract: the `0x80007670` and `0x8001F...` families also write the watched
range.

## Qualified port run

The Debug target was rebuilt once. The real-audio arm used the validated
LLE-forced, ungated, solo, spin-yield, autopilot route and was phase-gated at
VI 1024 before following the 512 hangar transition. Both positive controls
fired: the RSP-source hook control fired once and the phase source controls
fired for title and hangar.

The hangar table contained 512 source-range rows. Every row had zero DMEM
payload bytes and zero post-write RDRAM bytes. The latest joined DMEM
predecessor was a zero-valued vector write on all 512 rows. Only 147/512
predecessors overlapped the output DMA's DMEM window; 365/512 did not. The
predecessor route ordinal was newer than the source route on 274/512 rows and
equal on 238/512; none was older. The port's DMEM writer census had 1,024
hangar rows, so the join was live rather than a null instrument.

## Classification

This selects `H-DMEMWriterWrongWindow` for the latest-predecessor explanation.
The last observed vector store is not a stable producer for the output window:
most joined stores do not overlap it, and the overlapping stores cover only a
two-byte edge while the DMA reads `0xC30`/`0xCB0` ranges. The all-zero payload
is therefore still unexplained upstream. The retail writer contract also
keeps `H-RetailSourceDifferent` open: the port's host-side vector DMEM table
does not account for retail's named scalar/vector writer families.

No mitigation or guard was added. The zero writer is treated as observed
state, not as proof that zero is legitimate for the output window.

## Reproduction artifacts

- Retail oracle capture: `/tmp/rs64_s3697_retail_dmem_boundary.log`
- Port log: `scratch/agent/s3697_m5_dmem_predecessor/run.log`
- Run recipe: qualified `tools/probe.sh` invocation recorded in the session
  ledger.
