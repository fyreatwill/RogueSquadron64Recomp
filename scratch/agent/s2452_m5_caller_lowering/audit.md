# s2452 caller-boundary audit

Date: 2026-08-26

Retail `0x8002BEEC` is not a generated game-function address. The symbol table
places it at the final instruction of `__osDispatchThread`, whose range is
`0x8002BD74..0x8002BEEF`; `__osCleanupThread` begins at `0x8002BEF0`. The
generated tree has no `__osDispatchThread` body or `0x8002BEEC` label.

The known generated alternate is in `funcs_23.c`:

```text
0x8008F2BC: addu  a0, v0, zero
0x8008F2C0: addu  a1, zero, zero
0x8008F2C8: sw    a0, -0x689C(at)
0x8008F2CC: jal   0x800078E0
0x8008F2D0: addiu a2, zero, 0x298
           rs_memset(rdram, ctx); goto after_6;
0x8008F2D4: lui   a0, 0x8015
0x8008F2D8: lw    a0, -0x689C(a0)
0x8008F2DC: jal   0x800358B0
```

The continuation reloads the result for `osWritebackDCache`, but it is a
distinct generated function/path from the retail dispatcher boundary. The
complete generated direct-call census contains 88 `jal 0x800078E0` sites; none
is at `0x8002BEEC`.

Selected: `H-DifferentGeneratedBoundary`. This is a static structural result;
it does not identify the port-side runtime replacement and authorizes no
behavior change.

ORIGIN: retail ELF symbol ranges and generated source inventory; the alternate
call/continuation is in `RecompiledFuncs/funcs_23.c`.
