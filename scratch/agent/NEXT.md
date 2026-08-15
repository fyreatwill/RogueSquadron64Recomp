# NEXT work unit (s1227)

HYPOTHESIS-ID: retail-entry-capability

The s1226 audit selected H2 for the generated handoff: `mainGameLoop` has no
direct generated caller. `thread3_video_handle` obtains `gBootConfig`, and
`mainBootstrapWorker` invokes its `+0x04` callback through `jalr`; the
companion map names that callback `mainGameLoop`. No input-dependent branch
precedes it.

Work unit: perform a bounded provenance audit of `gBootConfig+0x04`. Identify
the ROM/data initializer and runtime/front-end registration that supplies the
`mainGameLoop` callback. Decide whether the missing retail-entry event is
outside the generated game path. Do not build, run, or write an oracle target.

Competing hypotheses and discriminator:
- H1: `gBootConfig+0x04` is initialized by a concrete input/event-controlled
  transition or front-end handoff.
- H2: the callback is a static/unconditional ROM or data initializer and the
  missing retail transition is outside the generated game path.
- H3: the config callback provenance is incomplete/malformed and requires
  symbol or regeneration work before the entry route can be named.

Discriminator: trace the exact writer/initializer of the four bytes at
`0x80037564`, then trace the runtime callback registration and first invocation.
An input/event-dependent writer selects H1; a static data initializer with an
unconditional callback selects H2; absent/malformed provenance selects H3.

Exact commands:
```
rg -n -C 10 "mainGameLoop|gBootConfig|boot config|0x8003DFA0|8003DFA0" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "mainGameLoop|gBootConfig|8003DFA0|boot" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Then inspect the ROM/data provenance with bounded searches for `0x80037564`,
`gBootConfig`, and the linker/ELF data section containing the 0x50-byte config.
