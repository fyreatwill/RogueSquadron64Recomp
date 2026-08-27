# NEXT work unit (s2665) — write the M5 audio de-stubbing plan

HYPOTHESIS-ID: m5-audio-destub-plan

## Work unit

Create `docs/M5-AUDIO-PLAN.md`. Survey every audio stub, immediate-return
trap, disabled route, and defensive gate currently in force in `src/`,
`patches/`, the generated fixups, and the runtime integration. For each item,
record its symbol/site, current behavior, retail contract if known, risk,
rollback, and a phase-gated validation soak. Order the smallest incremental
de-stubbing steps so each step has an independent positive control and does
not conflate MusyX RSP with the CPU MORT speech boundary. Do not implement a
de-stub in this work unit.

## Competing hypotheses and discriminator

- `H-Plan-covers-all-gates`: the survey enumerates every active audio stub/trap/
  gate and can assign each one a bounded validation step.
- `H-Plan-misses-live-edge`: at least one active audio behavior is absent from
  the survey or cannot be assigned a contract and positive control.
- `H-Plan-conflates-contracts`: the proposed sequence mixes MusyX RSP task
  execution with CPU MORT publication and therefore lacks a valid rollback or
  discriminator.

The discriminator is one completeness table: every active stub/trap/gate must
have a named owner, current branch behavior, retail/port contract, positive
control, expected phase-gated signal, rollback, and soak recipe. A complete,
separated table selects `H-Plan-covers-all-gates`; any missing site or mixed
contract selects the corresponding hypothesis and requires repairing the plan
before implementation.

## Exact commands

1. `rg -n -i 'stub|noop|no-op|Broke|AUDIO_UCODE|MORT|MusyX|audio' src patches tools ../N64Recomp/RecompiledFuncs/funcs_*.c`
2. Inspect bounded windows around each unique active site and the canonical
   env-var catalog before recording it.
3. Write `docs/M5-AUDIO-PLAN.md` with the complete discriminator table and
   exact one-run-per-step validation recipes. No build or runtime run is
   required for the design-only unit.

## Expected outcomes

- A complete, separated table selects `H-Plan-covers-all-gates`.
- An unlisted active site selects `H-Plan-misses-live-edge`.
- A step that lacks contract separation, rollback, or positive control selects
  `H-Plan-conflates-contracts`.
