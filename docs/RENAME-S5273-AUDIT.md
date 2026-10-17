# Session 5273 — `__osPiTable` companion classification

The bounded helper was run over `0x8003914C..0x80039150`:

```text
renamed 0 references in 0 files
candidate 0x8003914C __osPiTable: already-synchronized
```

Independent inspection found the companion data-map entry
`__osPiTable = 0x8003914C`, typed `OSPiHandle_s*` with size `0x4`. The
generated tree has no distinct callable body, placeholder, declaration,
overlay record, or direct generated caller at the address; it is only a `nop`
immediately before the next generated fragment at `0x80039150`. This is not a
callable placeholder eligible for propagation. Preserve the existing data
name; no generated edit, build, or soak is warranted.

The next companion candidate is `__osCurrentHandle = 0x80039150`.
