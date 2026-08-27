# s2551 generated-symbol census: `0x800CC3D4`

## Region table

| placeholder | complete generated span | candidate | evidence | confidence | result |
|---|---|---|---|---|---|
| `fake_func_800CC3D4` | `0x800CC3D4–0x800CC9B7` (`0x114C` bytes) | none | The generated overlay entry has `rom_size=0x114C`; its end is exactly `0x800CC9B8`, where `tickAtAtAudioAndWeaponState` begins. The active C body is only the regeneration gap-filler trap. The companion menu symbol file retains the fake name and has no human function at the address. It instead declares menu-overlay data beginning at `hangarCameraState` (`0x800CC3E4`) and continuing through the region (`hangarShipShadowFaces`, bridge tables/colors, and menu colors). Exact-address/source/m2c/caller searches found no candidate. | high for boundary classification; single-source static evidence | `H-data-boundary` / `H-no-match`; unchanged |

## Competing hypotheses and discriminator

- `H-named-match`: an exact companion or local semantic function name exists.
- `H-no-match`: no defensible function mapping exists.
- `H-data-boundary`: the generated placeholder represents a data/conversion
  boundary rather than a callable function.
- `H-regeneration-risk`: a possible name exists but cannot be carried safely
  through the active rename path.

The discriminating measurement was the complete region table above: span end,
instruction/body shape, symbol/data coverage, exact-address/source/m2c/caller
matches, and resulting diff. The exact end alignment with the next function,
the trap-only generated body, and companion data labels select
`H-data-boundary`; absence of a human mapping also selects `H-no-match`.
There is no rename candidate to validate, so `H-regeneration-risk` is not
reached.

## Commands and result

The required session-title preflight, generated/companion exact-address
searches, bounded generated-body inspection, companion symbol window, and
next-placeholder census all completed successfully. No build or runtime run
was warranted: renaming this data boundary would be speculative and would not
change generated behavior.

ORIGIN: diagnostic-only. No generated code, symbol input, runtime, or
mitigation-shaped behavior changed.
