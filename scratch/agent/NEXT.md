# NEXT work unit — audit the VI selector-state divergence

HYPOTHESIS-ID: m5-vi-selector-state-divergence

## Single work unit

Perform a bounded static audit of the four-record VI mode table at
`0x80128D50` and the selector state consumed by `applyPendingViChanges` at
`0x8001B8DC`. Explain retail selection `0x80128DA0` (width 1024) versus port
selection `0x80128DF0` (width 640). Do not change behavior or add a probe
unless the source audit identifies a specific writer/state mismatch.

## Competing hypotheses

- H-SelectorWriter: a game-side writer or initialization path populates or
  selects a different table record in the port.
- H-SelectorAlias: the table is correct but pointer arithmetic, base address,
  or field offset differs between generated/runtime surfaces.
- H-ModeConsumer: selection matches, but a consumer or host VI publication
  changes the descriptor before commit.
- H-Unresolved: static surfaces agree and no mismatch explains the divergence.

## Discriminating measurement

Table every writer/initializer of `0x80128D50..0x80128E10`, every selector
read at `applyPendingViChanges`, the selected pointer and `+8` width field,
and the handoff into `osViSetMode`/`update_vi`. A named state writer with a
port/retail value difference selects H-SelectorWriter; an address/offset
mismatch selects H-SelectorAlias; a post-selection mutation selects
H-ModeConsumer; complete agreement selects H-Unresolved. Source-only results
are labeled single-source and do not authorize mitigation.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n '80128D50|80128DA0|80128DF0|applyPendingViChanges|osViSetMode|initVideoSubsystem' docs src syms tools scratch/agent --glob '!soak_results/**'`
3. Inspect bounded generated/companion windows only at identified hits.
4. Record the writer/selector/consumer table in
   `scratch/agent/s<next>_m5_vi_selector_state/AUDIT.md`.
