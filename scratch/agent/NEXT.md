# NEXT work unit — M3 voice/list/table-pointer idiom audit

HYPOTHESIS-ID: m3-musyx-voice-list-table-pointer-contract

## Single work unit

Audit every producer and consumer edge in the existing voice/list/table
pointer guard inventory in `funcs_25.c` and `funcs_26.c`. This is a complete
source audit, not a single-site guard change. M5 remains blocked at VI 640.

Competing hypotheses and the discriminating measurement:

- `H-LegitimateWriter`: every guarded pointer has a reachable initialized
  writer and a valid traversal bound.
- `H-BadProducer`: a reachable writer can publish an invalid pointer before a
  guarded consumer; identify the ordering edge.
- `H-UnreachableGuard`: no guarded consumer has a callable producer/consumer
  edge in the current image.

The discriminator is one whole-class census of all guarded pointer loads,
their writers, traversal bounds, and callable edges, joined by guest PC and
field offset. A null is invalid unless every known guard and writer is marked
by the census positive control.

Exact commands:

```sh
rg -n 'voice|song|table|list|guard|KSEG0|0x8014' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_25.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_26.c
rg -n 'voice|song|table|list|0x8014' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/src 2>/dev/null
```

Expected outcome: one complete writer/consumer table that proves the
contract, names a legitimate bad producer and ordering edge, or proves the
path unreachable. Do not add a guard or build/run until the table selects one
outcome.
