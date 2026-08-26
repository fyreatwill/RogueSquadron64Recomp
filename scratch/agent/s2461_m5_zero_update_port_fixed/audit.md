# s2461 M5 zero-update resolver-edge capture

## Ground truth control

The retail oracle ran for 70 seconds with Rice, the whole-RDRAM write watch,
the 512/0x006AB400 phase drive, and watches at `0x8002BEEC` and `0x800078EC`.
The positive control reached 11,206,982 writes. It reached the target hangar
phase and observed `0x800078EC` 624 times with predecessor `0x8002BEEC`.

## Port capture

Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`

Qualified environment: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`,
`ROGUESQ_AUDIO_UCODE=1`, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, `ROGUESQ_LOG_SLOT_DISPATCH=1`,
`ROGUESQ_SLOT_DISPATCH_PHASE_MIN=8`, `ROGUESQ_LOG_M5_SECOND_EXEC=1`, and
`ROGUESQ_LOG_A1_ABORT=1`.

The port reached width 1024 after 47.1 seconds and captured one frame. The
indirect resolver positive control fired once at phase 2. The process then
crashed 0.6 seconds into the target frame with `si_addr=0xfffffffffffffff8`
and `last-guest-pc=0x80007904`. There were zero target-phase
`m5-dispatch-boundary`, `slot-dispatch kind=pre`, or `get_function(0)` rows.

The earlier same-run attempt with `ROGUESQ_LOG_ALL=1` also had a live positive
resolver control, but its bounded slot rows were exhausted in phase 6; it was
discarded as non-discriminating. The phase-8 rerun is the corrected capture,
but its pre-target crash still prevents the requested join.

## Result

`H-ResolverControlFailure` is refuted for the corrected run. The capture is a
qualified non-result for `H-ZeroUpdateTerminal` versus
`H-NonzeroSlotThenMatch`; no audio behavior, dispatch guard, output mapping, or
mitigation is authorized.
