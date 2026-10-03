# Next work unit: M5 task-data native watch coverage and value retry

HYPOTHESIS-ID: m5-task-data-native-value

Session 3757 passed the page positive control and title phase in both arms,
and hangar in real, but neither arm generated a target-range fault before the
known MusyX/VI-retrace crash paths. The target-only decoder was therefore not
exercised. This is run instability/no-target-fault, not evidence of a zero
producer.

Competing hypotheses:

- `H-TaskDataNativeFaultWindow`: target stores occur, but the page is not
  protected at the relevant target-window times.
- `H-TaskDataNativeNoStore`: this run reaches the target phase without native
  stores to the watched range.
- `H-TaskDataNativeRunUnstable`: a crash or page-watch interaction prevents a
  complete target capture.

Discriminator: add phase-scoped arm/rearm counters and a bounded first/last
target-window heartbeat to the existing watcher, retaining the positive
control, target-only ARM64 decode, and post-store sample. A target-window
with continuous arm coverage plus no target faults selects `H-TaskDataNativeNoStore`
for that run; a target-window gap selects `H-TaskDataNativeFaultWindow`;
another pre-hangar crash or missing target window selects
`H-TaskDataNativeRunUnstable`. Do not interpret post-store values unless a
target fault is captured. Do not repeat the retail preflight, scalar census,
central API census, route-load list, or alter `0x800078EC`.

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run once from `build/`, with both arms concurrently, 75 seconds, SIGKILL
cleanup, using `scratch/agent/run_s3757_m5_task_value_retry.sh` as the base
recipe and retaining `ROGUESQ_AUDIO_UCODE=1/0`, LLE-solo, spin-yield,
autopilot, `PROBE_PHASE_WIDTH=1024`, and `PROBE_KEYS_FROM_PHASE=1`.
