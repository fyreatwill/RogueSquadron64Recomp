# NEXT work unit (s2393) — capture the port image-stage bytes at the exact event

HYPOTHESIS-ID: m5-image-stage-nonzero-contract

## Work unit

Perform one bounded port-side capture of the exact image-stage event and its
payload bytes for the representative rows already identified by s2392:
title `0x167050/0x300`, title `0x1935E0/0x198`, and hangar `0x166D50/0x300`.
Use one build and one run with the existing qualified image arm. Record the
stage event, physical destination, length, byte count, FNV, and a bounded byte
sample before any reporter/image predicate is evaluated. Recompute the tuple
from the captured bytes and compare it with the retained stage/DMA fields.
Do not change task data, audio, gate, fallback, dispatch, VI, or output
behavior. If the capture cannot expose the stage bytes at the event, record
that discriminator failure and stop.

## Competing hypotheses and discriminator

- H-StageLoggerWrongRegion: the logger's `stage_nz`/FNV reads a different
  region than the DMA/stage destination; the same-event byte recomputation
  disagrees with the retained tuple.
- H-StagePayloadZeroLegit: the exact stage bytes are zero at the event and the
  retained zero predicate is legitimate.
- H-StagePcmRepresentationMismatch: the exact stage bytes match the retained
  tuple, but the later PCM/source representation differs; stage-to-PCM joins
  remain unequal.
- H-PortStageCaptureInvalid: the event or bytes cannot be captured with the
  required route/phase controls.

The discriminating table is one row per selected stage event: arm, phase,
destination, length, captured nonzero count, recomputed FNV, retained
`stage_nz`/FNV, and exact-byte agreement. Agreement with zero bytes selects
H-StagePayloadZeroLegit; disagreement selects H-StageLoggerWrongRegion;
agreement followed by a distinct PCM tuple selects
H-StagePcmRepresentationMismatch; failed controls select
H-PortStageCaptureInvalid.

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
