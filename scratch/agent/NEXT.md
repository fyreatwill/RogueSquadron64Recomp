# NEXT work unit (s2979) — M5 audio de-stubbing design

HYPOTHESIS-ID: m5-audio-destub-design

## Unit

Create `docs/M5-AUDIO-PLAN.md`, a bounded design document for the first
incremental M5 audio de-stubbing step. Survey every active audio stub, trap,
early return, and environment gate in `src/main/main.cpp`,
`src/rsp/aspMain.cpp`, and the maintained runtime/audio paths. For each one,
record its current contract, whether it is Factor 5 MORT or stock ASP, the
smallest safe replacement, and a same-build validation soak with a positive
control. Do not change runtime behavior in this unit.

## Competing hypotheses and discriminator

- `H-audio-stubs-are-independent`: each stub can be replaced and validated as
  a separate contract; the survey identifies an ordered first step.
- `H-audio-stubs-share-one-contract`: the stubs are coupled through task,
  DMA, slot, or queue state; the survey must identify the shared invariant
  before any replacement.
- `H-audio-path-is-not-locally-actionable`: required MORT inputs or code are
  absent from the maintained tree; the plan must document the exact external
  dependency and choose a non-audio follow-up.

The discriminator is a complete table of all active gates/stubs and their
callers/data contracts, cross-checked against the ROM/configuration symbols:
an ordered locally implementable first step selects the first hypothesis, a
shared state invariant selects the second, and a missing required input
selects the third. The document must include the positive-control marker and
phase-gated soak recipe for the proposed first step.

## Evidence commands

```sh
rg -n -i 'audio|musyx|mort|aspMain|AUDTASK|audio_ucode|audio.*stub|return.*Broke|RspExitReason::Broke' src lib include syms tools
sed -n '1,260p' src/main/main.cpp
sed -n '1,220p' src/rsp/aspMain.cpp
rg -n 'M_AUDTASK|submit_rsp_task|audio' docs README.md tools
```

Do not run the route-preparation capture again unless a new local repair or
ground-truth handoff changes the measured VI-640 stall.
