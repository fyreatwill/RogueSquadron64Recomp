# s2469 M5 setup-caller boundary

The retail control run completed with `oracle_rc=0`, whole-RDRAM and driven
VI controls active, and reached the driven 1024 title route. It is independent
ground truth that the route was exercised; this run did not claim retail
execution of the port-only generated caller.

The qualified port run used `ROGUESQ_AUDIO_UCODE=0`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, and `ROGUESQ_LOG_M5_PRETARGET=1`. The resolver positive
control requested `0x8009123C` in phase 4, and the run emitted 23
`[m5-setup-caller]` rows before the existing null dispatch. Every row was:

```
caller=runMenuModelViewerScreen callsite=0x800C2D84
r31=0x00000000 r4=0x800CF090 r5=0x00000000
```

The same run then emitted the existing setup-to-traverse row with `r31=0`,
reported `Failed to find function at 0x00000000`, and aborted with the known
`last-guest-pc=0x80001f88` breadcrumb.

## Discriminator

- Caller-side zero selects `H-SetupCallerZero`: selected.
- Caller-side nonzero with setup entry zero would select
  `H-SetupCallerNonzero`: not observed.
- No live row from the statically selected caller would select
  `H-UnreachableCaller`: refuted; the live row is present.

The 39-callsite static census was regenerated into the fixup output across 11
files. The live phase-4 callsite is therefore identified, but the first caller
that supplies zero to `runMenuModelViewerScreen` remains open. No guard,
stub, dispatch, audio, output, or task-data change was made.
