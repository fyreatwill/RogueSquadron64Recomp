# s2904 M5 Step 6 drain-tick validation

Date: 2026-08-27

The Debug target built successfully. The existing validation harness launched
the retail oracle and same-build `tick_off` and `tick_on` port arms. The oracle
positive control reached its 10,000 whole-RDRAM-write threshold (`oracle_gate=1`).

Both port arms reached only pre-title `VI 640 @ 0x0066A500`. Each emitted 44
`[audtask-dispatch]` controls, while neither emitted the target-phase drain,
task-ABI, DMA/image-stage, SP-completion, PCM, or audio-return markers. Neither
arm emitted `[CRASH]` or `[ABORT]`. The phase gate therefore did not qualify
the Step 6 A/B comparison; the identical dispatch counts do not prove drain
equivalence.

Selection: `H-RouteInvalid` for this recipe. `H-DrainDefaultSafe` and
`H-DrainTickRequired` remain unevaluable. No behavior change or mitigation is
authorized.
