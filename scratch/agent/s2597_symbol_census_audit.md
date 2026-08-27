# s2597 generated-symbol census: `0x800CEF1C`

## Result

Selected `H-BoundaryOnly`. No rename was added.

## Discriminating table

| Evidence source | Observation | Outcome |
|---|---|---|
| Generated output | `funcs_37.c` defines `fake_func_800CEF1C` as one instruction, `sw $s1, 0x44($sp)`, ending at `0x800CEF20`. | Boundary fragment, not a complete body |
| Generated neighbors | The preceding body ends at `0x800CEF18`; the next complete body starts at `0x800CEF20` as `advanceAtStEffectPhaseSound`. | Address is an isolated entry fragment |
| Companion symbols | `mission_overlay.txt` retains `fake_func_800CEF1C`; its comment says `func_800CEF20` was deleted as a duplicate-symbol collision with `advanceAtStEffectPhaseSound`. | No companion semantic name for the placeholder |
| Exact source/m2c/caller search | No exact-address source, m2c, caller, or alternate-name match was found. | No independent mapping |
| Rename generator | `build_redefs.py` completed; `redefs.txt` contains the `0x800CEF20` mapping but no `fake_func_800CEF1C` mapping. | Tool inputs agree that the placeholder stays unresolved |

The instruction is a stack-save fragment adjacent to the next function's entry,
not enough evidence for a semantic function name. It remains unchanged.

