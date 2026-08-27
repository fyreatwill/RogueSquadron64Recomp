# Session 2568 generated-symbol census

Target: `0x801044D8–0x801044DF` in the mission overlay.

| Check | Result |
|---|---|
| Complete generated span | `0x801044D8`: `sh v1,0x10C(v0)`; `0x801044DC`: `addu a0,zero,zero`. |
| Previous named symbol | `lv6_dispatchStageTick` ends at `0x801044D7`; the active generated overlay entry is 0x24 bytes at `0x801044B4`. |
| Following named symbol | `lv7_checkComplexObjectives` begins at `0x801044E0`; the active generated entry is 0x52C bytes. |
| Companion symbol result | `fake_func_801044D8` is retained explicitly, followed by `// real function is lv7_checkComplexObjectives`. |
| Active project/generated names | `syms/rogue_squadron.syms.toml`, `funcs.h`, `funcs_45.c`, and `recomp_overlays.inl` all retain `fake_func_801044D8`. |
| Exact candidate search | No alternate human symbol, source/m2c definition, or caller match was found for `0x801044D8` / `fake_func_801044D8`. |
| Semantic candidate | None defensible: the span has no callable prologue, return, or complete body and ends with a delay-slot register setup before the next function. |

## Decision

`H-data-or-boundary` is selected at static scope. `H-human-candidate` and
`H-already-mapped` are unsupported; `H-uncertain` is not selected because the
span and both neighboring boundaries are explicit. The placeholder remains
unchanged. This is a static, single-source conclusion: no runtime reachability
or origin claim follows, and no build was required.
