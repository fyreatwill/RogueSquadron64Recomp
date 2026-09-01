# M5 s3529 selector input boundary

The retail oracle passed its whole-RDRAM positive control and observed
`0x8009192C`/`0x80091934`; retail loaded `a1=0x561F`. The same-build port
passed startup and title/hangar controls and observed `0x5622` at the
`0x8009192C` load, while existing allocator and selector-store witnesses
remained live.

This selects `H-InputLoadDivergence` and moves the next boundary to the
writer/source of `MEM_W(0x80165ED0)`, not the call ABI or allocator. The
oracle's hangar origin was `0x006AB800`, so its stale `0x006AB400` bucket was
not used as evidence.

Captures: `scratch/agent/s3529_selector_input_oracle/run.log` and
`scratch/agent/s3529_selector_input_port/run.log`.
