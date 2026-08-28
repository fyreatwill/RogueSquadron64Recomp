# NEXT work unit (s2980) — qualify M5 Step 1 after a new route repair

HYPOTHESIS-ID: m5-audio-destub-step1

## Unit

Do one new route-repair or independent handoff work unit that makes the port
reach a target phase, then run the existing same-build M5 Step 1 image/silent
qualification. Do not repeat s2978 unchanged. Preserve the silent control
(`ROGUESQ_AUDIO_UCODE=0`) and Factor 5 image arm (`=1`) in one build/run pair.

## Competing hypotheses and discriminator

- `H-port-route-repair`: a new local route repair reaches title/hangar and
  makes the audio task contract measurable.
- `H-audio-degeneracy`: once the route reaches a target phase, the silent arm
  lacks task/DMEM/DMA/SP/service/slot/PCM progress that the image arm supplies.
- `H-image-contract-gap`: both arms reach the target phase, but the image's
  real DMEM/DMA activity fails to close a named downstream task/output edge.

The discriminating measurement is one same-build phase-keyed table containing,
for both arms: VI target transition; `M_AUDTASK` dispatch; task fields; DMEM
and DMA activity; image break/exit; `run-task-return`; SP completion; guest
service and slot/status transitions; voice/reap; MORT descriptor class; and
PCM source/consumer joins. A missing target VI selects route-repair blockage
and leaves audio nulls unevaluable. Target-phase silent-vs-image divergence
selects audio degeneracy. Matching route plus real image activity without a
downstream close selects an image contract gap.

## Required checks

Before building, obtain a genuinely new route angle or ground-truth handoff;
do not add a diagnostic field to the old route-preparation probe. Build all
arms together, retain the positive controls, run from `build/` with the ROM,
phase-gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`, and terminate with
SIGKILL. If no new route repair or handoff is available, stop and ask for one
instead of spending a third stalled route iteration.

Expected outcomes:

- target phase absent: record the exact phase gate and do not interpret audio
  nulls; pivot to the generated-symbol sweep or request a route repair.
- target phase present and silent/image differ: select the first downstream
  edge and design one behavior change with a named writer/consumer.
- target phase present but image contract remains open: identify exactly one
  missing task/output edge; no broad guard, forced status, or writeback.
