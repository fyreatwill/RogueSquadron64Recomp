# NEXT work unit (s2394) — stabilize the M5 image-arm route for byte capture

HYPOTHESIS-ID: m5-image-stage-capture-route

## Work unit

Run one same-build, two-arm route control (`ROGUESQ_STUB_MISSING_FUNCS=0/1`)
using the known phase-gated title/hangar recipe, with the new stage-byte
capture enabled. Determine whether missing-function suppression is required
to reach title 1024 and the exact stage event. If either arm reaches title,
retain its byte table; otherwise retain the crash/stall PC and stop. Do not
change task data, audio, gate, fallback, dispatch, VI, or output behavior.

## Competing hypotheses and discriminator

- H-MissingFunctionSuppressionRequired: only the suppression arm reaches the
  title phase and emits stage events.
- H-MissingFunctionSuppressionIrrelevant: both arms have the same route result.
- H-MissingFunctionSuppressionHarmful: only the unsuppressed arm reaches title.
- H-PortStageCaptureInvalid: neither arm reaches the required phase.

The discriminating table is one row per arm: suppression value, title/hangar
VI control, crash/abort status, last guest PC, stage-row count, and byte-row
count. One-arm-only title reach selects the corresponding suppression
hypothesis; equal arm results select irrelevance; two invalid arms select the
route-invalid hypothesis.

## Ground-truth result carried forward

s2392's oracle control passed (`12,962` whole-RDRAM writes) and reached title
and hangar. Retail exact window `0x1935E0:0x198` had target-phase writers and a
final `186/408` nonzero snapshot, FNV `0xE2F69C77`, while the retained port row
was `stage_nz=0`, FNV `0x762B22A5`. This authorizes a port byte-capture
discriminator, not a predicate relaxation.

## Exact commands / controls

    rg -n -C 20 'audtask-image-stage-row|stage_nz|image_stage|fnv' src lib
    rg -n -C 20 'ROGUESQ_LOG|PROBE_PHASE_WIDTH|image-stage' docs scratch/agent
    # Build once, run the qualified image arm once, and emit the complete
    # selected-event byte/FNV table with title and hangar phase controls.

Required controls are the existing route/VI controls, a positive image-stage
event, and a recomputed byte tuple from the same captured span. A null without
those controls is inconclusive.
