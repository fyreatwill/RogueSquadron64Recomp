# Session 5117 rename audit: `__osPackReadData`

Candidate: companion symbol `__osPackReadData = 0x8002AD64`.

The generated snapshot has no `func_8002AD64` or `fake_func_8002AD64`
prologue/body and no direct generated caller. The companion map places the
neighboring entries at `osContInit = 0x8002AE50` and
`__osContGetInitData = 0x8002AFC0`; no generated span begins at the candidate.

The bounded rename helper reported:

```text
renamed 0 references in 0 files
candidate 0x8002AD64 __osPackReadData: already-synchronized
```

This selects H-host-wrapper/H-unproven over a generated-body rename. Preserve
the existing ABI naming; no build or soak was warranted. Next candidate:
`__osContGetInitData = 0x8002AFC0`.
