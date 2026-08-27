# Session 2525 symbol census

Selected interval: `0x80079278–0x80079278` in the main overlay, the next
unresolved placeholder after `0x80072CE8`.

| VRAM | Generated symbol | Body / boundary | Companion evidence | Result |
|---|---|---|---|---|
| `0x80079278` | `fake_func_80079278` | `funcs_19.c` contains an 8-byte boundary fragment: `nop` at `0x80079278` followed by `lw a0, 0x1C(fp)` at `0x8007927C`. It is immediately before the named `heavyMechSubEffectNpcHandler` at `0x80079280`; `recomp_overlays.inl` and `syms/rogue_squadron.syms.toml` both assign it an 8-byte span. | `rogue_squadron64/symbol_files/main_overlay.txt` retains `fake_func_80079278 = 0x80079278`. Exact-address and name searches over the companion source, symbols, and docs found no human definition, m2c implementation, caller attribution, or semantic candidate. | No defensible human rename. |

The generated artifacts agree on the placeholder and its boundary. The
two-instruction body is consistent with a padding or function-boundary
artifact, and the adjacent named handler accounts for the following address;
there is no evidence to rename the fragment itself. This is a static,
single-source result. No generated code or runtime behavior was changed, and
no build was warranted.

Hypothesis result: `H-no-match` for this bounded region. `H-named-match` and
`H-regeneration-risk` were not selected because no rename candidate existed.
