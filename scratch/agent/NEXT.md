# NEXT work unit (s1127)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the exact selector branch after the
resolved boot value `gameConfig+0x44 = 0x00001800`. Trace the stack argument
through `initVideoBootWrapper` into `buildAndRegisterDefaultMaterial`, map its
zero bits to selector bytes, then evaluate `selectAndApplyViMode`'s branch and
the copied-record index/width.

Competing hypotheses and discriminator:

- H-selector-zero-to-320: zero selector bytes take the `0x50` branch, whose
  NTSC record is one of the independently observed 320-wide indices.
- H-selector-zero-to-other: zero selector bytes take `0x00`, `0xA0`, or `0xF0`,
  requiring a different mapping or explaining the retail width discrepancy.
- H-argument-transformed: the `0x1800` field is transformed before the
  material writer, so its zero selector bits are not the effective boot bits.

Discriminator: the generated branch trace must produce one concrete selector
byte tuple, copied-record offset, table index, and width. A zero tuple that
selects the 320 record proves H-selector-zero-to-320; a non-320 record selects
H-selector-zero-to-other; any intervening nonzero-producing operation selects
H-argument-transformed. Do not build or run.

Exact commands:

```sh
rg -n -C 40 'initVideoBootWrapper|0x800012B8|0x800012BC|0x80017B88|0x80017C7C|0x80017C90|0x80017CA0|0x80017CB0|0x80017CC0|0x80017CCC' ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n -C 35 'selectAndApplyViMode|0x8001BB80|0x8001BB98|0x8001BBB0|0x8001BBC4' ../N64Recomp/RecompiledFuncs/funcs_5.c
xxd -g 1 -s $((0x80037560 - 0x80000000 + 0xC00 + 0x44)) -l 4 build/rogue_squadron.z64
```

Use bounded `sed` windows around the argument construction, selector stores,
selector branch, and ROM word. Append the branch/index/width classification to
the ledger and current truth. No mitigation is authorized.
