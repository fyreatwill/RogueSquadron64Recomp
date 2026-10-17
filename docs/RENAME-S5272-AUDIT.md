# Session 5272 — `__osPiDevMgr` companion classification

The bounded helper was run over `0x80039130..0x8003914C`:

```text
renamed 0 references in 0 files
candidate 0x80039130 __osPiDevMgr: already-synchronized
```

Independent inspection found the companion data-map entry
`__osPiDevMgr = 0x80039130`. The generated tree has no distinct declaration,
callable body, placeholder, overlay record, or direct generated caller at the
address; it is a `nop` inside the preceding `__OSGlobalIntMask`
data/fragment decode. This is not a callable placeholder eligible for
propagation. Preserve the existing name; no generated edit, build, or soak is
warranted.

The next companion candidate is `__osPiTable = 0x8003914C`.
