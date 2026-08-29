# NEXT work unit — audit slotDispatcherInner derived heap/list pointers

HYPOTHESIS-ID: m3-null-offset-idiom-audit

## Single work unit

The M5 paired qualification remains blocked by the current route stopping at
VI 640. Continue useful work without changing that route. Audit every
dereference through the derived heap/list pointers (`$a0`, `$v1`, and `$v0`)
in `slotDispatcherInner` from guest PC `0x8003EAE0` through `0x8003EBF8`.
Enumerate the complete class and classify each pointer's null check, writer,
and reachability before adding any guard.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent arm suppresses downstream task/service/slot/
  voice/PCM progress once target phases are reachable.
- `H-ContractGap`: the image arm completes DMEM/DMA but fails a named guest or
  output contract edge, while the silent control does not.
- `H-M3-Unclassified`: at least one derived-pointer site remains an
  unclassified reachable dereference or lacks a defensible contract.
- `H-M3-Proven`: every site is classified as guarded, unreachable, or
  legitimate under a named caller contract, so the class closes without a
  behavior change.

## Discriminating measurement

The decisive measurement is a complete static site table for every `MEM_*`
access through `$a0`, `$v1`, or `$v0` in the selected range. Each site must
have a guest address, offset, null-check/data-flow edge, writer or allocator
provenance, and reachability disposition. Any unclassified reachable site
selects `H-M3-Unclassified`; a complete classification selects
`H-M3-Proven`. A runtime run is not needed unless the table identifies a
specific reachable site whose behavior must be checked.

## Exact commands

```sh
sed -n '24729,25104p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | rg -n 'MEM_[A-Z]+\(.*ctx->r(2|3|4)'
rg -n -C 3 'slotDispatcherInner' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c
git diff --check
```
