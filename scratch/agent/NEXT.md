# NEXT work unit (s1069)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded ownership audit of selector byte `0x80130B54` outside
`RecompiledFuncs/`: inspect host/runtime writes, patch/fixup-generated writes,
overlay-loader/data initialization, and any companion decomp symbol or C
references. Classify each candidate as a real writer, a read-only alias, or
an unresolved boundary.

Competing hypotheses and discriminator:

* `H-host-write`: a host/runtime or patch path writes the selector directly.
* `H-overlay-data`: overlay DMA or initialized overlay data owns the value,
  with no executable writer.
* `H-pointer-write`: a pointer-mediated guest path writes it outside the
  generated-tree search.
* `H-boundary`: ownership remains unresolved after the bounded source audit.

Discriminating measurement: produce one table of every non-generated
reference, including file/line, access width, address expression, and whether
it writes or only reads. A direct host/patch write selects `H-host-write`; an
overlay/data-only source selects `H-overlay-data`; a concrete pointer-mediated
guest writer selects `H-pointer-write`; otherwise retain `H-boundary`.

Exact commands:

```sh
rg -n -B 8 -A 12 '80130B54|80130B40|0xB54|0xB40|demoId|cycleIdleDemoId' src patches lib submodule-patches 2>/dev/null
rg -n -B 8 -A 12 '80130B54|80130B40|0xB54|0xB40|demoId' docs syms /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null | head -1200
rg -n -B 6 -A 10 'overlay|DMA|load_overlays|.ovl\.menu|0x1345A4' src lib docs syms 2>/dev/null | head -1200
```

No build or runtime run is needed unless the source audit finds a concrete
host/patch writer whose effect cannot be classified statically.
