# Next work unit: validate the landed free-list guard or obtain the MIPS toolchain

HYPOTHESIS-ID: m3-free-list-reciprocal-chain

The bounded M3 guard change is landed in `patches/heap_guards.c`, but runtime
validation is blocked by the absent MIPS cross-toolchain. Do not add another
guard or repeat the M5 writer census until this validation dependency changes.

Competing hypotheses:

- H1: valid allocator chains pass the whole-chain audit and the patch builds.
- H2: a chain with a cycle or foreign reciprocal link is rejected before any
  later dequeue dereference.
- H3: the patch cannot be validated in this checkout because the required MIPS
  compiler/linker is unavailable.

Discriminator: run `make -C patches` after the toolchain is supplied, then
exercise a valid long free list and malformed cycle/foreign-link fixtures.
H1 requires a successful MIPS build and unchanged valid-chain behavior; H2
requires the malformed fixtures to return before dequeue mutation; H3 is the
only valid result while the compiler/linker remains absent.

Exact command:

    make -C patches

Do not infer runtime safety from source review alone. The guard's ORIGIN is
the allocator's successor/predecessor link stores; valid reciprocal links are
legitimate, while cycles/foreign links are not.
