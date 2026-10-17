# Session 5116 rename audit: `osContGetReadData`

Candidate: companion symbol `osContGetReadData = 0x8002ACBC`.

The generated snapshot has no `func_8002ACBC` or `fake_func_8002ACBC`
prologue/body. It has one direct generated caller in `funcs_0.c`, calling
`osContGetReadData_recomp` through the runtime ABI, plus the declaration in
`funcs.h`.

The overlay table entry is:

```text
{ .func = osContGetReadData_recomp, .offset = 0x0002A87C, .rom_size = 0x00000000 }
```

The companion symbol file places the next entry at
`__osPackReadData = 0x8002AD64`; there is no generated span to rename. The
runtime wrapper is an ABI boundary rather than generated game code.

The bounded rename helper reported `renamed 0 references in 0 files` and
classified the candidate as `already-synchronized`. Preserve the
`osContGetReadData_recomp` ABI name. No build or soak was warranted.

Discriminator result: H-host-wrapper. This is single-source source-audit
evidence, independently supported by the companion boundary, generated
caller/overlay grep, and runtime wrapper classification.
