# NEXT work unit — audit the caller-side state-pointer selection idiom

HYPOTHESIS-ID: m5-state-pointer-writer

Session 3475 ruled out the four measured latest candidate links as the direct
source of incoming `rs_free` `$s1`; do not repeat that join unchanged.

Competing hypotheses and discriminating outcomes:

- `H-UninstrumentedWriter`: a caller-side load/assignment supplies the
  consumer `$s1`; matching its value to the next `rs_free` entry selects it.
- `H-AlternateDispatch`: no caller-side assignment/load in the complete
  enumerated idiom supplies the observed value; live entry rows without a
  match select this at the audited scope.
- `H-ObservationInvalid`: controls or entry rows fail; no conclusion is
  allowed without same-run positive controls.

Discriminating measurement: enumerate every generated caller-side load or
assignment of `$s1` feeding the `0x80005268 -> rs_free` edge, then add one
regeneration-safe, title-gated table containing site PC, loaded source/address,
value, caller ordinal, and the immediately following `rs_free` `$s1`. Keep the
pointer-checkpoint and four-PC controls, and run one image arm only.

Before building, inspect all generated callers of `rs_zcfree` and the
`0x80005268` edge. Ask the retail oracle first with whole-RDRAM control plus
the identified caller PCs and any source-address watches. Then batch all port
hooks in one build and run from `build/` using the validated LLE/spin-yield
route from Session 3475.

Expected outcomes: an exact caller load/value-to-entry match selects
`H-UninstrumentedWriter`; live controls and consumer rows with no match after
complete enumeration select `H-AlternateDispatch`; missing controls or
entries are `H-ObservationInvalid` and require redesign.
