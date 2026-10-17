# Session 5271 — `__osMotorinitialized` companion classification

The bounded helper was run over `0x80039120..0x80039130`:

```text
renamed 0 references in 0 files
candidate 0x80039120 __osMotorinitialized: already-synchronized
```

Independent inspection found the companion symbol map entry
`__osMotorinitialized = 0x80039120` as typed `u32` data with size `0x10`.
The generated tree has no distinct declaration, callable body, placeholder,
overlay record, or direct generated caller at that address; it is a `nop`
inside the preceding `__OSGlobalIntMask` data/fragment decode. This is not a
callable placeholder eligible for propagation. Preserve the existing name; no
generated edit, build, or soak is warranted.

The next companion candidate is `__osPiDevMgr = 0x80039130`.
