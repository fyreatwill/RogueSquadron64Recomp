# Next work unit (s4337): recover the qualified port hangar route

HYPOTHESIS-ID: m5-step9-port-route-recovery

The s4336 C904/C88C comparison was substituted: all three port arms crashed at
`musyxSynthFrame+4284` after VI 1024 and before VI 512, so zero field rows were
available. First reproduce or falsify the route failure with a bounded route
probe using the same seeded save, then compare only if VI 512 and a C88C row
both fire.

Competing hypotheses:

- H-stale-save-config: the direct probe used a stale or incomplete save/config;
  restoring the known seeded matrix recipe reaches VI 512.
- H-synth-lifetime: the current binary deterministically hits the known
  `musyxSynthFrame+4284` lifetime defect before hangar regardless of A14 yield.
- H-route-schedule: the field probe's key/phase schedule changes the route;
  the known s4332 schedule reaches VI 512 when reproduced exactly.

Discriminator: one bounded A/B run with the known s4332 seeded-save route and
the current field-probe route, both phase-gated to VI 512, recording crash PC,
VI phases, and C88C witness count. H-stale-save-config predicts only the
seeded arm reaches VI 512; H-synth-lifetime predicts identical
`musyxSynthFrame+4284` pre-512 failures; H-route-schedule predicts a VI-512
control in the known route but not the field route. Do not add a guard.

The retail C904 field table remains at
`scratch/agent/oracle_s4335_c904_field.log`; defer comparison until the route
control passes.
