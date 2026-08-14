# NEXT work unit (s991)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Design one batched, phase-gated runtime probe that records the generated
guest PC immediately before every ordinary `MEM_*` write whose host address
falls on the two shared phase-4/phase-6 pages, then compares exact target
range overlap against the s989 recovered page-fault census. Do not add a
guard or change shade behavior.

## Competing hypotheses and discriminating measurement

- H-generated-target: a generated `MEM_*` write overlaps the exact target
  range and carries a matching guest PC.
- H-generated-unrelated: generated writes occur only at non-target offsets,
  leaving the page-sharing gap unresolved.
- H-runtime-copy: exact target overlap appears only through a runtime copy or
  renderer/state-conversion path, not generated `MEM_*`.

Discriminating measurement: same-run positive-control records plus phase-4 and
phase-6 counts of (a) exact-target ordinary generated writes with guest PC,
(b) non-target page writes with guest PC, and (c) exact-target runtime-copy
writes. Exact-target (a) selects H-generated-target; only non-target (b)
selects H-generated-unrelated; exact-target (c) selects H-runtime-copy.

## Exact commands

Before editing, inspect the existing phase/page-fault hooks and fixup path:

`rg -n "vtx-write-fault|PROBE_PHASE_WIDTH|MEM_[BHW]|MEM_W" src N64Recomp tools`

Arm every measurement in one build/run and require the existing F5/shade and
all-DMA controls to fire. If ordinary generated writes cannot be scoped to
the shared pages without a regeneration-hostile edit, stop and record the
blocking measurement rather than adding a temporary generated-file probe.
