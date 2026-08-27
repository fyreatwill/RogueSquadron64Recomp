# Session 2537 — generated-symbol census at `0x80099C4C`

## Discriminator

| Region | Candidate | Evidence | Result |
|---|---|---|---|
| `0x80099C4C–0x80099C4F` (4 bytes) | none | Project TOML, generated declaration/implementation/overlay table, companion `main_overlay.txt`, exact-address repository search, and ROM bytes | `H-no-match`; unchanged |

## Boundary and bytes

- `recomp_overlays.inl` gives ROM offset `0x0009980C` and size `0x4`, followed immediately by the independently named `transformVec3ByAffineMatrix` at `0x80099C50` with size `0xAC`.
- The retail ROM at that offset is `af b2 00 38`, the instruction `sw s2, 0x38(sp)`. It does not establish a function-level name or callable entry semantics by itself.
- The active generated body is a trap. The fixup report records that the original conversion was neutered because of missing label `L_80099C88`. This is a converter/boundary artifact, not evidence that the instruction is dead or safe to rename.

## Provenance checks

- `syms/rogue_squadron.syms.toml` and the companion symbol file both retain `fake_func_80099C4C`.
- The companion file names the next function `transformVec3ByAffineMatrix`; no source, m2c, caller, or exact-address search produced a name for `0x80099C4C`.
- No generated code, symbol input, or runtime behavior was changed.

This is a static, single-source result. The next bounded unresolved main-overlay placeholder is `0x80099FDC`.
