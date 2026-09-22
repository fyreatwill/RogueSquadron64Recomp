# Next work unit: identify the selector input writer before the early clear

HYPOTHESIS-ID: m5-selector-input-writer

S3709 selected `H-CallerSelectorRoute`: retail and both port arms matched at
`0x80091934`/`0x8008F0A0` (`a1=0x561F`, `a2=0`, `s0=0x12`, `s2=1`, `s3=0`).
The next boundary is the value loaded from `MEM_W(0x80165ED0)` at
`0x8009192C`, immediately before the allocator call.

Competing hypotheses:

- `H-SelectorInputWriterParity`: the port writer PC/value sequence matches
  retail and the input is legitimately `0x561F`; the early clear is downstream
  of a matching selector state.
- `H-SelectorInputWriterDivergence`: the port writes `0x561F` from a different
  PC or with a different preceding state than retail, selecting the clear route
  through a port-specific producer difference.
- `H-SelectorInputNotWriter`: the observed load is stale or sourced from an
  earlier publication, so the relevant discriminator is the pointer/source
  chain rather than the final scalar writer.

Discriminator: one phase-gated writer/source table for physical
`0x80165ED0`, the `0x8009192C` load, and the `0x80091934` caller, carrying
writer PC, value, source pointer, route ordinal/row, latest producer sequence,
and predecessor ordering. Retail and both port arms must pass positive
controls. A matching writer PC/value/order selects `H-SelectorInputWriterParity`;
a port-only writer/state selects `H-SelectorInputWriterDivergence`; no writer
with a valid pointer/source join selects `H-SelectorInputNotWriter`.

Build:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the real/silent paired arms from one build with the existing route recipe,
adding the new phase-gated writer probe:

`zsh scratch/agent/run_s3710_m5_selector_input_writer.sh`

Do not alter the clear, selector state, audio route, or payload.
