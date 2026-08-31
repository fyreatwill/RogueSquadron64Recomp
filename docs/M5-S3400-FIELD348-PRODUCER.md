# M5 s3400 — field348 producer census

The fresh build ran `run_s2285_m5_step1_contract_pair.sh` with the field348
writer, candidate, memset, and static `rs_memset` caller probes enabled. The
retail arm passed the whole-RDRAM control, title 1024 gate, hangar 512 gate,
and checkpoint; its `0x1935E0` checkpoint retained 18 post-store samples,
including 12 nonzero samples from `0x800078EC`.

Both port arms reached title and hangar without crash or abort. The image arm
reported stage 3 with `field348=0x801797B0` on every sampled row and copied
DMEM `0xCB0..0xE48` to `0x1798B0` with `762B22A5`, `nz=0`. Its field348 span
was zero-valued (`25E26BC5`, `nz=0`). The field348 buffer was initialized by
the target zero-fill at `0x8008F2CC` (`dst=0x801797B0`, `len=0x298`), and the
only observed span writer was `0x800078EC`, writing zero bytes. DMA/exit,
guest service, and PCM controls remained live; PCM stayed zero.

This selects `H-PortStage3Field348ProducerGap` as a content/producer-contract
gap at the observed boundary and refutes `H-PortStage3Alias` and
`H-PortStage3LegitimateZero` for the retail-equivalent publication. It does
not yet identify the input that should precede the port zero-fill. No audio
behavior or mitigation changed. Evidence: `scratch/agent/s3400_m5_field348_producer_census/`.
