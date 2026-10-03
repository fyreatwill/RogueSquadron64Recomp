# M5 s3765 — pre-input producer boundary

The existing s3762 same-build oracle/image/silent capture was re-read without
building or adding instrumentation. The oracle positive control passed
(`whole_rdram=10000`), and the image and silent arms both reached title and
hangar.

For the image arm, 33 phase-5, width-512 input-DMA rows used
`dram=0x1798B0`, `len=0x198`, and `dmem=0xCB0`. Every row had
`input_fnv=0x762B22A5`, `input_nz=0`, and an empty `prev_writer_*` tuple.
The corresponding image-stage rows preserved the same zero payload through
stage 2 and stage 3. The separate field-writer census recorded the known
zero-valued writer `PC=0x800078EC` across the source-span clear
(`0x1797B0..0x179A48`, including the input range), with no nonzero value.

This selects `H-M5-ProducerAbsent` for the measured pre-input producer
classes and identifies the known zero clear as the last observed writer. It
does not prove why that clear is reached, whether another computed/non-native
producer is missing, or that the clear should be suppressed. The next probe
must join the clear's caller/ordering to the route and retail writer timing.
