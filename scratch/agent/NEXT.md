# NEXT work unit (s2417) — obtain an independent phase-transition handoff witness

HYPOTHESIS-ID: m5-phase-transition-identity

## Work unit

Ask the retail oracle for one independent, positive-controlled witness of the
title-to-hangar handoff before adding any port instrumentation. Cover
whole-RDRAM, title `0x00790400`, hangar `0x006AB400`, and a bounded watch on a
task/data or slot field that can distinguish the two valid port task ordinals.
If retail attributes a stable writer/reader relation, add one batched port
probe for exactly that relation; otherwise record the oracle limitation and do
not alter runtime behavior.

## Competing hypotheses and discriminator

- H-RetailStableWriter: retail attributes a stable handoff writer/reader that
  can be mapped to a port field.
- H-RetailPhaseOnly: retail confirms the handoff but only phase/order survives;
  no field-level port instrument is justified.
- H-RetailNoCoverage: the oracle reaches title/hangar controls but cannot
  observe the relevant handoff, leaving port identity open.
- H-RetailWatchMisarmed: a positive control fails, so the run is invalid and
  must be fixed before interpreting a null.

The discriminator is the oracle's positive-control and handoff-attribution
table. A stable retail writer/reader relation selects H-RetailStableWriter;
phase-only attribution selects H-RetailPhaseOnly; no relevant coverage selects
H-RetailNoCoverage; a failed positive control selects H-RetailWatchMisarmed.
Do not interpret zero-valued payloads as identity.

## Exact commands

Use the oracle instructions in `tools/oracle/README.md`. Arm the whole-RDRAM
positive control first, then the exact title/hangar windows and one candidate
handoff watch in the same run. Run from the oracle's prescribed directory,
capture the bounded result under `scratch/agent/s2417_retail_handoff/`, and
SIGKILL the emulator process group. Do not build until the oracle positive
control visibly fires.
