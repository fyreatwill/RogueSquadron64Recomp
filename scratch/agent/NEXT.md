# NEXT work unit (s2198) — trace the port VI-state publication boundary

HYPOTHESIS-ID: m5-a1-host-vi-commit-boundary

## Work unit

Instrument one bounded, phase-scoped port table across the three host edges:
`osViSwapBuffer_recomp` call, `ViState::update_vi` committed-register update,
and RT64 `update_screen`. Key rows by edge, VI origin, requested/committed
framebuffer, width, and ordinal; retain the existing host caller fields only
as join keys. The table must show whether the retail-matching pair
`(prev_pc=0x8001BE24, a0_phys=0x0062B800)` reaches the port's committed
`0x00696600` state and then `update_screen`.

Before building, add the whole table in one batch: a target-origin swap-call
row, a `ViState::update_vi` commit row after `regs.VI_ORIGIN_REG` and
`regs.VI_WIDTH_REG` are assigned, and an `update_screen` consume row. Keep
each edge bounded to 64 rows per target origin and print a shutdown summary.
Because `lib/N64ModernRuntime` is edited, run
`./submodule-patches/export.sh` after the edit and commit the refreshed patch
in the same iteration.

## Competing hypotheses and discriminator

- H-PortViStateCommit: the matching swap call occurs, but
  `ViState::update_vi` never commits `0x00696600`; the boundary is the VI
  thread's pending-state application.
- H-PortScreenConsume: `update_vi` commits `0x00696600`, but RT64
  `update_screen` never consumes it; the boundary is the renderer event.
- H-PortOriginAliasing: the swap call occurs, but the mode/field calculation
  commits a different origin or framebuffer than the requested
  `0x0062B800` pair.
- H-CoverageFailure: the same-run caller control, writer control, or either
  target phase is absent; reject the comparison rather than treating a null
  edge as evidence.

The single joined edge table selects: swap present + commit absent selects
H-PortViStateCommit; commit present + consume absent selects
H-PortScreenConsume; a wrong committed origin/framebuffer selects
H-PortOriginAliasing; missing controls selects H-CoverageFailure.

## Build and run

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_M5_WRITER_PARITY=1 ROGUESQ_LOG_VI_COMMIT=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2198_vi_commit 30 12
```

Accept the run only if `[vi-callers-control]` fires, the writer control is
positive, and the log reaches repeated 640 rows at both
`0x00696100` and `0x00696600`. Do not add a guard, mitigation, task rewrite,
writer filter, or audio-default change.
