# NEXT work unit (s1072)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded source audit of the `func_800C1D3C` caller and
initialization chain, focused only on `arg0->rest01[3]` at the computed-base
write in `func_800C1D3C.c:389-390`. The prior unit found that index 2 aliases
`D_80130B40+0x14` and selected the pointer-mediated writer hypothesis, but did
not classify the index value.

Competing hypotheses and discriminator:

* `H-index-2`: the chain proves `arg0->rest01[3] == 2` before the XOR branch,
  making the write a concrete demoId writer.
* `H-index-other`: the chain proves a value other than 2, or resets the field
  to such a value before the branch, making the +0x14 alias inactive there.
* `H-index-open`: the chain does not determine the value; retain the static
  writer but do not claim runtime demoId corruption.

Discriminating measurement: produce one caller/initializer table with every
write or copy into `rest01[3]`, its value source, and the call path to
`func_800C1D3C`. A proven 2 selects `H-index-2`; a proven non-2 selects
`H-index-other`; unresolved sources select `H-index-open`.

Exact commands:

```sh
rg -n -B 8 -A 14 'func_800C1D3C|rest01\[3\]|rest01\[0x3\]' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/RecompiledFuncs \
  --glob '*.c' --glob '*.h' 2>/dev/null
rg -n -S 'rest01\[3\]|rest01\[0x3\]|0xD?F0|0x22C' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  --glob '*.c' --glob '*.h' 2>/dev/null
```

No build or runtime run is needed for a source-classification result.
