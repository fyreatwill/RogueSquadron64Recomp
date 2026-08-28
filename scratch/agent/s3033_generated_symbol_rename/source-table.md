# Generated-symbol audit: `0x8006B704`

## Discriminator

The candidate is an exact callable only if the companion map, generated
function boundaries, callers, header, and overlay registration agree on a
human identity. A boundary-only fragment is preserved as a placeholder; a
conflict is recorded as ambiguous.

## Evidence table

| Evidence source | Observation | Result |
|---|---|---|
| Companion symbol/source map | `main_overlay.txt` contains only `fake_func_8006B704 = 0x8006B704`; no m2c/source identity or descriptive name is present. | No exact companion rename. |
| Generated body/boundary | `funcs_16.c` registers a `0xC`-byte body: `sw a1, 0(a0)` at `0x8006B704`, `addiu a2, fp, 0x28` at `0x8006B708`, and `lw a0, 0x5C(fp)` at `0x8006B70C`; it has no `jr`, return, or callable epilogue. The next generated function begins at `0x8006B710` as `loadCraftShadowTextures`. | Inline/fragment-shaped; not a supported callable boundary. |
| Direct generated callers | No call-site reference to `fake_func_8006B704`, `func_8006B704`, or the address exists outside its own generated definition. | No caller evidence for a semantic identity. |
| Header declaration | `funcs.h` has one declaration for `fake_func_8006B704`, generated from the artificial boundary. | Mechanical artifact only. |
| Overlay registration | `recomp_overlays.inl` registers the token at ROM offset `0x6B2C4` with size `0xC`, matching the fragment exactly. | Confirms registration, not callable semantics. |
| Project symbol TOML | `syms/rogue_squadron.syms.toml` has the same placeholder and `0xC` size. | Already synchronized; no edit required. |
| Local duplicate definitions | The token occurs once as a generated definition and once each in the header and overlay registration; no second definition exists. | No duplicate identity conflict. |

## Decision

Preserve `fake_func_8006B704`. The evidence supports only a generated
boundary/inline fragment classification, not a human-mapped callable name or
a safe `data_gap_*` rename. The positive control was visible: the generated
token, header declaration, overlay registration, and project TOML all formed
the expected synchronized registration set.

## Next cursor

The next generated placeholder after `0x8006B704` is `0x8007C298` in
`funcs_19.c`.
