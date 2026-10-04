# Next work unit: audit the free/active ownership overlap class

HYPOTHESIS-ID: m3-free-active-overlap

The M5 writer census remains pending, but the six-iteration no-engineering-
change guard requires a bounded M3 code pivot. The current heap patch checks
the free chain against only the active queue tail; an active/free alias at an
earlier active node can therefore survive the existing audit.

Competing hypotheses:

- H1: a shared non-tail node is possible and the new bounded audit is needed.
- H2: the existing reciprocal-link and tail checks already prove disjointness;
  the new check should be redundant and preserve behavior.
- H3: the queue invariant is not safely enumerable at the allocator bound; a
  separate invariant or proof is required before adding the guard.

Discriminator: enumerate the active queue from its published head with the
same `MAX_FREE_BLOCKS` bound, compare every node against the free-list chain,
and build the patch. H1 is selected if the old tail-only predicate is not
equivalent to whole-chain disjointness; H2 if the new bounded predicate is
provably redundant; H3 if the bound cannot safely cover the allocator.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
git diff --check
```

The ordinary target build is the host-side check. `PatchesLib` qualification
requires the unavailable MIPS GCC/LD toolchain and is not inferred from this
build.
