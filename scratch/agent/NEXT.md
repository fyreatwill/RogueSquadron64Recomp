# NEXT work unit — audit slotDispatcherInner slot-pointer dereferences

HYPOTHESIS-ID: m3-null-offset-idiom-audit

## Single work unit

The M5 paired qualification remains blocked by a real route dependency: the
current Debug binary's documented LLE-only/spin-yield/autopilot route reaches
VI 640 but not title 1024. Continue useful work without changing that route.
The next class is every original nonzero-offset dereference through
`slotDispatcherInner`'s slot pointer (`$s1`, represented as `ctx->r17`), from
guest PC `0x8003EA60` to that function's return. Enumerate the complete class
with `rg`, then classify pointer provenance, writer, and reachability before
adding any guard.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent arm suppresses downstream task/service/slot/
  voice/PCM progress once target phases are reachable.
- `H-ContractGap`: the image arm completes DMEM/DMA but fails a named guest or
  output contract edge, while the silent control does not.
- `H-M3-Unclassified`: at least one slot-pointer site remains an unclassified
  reachable dereference or lacks a defensible caller contract.
- `H-M3-Proven`: every site is classified as guarded, unreachable, or
  legitimate under a named caller contract, so the class closes without a
  behavior change.

## Discriminating measurement

The decisive measurement is a complete static site table for the selected
idiom: each site must have a source location, guest address, dereference
offset, writer/provenance classification, and reachability disposition. A
remaining unclassified reachable site selects `H-M3-Unclassified`; a complete
classification selects `H-M3-Proven`. A runtime run is not needed unless the
static table identifies a specific reachable site whose behavior must be
checked.

## Exact commands

```sh
rg -n -C 3 'ctx->r17, 0X' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c
sed -n '24690,25020p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c
git diff --check
```
