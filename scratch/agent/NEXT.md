# NEXT work unit — identify the earlier frequency producer edge

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3438 selected `H-EarlierPortInputGap`: port caller tuples were live and
unchanged through `osRecvMesg_recomp`, but the 107-tuple port set had zero
intersection with the 7,806-tuple retail set at `0x800331D0`.

Before building, ask ground truth for the selected earlier producer edge. Use
the retail oracle with whole-RDRAM control, both title origins, and the
high-count predecessor PCs `0x80001B04`, `0x80001CB8`, `0x80006EFC`, and
`0x80006F5C`. Then add one phase-scoped port census at the first input-producing
edge before those callers, preserving the existing caller and wrapper rows.
Build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`, and run from `build/` with the validated
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1` route, title/hangar phase gates, and
SIGKILL cleanup.

Competing hypotheses and the single discriminating measurement:

- `H-EarlierPortInputGap`: no producer-side normalized tuple matches the
  retail predecessor family.
- `H-LaterPortBoundaryGap`: a retail tuple appears at the producer and caller,
  so the first divergence is later than the caller census.
- `H-EarlierBoundaryUnevaluable`: the producer census has no usable
  phase-qualified rows despite live phase and route controls.

The measurement is the exact normalized-tuple intersection between the new
producer edge, the existing caller rows, and the retail predecessor rows.
Producer absence selects `H-EarlierPortInputGap`; a retail tuple appearing at
the producer and caller selects a narrower later boundary; no producer rows
with live controls selects `H-EarlierBoundaryUnevaluable`. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.
