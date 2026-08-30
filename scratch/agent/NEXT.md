# NEXT work unit — compare the external regenerated scheduler body

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3258 audited the checked-in binary and host runtime. The crash site is
generated guest code performing `MEM_HU(0x22, r17)` at host `0x100AD3930`.
The local runtime queue handoff is not the identified host-pointer fault, but
the producer and legitimacy of `r17` remain unevaluable because the external
regenerated tree is unavailable.

## Competing hypotheses

- `H-Regeneration-Missing-Patch`: the external N64Recomp/fixup output omitted a
  required marker or wrapper.
- `H-Regeneration-Compiler-Drift`: the external generated body differs in
  control-flow or register handling without a missing marker.
- `H-Port-Baseline-Crash`: the checked-in baseline has the same malformed
  `r17` producer and the crash is independent of regeneration.

## Discriminator

When the external artifact is available, compare the generated body around
guest `0x80019CD0` and the faulting scheduler continuation with the checked-in
binary. Identify the exact producer of `r17`, its value at the `+0x22` load,
and any fixup marker covering that boundary. A missing marker selects the
first hypothesis; a body/register difference with all markers present selects
compiler drift; matching body and malformed `r17` selects baseline crash. A
missing artifact is not a result and authorizes no guard or repeat run.

## Exact start

```sh
test -d /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs && \
  rg -n "80019CD0|spTaskSchedulerThread|8000834C|RECV|fixup" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools
nm -an build/RogueSquadron64Recomp | rg "spTaskSchedulerThread|80019cd0"
```

Only after one of the three outcomes is identified may the matching exact
marker/contract change be built and run. If the external tree is absent, stop
and leave the issue blocked on that artifact; do not repeat the local control.
