# Session 2524 symbol census

Selected interval: `0x80072CE8–0x80072CE8` in the main overlay, the next
unresolved placeholder after `0x8006F4AC`.

| VRAM | Generated symbol | Body / boundary | Companion evidence | Result |
|---|---|---|---|---|
| `0x80072CE8` | `fake_func_80072CE8` | `funcs_18.c` contains only `addiu v1, v1, -0x4160` followed by `addu v0, v1, v0`; generated size and overlay entry are `0x8`. It is immediately after `walkDatTreeAndScaleLeafByFloat` (`0x80072BE0`, size `0x108`) and before `initWaterSprayParticles` (`0x80072CF0`). | `rogue_squadron64/symbol_files/main_overlay.txt` retains `fake_func_80072CE8 = 0x80072CE8`. Exact-address and name searches over the companion tree found no human definition, m2c implementation, or caller attribution. | No defensible human rename. |

The repository generation artifacts agree on the placeholder and its eight-byte
ROM span: `funcs.h`, `funcs_18.c`, and `recomp_overlays.inl`. The companion
symbol file explicitly marks it fake. This is a static, single-source result:
the two-instruction fragment may be a function-boundary artifact, but there is
no evidence to choose a name. No generated code or runtime behavior was
changed, and no build was warranted.

Hypothesis result: `H-no-match` for this bounded region. `H-named-match` and
`H-regeneration-risk` were not selected because no rename candidate existed.
