# NEXT work unit — identify port callers of the selector AI boundary

HYPOTHESIS-ID: m5-selector-producer-context

Session 3520 qualified retail execution at `0x80029E78`, but the port's
corresponding `osAiSetFrequency_recomp` hook was absent in the hangar despite
a startup positive control and live downstream selector-store controls. The
next single work unit is to label every generated port callsite entering
`osAiSetFrequency_recomp`, then run the independent retail caller watch and
the qualified real-audio port route in one batched build/run.

Before building, arm the oracle with whole-RDRAM and selector-span controls,
`--watch-pc 0x80029E78`, and `--pc-phase-log-width 0x006AB400:512`. Add
callsite IDs to the two known generated calls at `0x80091BAC` and
`0x80091CB8`; keep the native boundary positive control and hangar rows, plus
the existing producer/store controls. Use `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, and the validated real-audio LLE/spin-yield/
autopilot route. Do not rewrite audio, selector, task, or output state.

Competing hypotheses:

- `H-PortCallMissing`: no port callsite enters the native AI primitive during
  hangar, selecting a missing or route-gated call.
- `H-PortCallerMismatch`: a target-phase port call exists but its caller or
  arguments differ from retail, selecting that caller edge.
- `H-RetailEquivalentMismatch`: the retail instruction is not equivalent to
  the host primitive, so matching callsite activity does not explain the
  watch-PC row.
- `H-CaptureInvalid`: whole-RDRAM, selector-span, startup hook, or phase/store
  controls fail.

The discriminator is the first phase-matched port callsite row against the
retail `0x80029E78` caller row. No target-phase port call with live controls
selects `H-PortCallMissing`; a target-phase call with differing arguments
selects `H-PortCallerMismatch`; matching call activity with no correspondence
selects `H-RetailEquivalentMismatch`; failed controls select capture invalid.
