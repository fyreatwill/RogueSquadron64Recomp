# Session 2569 generated-symbol census

Target: `0x80105B54–0x80105B5F` in the mission overlay.

| Check | Result |
|---|---|
| Complete generated span | `0x80105B54`: `addu v1,v1,a0`; `0x80105B58`: `lwc1 f0,0x8(v0)`; `0x80105B5C`: `lwc1 f2,0x8(v1)`. |
| Previous named symbol | `lv9_calculateFriendliesSaved` occupies `0x80105B08–0x80105B53`. |
| Following named symbol | `lva_initializeObjectTracking` begins at `0x80105B60` and occupies `0x2C8` bytes. |
| Companion symbol result | `fake_func_80105B54` is retained explicitly, followed by `// real function is lva_initializeObjectTracking`. |
| Active project/generated names | `syms/rogue_squadron.syms.toml`, `funcs.h`, `funcs_47.c`, and `recomp_overlays.inl` all retain `fake_func_80105B54`. |
| Exact candidate search | No alternate human symbol, source/m2c definition, or caller match was found for `0x80105B54` / `fake_func_80105B54`. |
| Semantic candidate | None defensible: the span has no prologue, return, or complete callable body; it adjusts a pointer and loads two float fields before the next function. |

## Decision

`H-data-or-boundary` is selected at static scope. `H-human-candidate` and
`H-already-mapped` are unsupported; `H-uncertain` is not selected because the
span and both neighboring boundaries are explicit. The placeholder remains
unchanged. This is a static, single-source conclusion: no runtime reachability
or writer/origin claim follows, and no build was required.
