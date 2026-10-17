# Session 5269 — `__osShutdown` companion classification

The bounded helper was run over `0x8003910C..0x80039110`:

```text
renamed 0 references in 0 files
candidate 0x8003910C __osShutdown: already-synchronized
```

Independent inspection found the companion entry in
`rogue_squadron64/symbol_files/libultra.txt` as
`__osShutdown = 0x8003910C; // type:u32`. The generated tree has no callable
body, placeholder, declaration, overlay record, or direct generated caller at
the address. The next companion entry, `__OSGlobalIntMask = 0x80039110`, is
also a data record.

Conclusion: this is a data/fragment record, not a callable generated symbol.
Preserve the companion name; no generated edit, build, or soak is warranted.
