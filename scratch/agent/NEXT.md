# NEXT work unit (s1123)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit that resolves the active descriptor index
for the port's host-initialized NTSC path. s1122 found the host writes
`osTvType=1`, while the index window is ROM-backed immutable data at the
established `VRAM -> ROM (+0xC00)` mapping; generated code only reads it.
Trace `setViModeType`'s exact `rsViModeType` result for `osTvType=1`, map every
indexed byte used by `initVideoSubsystem`, and read the corresponding
`osViModeTable` record width from the retail ROM. Reconcile that static width
with the independent retail-oracle width-320 observation.

Competing hypotheses and discriminator:

- H-index-320: active NTSC index bytes select a 320-wide record.
- H-index-non320: active NTSC index bytes select a non-320 record, exposing a
  source-level contradiction with the retail oracle or an address mapping
  error.
- H-index-state-dependent: the active byte is not fixed by `osTvType=1` and
  requires another lifecycle state before the mode copy.

Discriminator: the concrete `rsViModeType`, indexed ROM bytes, and table `+8`
width must select one hypothesis. Do not build or run; no mitigation is
authorized.

Exact commands (no build or game run):

```sh
rg -n -C 8 'setViModeType|0X780C|0X7810|0X7814|0X7818|0X781C|0X7820|0X7824|0X7828|0X782C|0X7830' ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs_5.c
rg -n 'osViModeTable|OSViMode' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c
xxd -g 1 -s <mapped-index-offset> -l 0x30 build/rogue_squadron.z64
```

Use bounded `sed` windows around the setter and indexed reads. Append the
resolved index/width or the explicitly open state dependency to the ledger and
current truth. No mitigation is authorized.
