# Session 5270 — `__OSGlobalIntMask` companion classification

The bounded helper was run over `0x80039110..0x80039120`:

```text
renamed 0 references in 0 files
candidate 0x80039110 __OSGlobalIntMask: already-synchronized
```

Independent inspection found the companion symbol map entry as
`__OSGlobalIntMask = 0x80039110` (volatile data, with the next data symbol at
`0x80039120`). The generated tree exposes a same-named function and a large
overlay record, but its first word at `0x80039110` is an invalid instruction
(`0x003FFF01`) and the record spans `0x4E10` into the following data/code
region. This is data decoded as code, not a callable placeholder eligible for
propagation. Preserve the existing name; no generated edit, build, or soak is
warranted.

The next companion candidate is `__osMotorinitialized = 0x80039120`.
