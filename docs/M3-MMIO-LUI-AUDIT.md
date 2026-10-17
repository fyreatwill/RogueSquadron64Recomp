# M3 audit: direct hardware-register (MMIO) / KSEG1 address idiom (s5350)

Tool: `tools/audit_mmio_lui.py <elf> <out>` (`--selftest` has a synthetic positive control).
ELF: `../rogue_squadron64/build/roguesquadron.elf` (302,115 instructions).

- Same-run control: 20,387 ordinary RDRAM `lui 0x80xx` and 1,665 low-immediate `lui` parsed, so a
  parser that sees nothing is excluded (the first attempt parsed 0 `lui`; objdump prints registers
  without `$`, and the empty control exposed it).
- 624 `lui` with an upper half outside RDRAM. Buckets: mmio-A 0xA3F0-0xA7FF 112, mmio-B/rom 0xB000+ 250,
  kseg0-high 23, kseg1-rdram 8, other 231. The B/other/kseg0-high buckets sit in game functions (draw,
  audio, menu) and are float/display-list/data constants: no memory op consumes them as a base.
- The 110 memory ops that consume an MMIO `lui` as a base are ALL inside 31 libultra functions
  (`__osSp*`, `__osVi*`, `osAi*`, `osPi*`, `__osSi*`, `osDp*`, `osSetIntMask`, `__osException`, Leo...).
  Zero are in game code.
- Generated tree (`../N64Recomp/RecompiledFuncs`): all 31 have NO emitted body (control: `mainGameLoop`
  matches the same regex), and callers bind to host `*_recomp` implementations (osSpTaskLoad 7,
  osVirtualToPhysical 9, osAiSetNextBuffer 4, osSetIntMask 2, osViGetCurrentField 1). The internal
  `__os*` helpers have no generated references at all.

Verdict: class closed. No recompiled code dereferences `rdram + 0x04xxxxxx` / KSEG1 hardware registers.
Not covered: the rom/other buckets were classified by absence of a base-register consumer, not decoded one by one.
