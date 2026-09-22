# Next work unit: join the final source writer to the zero output DMA

HYPOTHESIS-ID: m5-source-overwrite-order

S3702 selected `H-PrePhaseScalarProducer`: both qualified port arms recorded
652 source-range stores, including retail-shaped producer PCs before target
route publication, followed by the zero-valued `0x800078EC` fill. The output
DMA still carried zero bytes.

Competing hypotheses:

- `H-ProducerAfterClear`: a nonzero source-range writer follows `0x800078EC`
  and is the producer consumed by the output DMA.
- `H-ClearIsFinal`: `0x800078EC` is the final source-range writer before the
  output DMA, explaining the zero payload.
- `H-DescriptorOrdering`: a descriptor/publication edge makes the apparent
  final writer belong to another task or range.

Discriminator: retain the retail writer census, RSP/DMEM controls, and 512
output rows in one phase-gated port run, but log the monotonic source-store
sequence in each output-DMA row (writer PC/range/value/sequence and DMA source
FNV). A nonzero writer after the zero-fill selects `H-ProducerAfterClear`;
only the zero-fill immediately before zero DMA selects `H-ClearIsFinal`; a
writer with a different route/task identity selects `H-DescriptorOrdering`.

Use the existing source-writer driver as the starting point, keep the RSP,
DMEM, retail, and 512-row positive controls live, build once with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through the existing paired driver with
`env ROGUESQ_LOG_M5_SOURCE_PRODUCER=1 zsh
scratch/agent/run_s3692_m5_input_payload_writer.sh`, and kill with SIGKILL
after the qualified 512 hangar rows are captured. Expected splits are:
post-clear nonzero writer, final zero-fill, or mismatched route/task identity.
