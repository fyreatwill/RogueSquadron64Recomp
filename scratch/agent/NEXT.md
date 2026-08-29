# NEXT work unit — audit one M3 NULL-plus-offset idiom class

HYPOTHESIS-ID: m3-null-offset-idiom-audit

## Single work unit

The M5 paired qualification remains blocked by a real route dependency: the
current Debug binary's documented LLE-only/spin-yield/autopilot route reaches
VI 640 but not title 1024. Continue useful work without changing that route.
Select one concrete generated NULL-plus-offset guest-pointer dereference
idiom class, enumerate every site with `rg`, and classify pointer provenance,
writer, and reachability. Guard or prove every site only after the table is
complete; do not use a mitigation to make a run pass.

## Competing hypotheses

- `H-AudioDegeneracy`: the silent arm suppresses downstream task/service/slot/
  voice/PCM progress once target phases are reachable.
- `H-ContractGap`: the image arm completes DMEM/DMA but fails a named guest or
  output contract edge, while the silent control does not.
- `H-M3-Unclassified`: at least one site in the complete class table remains
  an unclassified reachable dereference.
- `H-M3-Proven`: every site is classified as guarded, unreachable, or
  legitimate, so this idiom class is closed without a behavior change.

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
rg -n -C 3 'KSEG0|0x[0-9A-Fa-f]+|\+[0-9A-Fa-fx]+|\[[^]]+\]' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 5 'get_function\(0\)|NULL.*offset|offset.*NULL|guest.*pointer' src /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
git diff --check
```
