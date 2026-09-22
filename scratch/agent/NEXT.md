# Next work unit: join the zero DMEM-DMA source to its RDRAM producer

HYPOTHESIS-ID: m5-dmem-dma-source

S3699 closed the coverage gap: the missing `0xCC0..0xCD0` records were
RDRAM-to-DMEM DMA writes on all 255 hangar rows using the `0xCB0` window.
Those DMA bytes and the later output payload are zero. The next discriminator
must identify whether the zero source is a legitimate producer/layout or a
port-side omission.

Competing hypotheses:

- `H-PortSourceProducer`: the port has a legitimate zero-producing source
  writer or descriptor, matching retail's source contract.
- `H-RetailSourceDifferent`: the port's DMA source bytes are zero because the
  retail named writer families are absent or mapped to a different field.
- `H-InputDescriptorWrong`: the `0xCB0` DMA range/owner is not the retail image
  descriptor, despite the same destination span.

Discriminator: in one build/run, carry the pre-DMA RDRAM source range and
bytes/FNV/nonzero, task/event identity, and latest guest scalar/vector writer
covering that range into every 255 hangar `0xCB0` source row. The RSP, DMEM,
and 512-row controls must fire in the same process. Nonzero or retail-matching
source bytes select `H-PortSourceProducer`; zero bytes with no matching writer
select `H-RetailSourceDifferent`; a divergent range or owner selects
`H-InputDescriptorWrong`.

Before the build, refresh retail ground truth with the whole-RDRAM positive
control and `0x1797B0..0x179930` watch. Then enumerate the existing source-DMA
and scalar-writer hooks, add only the source-side join, export submodule
patches if `lib/` changes, and build:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from `build/` with the qualified real-audio/LLE-ungated/LLE-solo/
spin-yield/autopilot route, `ROGUESQ_LOG_M5_RSP_SOURCE=1`, and
`ROGUESQ_LOG_M5_SOURCE_WRITER=1`; kill with SIGKILL after the 512 phase is
captured. The run is invalid unless all three controls and the 512 source rows
appear together.
