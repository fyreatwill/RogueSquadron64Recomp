# Session 5151 symbol audit — `__osRepairPackId`

Candidate: `__osRepairPackId = 0x8002F454`, companion span ending at
`__osCheckPackId = 0x8002F86C`.

The generated-tree search for `__osRepairPackId`, `func_8002F454`, and
`fake_func_8002F454` produced no match. The bounded rename helper reported
`renamed 0 references in 0 files` and
`candidate 0x8002F454 __osRepairPackId: already-synchronized`.

Classification: unmaterialized libultra/ABI entry (`H-host-wrapper`). There is
no generated body on which to prove a span or independent caller, so the
existing ABI name is preserved. No build or soak was needed.
