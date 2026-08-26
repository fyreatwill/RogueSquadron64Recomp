# NEXT work unit (s2424) — close guest-store coverage for M5 candidate ranges

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use the existing phase-keyed candidate-range table as the base and add one
bounded observation-only table for guest CPU stores/DMA consumers in
`0x167000:0x169B00`, `0x179800:0x179B00`, and `0x18FC00:0x18FD00`. Join each
row to image ordinal/row, task data pointer, DMA destination, and SP return.
Do not change task data, output ranges, gates, guards, dispatch, or defaults.

## Competing hypotheses and discriminator

- H-ImageOnly: the image DMA is the only port writer in the candidate ranges.
- H-PortGuestConsumer: a guest CPU writer/consumer exists and joins the image
  row by phase/range/order.
- H-SharedConsumer: a guest consumer exists but joins only by phase or task
  field, not image ordinal/row.
- H-TableInvalid: route or positive controls fail, so a null is unevaluable.

The discriminator is a single phase-scoped table containing writer kind,
guest PC, address/length/value, image ordinal/row, task data pointer, image
DMA destination, SP return, and PCM/slot controls. A same-row guest writer
selects H-PortGuestConsumer; only phase/task-field association selects
H-SharedConsumer; valid controls with only `kind=2, pc=0` image DMA selects
H-ImageOnly; missing controls selects H-TableInvalid.

## Ground-truth and exact commands

1. Before instrumentation, map the fixup hooks and candidate sites:
   `rg -n 'rs64_m5_pcm_writer_(store|dma)|0x167000|0x179800|0x18FC00|slot-sb|filter-voice' tools src lib`
   and confirm the oracle writer PCs/ranges already recorded in
   `scratch/agent/s2422_m5_writer/oracle.log`.
2. Add only the bounded table in the fixup/runtime hook identified above,
   retaining a positive-control row and all existing phase gates.
3. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
4. Run the oracle-gated two-arm capture with all passive controls:
   `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2424_m5_guest_writer`
5. Summarize only title/hangar phase rows in
   `scratch/agent/s2424_m5_guest_writer/`. Require oracle whole-RDRAM/title/
   hangar controls, both port route controls, and the table positive control.

Expected outcomes: same-row guest writes select H-PortGuestConsumer; only a
phase/task-field join selects H-SharedConsumer; valid controls with no guest
writer beyond image DMA preserve H-ImageOnly. No behavior change is allowed.
