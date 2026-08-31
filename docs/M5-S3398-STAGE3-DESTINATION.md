# M5 Session 3398 — stage-3 destination qualification

The existing checkpointed contract recipe was rebuilt once and run with the
retail oracle plus concurrent silent and image port arms.

The retail whole-RDRAM positive control reached 10,000 callbacks, and title
and hangar phase gates fired. Its `0x1935E0` watch recorded 34 writes; the
checkpoint retained 18 post-store samples, including 12 nonzero samples from
guest writer `0x800078EC`.

Both port arms reached hangar without crash/abort markers. The image arm had
2,753 image-stage and 1,372 DMA rows. Stage 3 completed from DMEM `0xCB0`,
length `0x198`, to `0x801798B0` (`0x1798B0` physical), with zero payload
(`762B22A5`, `nz=0`), and no matching publication to `0x1935E0`. DMA/exit,
external SP delivery, guest receive, and PCM-boundary rows were present; PCM
remained zero (`FNV=F59C39C5`, `nz=0`). The silent arm supplied the route
control with 682 ABI/DMA rows and no image-stage rows.

The independent retail writer evidence and same-build port route evidence
select `H-PortStage3Missing` at the observed publication boundary and refute
`H-PortStage3Alias` and `H-PortStage3LegitimateZero` at that boundary. This
does not identify why the destination differs or whether the zero DMEM output
is legitimate. No audio behavior changed.

Evidence: `scratch/agent/s3398_m5_stage3_destination_pair/driver.log`,
`oracle.log`, and the paired port logs.
