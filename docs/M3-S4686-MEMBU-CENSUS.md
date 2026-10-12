# M3 s4686: backward non-self zero-offset `MEM_BU` census

The prescribed source scans were run before any build. `tools/census_membu.py`
then performed two independent count paths over the external generated tree
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`).

## Counts

| scope | count |
|---|---:|
| direct assignment-shaped zero-offset `MEM_BU` loads | 861 |
| independent direct-regex count | 861 |
| loads inside a backward label edge | 602 |
| non-self source/destination register sites in those loops | 515 |

The complete per-site table is reproducibly emitted by:

```sh
python3 tools/census_membu.py
```

Each row records file, generated line, function, guest PC, source and
destination registers, backward target, back-edge line, a local consumer
classification, and the immediate generated consumer lines.

## Classification

The local review classified all 515 non-self sites as unsigned-byte scalar,
index, packed-field, table, flag, checksum, text, geometry, or audio-data
consumers. The script's review labels were 366 scalar-field, 140
derived-scalar-review, and 9 pointer-transition-review candidates; the latter
were manually resolved as nearby unrelated loads or byte indices, not pointer
reconstruction. None has a named guest writer publishing a guest pointer, and
the allocator/free-list anchor scan does not implicate this byte-load class.

This selects H-MEMBU-bounded for the static census. H-MEMBU-invalid is not a
runtime-probe candidate, and H-MEMBU-unreached is not testable from this
source-only work unit. No build, runtime probe, guard, or mitigation was
authorized.

ORIGIN: no mitigation; this is read-only generated-source enumeration and
consumer classification evidence.
