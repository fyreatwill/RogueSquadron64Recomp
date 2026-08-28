# NEXT work unit — new M5 route repair or independent handoff

HYPOTHESIS-ID: m5-route-repair-blocked

## Blocker

Do not repeat the current route-edge probe family. A human must supply or
approve one genuinely new route repair/signal, or an independent retail-
grounded handoff whose port-side producer can execute before the title/hangar
phase gates. The existing host transition repair regressed boot, and the last
three generated-edge probes all stopped at VI 640.

## Evidence table

| Iteration | Edge | Same-run controls | Target phase | Target rows | Outcome |
|---|---|---:|---|---:|---|
| s2990 | waitOnVideoQueue | positive | none; VI 640 | 0 | unevaluable |
| s2991 | bufferArbiterAllocSlot | 4,806 LLE + filter/shade | none; VI 640 | 0 | unevaluable |
| s2992 | bufferArbiterProducerMark at 0x8000BFE8 | 80 LLE/audio | none; VI 640 | 0 | unevaluable |

The s2992 generated audit also corrected the prior edge premise:
`0x8000C0C4` is the READY call, not ProducerMark. The single discriminating
measurement for the next unit must include an independent ground-truth row,
all same-build positive controls, VI transitions, target route rows, and
crash/abort markers. A target null is valid only when target phase fires.

## Exact entry condition

After a new edge or repair is approved, document its retail PC/predicate in
this file, add one regeneration-safe probe, build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
from `build/` with `tools/probe.sh`, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, the qualified LLE/image/task
controls, and SIGKILL/watchdog cleanup. Do not change audio behavior until a
target-phase Step 1 comparison is evaluable.
