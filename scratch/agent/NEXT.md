# NEXT work unit (s1163)

HYPOTHESIS-ID: slot-dispatcher-runtime-origin

Perform one bounded runtime-origin audit of the recurring
`slotDispatcherIter+872` SIGBUS. Build one phase-gated capture with the existing
slot-dispatch positive control and crash markers, and attribute the guest `$sp`
and failing spill address to the last generated or host-side writer. Do not add
a skip or guard; any wild value requires an `ORIGIN:` writer attribution and a
legitimacy assessment.

Competing hypotheses and discriminator:

- H1: a runtime-side writer corrupts the caller frame/value before the failing
  dispatcher entry.
- H2: the generated dispatcher prologue observes a legitimate but invalid
  caller `$sp` due to an unobserved ABI transition.
- H3: the crash value is produced inside the dispatcher prologue itself.

The discriminating measurement is a writer-attribution row immediately before
the crash: H1 requires a prior writer and a changed value; H2 requires an ABI
transition with no ordinary writer; H3 requires the prologue's own first write
to create the bad value. A null is invalid unless the independent phase and
slot-dispatch controls fire.

Commands:

    sed -n '1,240p' tools/oracle/README.md
    sed -n '1,260p' docs/F5-UCODE-REFERENCE.md
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 zsh scratch/agent/run-slot-origin.sh

Expected outcomes: one run must pass the slot-dispatch positive control and
emit a bounded pre-crash writer row, or prove the capture unevaluable. Do not
infer parser or renderer causality from this frame-origin audit.
