# NEXT work unit (s2368) — M5 A1 second-origin ground-truth boundary

HYPOTHESIS-ID: m5-a1-second-origin-discriminator

## Work unit

Design and run one ground-truth-first capture for the retail A1 transition.
Restore positive, phase-gated coverage for `0x00696100` and `0x00696600` in
the oracle and port controls, then compare the transition's field/current-line
writer and origin publication rows in one same-build run. Do not repeat the
prior four-arm/two-wave matrix, alter VI selection, write back a field, or add
a guard. If the oracle cannot positively reach both origins, stop with
`H-TimingCaptureInvalid` and do not interpret port nulls.

## Competing hypotheses and discriminating measurement

- H-A1-RetailTransition: the oracle reaches both origins with positive named-PC
  and target-window controls, and the transition has a paired retail writer or
  current-line/source relation that is absent or different on the port.
- H-A1-PortPublisher: both arms reach both origins and the port publishes the
  same transition relation; the remaining A1 gap is not a missing publisher.
- H-A1-CoverageInvalid: either origin or its required positive control is absent
  in the oracle, so no port conclusion is valid.
- H-A1-UnpairedTransition: both origins are positively reached but no paired
  writer/current-line relation exists in either runtime.

The discriminator is one table keyed by VI phase and origin containing oracle
origin counts, named-PC/target-window controls, field/current-line writes,
writer PC, port publication rows, and origin deltas. Select a hypothesis only
when both origin rows and all positive controls are present; otherwise select
`H-A1-CoverageInvalid`.

## Exact commands

    apply_patch < persistent A1 phase/origin table parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2368_m5_a1_second_origin_discriminator.sh s2368_m5_a1_second_origin_discriminator
    grep -E '^(controls|table|verdict) ' scratch/agent/s2368_m5_a1_second_origin_discriminator/driver.log

The driver must run the retail oracle before the port arms, arm whole-RDRAM
and named-PC positive controls, use VI-gated phase budgets, launch all A/B
arms from one build, and kill game processes with SIGKILL. A null without
same-run positive controls is invalid. No behavior change is authorized.
