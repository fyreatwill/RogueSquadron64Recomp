# NEXT work unit — audit the status-03 audio idiom class

HYPOTHESIS-ID: m3-status03-publication-consumer-audit

The M5 guard-build dependency is external and does not block a static M3
audit. Audit every generated-source status-03 read, writer, and terminal
transition in the MusyX service/slot family as one complete idiom class. Do
not change guards, waits, audio routing, or output behavior in this unit.

## Competing hypotheses

- `H-Status03NamedContract`: every status-03 read has a named legitimate
  publisher and a bounded consumer/reaping transition in the guest code.
- `H-Status03MissingPublisher`: at least one live status-03 read has no
  publisher or terminal transition in the reachable generated call graph.
- `H-Status03SafetyOnly`: the reads are only defensive/safety paths and do not
  authorize changing the existing wait hatch.

## Discriminator

Build one complete table from static sources: for each status-03 read, record
the function/address, field offset, all stores to that field, caller/callee
edge, and terminal `02/00` or reap transition. A class-wide named writer and
consumer for every live read selects `H-Status03NamedContract`; a live read
without one selects `H-Status03MissingPublisher`; unreachable or defensive
reads with no live transition select `H-Status03SafetyOnly`. Do not infer
runtime causation from a guard hit.

## Exact commands

1. `rg -n "status|STATUS|03|0x03|+0x|lbu|lb|sb|sh|sw" RecompiledFuncs/funcs_*.c`
   and enumerate only the MusyX service/slot status-03 idiom.
2. Trace each enumerated address through the companion named symbols and
   callers in `syms/` and `docs/game-architecture.md`; inspect bounded source
   windows, never the full generated files.
3. Write one evidence table under `scratch/agent/` with the selected
   hypothesis and any unresolved address. No build or runtime instrument is
   authorized unless the table proves a specific missing contract.

The parked M5 Step 3 validation remains: a configured Windows/MIPS host (or
   equivalent Rogue Squadron generated patch artifacts) must eventually run
   `cmake --build build --config Debug --target PatchesLib` and the existing
   Step 3 recipe.
