# Session 5115 rename audit: `osContStartReadData`

Candidate: companion symbol `osContStartReadData = 0x8002AC30`.

The generated snapshot has no `func_8002AC30` or `fake_func_8002AC30`
prologue/body. It has one direct generated caller in `funcs_0.c`, calling
`osContStartReadData_recomp` through the runtime ABI, plus the declaration in
`funcs.h`.

The overlay table entry is:

```text
{ .func = osContStartReadData_recomp, .offset = 0x0002A7F0, .rom_size = 0x00000000 }
```

The companion symbol file places the next entry at
`osContGetReadData = 0x8002ACBC`; there is no generated span to rename. The
runtime wrapper translates the guest queue pointer and calls the host
`osContStartReadData` implementation.

The bounded rename helper reported `renamed 0 references in 0 files` and
classified the candidate as `already-synchronized`. Preserve the
`osContStartReadData_recomp` ABI name. No build or soak was warranted.

Discriminator result: H-host-wrapper. This is single-source source-audit
evidence, independently supported by the companion boundary, generated
caller/overlay grep, and runtime wrapper definition.
