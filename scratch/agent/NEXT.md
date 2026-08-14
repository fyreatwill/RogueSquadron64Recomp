# NEXT work unit (s1074)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded generated-source audit of raw stores that can reach
`0x80130B54` / `D_80130B40+0x14`, excluding already classified named-field
accesses. Start with generated files and address expressions, then trace only
the base/index assignments needed to classify each candidate.

Competing hypotheses and discriminator:

* `H-raw-generated-writer`: a raw generated store reaches `0x80130B54`, adding
  a concrete generated writer beyond the named-field sweep.
* `H-raw-other-field`: every candidate resolves to another field/base or a
  non-aliasing index, closing this raw-store class.
* `H-raw-open`: one or more candidates retain unresolved base/index provenance;
  keep the pointer-mediated possibility without claiming runtime corruption.

Discriminating measurement: one table containing every raw candidate, its
effective address expression, width, writer function, and base/index proof.
A candidate proven to target `0x80130B54` selects `H-raw-generated-writer`;
all candidates proven elsewhere selects `H-raw-other-field`; unresolved
provenance selects `H-raw-open`.

Exact commands:

```sh
rg -n -S '0x80130B54|0x130B54|D_80130B40|\+ 0x14|\+0x14' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --glob 'funcs_*.c' --glob '*.h' 2>/dev/null
rg -n -B 8 -A 12 '0x80130B54|0x130B54|D_80130B40' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --glob 'funcs_*.c' 2>/dev/null
```

No build or runtime run is needed for a source-classification result.
