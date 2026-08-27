# NEXT work unit (s2587) — qualify the M5 writer census past the 640 abort

HYPOTHESIS-ID: m5-audio-boundary-qualification

## Single work unit

Run the already-built image arm once with the new writer logger disabled and
the existing `ROGUESQ_LOG_M5_PRETARGET=1` boundary breadcrumb enabled. This
isolates whether the 640 abort is caused by the new diagnostic calls or is the
known `get_function`/scene-graph boundary that prevents the writer census from
reaching title/hangar. Preserve the build and behavior; do not change a gate,
store, task field, or output pointer.

## Competing hypotheses and discriminator

- `H-Diagnostic-Induced`: disabling the new logger allows title/hangar to
  appear, so the added calls perturb the qualified route.
- `H-KnownBoundary`: disabling it reproduces the 640 abort at guest PC
  `0x80001F88`, with `get_function`/scene-graph evidence and no target phase.
- `H-NewBoundary`: the disabled arm reaches a different stable boundary or
  crash, requiring a new discriminator before the writer census can run.

The discriminator is same-build target-phase reachability plus the
`ROGUESQ_LOG_M5_PRETARGET` rows immediately before the abort. Title and hangar
controls make the result evaluable: target phases with no writer rows then
select a writer hypothesis; absent target phases select only the boundary
hypothesis and authorize no M5 behavior change.

## Required command

Use the current executable from `build/`:

```sh
cd build
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
  ROGUESQ_LOG_AUDTASK=1 ROGUESQ_LOG_M5_WRITER_ENTRY=0 \
  ROGUESQ_LOG_M5_PRETARGET=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2587_m5_writer_boundary.log 2>&1
```

Run from `build/`, SIGKILL the game PID at 90 seconds, and verify exact
title/hangar rows or the boundary crash marker. Do not promote a store, task
field, output pointer, or gate from the result.
