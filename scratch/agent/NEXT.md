# Next work unit: M5 qualify live descriptor-selector writers on the port

HYPOTHESIS-ID: m5-port-descriptor-selector-writer

Retail ground truth identified two live hangar-phase selector writers. The
next bounded unit compares those exact writers with the qualified declared-real
port route in one same-build capture.

Competing hypotheses:

- Hport-writer-live: port rows at `0x80090AAC`/`0x80090BA4` carry the same
  selector/source relationship as retail in title or hangar.
- Hport-writer-gap: retail has phase-qualified rows, but the paired port has
  no row from either live writer despite reaching both target VIs.
- Hroute-invalid: either the retail positive control or one port target phase
  is absent, so a port writer null is unevaluable.

Discriminating measurement: one same-build run must retain the retail
whole-RDRAM/title/hangar controls and launch the declared-real port with the
existing phase-gated selector-store witness. Compare rows for exactly
`0x80090AAC` and `0x80090BA4`, including selector, source, phase, and VI
origin/width. Paired port rows with the retail-shaped relationship select
Hport-writer-live; qualified retail rows plus zero port rows select
Hport-writer-gap; missing control or either target phase selects Hroute-invalid.

Ground truth is already checked in `tools/oracle/README.md`; the port witness
is diagnostic-only and no guest behavior change is authorized by this unit.

Commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_M5_SELECTOR_STORE_CONTEXT=1 build/Debug/RogueSquadron64Recomp.exe > /tmp/rs64-port-selector-writer-20261006.log 2>&1`

Run the existing retail oracle command from the prior unit concurrently, saving
it to `/tmp/rs64-retail-selector-writer-20261006.log`; retain its whole-RDRAM
and both phase controls. Inspect only phase-gated rows and the positive-control
markers.
