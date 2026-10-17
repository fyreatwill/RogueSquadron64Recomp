# Session 5113 rename audit: `osContStartQuery`

Candidate: companion symbol `osContStartQuery = 0x8002AB80`.

The generated snapshot has no `func_8002AB80` or `fake_func_8002AB80`
prologue/body. It has four direct generated callers, all calling
`osContStartQuery_recomp` through the runtime ABI (`funcs_0.c` once and
`funcs_2.c` three times), plus the declaration in `funcs.h`.

The overlay table entry is:

```text
{ .func = osContStartQuery_recomp, .offset = 0x0002A740, .rom_size = 0x00000000 }
```

The companion symbol file places the next entry at `osContGetQuery =
0x8002AC04`; this candidate therefore does not have a generated span to
rename. The host wrapper extracts the guest queue pointer and calls the
runtime `osContStartQuery`, whose implementation sends the SI message and
returns zero.

The bounded rename helper reported `renamed 0 references in 0 files` and
classified the candidate as `already-synchronized`. Preserve the
`osContStartQuery_recomp` ABI name. No build or soak was warranted.

Discriminator result: H-host-wrapper. This is single-source source-audit
evidence, independently supported by the generated caller/overlay grep and
the runtime wrapper implementation.
