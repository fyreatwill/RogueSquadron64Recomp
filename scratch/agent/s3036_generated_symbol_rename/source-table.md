# Session 3036 — generated symbol audit at `0x8009C2C8`

| Evidence field | Observation | Selection |
|---|---|---|
| Companion symbol/source | `main_overlay.txt` retains `fake_func_8009C2C8 = 0x8009C2C8` and immediately identifies `computeVoicePanCoefficients = 0x8009C2D0`; no human identity is supplied for the target. | H-inline-fragment |
| Generated prologue/body boundary | `funcs_27.c` emits exactly two instructions at the target: `mul.s $f2,$f2,$f4` and `add.s $f0,$f0,$f2`, followed immediately by the standalone `computeVoicePanCoefficients` prologue at `0x8009C2D0`. The fragment has no return or callable epilogue. | H-inline-fragment |
| Direct callers | No generated call site references `fake_func_8009C2C8`; callers reference `computeVoicePanCoefficients` instead. | H-inline-fragment |
| Header declaration | `funcs.h` contains a declaration because the generated overlay table exposes every emitted label, but this is not evidence of a callable boundary. | H-inline-fragment |
| Overlay registration | `recomp_overlays.inl` registers the target at offset `0x0009BE88` with `rom_size = 0x8`, matching the two-instruction fragment and not a callable body. | H-inline-fragment |
| Project symbol TOML | `syms/rogue_squadron.syms.toml` agrees with the generated placeholder and 8-byte size. | H-inline-fragment |

## Result

Preserve `fake_func_8009C2C8`. The positive control is visible in both the
generated function definition and overlay registration. The evidence rules out
an exact companion rename and a callable-boundary interpretation; renaming
would invent a symbol for an inline floating-point expression.
