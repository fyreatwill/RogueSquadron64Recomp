# NEXT work unit (s2111) — identify the B40 route consumer

HYPOTHESIS-ID: m5-audio-gate-writer-sweep

## Work unit

Add one regeneration-stable, whole-tree census of every generated read and
branch using the B40 byte at `0x800A0F50`, and join those rows to the existing
phase-keyed route table. Record guest PC, read value, branch direction, arm,
phase/width/origin, and the nearest route ordinal. Keep the B40 value arm,
explicit C88=0, and all route, ABI/DMA, stage, slot, PCM, and ordering
controls. This is diagnostic-only: do not alter any store, branch, dispatch,
output routing, task field, canary, wait, guard, or queue policy. Build all
diagnostics once, then run both arms concurrently.

## Competing hypotheses and discriminator

- H-B40-Consumer: a named B40 read/branch differs between the matched phase-6
  route and treatment-only phase-7 reapply entry; that branch admits the route.
- H-OtherState: all B40 reads/branches match, so another guest state or input
  activation differs before the missing control edge.
- H-RecipeVariance: both arms expose the same B40 read/branch sequence and the
  existing route split is timing variance, not B40-dependent admission.
- H-UnobservedRead: the census is positive in the treatment but misses a
  generated or indirect read site; this is an instrument-coverage failure and
  requires static-site repair, not a runtime conclusion.

The one paired table of all B40 reads/branches plus route edges is the
discriminator. A treatment-only read/branch before phase-7 reapply selects
H-B40-Consumer; identical rows select H-OtherState or H-RecipeVariance only if
the phase-7 timing and route rows also match; absent rows with a positive
writer/route control select H-UnobservedRead. Do not interpret target
stage/PCM rows unless both arms reach title and hangar.

## Ground-truth prerequisite

The s2107 retail oracle already passed its whole-RDRAM control and observed the
live B40 and reapply writers. Before adding the reader census, arm the oracle's
whole-RDRAM positive control and a physical read watch for `0x000A0F50`; only
then use the port-side generated-site census. A retail null is not evidence
about the port route because the oracle currently reaches only boot/attract.

## Exact commands

Locate the existing regeneration hook and enumerate every B40 read site before editing:

    rg -n -A8 -B4 's2107_b40|0x800A0F50|0x8008EB40|0x8008EB7C|0x8008EC88|reapplyDisplayMode' ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_*.c

Add the read/branch census to the existing fixup-generated witness, regenerate
in the established order, and build once:

    python3 ../rogue_squadron64/tools/make_elf.py
    cd ../N64Recomp
    ../RogueSquadron64Recomp/build/Debug/N64Recomp.exe rogue_squadron.toml
    python3 fixup_game_funcs.py
    cd ../RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root, retaining the reduced
capture recipe and adding only the new read-census log variable:

    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2111_m5_b40_read_control 30 12 > scratch/agent/s2111_m5_b40_read_control_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_B40_READ=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2111_m5_b40_read_treatment 30 12 > scratch/agent/s2111_m5_b40_read_treatment_driver.log 2>&1

Use SIGKILL for any remaining process group. Inspect only phase-keyed counts
and bounded tails; do not read the run logs whole.
