# Session 3024 — `0x8003DFA0`

| Evidence source | Observation |
|---|---|
| Companion symbol map | `mainGameLoop = 0x8003DFA0`, documented as the outer game loop entered from `gBootConfig+0x04`. |
| Generated body | `funcs_8.c` contains one standalone `RECOMP_FUNC void mainGameLoop(...)` definition spanning the mapped `0x5BC` bytes. |
| Generated callers | Eight `mainGameLoop` caller-boundary sites occur in the generated body; no conflicting `func_8003DFA0` callable reference was found. |
| Header | `funcs.h` declares `mainGameLoop` once. |
| Overlay registration | `recomp_overlays.inl` registers `mainGameLoop` at offset `0x0003DB60` with `rom_size = 0x000005BC`. |
| Project symbol TOML | The only mismatch was `{ name = "func_8003DFA0", vram = 0x8003DFA0, size = 0x5BC }`; synchronized to `mainGameLoop`. |
| Sweep scanner | Reported one coherent generated match; its stop was caused by the stale placeholder name rather than a callable collision. |

Conclusion: synchronize the exact companion name. No data-gap classification or manual collision review is needed.
