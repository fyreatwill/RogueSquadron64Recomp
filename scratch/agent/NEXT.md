# Next work unit: validate the zero-fill object and ordering

HYPOTHESIS-ID: m5-source-clear-legitimacy

S3703 selected `H-ClearIsFinal`: both qualified port arms recorded 652
source-range stores, and the final observed writer was the zero-valued
`0x800078EC` fill. The real arm then emitted 512 zero output-DMA rows.

Competing hypotheses:

- `H-ClearWrongObject`: the fill destination/length or route/task identity does
  not match the image source object.
- `H-ClearLegitimateButEarly`: the fill is the expected `0x801797B0`/`0x298`
  clear on the same route, but occurs at the wrong stage of the producer.
- `H-ProducerAfterClear`: a later nonzero producer exists but was missed by the
  current source-store witness.

Discriminator: retain the retail writer census, RSP/DMEM controls, and 512
output rows in one phase-gated port run, but join the `0x800078EC` call's
destination, length, route/task identity, and ordering to each output-DMA row.
A wrong range/owner selects `H-ClearWrongObject`; the expected clear on the
same route selects `H-ClearLegitimateButEarly`; a later nonzero writer selects
`H-ProducerAfterClear`.

Before building, inspect the existing `0x800078EC` call-site witness and the
retail oracle's matching PC watch. Build once with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through a self-contained paired driver based on
`scratch/agent/run_s3692_m5_input_payload_writer.sh`, adding the clear-call
fields and preserving all controls. Kill with SIGKILL after the qualified 512
hangar rows are captured. Expected splits are wrong object/range, expected
clear on the same route, or a missed post-clear writer.
