# NEXT work unit — attribute the port-side output writer/order edge

HYPOTHESIS-ID: m5-output-contract-boundary

Session 3537 selected `H-MissingOutputWriter`/`H-OutputContractGap`: retail
produced legitimate nonzero PCM/image output at the watched destinations,
while the real-audio port reached both title and hangar and completed the
corresponding joins with zero payloads. No output state was changed.

Next unit: add one batch instrument that phase-keys every write path into the
observed port output destinations and joins it to source-DMA, image-stage,
completion, PCM source, and PCM consumer rows. Cover CPU stores, RSP DMA
writebacks, and any host callback copy. Use the retail PCs
`0x800078EC`, `0x80018F5C`, and `0x80018F60` only as attribution anchors, not
as values to copy.

Competing hypotheses and discriminator:

- `H-PortMissingWriter`: the port has no CPU/host writer for the nonzero
  output edge; select the first missing port writer and its legitimate source.
- `H-PortOrdering`: the port writer exists but a later zero DMA/clear overwrites
  it; select the ordered writer/overwrite pair.
- `H-PortOutputParity`: port and retail writers/order are equivalent and the
  hash observation is not comparable; keep the edge open for a new join.
- `H-CaptureInvalid`: a positive control, target phase, or join key is absent.

The discriminating measurement is one table in one run: phase, destination,
writer kind/PC, payload hash/nonzero count before and after each writer, and
the nearest source/consumer event. Positive controls must include whole-RDRAM
port writes and the existing image/PCM route controls; both title
`0x00790400/1024` and hangar `0x006AB400/512` must be present. Missing writer
selects `H-PortMissingWriter`; nonzero-then-zero ordering selects
`H-PortOrdering`; matching nonzero rows selects `H-PortOutputParity`; failed
controls select `H-CaptureInvalid`.

Exact starting commands:

    sed -n '1,260p' tools/oracle/README.md
    rg -n "pcm|DMA|image-stage|writer|consumer|memset|memcpy" src lib/N64ModernRuntime --glob '!**/*.log'
    zsh scratch/agent/run_s3537_m5_output_writer.sh

Build once after the complete table is designed:

    cmake --build build -j8

Run the full table with the validated real-audio LLE/spin-yield/autopilot
route and the independent retail oracle controls. Do not repeat the silent
arm, copy retail bytes, or add a single-field diagnostic.
