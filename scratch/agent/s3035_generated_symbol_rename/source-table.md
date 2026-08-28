# Session 3035 — `0x80099FDC` generated-symbol audit

| Evidence source | Observation | Result |
|---|---|---|
| Companion `main_overlay.txt` | `fake_func_80099FDC = 0x80099FDC`; comment says there is no accompanying real function. | No human identity is available. |
| Project `syms/rogue_squadron.syms.toml` | Placeholder entry is `fake_func_80099FDC`, size `0x4`; the next named entry is `findVoiceSlotByAge` at `0x8009AF60`. | The one-word size is inconsistent with the generated body and is not sufficient evidence of a callable boundary. |
| Generated `funcs_26.c` | `fake_func_80099FDC` starts at `0x80099FDC`, contains the interrupt/COP2 setup and audio/resource initialization sequence, and continues through `0x8009AF5C`, ending with `jr $t0` / `return`. | This is a large indirect-return routine, not a one-word fragment. |
| Generated next definition | `findVoiceSlotByAge` begins at `0x8009AF60` with its own prologue. | Boundary at `0x8009AF60` is independently supported. |
| Generated declarations/registration | `funcs.h` and `recomp_overlays.inl` use `fake_func_80099FDC`; the overlay entry spans ROM offset `0x00099B9C` with size `0xF84`. | Generated registration preserves the placeholder and does not supply a semantic name. |
| Direct callers / alternate definition | No direct generated caller or duplicate definition was found for `fake_func_80099FDC`. | No caller contract or duplicate resolves the identity. |

## Discriminator result

Selected `H-inline-fragment`/unresolved-boundary handling. The body is clearly
larger than the stale one-word symbol entry, but neither the companion map nor
the generated artifacts provide a safe human name. Preserve
`fake_func_80099FDC`; do not synthesize a callable or address-coded semantic
rename. No game behavior was changed.

