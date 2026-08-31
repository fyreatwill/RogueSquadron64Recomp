# M5 s3412 downstream producer join

The fresh Debug build was run with the existing phase-qualified silent/image
recipe in `scratch/agent/s3411_m5_downstream_join/`. Both arms passed title VI
1024 and hangar VI 512, had no crash or abort markers, and supplied the task
controls:

| arm | ABI | DMA | image stage | joined rows |
|---|---:|---:|---:|---:|
| silent / `ROGUESQ_AUDIO_UCODE=0` | 1212 | 1212 | 0 | 64 |
| image / `ROGUESQ_AUDIO_UCODE=1` | 1209 | 1209 | 4869 | 64 |

The image arm's hangar route joined the target clear at `0x8008F2CC` to
`field348=0x801797B0`, with `len=0x298` and zero fill. The downstream writer
`0x800078EC` did execute on that route and wrote the source span, but every
observed byte was zero. Stage 3 copied DMEM `0xCB0..0xE48` to `0x801798B0`
with `FNV=762B22A5`, `nz=0`. PCM remained zero. The silent arm had no
image-stage rows, as expected for the control.

This selects `H-PortImageSourceStillZero`: the producer edge is present, but
its input/output is zero on the joined hangar route. It refutes
`H-PortIndirectProducerMissing` at the observed edge and does not support
`H-PortProducerRunsWrongRoute`. The result does not identify why the producer
receives zero input; the next discriminator is an independent retail census
of the corresponding source span and producer phase.
