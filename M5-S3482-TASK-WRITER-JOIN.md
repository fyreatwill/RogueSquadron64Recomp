# M5 Session 3482 — task writer join

The independent Rice oracle and the validated port arm were run with title
phase gates at origins `0x00790400` and `0x00790800`, plus a same-run
whole-RDRAM positive control.

## Controls and reachability

- Oracle whole-RDRAM control: 10,000 callbacks before removal; task-PC
  execution control fired; 1,257 type-2 task rows were captured across 2,307
  phase-qualified executions; title reached both target origins and then
  hangar.
- Port task-handoff control fired twice, the title phase reached origin
  `0x790400`, and the task-writer control fired. The port witness emitted
  2,048 rows before its cap and the host enqueue witness emitted 481 rows.

## Writer route

The oracle's physical task-span watch recorded 52,980 writes. Its title
writer-PC histogram had the same ten PCs at both target origins:

`0x80091718`, `0x8009172C`, `0x8009173C`, `0x80091748`, `0x80091758`,
`0x80091764`, `0x8009176C`, `0x80091774`, `0x8009177C`, and `0x80091784`.

The port witness independently recorded those same ten PCs, 204–205 rows per
PC, writing fields in `0x149470:0x1494B0`. This rules out an absent or wholly
different writer route at this boundary.

## Payload divergence

Retail task rows at `0x80033FCC` used `data_ptr=0x80171CE0` or
`0x80173B20`, with `data_size` 1 or 2. Port enqueue rows also used those
values, but began with `0x8018DD30`/size 3 and `0x8018FB70`/size 1; the port
writer witness shows the corresponding payload fields being stored. Task
type, task pointer, output fields, and yield fields remained equivalent.

This selects the broad payload/operand divergence hypothesis and rules out an
absent observation and a writer-route-only explanation. It does not yet prove
whether the difference is in the value supplied to `0x8009177C/0x80091784`
or a mutation after those stores. The oracle writer histogram has no ordered
post-store value rows, so that exact edge remains open.

The witness is diagnostic-only: it observes generated stores and does not
rewrite, skip, or validate task fields.
