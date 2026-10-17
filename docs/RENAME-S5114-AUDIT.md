# Session 5114 rename audit: `osContGetQuery`

Candidate: companion symbol `osContGetQuery = 0x8002AC04`.

The generated snapshot has no `func_8002AC04` or `fake_func_8002AC04`
prologue/body. It has four direct generated callers, all calling
`osContGetQuery_recomp` through the runtime ABI (`funcs_0.c` once and
`funcs_2.c` three times), plus the declaration in `funcs.h`.

The overlay table entry is:

```text
{ .func = osContGetQuery_recomp, .offset = 0x0002A7C4, .rom_size = 0x00000000 }
```

The companion symbol file places the next entry at
`osContStartReadData = 0x8002AC30`; this candidate therefore has no generated
span to rename. The runtime wrapper translates the guest `OSContStatus*` and
calls the host `osContGetQuery`, which fills the status data through the
runtime input implementation.

The bounded rename helper reported `renamed 0 references in 0 files` and
classified the candidate as `already-synchronized`. Preserve the
`osContGetQuery_recomp` ABI name. No build or soak was warranted.

Discriminator result: H-host-wrapper. This is single-source source-audit
evidence, independently supported by the generated caller/overlay grep and
the runtime wrapper implementation.
