# NEXT work unit (trace the static frame record initializer)

HYPOTHESIS-ID: m3-vi-argument-state-origin

Perform one bounded source/data audit. Trace `D_80037560` and the static frame
record passed as `D_80037560+0x10` by both `mainGameLoop` callsites. Identify
the ROM/data bytes at the corresponding `D_80037574` field, the loader or
initializer that materializes them, and any generated writer missed by the
previous register-scoped search. Do not add a probe, guard, or game-logic
change; no build or run is needed unless the data path cannot be resolved
statically.

## Competing hypotheses

- H-static-field-rom-intended: `D_80037574` is a ROM-backed initialized mode/timing scalar and is intentionally consumed.
- H-static-field-runtime-writer: a loader or runtime store populates the field outside the previously searched caller functions.
- H-static-field-unresolved: the available symbols/source/data do not expose the initializer or exact field bytes.

## Discriminating measurement

Resolve the virtual address and exact `+0x14` field offset to a named data
object, ROM initializer, or runtime store. A named ROM/data initializer with
decoded bytes supports the first hypothesis; an executable store or loader
path supports the second; failure to resolve either is the third. Do not
infer legitimacy from the clean run.

## Exact commands

```sh
rg -n -C 12 "D_80037560|0x80037560|0x80037574|0X7570|runVideoFrameTick" syms ../N64Recomp rogue_squadron64 docs
rg -n -C 8 "MEM_H\(0X14|sh .*0x14|0x14\(\$s[0-9]\)" ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "D_80037560|37574|37560" ../N64Recomp --glob '*.bin' --glob '*.s' --glob '*.inc' --glob '*.toml'
```
