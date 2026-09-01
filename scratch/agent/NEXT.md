# NEXT work unit — census the selector route gate or alternate caller

HYPOTHESIS-ID: m5-selector-route-gate

Session 3521 selected `H-PortCallMissing`: retail executed `0x80029E78` in
hangar, while both known generated port calls (`0x80091BAC`, `0x80091CB8`)
were absent there despite startup controls and live producer/store controls.
The next single work unit is a static census plus one phase-qualified runtime
probe of the route gate or an alternate caller; do not repeat those callsites.

Before building, enumerate every generated reference to `0x80029D20` and
`osAiSetFrequency_recomp` across `../N64Recomp/RecompiledFuncs`; inspect the
smallest enclosing generated functions and branch guards. Add labels to any
additional direct/wrapper call, and one phase-scoped probe at the first route
gate that can suppress those calls. Run the independent retail
`--watch-pc 0x80029E78` capture with whole-RDRAM and selector-span controls in
the same iteration. Use `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`,
and the validated real-audio LLE/spin-yield/autopilot route.

Competing hypotheses:

- `H-RouteGate`: the known calls are suppressed by a branch/state gate before
  their callsites during hangar.
- `H-AlternateCaller`: a different generated caller or wrapper reaches the
  equivalent host primitive, so the known-call census is incomplete.
- `H-RetailEquivalentMismatch`: the retail instruction is not equivalent to
  the host primitive; a port-side call may be elsewhere or absent for an
  intentional route difference.
- `H-CaptureInvalid`: whole-RDRAM, selector-span, startup hook, or phase/store
  controls fail.

The discriminator is the first phase-matched gate/call row against the retail
`0x80029E78` caller row. A live gate with a suppressed known call selects
`H-RouteGate`; a target-phase alternate call selects `H-AlternateCaller`; no
gate or alternate call with all controls live selects
`H-RetailEquivalentMismatch`; failed controls select capture invalid.
