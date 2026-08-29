# Session 3226 — route-state candidate writer audit

## Hypotheses and discriminator

The candidate fields could have been (1) a live pre-title route-state writer,
(2) an unrelated initialization/configuration writer, or (3) a field whose
publication ordering differs between retail and port. A retail physical write
watch, gated by a whole-RDRAM positive control, distinguishes these by writer
PC and timing; a static audit then checks the field's semantic owner and all
port-side stores/consumers.

## Retail oracle

Command used the validated Rice route `3:start,7:start,11:start,15:a,30:start,45:start`
for 45 seconds, with watches on whole RDRAM, `0x141AD0:0x141AD2`, and
`0x13B038:0x13B039`.

- Positive control passed: whole-RDRAM watch reached 10,000 callbacks at 0.7s.
- Retail reached title VI 1024 at `0x00790400` at 16.2s and held it.
- `0x141AD0:0x141AD2` had 8 writes, all during early setup. Writer PCs were
  `0x8008EA44` (1), `0x8008EA74` (1), `0x8008EB8C` (3), and `0x8008EBBC` (3).
- `0x13B038:0x13B039` had 4 writes. Writer PCs were `0x8008EA64` (1) and
  `0x8008EBAC` (3).

## Static audit

The companion architecture map identifies `0x80141AD0` as the display-mode
byte. Current generated code confirms `0x8008EA44`/`0x8008EA54` and
`0x8008EB8C`/`0x8008EB9C` store the validated mode, while the adjacent stores
at `0x8008EA64`/`0x8008EBAC` and `0x8008EA74`/`0x8008EBBC` belong to the same
display/audio setup chain. The route logger's existing callsites are
`reapplyDisplayMode` entry `0x8008EB5C`, its `reapplyAudioConfig` call
`0x8008EBC0`, and the return branch at `0x8008EBC8`; the watched fields are
configuration inputs to that chain, not a newly identified route publication.

## Result

The field candidate is rejected as an unrelated display/audio configuration
class. This does not explain the port's pre-title stop and does not select
`H-StateWriterAbsent`, `H-StateWriterWrongValue`, or `H-StateOrdering` for the
actual route state. No guest value, guard, or mitigation changed.
