# NEXT work unit — audit the next unclassified M3 pointer idiom class

HYPOTHESIS-ID: m3-null-offset-idiom-audit

## Single work unit

The M5 paired qualification remains blocked by the current route stopping at
VI 640. The `slotDispatcherInner` derived heap/list-pointer class closed in
Session 3148. Continue useful work without changing that route: select the
next bounded M3 NULL-plus-offset idiom from the existing audit inventory,
then enumerate its complete site table before adding any guard.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent arm suppresses downstream task/service/slot/
  voice/PCM progress once target phases are reachable.
- `H-ContractGap`: the image arm completes DMEM/DMA but fails a named guest or
  output contract edge, while the silent control does not.
- `H-M3-Unclassified`: at least one site in the next selected idiom remains
  an unclassified reachable dereference or lacks a defensible contract.
- `H-M3-Proven`: every site in the next selected idiom is classified as
  guarded, unreachable, or legitimate under a named caller contract, so the
  class closes without a behavior change.

## Discriminating measurement

The decisive measurement is a complete static site table for every `MEM_*`
access in the newly selected idiom. Each site must have a guest address,
offset, null-check/data-flow edge, writer or allocator provenance, and
reachability disposition. Any unclassified reachable site selects
`H-M3-Unclassified`; a complete classification selects `H-M3-Proven`. A
runtime run is not needed unless the table identifies a specific reachable
site whose behavior must be checked.

## Exact commands

```sh
rg -n 'MEM_[A-Z]+\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | rg '<next-selected-range>'
git diff --check
```
