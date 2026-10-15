# Next work unit: make the faithful allocateDisplayListBuffer assembly consumable
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. N64Recomp can consume the exact direct external `jal` after a symbol/config
   integration correction while retaining the `0xE8` machine-code span.
2. N64Recomp's external-call resolver cannot consume this faithful form, so a
   representable exact-span route is unavailable without a tool change.
3. The recovered generated snapshot is stale or mismatched despite the exact
   span, which would be exposed by a source/disassembly instruction diff.

Discriminating measurement: run the exact-span assembly through `build/N64Recomp
patches.toml` after the smallest resolver/config change that preserves the
direct call. Successful host emission with `0xE8` selects H1; the same
resolver error after a source-backed exact-span diff selects H2; an
instruction mismatch selects H3. Do not use an indirect call or enable the
override as a workaround.
