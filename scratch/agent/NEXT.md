# NEXT work unit — M5 Step 3 contract-edge selection

HYPOTHESIS-ID: m5-audio-contract-edge

Session 3235 completed the target-phase qualification attempt with valid
retail and dispatch controls, but both port arms stopped at VI 640, so the
target row is unevaluable. Repeating the same qualification is parked.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent `musyx_stub` path and related degenerate
  gates are responsible for the downstream failure.
- `H-ImageContract`: one specific image task/output contract edge is missing
  and is the next authorized behavior change.
- `H-PortRoute`: the pre-title route divergence is upstream of audio output;
  Step 3 must not be used to mask it without a named writer and ordering edge.

## Discriminator

Read the existing Step 1/2 evidence and select exactly one already-proven
image task/output contract edge (writer PC, destination span, payload polarity,
and completion ordering). If no edge is independently proven, do not guess or
patch; record the missing evidence and remain unevaluable. A selected edge
must produce a same-build old/new arm with task/SP completion and a downstream
DMEM/DMA or PCM join; a route-only change or a `Broke` return without such a
join rejects the edge.

## Exact preparation and validation

1. Inspect `docs/M5-AUDIO-PLAN.md` Step 1/2 and the Session 3235 results.
2. Use the existing fixup/build path; do not hand-edit generated functions.
3. Build both contract arms together with:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
4. Run the phase-gated pair only after the edge and rollback are named. The
   required validation row is dispatch → task fields/source → DMEM/DMA → image
   exit → SP completion → service → status/slot → voice/reap → MORT → PCM
   source/consumer → route phase, with the whole-RDRAM control.
