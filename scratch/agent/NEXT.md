# NEXT work unit (s2112) — trace the phase-7 route/state producer

HYPOTHESIS-ID: m5-audio-gate-route-variance

## Work unit

Add one regeneration-stable, phase-keyed census at the phase-7
`reapplyDisplayMode` entry and its sole caller. At the caller, record the
call-site edge and all four guest argument registers. At function entry and
at the route edge, record those arguments, the `a1` gate input, the current
`0x80141AD0`/`0x8013B038`/`0x80141AD1` state bytes, VI width/origin, arm,
B40/C88 values, and the existing route ordinal. Record the return edge and
whether `reapplyAudioConfig` returned nonzero. Use one bounded row table
joined by call ordinal; do not add a single-field breadcrumb.

Keep B40 value arms, explicit C88=0, route, ABI/DMA, stage, slot, PCM,
ordering, and VI controls unchanged. This is diagnostic-only: do not change
any gate store, branch, dispatch, output routing, task field, canary, wait,
guard, or queue policy. Build all diagnostics once and run both arms
concurrently.

## Competing hypotheses and discriminator

- H-Phase7State: a complete argument/state row differs before or at the
  phase-7 edge, and that difference explains the phase-7 origin divergence.
- H-RecipeTiming: the complete rows match and only the VI timing/phase order
  varies; the phase-7 origin split is ordinary recipe variance.
- H-B40Indirect: the direct B40 census was complete, but an indirect or
  non-generated consumer changes route state after the B40 store; the new
  table differs only after that edge.
- H-UnobservedCoverage: one arm has a positive entry/control row but the new
  caller/entry join is missing or cannot be paired, proving an instrumentation
  coverage failure rather than a state conclusion.

The paired full row table is the discriminator. A pre-edge argument/state
difference selects H-Phase7State; identical full rows with only timing
difference selects H-RecipeTiming; a post-B40-only difference selects
H-B40Indirect; missing paired rows despite positive entry and VI controls
select H-UnobservedCoverage. If the table does not split these outcomes, do
not add more fields in this iteration.

## Ground-truth prerequisite

Before adding the route-state witness, rerun the retail oracle's whole-RDRAM
positive control and physical B40 read watch. The oracle is only a coverage
control here: it reaches boot/attract, not the port's target route. A null
retail route result is not evidence about the port.

## Exact commands

Confirm the current call/entry addresses and fixup anchors before editing:

    rg -n -A35 -B12 'RECOMP_FUNC void reapplyDisplayMode|0x8008EB5C|0x8008EB7C|reapplyDisplayMode\(' ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs_23.c
    rg -n -A12 -B4 's2111 B40 read census|0x800A0F50|reapplyDisplayMode' ../N64Recomp/fixup_game_funcs.py

Run the independent retail controls first:

    tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 8 --hit-cap 100 --watch-write 0x0:0x800000 --watch-read 0x000A0F50 --first-watch 1 --detail-watch 1 --pc-hist-watch 1 --vi-trace > scratch/agent/s2112_oracle_b40_control.log 2>&1

Regenerate and build in the established order. On this macOS checkout, do
not invoke `build/N64Recomp`; it is the known unsupported-cache binary. Use
the older complete recompiler named in the project instructions when it is
available; if it is unavailable, stop the regeneration attempt and report
that environment blocker rather than truncating generated files:

    python3 ../rogue_squadron64/tools/make_elf.py
    cd ../N64Recomp
    E:/Projects/N64Recomp/Debug/N64Recomp.exe rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd ../RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root, retaining the reduced
capture recipe and all passive breadcrumbs. Add the new route-state log
variable to both arms:

    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2112_m5_route_state_control 30 12 > scratch/agent/s2112_m5_route_state_control_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2112_m5_route_state_treatment 30 12 > scratch/agent/s2112_m5_route_state_treatment_driver.log 2>&1

Kill any remaining game process group with SIGKILL. Inspect only bounded
phase-keyed counts and tails; never read a full run log.
