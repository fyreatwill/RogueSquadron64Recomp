# NEXT work unit (s2074)

HYPOTHESIS-ID: m5-writer-specific-gate-arm

## Work unit

Run one same-build, two-arm phase-gated port comparison. Keep the qualified
route and the opt-in Factor 5 image arm fixed; the only treatment difference
is the existing `ROGUESQ_M5_C88_VALUE=1` behavior arm, which restores the
retail value at `reapplyDisplayMode`'s guest store `0x8008EC88`. The control
leaves that variable unset. Do not change any other guest gate store, task
field, output route, canary reservation, wait, guard, or default.

ORIGIN: `0x8008EC88` is a legitimate retail `reapplyDisplayMode` writer and
s2073 observed its post-store value as `0x01000000`; the port's default fixup
force-zero is the treatment under test. No mitigation or host-side skip is
authorized.

## Competing hypotheses and discriminator

- **H-GateWriterCompletes** — the writer-specific retail gate value is the
  missing prerequisite, so the treatment improves the downstream image-task
  contract and produces valid slot/PCM evidence in title or hangar.
- **H-GateWriterPartial** — the treatment changes guest gate/voice activity or
  PCM, but the image task still returns `Broke` or retains the zero-payload
  contract; the gate is necessary for a later step but not sufficient.
- **H-GateWriterNoEffect** — the treatment changes the gate byte but task exit,
  slot status, DMA payload, and PCM joins remain the same as the control.
- **H-GateArmMissing** — the treatment does not produce the expected
  `0x8008EC88` value transition or either arm fails the target-route controls,
  so no downstream null is admissible.

The discriminator is one table with both arms and both target phases. Require
live route/input controls, `[m5-gate]` rows showing the `0x8008EC88` value,
audio-task exit/DMEM/DMA rows, slot-status transitions, and paired PCM
source/consumer rows. H-GateWriterCompletes requires a treatment-side
improvement in task completion plus valid slot/PCM evidence; H-GateWriterPartial
requires a downstream voice/PCM change without task-contract completion;
H-GateWriterNoEffect requires the gate transition with no downstream change;
H-GateArmMissing rejects the comparison before interpreting any null.

## Exact commands

Build once before the two arms:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run both arms concurrently from the same build. `probe.sh` starts the game
from `build/`, gates on title VI 1024, sends the established title/menu key
schedule relative to that phase, keeps capturing through hangar VI 512, and
SIGKILLs the game at the end:

```sh
(
  env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 \
    ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
    ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
    ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS="2:a 3:start 4:a 5:start 7:a" \
    PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2074_gate_off 180
) &
(
  env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 \
    ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
    ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
    ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS="2:a 3:start 4:a 5:start 7:a" \
    PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2074_gate_on 180
) &
wait
```

Cross-check each `run.log` for title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, no crash/abort marker, and the positive `[pad-host]` /
`[audtask-dispatch]` controls before comparing task, slot, DMA, and PCM rows.
Run `git diff --check`; no further code change is authorized if the gate
transition is absent or the route controls fail.
