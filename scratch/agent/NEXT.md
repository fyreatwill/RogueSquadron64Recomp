# Next work unit

HYPOTHESIS-ID: m5-retail-writer-store-attribution

Run one bounded retail-only store-site capture around `0x80091784`. s4935
passed the whole-RDRAM and VI controls, but its stable auxiliary context and
zero independent type-2 task rows select H-auxiliary-writer. Identify the
physical destination and source register/value for phase-gated stores in
hangar `0x006AB400`, first mission `0x00690400`, and following mission
`0x00620400`. Do not change runtime behavior.

Competing hypotheses and discriminator:

1. H-task-store: a phase-gated store in the `0x80091784` neighborhood writes
   an OSTask field or task-adjacent publication value.
2. H-auxiliary-store: the stores target an auxiliary table/cadence field and
   never an OSTask-shaped destination.
3. H-capture-invalid: whole-RDRAM or VI controls fail, so store nulls are not
   interpretable.

The discriminating measurement is the bounded phase-gated store-field table
for the writer's exact store sites, joined to `--watch-pc 0x80091784` and
`--pc-task-dump 0x80033FCC --pc-task-type 2`. A task-adjacent destination
selects H-task-store; stable auxiliary destinations select H-auxiliary-store;
a failed control selects H-capture-invalid. Use the same 240-second recipe,
with `--watch-pc-range 0x80091600:0x80091840` and the oracle's
`--store-field-dump` option once exact store PCs are enumerated from the range
output.
