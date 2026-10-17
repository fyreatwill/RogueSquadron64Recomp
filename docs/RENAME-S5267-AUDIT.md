# Session 5267 — `__osContinitialized` companion classification

The bounded helper was run over `0x800390D0..0x800390E0`:

```text
renamed 0 references in 0 files
candidate 0x800390D0 __osContinitialized: already-synchronized
```

Independent checks found the companion entry in
`rogue_squadron64/symbol_files/libultra.txt` as
`__osContinitialized = 0x800390D0; // type:u32`. The generated tree has no
placeholder or callable body at that address, and no matching declaration in
`RecompiledFuncs/funcs.h`, overlay record in `recomp_overlays.inl`, or direct
generated caller. The next companion entry is `__osHwIntTable = 0x800390E0`,
typed `u32` with size `0x14`.

Conclusion: this is a data/fragment record, not a callable generated symbol.
Preserve the companion name; no generated edit, build, or soak is warranted.
