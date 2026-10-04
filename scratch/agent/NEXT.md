# Next work unit: validate the allocator expansion ownership guard

HYPOTHESIS-ID: m3-expansion-active-ownership-4019

Competing hypotheses:

- H1: an allocator expansion chain can be returned with a node already owned
  by the active queue; the new guard must reject that chain before free-list
  splice stores.
- H2: expansion chains are disjoint from the active queue on the qualified
  path; the guard is inert and the ordinary target still builds.
- H3: the patch source cannot be compiled or linked in this checkout; the
  change is source-level only and runtime qualification remains blocked.

Discriminator: build the ordinary Debug target after the guard change and
inspect the generated patch input/target result. A successful target build
selects H1/H2 only as a source/build result; a missing PatchesLib target or
MIPS compiler selects H3. Runtime rejection versus acceptance of a synthetic
alias cannot be claimed without the unavailable patch pipeline, so do not
call this runtime-qualified.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    git diff --check

The guard's ORIGIN is `func_8002221C` and the expansion-chain link stores. A
node already reachable from the active queue is not legitimate allocator
ownership. Do not run another route or writer census in this iteration.
