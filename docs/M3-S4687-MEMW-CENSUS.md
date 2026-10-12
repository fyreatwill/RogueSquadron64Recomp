# M3 s4687: backward non-self zero-offset `MEM_W` census

The prescribed source scans were run before any build. `tools/census_memw.py`
then performed two independent count paths over the external generated tree
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`).

## Counts

| scope | count |
|---|---:|
| direct assignment-shaped zero-offset `MEM_W` loads | 3592 |
| independent direct-regex count | 3592 |
| loads inside a backward label edge | 1596 |
| non-self source/destination register sites in those loops | 1161 |

The complete per-site table is reproducibly emitted by:

```sh
python3 tools/census_memw.py
```

Each row records file, generated line, function, guest PC, source and
destination registers, backward target, back-edge line, a local consumer
classification, and the immediate generated consumer lines.

## Classification

The local review classified all 1161 non-self sites as 620 scalar/record/table
fields, 319 derived scalar or index consumers, and 222 pointer-transition
review sites. The latter are pointer-shaped consumer paths, but this census
did not identify a named guest writer publishing an invalid pointer or establish
that any value is illegitimate. They remain ordinary pointer/table consumers
pending a writer and legitimacy proof; they do not authorize a guard.

This selects H-MEMW-bounded for the static census. H-MEMW-invalid is not a
runtime-probe candidate, and H-MEMW-unreached is not testable from this
source-only work unit. No build, runtime probe, guard, or mitigation was
authorized.

ORIGIN: no mitigation; this is read-only generated-source enumeration and
consumer classification evidence.
