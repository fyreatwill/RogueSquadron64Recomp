# Session 3100 — `0x800AE3E4` six-surface audit

| Surface | Finding |
|---|---|
| Project TOML | Mission entry `fake_func_800AE3E4`, VRAM `0x800AE3E4`, size `0xC`; successor `initPlayerCraftTrailBuffers` starts at `0x800AE3F0`. |
| Companion maps | Mission retains the placeholder; menu independently names `tickEasedCameraKeyframeBlend` at `0x800AE3EC`, overlapping the final word. No exact identity is supplied. |
| Generated body | `funcs_28.c` contains only `lwc1 $f0,0x58($fp)`, `lwc1 $f2,0xC4($fp)`, and `mul.s $f0,$f0,$f2`; no prologue, return, or complete callable path. |
| Generated callers | No generated call or independent absolute lookup targets the placeholder; only declaration, definition, and registration remain. |
| Header / overlay registration | Generated declaration and mission `recomp_overlays.inl` agree on the 12-byte placeholder extent. |
| Rename tooling / duplicates | `tools/rename_generated_symbols.py` has no mapping; the sweep scanner stops here as unresolved. |

## Disposition

H-ExactIdentity is rejected: no exact semantic companion or callable
contract. H-Fragment is supported by the instruction-only body and missing
callable edges, but H-Ambiguous remains the safe disposition because these are
executable bytes rather than a proven data gap and the overlay overlap makes
both a semantic rename and `data_gap_*` unsafe. Preserve
`fake_func_800AE3E4` in all project and generated surfaces. This static,
regeneration-safe result says nothing about runtime reachability.
