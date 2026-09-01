# NEXT work unit — M5 corrected selector-table writer attribution

HYPOTHESIS-ID: m5-selector-table-writer-boundary

Session 3508 corrected the stale `0x80150000` target: the live table is
`0x80149758/0x8014975C`, and retail writes it at `0x8008F228`/`0x8008F264`.

Competing hypotheses and discriminating measurement:

- `H-PortWriterParity`: the port has a corresponding store route/value at the
  corrected table addresses; the first joined writer/value class matches.
- `H-PortWriterDivergence`: the port route is live but its first corrected
  table store/value differs, selecting its writer input or initializer.
- `H-PortWriterAbsent`: retail writer PCs are active while the port has no
  corrected table store despite positive title controls, selecting a route
  difference.
- `H-CaptureInvalid`: either the retail whole-RDRAM control/title or the port
  title/schema control fails; the result is unevaluable.

Discriminating measurement: add one regeneration-safe port witness for stores
to `0x80149758..0x80149760`, while the same build/run keeps the existing
selector pre-call/load/writer controls. Run the independent retail oracle first
with whole-RDRAM control, title phase, `--watch-write 0x149758:0x149760`,
`--post-value-watch`, and `--watch-pc 0x8008F228,0x8008F264`. Join by title
origin, table address, stored value, writer PC, selector index, and caller
arguments. A matching first class selects parity; a differing value or active
retail-only writer selects divergence/absence; missing controls are invalid.

Use the validated real-image/LLE/spin-yield/autopilot route and SIGKILL the
game after the bounded watchdog. Keep the stale `0x80150000` watch retired.
