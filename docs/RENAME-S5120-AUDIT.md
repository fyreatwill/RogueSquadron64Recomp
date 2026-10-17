# Session 5120 rename audit: `__osContGetInitData`

Candidate: companion symbol `__osContGetInitData = 0x8002AFC0`.

The generated snapshot has no `func_8002AFC0` or `fake_func_8002AFC0`
prologue/body and no direct generated caller. The companion source declares
the symbol with `INCLUDE_ASM`; the next companion entry is
`__osPackRequestData = 0x8002B090`, but no generated span begins at the
candidate.

The bounded rename helper reported:

```text
renamed 0 references in 0 files
candidate 0x8002AFC0 __osContGetInitData: already-synchronized
```

This selects H-host-wrapper/H-unproven over a generated-body rename. Preserve
the ABI naming; no build or soak was warranted. Next candidate:
`__osPackRequestData = 0x8002B090`.
