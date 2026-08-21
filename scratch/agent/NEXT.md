# NEXT work unit (s2108) — route-qualified B40 retry

HYPOTHESIS-ID: m5-audio-gate-writer-sweep

## Work unit

Run one reduced-capture, same-build control/treatment pair using the existing
regeneration-stable B40 value arm and its independent writer witness. Keep
C88 explicitly zero in both arms. Remove only the high-volume
ROGUESQ_LOG_AUDIOTICK_TRACE and ROGUESQ_LOG_AUDIO_DRAIN logs; retain the
route, task, stage/DMA, slot, gate, and PCM controls. Do not change any gate
store, output routing, task field, canary, wait, guard, queue policy, or
default dispatch.

## Competing hypotheses and discriminator

- H-B40-Required: B40=1 persists to the target consumer and produces a
  distinct nonzero stage-to-DMA/PCM outcome relative to B40=0.
- H-B40-OverwrittenOrIrrelevant: both arms have the valid phase-2 B40
  0/1 writer rows, but a later writer makes the target raw gate and
  downstream table equivalent.
- H-B40-RouteHazard: B40=1 causes a treatment-only route stall or crash
  before one of the title/hangar gates.
- H-B40-ReversedOrSuppressing: B40=1 reaches the target consumer but
  suppresses or reverses the control's downstream stage/PCM outcome.

The discriminating table is one phase-keyed paired row set: B40 writer
old/requested/stored values; title and hangar route gates; target raw gate
and branch; stage rows and matching DMA payloads; task exit/output/canary;
slot controls; PCM source/consumer FNV/count rows; and ordering violations.
Both arms must reach title and hangar before downstream rows are admissible.

Expected selection: a treatment-only route failure selects H-B40-RouteHazard;
equal target gate plus equal downstream rows selects
H-B40-OverwrittenOrIrrelevant; a persistent treatment gate with less
downstream data selects H-B40-ReversedOrSuppressing; a persistent treatment
gate with a distinct nonzero stage-to-PCM result selects H-B40-Required.

## Exact commands

Verify the already-generated arm and rebuild the current target once:

    rg -n -A8 -B2 '0x8008EB40|m5-b40-writer|ROGUESQ_M5_B40_VALUE' ../N64Recomp/RecompiledFuncs/funcs_23.c
    cmake --build build --config Debug --target RogueSquadron64Recomp

Run both arms concurrently from the repository root:

    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2108_m5_gate_b40_control 30 12 > scratch/agent/s2108_m5_gate_b40_control_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2108_m5_gate_b40_treatment 30 12 > scratch/agent/s2108_m5_gate_b40_treatment_driver.log 2>&1

Use SIGKILL for any remaining process group. Inspect only phase-keyed counts
and bounded tails; do not read the run logs whole.
