# NEXT work unit — repair regenerated-tree scheduler crash

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3256 established that the retail call site is live, but the freshly
regenerated port crashes in `spTaskSchedulerThread+2864` during VI 320. The
new identity hook is not the cause: the disabled-hook control crashed at the
same location with the same register pattern. Do not repeat the scheduler
identity capture until the port reaches the VI-640 wall.

## Competing hypotheses

- `H-Regeneration-Missing-Patch`: the fresh N64Recomp/fixup output omitted a
  previously required generated-tree patch, causing the early scheduler crash.
- `H-Regeneration-Compiler-Drift`: the current N64Recomp output differs in
  control-flow or register handling independently of the missing fixup sites.
- `H-Port-Baseline-Crash`: the crash is already present in the checked-in
  baseline and is unrelated to regeneration.

## Discriminator

Inventory the pre-regeneration generated-tree patch markers and compare them
with the current fixup report and the last known-good build artifacts. Restore
only the missing regeneration-preserved diagnostics/behavior through
`fixup_game_funcs.py` or its dedicated apply script, then build once. Run the
same prescribed port recipe with `ROGUESQ_RECV_TRACE=0` as a control. Reaching
VI 640 (without the identity hook enabled) selects a missing-patch/drift
explanation and authorizes the identity capture as the following unit; an
identical 320 crash after marker parity selects baseline/other runtime crash
and requires a new code-level discriminator. Do not treat a build-only success
or a 320-phase row as target coverage.

## Exact start

First use bounded `git diff`/marker checks in the external N64Recomp tree; do
not clear or regenerate again until the missing marker set is identified.
Then build from this repository's `build/` directory:

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_RECV_TRACE=0 ./RogueSquadron64Recomp
```

SIGKILL at 40 seconds and preserve the log under `scratch/agent/`.
