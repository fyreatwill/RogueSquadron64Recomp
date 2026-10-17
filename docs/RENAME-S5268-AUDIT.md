# Session 5268 — `__osHwIntTable` companion classification

The bounded helper was run over `0x800390E0..0x80039100`:

```text
renamed 0 references in 0 files
candidate 0x800390E0 __osHwIntTable: already-synchronized
```

Independent inspection found the companion entry in
`rogue_squadron64/symbol_files/libultra.txt` as
`__osHwIntTable = 0x800390E0; // type:u32 size:0x14`. The generated tree has
no callable body, placeholder, header declaration, overlay record, or direct
generated caller at the address.

Conclusion: this is a data/fragment record, not a callable generated symbol.
Preserve the companion name; no generated edit, build, or soak is warranted.
