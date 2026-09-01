# NEXT work unit — M5 selector writer input/initializer boundary

HYPOTHESIS-ID: m5-selector-writer-input-boundary

Session 3509 selected a real port-versus-retail value divergence at the
corrected stores `0x8008F228`/`0x8008F264` to
`0x80149758`/`0x8014975C`.

Competing hypotheses and discriminating measurement:

- `H-InputParity`: writer register/input context and selector index match
  across runtimes; the difference is an earlier table initializer value.
- `H-InputDivergence`: the first writer input or index differs, selecting the
  upstream producer/selection edge.
- `H-PortWriterRoute`: the port reaches the stores through a materially
  different caller/route despite matching writer PCs.
- `H-CaptureInvalid`: either independent retail whole-RDRAM/title controls or
  the port title/schema controls fail; the join is unevaluable.

Discriminating measurement: one batched retail/port capture that keeps the
whole-RDRAM control, corrected table-store watch, existing selector pre-call
and load controls, and the new store-register context. Join by title origin,
table address, writer PC, stored value, writer arguments/registers, and
selector index. Matching inputs with differing stored values selects an
earlier initializer; a first differing input/index selects that producer; a
route-only difference selects dispatch divergence; missing controls invalidate
the result.

Use the validated real-image/LLE/spin-yield/autopilot route and SIGKILL the
game after the bounded watchdog. Run the independent retail oracle first with
the whole-RDRAM control and corrected table span. Do not repeat the unchanged
3509 store census.
