# Next work unit: identify the input/state that makes the shared producer zero

HYPOTHESIS-ID: m5-source-clear-input

S3706 repaired the regeneration fixup and requalified the paired arms. The
target setup and clear use the same `0x801797B0`/`0x298` object, and the final
observed `0x800078EC` writer is a legitimate zero fill before later zero DMAs.
The next work unit must identify why the shared producer's input/state is zero.

Competing hypotheses:

- `H-ProducerInputZero`: the producer receives a legitimate zero input on the
  real-audio route.
- `H-ProducerStateClobbered`: an earlier store changes the producer state before
  the shared-object clear.
- `H-ProducerUsesOtherState`: the observed source-range stores are setup/padding,
  while the actual payload comes from a different state object.

Discriminator: add one phase-gated table at the producer entry/call boundary
that records every candidate input pointer/value and the shared-object word
immediately before the clear, retaining the existing RSP/DMEM/source controls
and both audio arms in one build/run. A zero producer input with unchanged
shared state selects `H-ProducerInputZero`; a changed shared-state word with a
prior writer selects `H-ProducerStateClobbered`; unchanged shared state plus a
different candidate input selects `H-ProducerUsesOtherState`.

Before building, use the retail writer PCs already established at
`0x80007670`, `0x8001E2C0`, and `0x8001F...` as the ground-truth matching set;
do not add a new instrument until its positive control is specified. Build once
with:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the build directory through the paired driver
`scratch/agent/run_s3692_m5_input_payload_writer.sh`, preserving all controls.
Kill with SIGKILL after qualified hangar rows are captured.
