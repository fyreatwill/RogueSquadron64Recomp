# M3 s4688: backward non-self zero-offset `MEM_WU` census

The prescribed source scans were run before any build. `tools/census_memwu.py`
then performed two independent direct-load count paths over the external
generated tree (`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`).

| scope | count |
|---|---:|
| direct assignment-shaped zero-offset `MEM_WU` loads | 1 |
| independent direct-regex count | 1 |
| loads inside a backward label edge | 1 |
| non-self source/destination register sites in those loops | 1 |

The row is `swizzleTextureRowsToTmem` at guest PC `0x800249D8`, loading `r9`
from `r10`. The loaded word is immediately ORed into the low half of a
64-bit texture row after the adjacent `MEM_W` supplies the high half, then
written by `SD`; the loop advances source and destination by eight bytes under
bounded row counters. This is packed texture data, not pointer reconstruction.

This selects H-MEMWU-bounded. H-MEMWU-invalid has no named writer or pointer
consumer to probe, and H-MEMWU-unreached is not needed for this source-only
discriminator. No build, runtime probe, guard, or mitigation was authorized.

ORIGIN: no mitigation; all observations are read-only generated-source and
consumer classification evidence.
