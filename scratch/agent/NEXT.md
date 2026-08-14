# NEXT work unit (s1071)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded audit of whole-struct and pointer-mediated companion-decomp
paths that can write `D_80130B40.demoId` at offset `0x14`. The direct source
audit in s1070 found no host/runtime, patch, overlay-loader, or direct
companion access to `0x80130B54`; this unit examines only functions that receive
or copy the containing struct.

Competing hypotheses and discriminator:

* `H-pointer-write`: a pointer-mediated guest path writes it outside the
  generated-tree search, or copies a source struct into the global.
* `H-boundary`: every matching path is read-only, incomplete, or lacks a
  concrete write to field `+0x14`.

Discriminating measurement: produce one table of every companion-decomp
function using `D_80130B40` or a parameter typed as `D_80130B40_type`, including
file/line, field/offset expression, access width, and read/write direction. A
concrete `+0x14` or whole-struct write selects `H-pointer-write`; otherwise
retain `H-boundary`.

Exact commands:

```sh
rg -n -S 'D_80130B40|D_80130B40_type|demoId|\+0x14|unk14' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --glob '*.c' --glob '*.h' --glob '*.md' --glob '*.txt' 2>/dev/null
rg -n -B 8 -A 12 'D_80130B40|gGameSettings|0x80130B54|0x80130B40' \
  src patches lib/N64ModernRuntime/librecomp submodule-patches docs syms \
  --glob '!**/thirdparty/**' 2>/dev/null | head -1200
```

No build or runtime run is needed unless the source audit finds a concrete
host/patch writer whose effect cannot be classified statically.
