# Generated-symbol rename audit — Session 5107

Candidate: `bzero_recomp` at guest address `0x8002A080`.

- Companion symbol files define `bzero = 0x8002A080`.
- `funcs_7.c` has a callable generated prologue at `0x8002A080`; its body is
  the libc zero-fill routine.
- `recomp_overlays.inl` assigns the entry ROM offset `0x29C40` and span
  `0xA0`; the next entry starts at `0x29CE0`, so the span is exact.
- Three independent generated callers in `funcs_27.c` target guest callsites
  `0x8009BE70`, `0x8009C1B4`, and `0x8009CAF8`.

All semantic-name, exact-span, and live-caller gates passed. The bounded
helper renamed six references across `funcs_7.c`, `funcs_27.c`, `funcs.h`, and
`recomp_overlays.inl`; a follow-up search found no `bzero_recomp` references.
No build or soak was run because this was a generated-symbol naming change.
