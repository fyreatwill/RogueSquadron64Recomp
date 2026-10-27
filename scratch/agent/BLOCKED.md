NEEDS-HUMAN: gate-defect

The active work unit is an owner gate, not a code experiment. The independent
cxd4 comparator crashed reproducibly before reaching the FD57 target vectors,
so this iteration has no valid reference-RSP result. The owner must either
approve `ROGUESQ_CULL_SPIKE=1` as an opt-in visual mitigation (retail defaults
stay unchanged) or provide a usable independent/reference-RSP path. No game
run or default change is justified before that choice.
