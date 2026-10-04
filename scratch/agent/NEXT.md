# Next work unit: validate the landed M3 ownership-alias guard

HYPOTHESIS-ID: m3-active-queue-ownership

Build the patch pipeline when a MIPS toolchain is available. First run
`cmake --build build --config Debug --target PatchesLib`; then run the normal
Debug target. If the patch target is still absent, record that exact build
failure and do not claim runtime validation.

Competing hypotheses:

- H1: the popped free-list block can alias an existing active-queue node;
  the new disjointness walk must reject it before queue-link stores.
- H2: the allocator's ownership invariant already prevents that alias; the
  new guard remains cold while valid allocations continue.
- H3: the patch cannot be built in this checkout; no MIPS/runtime conclusion
  is permitted.

Discriminator: one build must exercise the guard in the MIPS patch pipeline;
the positive control is a successful ordinary host build plus a valid queue
path. A guard hit without a named corrupted input is not proof of a retail
defect.
