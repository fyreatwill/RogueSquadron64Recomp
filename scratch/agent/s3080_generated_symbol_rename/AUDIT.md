# Session 3080 generated-symbol audit

Target: `0x8005C61C` (`fake_func_8005C61C`)

| Surface | Observation | Result |
|---|---|---|
| Companion map | Four-byte record immediately before `checkTrackedNpcProximityForCue`; no semantic annotation or companion caller | H-Fragment |
| Generated body | One instruction: `addu $v1, $v1, $a0`; no prologue, return sequence, or independent body | H-Fragment |
| Callers | Generated callsite targets `checkTrackedNpcProximityForCue` at `0x8005C620`; no call targets `0x8005C61C` | H-Fragment |
| Header | Standalone generated declaration existed only because the symbol table exposed the four-byte record | H-Fragment |
| Overlay registration | ROM offset `0x0005C1DC`, size `0x4`, matching the isolated instruction | H-Fragment |
| Project TOML | VRAM `0x8005C61C`, size `0x4`, matching the companion and generated registration | H-Fragment |

Conclusion: no independent semantic identity is defensible. The symbol was
renamed mechanically to `data_gap_8005C61C` in the companion map, project TOML,
regeneration rename mapping, generated definition/declaration, and overlay
registration. The former `checkTrackedNpcProximityForCuePreamble` convenience
mapping was removed because the one instruction is not an independently named
callable preamble. This is a naming-only change; no runtime, audio, or
instruction behavior changed.
