# NEXT work unit — select and audit the next M3 NULL-plus-offset idiom

HYPOTHESIS-ID: m3-next-idiom-class-audit

## Single work unit

Select the highest-information-value still-open NULL-plus-offset idiom from
the existing M3 audit inventory, enumerate every guest site and caller, and
classify each base pointer as locally proven, guarded, or unclassified. Do not
add a guard, change audio behavior, or run the blocked M5 route.

## Competing hypotheses

- `H-M3-Proven`: every site has a local nonzero/data-flow proof.
- `H-M3-Guarded`: every site is protected by an explicit control-flow guard.
- `H-M3-Unclassified`: at least one reachable site lacks either proof.

## Discriminating measurement

Build one complete site table: guest PC, base register, offset, defining load
or allocation, null/range test, and all reachable callers. `H-M3-Proven`
requires a proof at every site; `H-M3-Guarded` requires an explicit guard at
every site; one unclassified reachable site selects `H-M3-Unclassified`.

## Exact commands

```sh
rg -n -i 'm3.*(inventory|audit)|null.plus.offset|unclassified.*deref' docs scratch/agent --glob '*.md'
rg -n 'MEM_[BHW]|0x[0-9A-Fa-f]+\(\$[a-z0-9]+\)' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
git diff --check
```
