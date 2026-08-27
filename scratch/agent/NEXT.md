# NEXT work unit (s2658) — attribute retail task output-field writers

HYPOTHESIS-ID: m5-task-output-writer-attribution

## Work unit

Use the independent retail oracle to watch the physical task fields at
`0x149498` and `0x14949C` (task `0x80149470` plus offsets `0x28`/`0x2C`) with
PC attribution, while retaining the whole-RDRAM positive control and
title/hangar phase gates. In the same iteration, run the existing port
image/silent pair with current task ABI/dispatch rows as controls. Do not add
writeback, remapping, or a guest/host guard.

## Competing hypotheses and discriminator

- `H-RetailWritesFields`: retail stores legitimate nonzero output metadata
  before dispatch; the port lacks the corresponding producer.
- `H-RetailKeepsFieldsZero`: retail also leaves the fields zero, so output
  metadata is not the missing contract edge.
- `H-RetailWritesOtherTask`: retail writes these fields on another task object;
  the fixed task pointer is a sampling artifact.
- `H-PortOnlyGap`: the retail writer is known, but the port still lacks a
  source-side equivalent.

The discriminator is a phase-keyed PC-attributed write table for both fields,
joined to task pointer, value, previous PC, title/hangar phase, and port
dispatch rows. Whole-RDRAM hits and both route transitions must fire in the
same oracle run; port image must show DMEM/DMA/SP completion while silent shows
no image work. A narrow null without those controls is unevaluable.

## Exact commands

1. Reuse the unchanged oracle recipe represented by
   `scratch/agent/s2656_oracle_task_fields/oracle.log`, adding watches only
   for physical `0x149498:0x14949C` and `0x14949C:0x1494A0` (or the oracle's
   equivalent two 4-byte ranges), retaining the whole-RDRAM and phase
   controls.
2. Run `scratch/agent/run_s2656_m5_task_producer.sh` unchanged from `build/`
   for the port image/silent pair; SIGKILL remaining processes.
3. Parse writer PC/value/previous-PC rows by title and hangar, then join them
   to `m5-port-load`, `audtask-abi`, and `audtask-join` rows.

## Expected outcomes

- Nonzero retail stores select `H-RetailWritesFields`; the next unit maps the
  corresponding port-side writer, not writeback.
- Zero retail stores with positive controls select `H-RetailKeepsFields` and
  pivot to the next named output contract edge.
- Stores tied to another task pointer select `H-RetailWritesOtherTask` and
  require tracing the task handoff before changing the port.
