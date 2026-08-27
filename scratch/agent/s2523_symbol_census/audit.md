# Session 2523 symbol census

Selected interval: `0x8006F4AC–0x8006F4AC` in the main overlay, the next
unresolved placeholder after `0x8006D8FC`.

| VRAM | Generated symbol | Body / boundary | Companion evidence | Result |
|---|---|---|---|---|
| `0x8006F4AC` | `fake_func_8006F4AC` | `funcs_17.c` contains only `addiu sp, sp, 0x30`; generated size and overlay entry are `0x4`. It is immediately after `getSecondaryWeaponCount` (`0x8006F43C`, size `0x70`) and before `spawnDestructionDebris` (`0x8006F4B0`). | `rogue_squadron64/symbol_files/main_overlay.txt` retains `fake_func_8006F4AC = 0x8006F4AC`. Exact-address search over the companion tree found no named definition, m2c implementation, or caller attribution. | No defensible human rename. |

The repository generation artifacts agree on the placeholder and its four-byte
ROM span: `funcs.h`, `funcs_17.c`, and `recomp_overlays.inl`. The companion
symbol file also explicitly marks it fake. This is a static, single-source
result: the isolated prologue may be a function-boundary artifact, but there
is no evidence to choose a name. No generated code or runtime behavior was
changed, and no build was warranted.

Hypothesis result: `H-no-match` for this bounded region. `H-named-match` and
`H-regeneration-risk` were not selected because no rename candidate existed.
