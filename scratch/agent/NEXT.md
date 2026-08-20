# NEXT work unit (s2024)

HYPOTHESIS-ID: m5-phase-valid-route-recovery

## RESUME: s2023 phase-gate failure

s2023 regenerated and built the complete instrumented tree, then ran both the
prescribed forced-LLE capture and its `ROGUESQ_SPIN_YIELD=1` correction. The
first stayed at VI 640 until SIGKILL; the second aborted in
`RT64::RenderTarget::copyFromTarget` before VI 1024. Both had live s2020 and
s2022 body controls but no s2008 writer positive-control row. This does not
select H1, H2, or H3.

## Work unit

Recover a phase-valid route before attempting the status-writer join. Use the
same already-built binary and the same passive/body/writer controls in two
arms launched concurrently: arm A is the existing forced-LLE mission runner
with `ROGUESQ_SPIN_YIELD=1`; arm B is a direct no-LLE title/phase launch with
the same logging environment and no input. Each arm stops on VI 1024, a
process loss, or 120 seconds, and the game is killed with SIGKILL. Do not add
instrumentation or change audio behavior.

## Competing hypotheses and discriminator

- H1 `runner-LLE-boundary`: the existing runner's forced LLE path is the
  phase failure; the direct no-LLE arm reaches VI 1024 while arm A aborts or
  stalls before it.
- H2 `generated-tree-render-boundary`: the regenerated binary/runtime fails
  before VI 1024 independent of the LLE choice; both arms abort or stall at
  the same pre-1024 boundary.
- H3 `phase-observer-only`: both arms reach VI 1024, but the current status
  census is not attached to the route that the phase logger observes; the
  s2008 control remains absent while the independent VI transition is live.

The discriminating measurement is the same-build, same-window table of each
arm's first VI 1024 transition, pre-1024 terminal signature, and s2008
positive-control count. Only a VI 1024 arm with a live s2008 control reopens
the writer/read join. A no-LLE-only VI 1024 selects H1; matching pre-1024
RT64 failures select H2; two VI 1024 arms with no writer control select H3.

## Ground truth

No new diagnostic is being built. Still retain the retail whole-RDRAM control
before any rebuild or run:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --hit-cap 1 > scratch/agent/oracle_s2024_whole_control.log 2>&1
```

## Arms

Use one shared `env` prefix containing the existing passive controls:
`ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1
ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1
ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1
ROGUESQ_LOG_S2008_STATUS_WRITERS=1 ROGUESQ_SPIN_YIELD=1`.

Arm A:

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_S2008_STATUS_WRITERS=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2024-lle 0 0
```

Arm B must launch `build/RogueSquadron64Recomp` directly from `build/` with
the same prefix, but without `ROGUESQ_LLE_FORCE`, `ROGUESQ_LLE_UNGATED`, or
`ROGUESQ_LLE_SOLO`. Write to `scratch/s73_post_a_scene/s2024-hle/run.log`,
poll its `[phase] vi_width=` line for `1024` for 120 seconds, then SIGKILL
that exact PID. Record the first terminal signature and counts for
`[s2020-svc]`, `[s2022-svc]`, `[s2008-status-control]`, and
`[s2008-status-writer]` for both logs.

## If the route is recovered

The following unit, not this one, reruns the seven-site writer/read join on
the phase-valid arm. A writer null without `[s2008-status-control]` is still
an anchor failure and must not be called H1.
