# Session 3079 generated-symbol audit

Target: `0x80059B4C` (`fake_func_80059B4C`)

| Surface | Observation | Result |
|---|---|---|
| Companion map | Four-byte record immediately before `mat34CrossRowsAndCopyPos`; no semantic annotation or companion caller | H-Fragment |
| Generated body | One instruction: `sw $fp, 0x48($sp)`; no prologue, return sequence, or independent body | H-Fragment |
| Callers | No generated callsite targets `0x80059B4C`; callers target `mat34CrossRowsAndCopyPos` at `0x80059B50` | H-Fragment |
| Header | Standalone generated declaration existed only because the symbol table exposed the four-byte record | H-Fragment |
| Overlay registration | ROM offset `0x0005970C`, size `0x4`, matching the isolated instruction | H-Fragment |
| Project TOML | VRAM `0x80059B4C`, size `0x4`, matching the companion and generated registration | H-Fragment |

Conclusion: no independent semantic identity is defensible. The symbol was
renamed mechanically to `data_gap_80059B4C` in the companion map, project TOML,
generated definition/declaration, and overlay registration. This is a
naming-only change; no runtime, audio, or instruction behavior changed.
