# M5 s3537 — output-writer boundary

The batch used the retail oracle's whole-RDRAM positive control, phase-gated
watches for the PCM ring and image destinations, and the candidate writer
watch at `0x800078EC`. Two early port harness attempts stopped at title due
to scheduling/timeout bugs; the fixed run reached both target VIs.

Retail passed the positive control with 22,324 writes, reached title
`0x00790400/1024` and hangar `0x006AB400/512`, and left nonzero output
snapshots: PCM ring 12,054/12,288 bytes, image ranges 761/768 and 761/768.
At `0x1935E0`, title attribution included `0x800078EC` with 12/16 nonzero
samples; hangar attribution included `0x80018F5C` and `0x80018F60`, two
nonzero samples each.

The same-build real-audio port passed startup controls, reached both target
VIs, and executed source DMA, image-stage, image-DMA completion, PCM source,
PCM consumer, and PCM-writer joins. Sampled image-stage and PCM payloads were
zero (`FNV=F59C39C5`, `nz=0`); its bounded PCM-writer rows were DMA (`kind=2`)
rows rather than a nonzero CPU writer.

These are two independent evidence lines and select
`H-MissingOutputWriter`/`H-OutputContractGap` at the observed output scope.
This does not identify the port-side writer or ordering and authorizes no
output-state rewrite. The next unit must attribute that port-side edge.
