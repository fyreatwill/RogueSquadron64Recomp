# Next work unit: identify the port-side writer/layout producer for the zero source

HYPOTHESIS-ID: m5-dmem-dma-source

S3700 joined all 512 hangar output rows to the expected `0x1798B0..0x179A48`
RDRAM-to-DMEM source DMA. The source and output payloads were zero, and the
port's latest writer remained the title `0x800078EC` zero-fill. Retail's
independent census showed distinct hangar writer families.

Competing hypotheses:

- `H-PortSourceProducer`: the port has a legitimate source writer/layout
  matching retail's source contract.
- `H-RetailSourceDifferent`: the port's DMA source bytes are zero because the
  retail named writer families are absent or mapped to a different field.
- `H-InputDescriptorWrong`: the `0xCB0` DMA range/owner is not the retail image
  descriptor, despite the same destination span.

Discriminator: in one build/run, extend the source-side table through
`0x179A48` and carry every scalar/vector/DMA writer or descriptor producer into
the 512 hangar source rows. The RSP, DMEM, retail, and 512-row controls must
fire together. A retail-matching port writer selects `H-PortSourceProducer`;
no matching writer selects `H-RetailSourceDifferent`; a divergent range or
owner reopens `H-InputDescriptorWrong`.

Before building, obtain independent retail ground truth with the whole-RDRAM
positive control, target-span watch, title/hangar phase gates, and writer-PC
histogram. Enumerate the existing `rs64_m5_pre_dma_writer_store` coverage and
the source-DMA snapshots. Extend the phase-gated table through `0x179A48` so
each output row carries the latest scalar/vector/DMA producer covering its
source range. No `lib/` edit is expected.

Build once:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from `build/` with the qualified real-audio/LLE-ungated/LLE-solo/
spin-yield/autopilot driver `scratch/agent/run_s3537_m5_output_writer.sh`,
inheriting `ROGUESQ_LOG_M5_SOURCE_WRITER=1` and the RSP/source controls; kill
with SIGKILL after the 512 phase is captured. The run is invalid unless the
retail preflight, both target VIs, RSP and DMEM controls, and 512 source rows
appear together. A retail-matching writer selects `H-PortSourceProducer`; no
writer selects `H-RetailSourceDifferent`; a divergent source range/owner
reopens `H-InputDescriptorWrong`.
