# NEXT work unit (s1073)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded companion-decomp source audit of the two computed-base
writers in `controller_stuff/func_800B47C4.c` (the `temp_s1` index), focused on
whether either writer can alias `D_80130B40+0x14`. The prior unit found only a
zero initializer for `func_800C1D3C`'s `rest01[3]` and left raw guest ownership
open.

Competing hypotheses and discriminator:

* `H-temp-s1-2`: a caller/initializer chain proves `temp_s1 == 2` at one
  computed-base XOR write, establishing another concrete demoId writer.
* `H-temp-s1-other`: every reachable chain proves a value other than 2, making
  the `+0x14` alias inactive for these writers.
* `H-temp-s1-open`: the source does not determine the index; retain the
  pointer-mediated possibility without claiming runtime demoId corruption.

Discriminating measurement: produce one table for both `func_800B47C4` writes
with the index source, all writes/copies into that source, and the call path.
A proven 2 selects `H-temp-s1-2`; proven non-2 for both selects
`H-temp-s1-other`; unresolved provenance selects `H-temp-s1-open`.

Exact commands:

```sh
rg -n -B 8 -A 14 'func_800B47C4|temp_s1|D_80130B40' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  --glob '*.c' --glob '*.h' 2>/dev/null
rg -n -S 'temp_s1|0x80130B40|0x14' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs \
  --glob '*.c' --glob '*.h' 2>/dev/null
```

No build or runtime run is needed for a source-classification result.
