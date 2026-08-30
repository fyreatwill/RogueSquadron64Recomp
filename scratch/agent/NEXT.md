# NEXT work unit — identify the pre-VI-640 scheduler fault contract

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3256 established that the retail call site is live, but the freshly
regenerated port crashes in `spTaskSchedulerThread+2864` during VI 320. Session
3257 reproduced the same local control crash with the hook disabled: Bus error
at `0x103ACF930`, fault `0x380000021`, last guest PC `0x8000834C`, after width
320. The external regenerated tree is unavailable, so the next unit must use
the checked-in scheduler source and symbols to identify the invalid-value
contract before another run.

## Competing hypotheses

- `H-Regeneration-Missing-Patch`: the fresh N64Recomp/fixup output omitted a
  previously required generated-tree patch, causing the early scheduler crash.
- `H-Regeneration-Compiler-Drift`: the current N64Recomp output differs in
  control-flow or register handling independently of the missing fixup sites.
- `H-Port-Baseline-Crash`: the crash is already present in the checked-in
  baseline and is unrelated to regeneration.

## Discriminator

Audit the host implementation and generated call boundary for
`spTaskSchedulerThread+2864`, including the register/value that becomes the
fault address `0x380000021`. Produce a bounded source-level table naming the
consumer, its producer, and whether the value is a valid guest pointer or an
invalid scheduler contract. The discriminating outcome is: (a) a missing
regeneration-preserved wrapper/fixup is identified, which authorizes restoring
that exact marker and one build/run; (b) the checked-in host contract itself
accepts a malformed value, which authorizes one narrowly scoped contract fix;
or (c) no local source boundary can explain it, which leaves the issue
blocked on the external regenerated tree. Do not add a guard or repeat the
baseline run without one of these outcomes.

## Exact start

First use bounded `rg`/`nm`/`git log -S` checks in the checked-in source and
generated-library symbols; do not clear or regenerate. Candidate commands:

```
rg -n "spTaskSchedulerThread|0x80019CD0|8011D460|8000834C|0x380000021" src lib tools
nm -an build/RogueSquadron64Recomp | rg "spTaskSchedulerThread|80019cd0"
git log --all -S"spTaskSchedulerThread" --oneline -- src lib tools
```

Only if the audit identifies an exact missing marker or contract boundary,
build from this repository's `build/` directory:

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_RECV_TRACE=0 ./RogueSquadron64Recomp
```

SIGKILL at 40 seconds and preserve the log under `scratch/agent/`.
