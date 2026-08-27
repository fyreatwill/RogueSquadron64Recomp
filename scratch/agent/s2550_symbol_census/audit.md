# Session 2550 symbol census: `0x800CC038`

## Discriminating table

| Placeholder | Complete span | Generated body | Companion evidence | Classification | Change |
|---|---|---|---|---|---|
| `fake_func_800CC038` | `0x800CC038–0x800CC03F` (8 bytes) | `swc1 $f0,0x40($fp)`; `addiu $v0,$fp,0x20` | `menu_overlay.txt` retains `fake_func_800CC038`; the next menu symbol is `loadMedalInfo = 0x800CC040`. No companion source, m2c body, exact-address caller, or human name was found. | `H-data-boundary` / `H-no-match`: a menu-overlay fragment at a shared VRAM address boundary, not a complete callable body. | Leave unchanged. |

## Boundary checks

- The active menu symbol TOML and generated overlay table agree on the fake
  symbol and its 8-byte span, followed by `loadMedalInfo` at `0x800CC040`.
- The same VRAM window is occupied by the mission overlay's independently
  named `initActorFromSpawnTemplate` at `0x800CC03C`; its preceding mission
  function ends at `0x800CC038`. This is an overlay-shared address window, so
  borrowing the mission name or the menu `loadMedalInfo` name would be wrong.
- The generated function has no prologue, return, jump, or complete callable
  boundary. The two instructions are therefore insufficient for a defensible
  semantic rename.

## Result

The discriminator selects `H-data-boundary` / `H-no-match`. No generated code,
symbol input, fixup script, runtime, or behavior changed.
