# Session 5121 rename audit: `__osPackRequestData`

Candidate: companion symbol `__osPackRequestData = 0x8002B090`.

The companion source declares the function with `INCLUDE_ASM`; the generated
snapshot has no `func_8002B090` or `fake_func_8002B090` prologue/body and no
direct generated caller. The generated symbol map gives the candidate size
`0xF4`, ending at `0x8002B190`, where `cosf` begins. This is an exact
companion boundary but not evidence of a generated body in the current
snapshot.

The bounded rename helper reported:

```text
renamed 0 references in 0 files
candidate 0x8002B090 __osPackRequestData: already-synchronized
```

This selects H-host-wrapper/H-unproven over a generated-body rename. Preserve
the ABI naming; no build or soak was warranted. Next candidate:
`cosf = 0x8002B190`.
