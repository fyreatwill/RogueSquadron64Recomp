# NEXT work unit (s2106) — single-site guest gate arm

HYPOTHESIS-ID: m5-audio-guest-gate

## Work unit

Run one same-build control/treatment pair with the validated Factor 5 image
arm enabled in both processes. The control leaves the existing
`0x8008EC88` `reapplyDisplayMode` gate store at its default-zero behavior; the
treatment sets only `ROGUESQ_M5_C88_VALUE=1`. Enable the regeneration-stable
gate contract table and retain the ABI/DMA/stage/PCM and route controls. The
admission condition is both arms reaching title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400` in the same pair.

Do not change the other `0x800A0F50` writers, task fields, DMA arguments,
output routing, canary, waits, guards, queue policy, spin-yield default, or
default audio dispatch.

## Competing hypotheses and discriminator

- **H-C88-Required** — the default-zero C88 store leaves the guest gate at
  zero or suppresses a downstream consumer, while C88=1 preserves the gate
  and produces a distinct valid task/slot/PCM outcome. Both route gates plus
  a gate-value/branch difference and matching downstream evidence select this
  at the sampled scope.
- **H-C88-RouteHazard** — C88=1 keeps the gate live but causes a route failure
  or stall before a target VI. A treatment-only route failure with gate rows
  reaching the boundary rejects promotion of the writer and identifies the
  next gate/consumer boundary.
- **H-C88-Irrelevant** — both arms reach both target VIs and have the same
  phase-keyed gate transitions and downstream task/slot/PCM table. C88 is not
  the limiting writer at this recipe scope.
- **H-C88-Unreached** — the treatment has no target-phase C88 writer row, or
  both arms show the same C88 value because another writer overwrites it. The
  writer is not qualified as the source of the sampled gate state; select the
  next named `0x800A0F50` writer rather than changing this one.

The discriminating measurement is the phase-gated paired table: title/hangar
route gates and process outcome; `[m5-gate]` writer site, old/new value,
consumer branch, gate byte, countdown, and worker flag; then ABI/DMA/stage
rows, slot status transitions, exact PCM source/consumer matches, and ordering
violations. A gate counter without both route gates is not a positive control.

## Exact commands

From the repository root, rebuild once:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Launch both arms concurrently from separate shells:

```sh
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2106_m5_gate_control 30 12 > scratch/agent/s2106_m5_gate_control_driver.log 2>&1
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2106_m5_gate_c88 30 12 > scratch/agent/s2106_m5_gate_c88_driver.log 2>&1
```

Use SIGKILL for any remaining process group; inspect run logs with `grep` and
`tail`, never by reading them whole.
