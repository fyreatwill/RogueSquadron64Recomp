# NEXT work unit (s2988) — M5 route repair or independent handoff

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Design and run one genuinely new port-side route repair or independent handoff
probe tied to the retail `bufferArbiterProducerMark` route. Retain the same-run
whole-RDRAM positive control and title/hangar phase gates; do not repeat the
stalled s2972–s2978 capture unchanged.

## Competing hypotheses and discriminator

- `H-port-route-repair`: the new handoff/repair reaches title or hangar and
  makes the M5 Step 1 audio discriminator evaluable.
- `H-port-route-equivalent`: it reaches the target phase but still shows the
  same port-side route behavior as the retail handoff.
- `H-port-route-blocked`: it remains pre-title, so audio downstream nulls stay
  unevaluable and the repair angle is rejected.

The discriminator is one same-run table containing whole-RDRAM control,
handoff/route rows, VI phase gates, target-phase producer rows, and
crash/abort markers. Target-phase rows select a qualified route; a pre-title
stop leaves audio downstream outcomes unevaluable.

## Commands

Inspect the existing route/phase probe and retail handoff artifacts, choose one
new port-side repair or independent handoff, then run its same-build paired
arms with the whole-RDRAM positive control. Build using the project’s Debug
configuration before launching from `build/`; capture results under a new
`scratch/agent/s2988_m5_route_repair/` directory.
