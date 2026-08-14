# NEXT work unit (s1122)

HYPOTHESIS-ID: retail-oracle-mode-index-non-generated-boundary

Perform one bounded static audit of the non-generated/data boundary for
`osTvType` (`0x80000300`) and descriptor-index bytes
`0x8003780C..0x8003782F`. s1121 proved that `setViModeType` reads `osTvType`,
not `osResetType`, and found no generated or companion writer for the index
bytes.

Competing hypotheses and discriminator:

- H-host-init: the host/runtime initializes `osTvType` or the index bytes.
- H-rom-data: the index bytes are immutable ROM/data and the apparent missing
  writer is intentional; the retail width-320 result is data-selected.
- H-raw-guest-writer: a generated census missed a computed/raw guest store.

Discriminator: enumerate host/runtime/patch initialization and every generated
computed address reaching `0x80000300` or `0x8003780C..0x782F`; reconcile those
with section/data symbols and the retail ROM image. A host store selects
H-host-init; immutable source bytes with no store select H-rom-data; a complete
computed guest store selects H-raw-guest-writer. If none can be proved, retain
the boundary as open and do not infer a width or add a probe.

Exact commands (no build or game run):

```sh
rg -n '80000300|8000030C|8003780C|8003780c|800378[0-2][0-9]|3780C|3780c|osTvType|osResetType|rsViModeType' src lib patches ../N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n 'MEM_[BWH].*(0X378|0x378|0X300|0x300)|ADD32\([^)]*0X780|addiu.*0x78' ../N64Recomp/RecompiledFuncs
rg -n 'D_800378|osTvType|osResetType|rsViModeType|osViModeTable' syms /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Use bounded `sed` windows around every generated/host hit and inspect the ROM
bytes only at the corresponding mapped offsets. Append the classified owner or
the explicitly open boundary to the ledger and current truth. No mitigation is
authorized.
