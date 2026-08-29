# Session 3160 — bounded callable-placeholder census

## Discriminator

The generated snapshot and companion `symbol_files` were scanned for every
placeholder in `0x800A0000..0x800B0000`.

| Address | Generated record | Companion record | Generated body | Generated callers | Decision |
|---|---|---|---|---|---|
| `0x800A2114` | `static_3_*` in `funcs_49.c` | none | 166 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2218` | `static_3_*` in `funcs_49.c` | none | 265 lines | 1 in `funcs_27.c` | preserve |
| `0x800A23BC` | `static_3_*` in `funcs_49.c` | none | 263 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2558` | `static_3_*` in `funcs_49.c` | none | 360 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2790` | `static_3_*` in `funcs_49.c` | none | 254 lines | 1 in `funcs_27.c` | preserve: invalid/decode-fragment shape |
| `0x800A2924` | `static_3_*` in `funcs_49.c` | none | 103 lines | 1 in `funcs_27.c` | preserve |
| `0x800A29BC` | `static_3_*` in `funcs_49.c` | none | 270 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2B50` | `static_3_*` in `funcs_49.c` | none | 125 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2BE4` | `static_3_*` in `funcs_49.c` | none | 443 lines | 1 in `funcs_27.c` | preserve: invalid/decode-fragment shape |
| `0x800A2E98` | `static_3_*` in `funcs_49.c` | none | 92 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2F28` | `static_3_*` in `funcs_49.c` | none | 112 lines | 1 in `funcs_27.c` | preserve |
| `0x800A2FE4` | `static_3_*` in `funcs_49.c` | none | 617 lines | 1 in `funcs_27.c` | preserve: invalid/decode-fragment shape |
| `0x800A50AC` | `static_3_*` in `funcs_49.c` | none | 158 lines | 1 in `funcs_27.c` | preserve |
| `0x800AE3E4` | `fake_func_*` in `funcs_28.c` | `fake_func_800AE3E4` | 12-byte overlay record | 0 direct call; overlay registration only | preserve: companion marks fake |

The companion map has no non-fake name for any of the 14 addresses. The
generated tree independently confirms the 13 static records have bodies and
one generated caller each, while `0x800AE3E4` is only an overlay entry. The
bounded rename helper, run with the same bounds, reported
`renamed 0 references in 0 files`.

## Result

`H-AmbiguousFragments` is selected. `H-SemanticMatches` and
`H-NoReachablePlaceholder` are ruled out for this band: there are no exact
semantic companion callable names, but the static records do have generated
bodies and callers. No generated symbol or runtime behavior was changed.
