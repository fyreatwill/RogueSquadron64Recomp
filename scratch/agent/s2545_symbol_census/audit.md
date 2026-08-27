# Session 2545 generated-symbol census

## Region table

| Placeholder | Complete span | Generated body / neighbors | Companion and source evidence | Result |
|---|---|---|---|---|
| `fake_func_800AEC54` | `0x800AEC54–0x800AEC5F` (12 bytes) | The active overlay table gives `rom_size=0xC`. `funcs_29.c` emits a trap-only gap-filler body. `hangarUpdateSecWeaponIfChanged` ends at `0x800AEC54`; `initCraftSelectScreen` begins at `0x800AEC60`. | `rogue_squadron64/symbol_files/menu_overlay.txt` retains the same fake name. Exact-address searches across companion source, m2c, and symbol files found no human or m2c definition. The nearby craft-selection names describe adjacent functions, not this span. | Leave unchanged: `H-data-boundary` / `H-no-match`. |

## Discriminator

The complete span has no prologue, return, or callable body in the generated
output; it is explicitly represented as decoded data bytes that cannot be
executed safely. The companion project also preserves the placeholder and has
no exact-address candidate. Renaming it to either neighboring function would
change established function boundaries, so no regeneration-safe rename exists.

## Evidence commands

```sh
rg -n 'fake_func_800AEC54|800AEC54' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 10 'fake_func_800AEC54' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_29.c
rg -n -i 'AEC54|fake_func_800AEC54' /Users/williambuckley/Documents/Tools/rogue_squadron64/src /Users/williambuckley/Documents/Tools/rogue_squadron64/m2c /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

No generated code, symbol input, runtime, or mitigation-shaped behavior was
changed.
