# NEXT work unit (s1206)

HYPOTHESIS-ID: retail-execution-path-reachability

Work unit: choose and run one new debugger-enabled retail reachability
comparison that changes the execution path, not just R4300 emulator mode,
paired with an undriven control. Preserve the whole-RDRAM watch,
`--pif-trace`, and `--vi-trace` in both arms. Compare PIF words and VI
transitions/origins, not wall-clock timing. Do not arm an M4 target watch until
a later VI phase is reached. Before building any new arm, inspect the oracle
CLI/config for an available path-changing option and record the exact commands
here.

Competing hypotheses and discriminator:

- H1: a path-changing configuration reaches a later VI phase in the driven arm;
  the previous failure was specific to the tested execution route.
- H2: both arms still remain at VI 320/origin `0x006dd280` while controls pass;
  the failure is independent of the next route change and needs a different
  retail entry strategy.
- H3: either arm fails whole-RDRAM or PIF/VI controls; the comparison is
  invalid and the path hypothesis is untested.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
the driven arm must show the scheduled PIF `0x10000000` press/release pairs;
both arms must emit debugger-enabled VI trace records. A null without all
controls is invalid.

Exact commands: fill in both complete commands after selecting the one
path-changing option; run both arms in this iteration for 60 seconds each.

If H1 is selected, retain the path change and arm the next independent
reachability measurement. If H2 is selected, seek a different retail entry
strategy. If H3 is selected, repair the control setup before drawing any
conclusion.
