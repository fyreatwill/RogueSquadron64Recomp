# Session 2534 generated-symbol census

## Region table

| Address | Span | Generated body | Companion symbol | Source/m2c/caller evidence | Result |
|---|---:|---|---|---|---|
| `0x8009711C` | 4 bytes | `j 0x8009713C` | `fake_func_8009711C` | No exact-address human symbol or m2c definition. The jump target `0x8009713C` is the third instruction of the named `bindMacroIdsToSoundGroup` function at `0x80097130`; the nearby named function is `resetSongSubsystemCounter` at `0x80097120`. | `H-no-match`; unchanged |

The active generated implementation, declaration, overlay table, project
symbol input, and companion symbol file agree on the 4-byte span and fake
name. The fragment is a jump into a neighboring function rather than an
independently evidenced callable function. Naming it after either neighbor
would change the boundary representation without a defensible human mapping.

No generated code or build was changed because no regeneration-safe rename was
identified.
