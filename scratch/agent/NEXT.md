# NEXT work unit (s990)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Classify the five unique phase-4 host fault PCs from s989 with the local
symbol table and ARM64 disassembly, and compare their call sites with the
generated guest breadcrumb. This is a bounded static classification of the
faults that actually occurred; do not add a guard or infer target-byte
ownership from a page fault alone.

## Competing hypotheses and discriminating measurement

- H-generated: fault PCs resolve to generated game stores.
- H-runtime: fault PCs resolve to allocator/renderer runtime stores.
- H-page-gap: all faults are unrelated stores on shared host pages.

Discriminating measurement: independent PC-to-symbol/disassembly
classification for the repeated PCs `0x103300418`, `0x103356134`,
`0x103383458`, `0x103300210`, and `0x10334D084`, with the s989 guest-PC/LR
records as the comparison. A generated store selects H-generated; a runtime
store selects H-runtime; only unrelated shared-page stores select H-page-gap.

## Exact commands

`nm -n build/RogueSquadron64Recomp` (use the nearest preceding symbols), then
`otool -tvV build/RogueSquadron64Recomp` around those symbols and map any
generated caller with the existing local symbol/guest-PC tools.

Use only `scratch/agent/soak_results/s989_vtx_write_fault/run.log` as input;
no build or soak is needed unless the symbol/disassembly artifacts are
unavailable. Land no mitigation.
