# NEXT work unit (s2107) — single-site setDisplayMode gate arm

HYPOTHESIS-ID: m5-audio-gate-writer-sweep

## Work unit

Add a regeneration-stable opt-in arm for the named `0x8008EB40`
`setDisplayMode` success store. The new arm must default to the current
zero-valued behavior and be controlled only by
`ROGUESQ_M5_B40_VALUE`; leave `0x8008EC88` explicitly zero in both A/B arms.
Then run one same-build control/treatment pair with the Factor 5 image arm
enabled in both processes. Control uses `B40=0`; treatment uses `B40=1`.
Do not change any other `0x800A0F50` writer, task field, output routing,
canary, wait, guard, queue policy, spin-yield default, or default audio
dispatch.

## Competing hypotheses and discriminator

- **H-B40-Required** — `B40=0` suppresses the guest audio path, while
  `B40=1` preserves a valid gate and produces a distinct nonzero stage,
  task/slot, and PCM outcome.
- **H-B40-RouteHazard** — `B40=1` changes the gate but causes a route stall or
  crash before title or hangar. A treatment-only route failure with the
  writer/consumer rows present selects this boundary.
- **H-B40-Irrelevant** — both arms reach title and hangar with the same
  phase-keyed gate/branch, stage-to-PCM, task, and slot outcomes.
- **H-B40-Unreached** — the treatment has no target-phase B40 writer row, or
  another writer overwrites it before the consumer; select the next named
  writer instead of promoting B40.
- **H-B40-ReversedOrSuppressing** — as in s2106's C88 result, `B40=1` changes
  the consumer branch but suppresses the sampled nonzero stage/PCM path while
  `B40=0` retains it.

The discriminator is the phase-gated paired table: both title and hangar
route gates; B40 writer old/new values; raw gate, branch, countdown, and
worker flag; then phase-10 image-stage/DMA/join rows, task exit/output/canary,
slot status transitions, exact PCM source/consumer matches, and ordering
violations. A writer counter without both route gates and downstream rows is
not admissible.

## Exact commands

First update `../N64Recomp/fixup_game_funcs.py` so only the `0x8008EB40`
store reads `ROGUESQ_M5_B40_VALUE` with default zero, preserving the existing
C88 arm. Regenerate in the required order, then build once:

```sh
cd ../rogue_squadron64
splat split roguesquadron.yaml
python3 tools/make_elf.py
cd ../N64Recomp
find RecompiledFuncs -type f -delete
N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd ../RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Verify the generated `0x8008EB40` line contains the new B40 arm and the
`0x8008EC88` line still contains the C88 arm before launching both processes:

```sh
rg -n -A3 -B1 '0x8008EB40|0x8008EC88|ROGUESQ_M5_B40_VALUE|ROGUESQ_M5_C88_VALUE' ../N64Recomp/RecompiledFuncs/funcs_23.c
```

```sh
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2107_m5_gate_b40_control 30 12 > scratch/agent/s2107_m5_gate_b40_control_driver.log 2>&1
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2107_m5_gate_b40_treatment 30 12 > scratch/agent/s2107_m5_gate_b40_treatment_driver.log 2>&1
```

Use SIGKILL for any remaining process group. Inspect only bounded counts and
tails; do not read the run logs whole.
