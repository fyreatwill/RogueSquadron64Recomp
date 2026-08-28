# NEXT work unit — audit the descriptor source behind applyPendingViChanges

HYPOTHESIS-ID: m5-vi-mode-stall

## Single work unit

Perform one bounded static audit of the descriptor selected by retail's
`applyPendingViChanges` callsite at `0x8001B8DC`. Start from the generated body
and companion m2c/symbol data, enumerate the loads feeding the `osViSetMode`
argument, then enumerate their writers and compare the corresponding port
addresses/functions. Do not modify behavior or add instrumentation.

## Competing hypotheses

- H-SourceWriter: the selected retail descriptor is written by a game-side
  producer that is absent or inactive in the port.
- H-SourceAlias: the producer exists in the port, but a generated/overlay
  mapping sends the load to a different record or function.
- H-SourceSelection: the producer and mapping agree, but the runtime selects a
  different legitimate descriptor record before the call.

## Discriminating measurement

The audit must identify the retail source record and at least one writer. If
the writer has no corresponding port body/call path, H-SourceWriter wins; if
the port mapping points elsewhere, H-SourceAlias wins; if both agree and the
port selects a different record, H-SourceSelection wins. A function-name
match alone cannot select among them.

## Exact commands

1. `rg -n 'applyPendingViChanges|8001B8DC|osViSetMode_recomp|80128C90|80128DF0|80128E40' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/syms`
2. Read bounded windows around the generated body, companion symbol entries,
   and each identified writer; record the source record, writer, and port
   mapping in `scratch/agent/s3059_m5_vi_descriptor_source/AUDIT.md`.
