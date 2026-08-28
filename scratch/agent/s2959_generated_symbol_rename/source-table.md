# Session 2959 generated-symbol source table

Candidate: `0x800B2628`, current name `fake_func_800B2628`, menu overlay,
size `0x8`.

| Evidence | Result | Discrimination |
|---|---|---|
| Complete generated body | `0x800B2628: lwc1 $f0, -0x5D04($at)` followed by `0x800B262C: swc1 $f0, 0x168($v0)` | Valid instruction fragment, not an invalid-decode trap or data-only gap |
| Predecessor boundary | `playExitSoundAndToggleScreenMeshes` occupies `0x800B2564–0x800B2627` and ends with `jr $ra`/delay-slot stack restore at `0x800B2620–0x800B2624` | Candidate does not continue the predecessor's callable body |
| Successor boundary | `buildFormatMessageGlyphBuffer` begins at `0x800B2630` with stack allocation and saved registers | Candidate has no prologue and does not begin the successor |
| Return/prologue evidence | No `jr $ra`, stack frame setup, saved return address, or independent entry sequence in the 8-byte span | H-Callable not supported |
| Companion symbol map | `../rogue_squadron64/symbol_files/menu_overlay.txt` retains only `fake_func_800B2628`; no semantic name or description exists | No exact callable rename available |
| Generated/source callers and lookups | Exact searches for `fake_func_800B2628`/`0x800B2628` find only the generated declaration/body, overlay registration, and symbol-map entries; no call or independent lookup | No callable use established |
| Alternate source/m2c evidence | No `0x800B2628` reference under the companion `src/`, `docs/`, `include/`, or `tools/` trees | No second source identifies a function |

## Decision

H-Fragment selected. The two stores are a valid executable fragment, so this
is not a mechanically proven data gap; absent a prologue, return, callable
reference, or exact companion name, renaming it would invent semantics. Keep
`fake_func_800B2628` unchanged in all generated and source maps.
