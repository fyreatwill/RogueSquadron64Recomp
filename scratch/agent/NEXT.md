# Next work unit: trace the producer/layout of the zero RDRAM source

HYPOTHESIS-ID: m5-dmem-dma-source

S3701 selected `H-RetailSourceDifferent`: retail reached hangar and wrote the
source range through distinct hangar writer families, while the qualified
port's first 512 rows joined the correct `0x1798B0..0x179A48` DMA with zero
source and post-DMA payloads and no current scalar writer.

Competing hypotheses:

- `H-PortSourceProducer`: a legitimate non-scalar or descriptor producer
  supplies the source through a path not covered by the current writer census.
- `H-ProducerOmission`: the port never performs the retail-equivalent source
  production/publication before the DMA.
- `H-InputDescriptorWrong`: the source range is correct by address but belongs
  to a divergent descriptor owner/layout.

Discriminator: obtain the retail writer/descriptor census first, then build
one phase-gated port table that joins the source descriptor publication and
every scalar/vector/RDRAM-DMA producer to the first 512 hangar source rows.
A nonzero retail-matching producer selects `H-PortSourceProducer`; no
producer selects `H-ProducerOmission`; a divergent owner/range reopens
`H-InputDescriptorWrong`.

Use the existing source-writer driver as the starting point, keep the RSP,
DMEM, retail, and 512-row positive controls live, build once with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through a self-contained driver and kill with
SIGKILL after the qualified 512 hangar rows are captured.
