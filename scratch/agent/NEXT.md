# NEXT work unit (s2109) — isolate the B40 pre-title route boundary

HYPOTHESIS-ID: m5-audio-gate-writer-sweep

## Work unit

Add one regeneration-stable, phase-keyed route table around the existing B40
writer and the pre-title `reapplyDisplayMode`/title-transition edges. Keep the
existing B40 value arm, C88 explicitly zero, and all route, ABI/DMA, stage,
slot, gate, PCM, and ordering controls. The table must record arm, ordinal,
VI phase/width/origin, B40 writer return, reapply entry/success, and the first
title transition; it must not alter any store or dispatch behavior. Build all
diagnostics once, then run both arms concurrently.

## Competing hypotheses and discriminator

- H-B40-RouteRequired: B40=0 is the causal pre-title route blocker; the
  control will stop or omit an edge before the title transition while B40=1
  completes the chain.
- H-LaterWriterRoute: both arms complete the B40 edge, but a later
  `reapplyDisplayMode` edge or its return differs and determines admission.
- H-RecipeVariance: both arms complete the same pre-title chain, so the
  current split is a route-timing failure rather than a B40-caused boundary.
- H-InputBoundary: the arms differ in the runner's initial input/activation
  sequence before the guest route edge, not in B40 or the later gate writer.

The discriminator is one phase-keyed paired route table. A missing/halting
B40=0 edge selects H-B40-RouteRequired; matching B40 edges followed by a
later-writer divergence selects H-LaterWriterRoute; matching pre-title edges
with both target phases selects H-RecipeVariance only if the target table is
also comparable; an input/activation mismatch before the first guest edge
selects H-InputBoundary. Do not interpret target stage/PCM rows unless both
arms reach title and hangar. The B40=1 target rows from s2108 remain
single-arm controls, not a comparison.

## Ground-truth prerequisite

The s2107 retail oracle already passed its whole-RDRAM control and observed
the live `0x8008EB40`, `0x8008EB7C`, and `0x8008EC88` writers. No new retail
instrument is needed for this unit; only the port-side route join is added.

## Exact commands

Locate the existing regeneration hook and generated sites before editing:

    rg -n -A12 -B4 's2107_b40|0x8008EB40|0x8008EB7C|0x8008EC88|reapplyDisplayMode' ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_23.c

Add the route table to the existing fixup-generated host witness, regenerate
in the established order, and build once:

    python3 ../rogue_squadron64/tools/make_elf.py
    cd ../N64Recomp
    ../RogueSquadron64Recomp/build/Debug/N64Recomp.exe rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd ../RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root, retaining the reduced
capture recipe and adding only the new route-table log variable:

    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2109_m5_b40_route_control 30 12 > scratch/agent/s2109_m5_b40_route_control_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2109_m5_b40_route_treatment 30 12 > scratch/agent/s2109_m5_b40_route_treatment_driver.log 2>&1

Use SIGKILL for any remaining process group. Inspect only phase-keyed counts
and bounded tails; do not read the run logs whole.
