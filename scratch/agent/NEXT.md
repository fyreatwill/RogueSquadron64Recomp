# NEXT work unit (s2487) — reproduce target route for descriptor capture

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Run the existing descriptor capture unchanged with the exact s2484 qualified
eleven-Start recipe, using a 300-second phase-relative budget. Do not add
fields, alter scheduler behavior, or remap audio/output. The only question is
whether the already-valid instrument reaches the target 1024/512 route.

## Competing hypotheses

- H-Route-Stable: the s2484 route is reproducible and descriptor rows will be
  captured at `0x800377C8`.
- H-Route-Flaky: the current build remains on 640, so the descriptor boundary
  is still unobservable and requires route diagnosis.
- H-Instrument-Dead: the target phase is reached but neither descriptor nor
  start hook fires; this would identify a callsite/fixup or phase-gate defect.

## Discriminator

The same run must show the resolver positive-control row and a `[phase]` row
for width 1024 followed by width 512/origin `0x006AB400`. If those controls
pass, classify the sixteen-word yield rows and start joins. If only the
resolver fires and 1024/512 do not, select H-Route-Flaky. If 512 is present
but descriptor rows are absent, select H-Instrument-Dead.

## Exact command

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_M5_SCHEDULER_ID=1 ROGUESQ_LOG_M5_SECOND_EXEC=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh tools/probe.sh scratch/agent/s2487_m5_descriptor_capture 300 1`
