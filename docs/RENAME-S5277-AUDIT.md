# Session 5277 — `vi` companion classification

The bounded helper was run over `0x800391B0..0x80039210`:

```
renamed 0 references in 0 files
candidate 0x800391B0 vi: already-synchronized
```

Independent checks classify the candidate as data, not a callable placeholder.
`rogue_squadron64/symbol_files/libultra.txt` declares `vi = 0x800391B0` as
`OSViContext` with size `0x60`. The generated tree has a `nop` at the address
as part of the surrounding data/fragment decode, but no generated function
body, header declaration, overlay record, or direct generated reference for
`vi`.

Conclusion: preserve the existing `vi` data name; no rename, build, or soak is
warranted. This is a two-source static classification.
