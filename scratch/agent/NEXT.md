# NEXT work unit (s2791) — reset SP yield state at task start

HYPOTHESIS-ID: m5-audio-destub-sp-yield-lifecycle

## Work unit

Make the SP-yield request state task-local in the runtime by clearing it at
`osSpTaskStartGo_recomp`. Build the Debug target and inspect the diff. Do not
add probes or change task interruption/resumption behavior.

## Competing hypotheses and discriminator

- H-sticky: the process-global request remains set across later task starts,
  so a later `osSpTaskYielded_recomp` can report a stale request.
- H-task-lifecycle: starting any new SP task clears the prior request, matching
  the lifecycle of the task whose yield was requested.
- H-interruption: correct behavior requires task interruption/resumption, so a
  reset-only change is insufficient and must not be expanded here.

The discriminator is the runtime state transition: after a yield request,
`osSpTaskYielded_recomp` reports true until the next
`osSpTaskStartGo_recomp`; the next task start must make it report false.
The source-level reset selects H-task-lifecycle. Evidence that a task must be
interrupted/resumed selects H-interruption and rejects any broader de-stub.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
git diff --check
```
